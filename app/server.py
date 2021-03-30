
import tornado.ioloop
import tornado.template
import tornado.web
import random
import json
import uuid
import re
import os
import sys
sys.path.append("/util")

# package from /util
import util.config
from util.redis_singleton import redis_connection_instance
from util.app import Application, ProtocolObject

redis = redis_connection_instance()
html_loader = tornado.template.Loader(os.path.dirname(os.path.abspath(__file__)) + "/static/html")

class SessionHandler(tornado.web.RequestHandler) :

    def get_current_user(self):
        if not self.get_secure_cookie("session_id") : 
            session = self.__create_session__()
            self.set_secure_cookie("session_id", session)
        return self.get_secure_cookie("session_id").decode()

    def __create_session__(self) :
        return uuid.uuid4().hex
    

class MainHandler(SessionHandler) : 

    @tornado.web.authenticated
    def get(self) :
        self.write(html_loader.load("main.html").generate())

    @tornado.web.authenticated
    def post(self) -> None :    
        data = json.loads(self.request.body)
        data["session_id"] = self.current_user
        result = json.loads(Application(redis).store_data(**data).extract())
        print(result)
        if not result["message"] :
            self.write(ProtocolObject(self.request.host + "/%s"%result["output"]).extract())
        else :
            self.write(ProtocolObject("", message=result["message"]).extract())
        
        
class PatternRedirectHandler(SessionHandler) : 

    @tornado.web.authenticated
    def get(self, path) -> None :
        result = json.loads(Application(redis).get_url(path).extract())
        if not result["message"] :
            self.redirect(result["output"])
        else :
            self.redirect("/error?err_msg=%s"%result["message"])

class ErrorHandler(SessionHandler) :

    @tornado.web.authenticated
    def prepare(self):
        if "err_msg" in self.request.arguments :
            self.finish(self.get_argument("err_msg"))
        else :
            self.clear()
            self.set_status(404)
            self.finish("404 : Page Not Found")
    
        
settings = {
    "cookie_secret" : os.environ["session_secret"],
    "login_url" : "/",
    "default_handler_class" : ErrorHandler
}

def make_app() :
    return tornado.web.Application(
        [
            (r"/", MainHandler),
            (r"/auth/(SignIn|SignUp)", SessionHandler),
            (r"/(\w{"+os.environ["key_length"] + r"})", PatternRedirectHandler),
            (r"/error", ErrorHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path":os.path.join(os.path.dirname(__file__), 'static')})
        ],
        **settings
    )


if __name__ == "__main__" :
    app = make_app()
    app.listen(8888) 
    tornado.ioloop.IOLoop.current().start()