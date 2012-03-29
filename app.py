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

class RESTfulHandler(BaseHandler):
    def get(self, id):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        query = self.db.query.filter(Todo.user == user)
        todos = []
        for todo in query:
            todo.append(todo.toDict())
        todos = json.dumps(todos)
        self.write(todos)

    def post(self):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        todo = json.loads(self.request.body)
        todo = Todo(order=todo['order'],
                    content=todo['content']
                    done=todo['done'],
                    user=user)
        self.db.add(todo)
        self.db.commit()
        todo = json.dumps(todo.toDict())
        self.write(todo)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
