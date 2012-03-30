import tornado.ioloop
import tornado.httpserver
import tornado.web
import os, json

from sqlalchemy.orm import scoped_session, sessionmaker
from models import *

class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/todos\/?([0-9]*)", RESTfulHandler),
        ]

        settings = dict(
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
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
        if self.get_cookie('todos') is None:
            remote_ip = self.request.remote_ip
            user = User(remote_ip)
            self.db.add(user)
            self.db.commit()
            self.set_cookie('todos', user.session)
        self.render("index.html")

class RESTfulHandler(BaseHandler):
    def get(self, id):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        todos = []
        for todo in user.todos:
            todos.append(todo.toDict())
        todos = json.dumps(todos)
        self.write(todos)

    def post(self, id):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        todo = json.loads(self.request.body)
        todo = Todo(order=todo['order'],
                    content=todo['content'],
                    done=todo['done'],
                    user=user.id)
        self.db.add(todo)
        self.db.commit()
        todo = json.dumps(todo.toDict())
        self.write(todo)

    def put(self, id):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        todo = self.db.query(Todo).filter(Todo.id == id).filter(Todo.user == user.id).first()
        if todo is not None:
           tmp = json.loads(self.request.body)
           todo.content = tmp['content']
           todo.done = tmp['done']
           self.db.commit()
           todo = json.dumps(todo.toDict())
           self.write(todo)
        else:
           self.set_status(403)

    def delete(self, id):
        session_hash = self.get_cookie('todos')
        user = self.db.query(User).filter_by(session=session_hash).first()
        todo = self.db.query(Todo).filter(Todo.id == id).filter(Todo.user == user.id).first()
        if todo is not None:
            self.db.delete(todo)
            self.db.commit()
        else:
            self.set_status(403)

def main():
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
