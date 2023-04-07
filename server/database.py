from commons.config import Base, SessionLocal
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String

def db_session():
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


