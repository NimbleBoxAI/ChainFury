from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from commons.config import Base, SessionLocal, engine
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

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
    username = Column(String, unique=True)
    password = Column(String)
    meta = Column(String)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, password={self.password}, meta={self.meta})"


