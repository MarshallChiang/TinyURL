
import tornado.ioloop
import tornado.template
import tornado.web
import random
import json
import re
import os
import sys
sys.path.append("/util")

# package from /util
import util.config
from util.redis_singleton import redis_connection_instance
from util.app import Application

redis = redis_connection_instance()
html_loader = tornado.template.Loader(os.path.dirname(os.path.abspath(__file__)) + "/static/html")

class MainHandler(tornado.web.RequestHandler) : 

    def get(self) :
        self.write(html_loader.load("main.html").generate())

    def post(self) -> None :    
        data = json.loads(self.request.body.decode("utf-8"))
        result = json.loads(Application(redis).store_data(**data).extract())
        if not result["message"] :
            return self.write(self.request.host + "/%s"%result["output"])
        else :
            self.redirect("/error")
        
        
class PatternRedirectHandler(tornado.web.RequestHandler) : 

    def get(self, path) -> None :
        result = json.loads(Application(redis).get_url(path).extract())
        if not result["message"] :
            return self.redirect(result["output"])
        else :
            self.redirect("/error")

class ErrorHandler(tornado.web.RequestHandler) :

    def prepare(self):
        if "err_msg" in self.request.arguments :
            return self.finish(self.get_argument("err_msg"))
        else :
            self.clear()
            self.set_status(404)
            self.finish("404 : Page Not Found")
    
        
settings = {
    "secret" : os.environ["session_secret"],
    "default_handler_class" : ErrorHandler
}

def make_app() :
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/(\w{"+os.environ["key_length"] + r"})", PatternRedirectHandler),
            (r"/error", ErrorHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {'path':'/static'})
        ],
        **settings
    )


if __name__ == "__main__" :
    app = make_app()
    app.listen(8888) 
    tornado.ioloop.IOLoop.current().start()