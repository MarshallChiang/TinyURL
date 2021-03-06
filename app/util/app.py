import os
import re
import json 
import hashlib
import datetime
from urllib.parse import urlparse
from typing import Optional, final
'''
retreive connected redis instance in pool to excute command.
'''

max_retry = int(os.environ["collision_retry_threshold"])
hash_func = os.environ["hash_func"]
hash_len = int(os.environ["key_length"])


class ProtocolObject :
    
    def __init__(self, output : str = None, messages : list = None) :

        self.output = output
        self.message = messages

    def extract(self) :

        return json.dumps(self.__dict__)

    @classmethod
    def convert(self, f) :
        def function_wrapper(*args, **kwargs) :
            
            output, message = f(*args, **kwargs) 
            return ProtocolObject(output=output, messages=message)

        return function_wrapper
    
    def appendErrors(self, errors) :

        self.message.append(errors)  

class MiddleWare :

    def __init__(self, redis_instance) -> None :

        self.redis_instance = redis_instance
    
    def __hashkey__(self, key : str) -> str:

        hash_func = getattr(hashlib, os.environ["hash_func"])
        salt = datetime.datetime.now().strftime('%s')

        return hash_func((key + salt).encode()).hexdigest()[:hash_len]
    
    def __collision_check__(self, key: str) -> str:

        return self.redis_instance.exists(key)

    def gen_hash(self, key : str) -> str :

        key = self.__hashkey__(key)

        while self.__collision_check__(key) :
            key = self.__hashkey__(key)

        return key
    
    @ProtocolObject.convert
    def store(self, key : str, data, required_hash: bool=False) -> str :

        key, message = key, ""
        
        try :
            if required_hash :
                key = self.gen_hash(key)

            if isinstance(data, (str, int)) :
                self.redis_instance.set(key, data)

            elif isinstance(data, list) :

                for d in data :
                    self.redis_instance.lpush(key, d)

            elif isinstance(data, dict) :
                r = self.redis_instance.hset(key, mapping=data)

        except Exception as e :
            message = e 

        finally :

            return key, message

    @ProtocolObject.convert
    def fetch(self, key : str, filters : str = None) -> str :

        key_type = self.redis_instance.type(key)
        output, message = None, ""

        try :
            if key_type == "str" :
                output = self.redis_instance.get(key)

            elif key_type == "list" and isinstance(filters, tuple): 
                output =  self.redis_instance.lrange(key , filters[0], filters[1])

            elif key_type == "hash" :
                output = self.redis_instance.hgetall(key)

        except Exception as e :
            message = e

        finally :

            return output, message

    @ProtocolObject.convert
    def increment(self, key : str, incrby : int = 1, field : str = None) :

        key_type = self.redis_instance.type(key)
        output, message = None, ""

        try :

            if key_type == "str" : 

                if not incrby : 
                    output = self.redis_instance.incr(key)

                else :
                    output = self.redis_instance.incrby(key, incrby)
            
            elif key_type == "hash" and field:
                output = self.redis_instance.hincrby(key, field, incrby)

        except Exception as e :
            message = e

        finally :

            return output, message

    @ProtocolObject.convert
    def update(self, key : str, data : str, field : str = None, force_update=False) :

        key_type = self.redis_instance.type(key)
        output, message = None, ""

        try :

            if key_type == "str" :

                if force_update :
                    output = self.redis_instance.set(key ,data)

                else :
                    output = self.redis_instance.setnx(key, data)

            elif key_type == "hash" :

                if force_update :
                    output = self.redis_instance.hset(key, field, data)

                else :
                    output = self.redis_instance.hsetnx(key, field, data)

        except Exception as e :
            message = e 

        finally : 

            return output, message

            


class Application(MiddleWare) :

    def __init__(self, redis_instance) :

        super().__init__(redis_instance)
    
    def data_get(self, key: str) -> Optional[str] :
        
        return self.fetch(key).extract()
    
    def data_store(self, **kwargs) -> ProtocolObject :

        if "url" not in kwargs :

            return ProtocolObject("", messages="Input URL is empty.").extract()

        s = urlparse(kwargs["url"])

        if not s.scheme :

            return ProtocolObject("", messages="Incorrect format of input URL.").extract()

        if "session_id" not in kwargs :

            return ProtocolObject("", messages="Invalid user with no session_id.").extract()

        else :
            return self.store(kwargs["url"], dict(kwargs), required_hash=True).extract()
    
    def pageview(self, key, incrby=1) :

        current = int(datetime.datetime.now().strftime("%s"))
        self.update(key, current, field="last_viewed", force_update=True)
        return self.increment(key, field="pageview", incrby=incrby)

    def client_history_update(self, key, data) :
        
        return self.store(key, [data])

    def client_history_get(self, key, filters=(0, -1)) :

        stats = []
        history = json.loads(self.fetch(key, filters=filters).extract())["output"]
        if history : 
            for h in history :  
                stat = json.loads(self.fetch(h).extract())["output"]
                stat["key"] = h
                stats.append(stat)
        return ProtocolObject(stats).extract()
    




if __name__ == '__main__' : 
    import redis_singleton, config
    r = redis_singleton.redis_connection_instance()
    store_result = Application(r).store_data(url='https://www.google.com', session_id='123')
    get_result = Application(r).get_url(json.loads(store_result)["output"])
    add_result = Application(r).pageview(json.loads(store_result)["output"], field="session_id")

        
        
        




        
