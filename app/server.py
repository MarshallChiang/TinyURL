
import tornado.ioloop
import tornado.web
import random
import json
import re
import os

import sys
sys.path.append('/util')
import util.config
from util.redis_singleton import redis_connection_instance
from util.app import Application

redis = redis_connection_instance()


class MainHandler(tornado.web.RequestHandler) : 

    def post(self) -> None :    
        data = json.loads(self.request.body.decode("utf-8"))
        hash_key = Application(redis).store_data(**data)
        self.write(self.request.host + "/%s"%hash_key)
        
        
class PatternRedirectHandler(tornado.web.RequestHandler) : 

    def get(self, path) -> None :
        target = Application(redis).get_url(path)
        target = target if target else '/'
        self.redirect(target)

class PathNotFoundHandler(tornado.web.RequestHandler) :
    def prepare(self):
        self.finish("not found")
    
        
settings = {
    "secret" : os.environ["session_secret"],
    "default_handler_class" : PathNotFoundHandler
}

def make_app() :
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/(\w{"+os.environ["key_length"] + r"})", PatternRedirectHandler),
        ],
        **settings
    )


if __name__ == "__main__" :
    app = make_app()
    app.listen(8888) 
    tornado.ioloop.IOLoop.current().start()