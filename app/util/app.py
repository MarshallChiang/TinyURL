import os
import json 
import hashlib
import datetime
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



class Application(MiddleWare) :

    def __init__(self, redis_instance) :
        super().__init__(redis_instance)
    
    def get_url(self, key: str) -> Optional[str] :
        result = self.fetch(key)
        return result if not result else result["url"]
    
    def store_data(self, **kwargs) -> str :
        return self.store("url", **kwargs)
        
        
        




        
