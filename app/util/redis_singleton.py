import redis 
import os

class redis_connection_instance(object) :
    def __new__(self) :
        if not hasattr(self, "instance") :
            pool = redis.ConnectionPool(host=os.environ["host"], port=os.environ["port"], db=os.environ["db"], decode_responses=True)
            self.instance = redis.StrictRedis(connection_pool=pool)
        return self.instance
