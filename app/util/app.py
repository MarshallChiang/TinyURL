import os
import re
import json 
import hashlib
import datetime
from urllib.parse import urlparse
from typing import Optional

'''
retreive connected redis instance in pool to excute command.
'''

max_retry = os.environ["collision_retry_threshold"]
hash_func = os.environ["hash_func"]
hash_len = int(os.environ["key_length"])

class MiddleWare :

    def __init__(self, redis_instance) -> None :
        self.redis_instance = redis_instance
    
    def __hashkey__(self, key) -> str:
        hash_func = getattr(hashlib, os.environ["hash_func"])
        salt = datetime.datetime.now().strftime('%s')
        return hash_func((key + salt).encode()).hexdigest()[:hash_len]


    def store(self, hash_on: str, **kwargs) -> str :
        assert hash_on in kwargs, "%s doesn't exist"%hash_on 
        retry_threshold = int(max_retry)
        retry = 0
        while  retry < retry_threshold:    
            store_key = self.__hashkey__(kwargs[hash_on])
            if self.redis_instance.hsetnx(store_key, hash_on, kwargs[hash_on]) : 
                self.update(store_key, **kwargs)
                break
            retry += 1
        return store_key

    def update(self, key, **kwargs) -> int :
        return self.redis_instance.hset(key, mapping=kwargs)

    def fetch(self, key) -> str :
        return self.redis_instance.hgetall(key)

class ProtocolObject :
    
    def __init__(self, output : str, message : str = "" ) :
        self.output = output
        self.message = message

    def extract(self) :
        return json.dumps(self.__dict__)


class Application(MiddleWare) :

    def __init__(self, redis_instance) :
        super().__init__(redis_instance)
    
    def get_url(self, key: str) -> Optional[str] :
        output = self.fetch(key)
        message = "" if output else "Unable to find URL to redirect to."
        return ProtocolObject(output, message=message)
    
    def store_data(self, **kwargs) -> str :
        s = urlparse(kwargs["url"])
        if not (s.scheme and s.path) :
            return ProtocolObject("", message="Incorrect format of input URL.")
        else :
            return ProtocolObject(self.store("url", **kwargs))
        
        
        




        
