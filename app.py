import tornado.ioloop
import tornado.httpserver
import tornado.web

from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
        ]

        settings = dict(
            debug=True,
        )

        tornado.web.Application.__init__(self, handlers, **settings)

        self.db = scoped_session(sessionmaker(bind=engine))

class BaseHandler(tornado.web.RequestHandler):
    @property
    def db(self):
        return self.application.db

class MainHandler(BaseHandler):
    def get(self):
        self.write("Hello World!")

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
