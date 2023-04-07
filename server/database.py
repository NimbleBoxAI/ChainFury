from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from commons.config import Base, SessionLocal, engine
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON

def db_session() -> Session:  # type: ignore
    session_factory = sessionmaker(bind=engine)
    session_class = scoped_session(session_factory)
    # now all calls to session_class() will create a thread-local session_class
    try:
        return session_class()
    finally:
        session_class.remove()

def fastapi_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    meta = Column(JSON)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password}, meta={self.meta})"
    
class ChatBot(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    dag = Column(JSON)
    meta = Column(JSON)

    def __repr__(self):
        return f"ChatBot(id={self.id}, name={self.name}, created_by={self.created_by}, dag={self.dag}, meta={self.meta})"


