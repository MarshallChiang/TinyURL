import os
import json 
import hashlib
import datetime
from typing import Optional

'''
retreive connected redis instance in pool to excute command.
'''

class storeProcess :


    def __init__(self, redis_instance, strict_mode=True) -> None :

        self.redis_instance = redis_instance
        self.__strict_mode = strict_mode
    
    def __hashkey__(self, key) -> str:

        hash_func = getattr(hashlib, os.environ["hash_func"])
        salt = datetime.datetime.now().strftime('%s')
        return hash_func((key + salt).encode()).hexdigest()[:int(os.environ["key_length"])]


    def store(self, **kwargs) -> str :
        
        retry_threshold = int(os.environ["collision_retry_threshold"])
        retry = 0
        while  retry < retry_threshold:    
            store_key = self.__hashkey__(kwargs['url'])
            if self.redis_instance.hsetnx(store_key, 'url', kwargs['url']) : 
                self.update(store_key, **kwargs)
                break
        return store_key


    def update(self, key, **kwargs) -> int :
        return self.redis_instance.hset(key, mapping=kwargs)
        


class IOProcess(storeProcess) :
    def __init__(self, redis_instance) -> None :
        super().__init__(redis_instance)

    def fetch(self, key: str) -> Optional[str] : 
        query = self.redis_instance.hgetall(key)
        return query
    



        
