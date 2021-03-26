import os 

'''
* host : host of redis server
* port : port of redis server
* db : selected database of redis server
* key_length : length of generate key for output suffix
* collision_retry_threshold : 
'''

conf = {
    "host" : "localhost",           
    "port" : 6379,                  
    "db" : 0,                             
    "key_length" : 6, 
    "hash_func" : "sha256",     
    "collision_retry_threshold" : 3,
    "session_secret" : "SimpleSecret",
    "session_expired_days" : 100,
}

if __name__ != '__main__' :
    for k, v in conf.items() :
        os.environ[k] = str(v)