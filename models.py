from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import relationship

from datetime import datetime

from secret import *

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    session = Column(String(32))
    created_on = Column(DateTime, default=datetime.now())
    todos = relationship("Todo", backref="users")

class Todo(Base):
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True)
    order = Column(Integer, primary_key=True)
    content = Column(String(256))
    done = Column(Boolean, default=False)

    def toDict(self):
        todo = {
            'id': self.id,
            'order': self.order,
            'content': self.content,
            'done': self.done
            }
         return todo

engine = create_engine('postgresql://' + USER + ':' + PASSWORD + '@localhost/todos')

Base.metadata.create_all(engine)
