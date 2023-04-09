from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from commons.config import Base, SessionLocal, engine
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Text
from database_constants import PromptRating
from sqlalchemy import Float, DateTime, Enum


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
    __tablename__ = "chatbot"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), unique=True)
    created_by = Column(Integer, ForeignKey("user.id"), nullable=False)
    dag = Column(JSON)
    meta = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "created_by": self.created_by,
            "dag": self.dag,
            "meta": self.meta,
        }

    def __repr__(self):
        return f"ChatBot(id={self.id}, name={self.name}, created_by={self.created_by}, dag={self.dag}, meta={self.meta})"


class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(Integer, primary_key=True)
    chatbot_id = Column(Integer, ForeignKey("chatbot.id"), nullable=False)
    input_prompt = Column(Text, nullable=False)
    gpt_rating = Column(String(5), nullable=True)
    user_rating = Column(Enum(PromptRating), nullable=True)
    chatbot_user_rating = Column(Enum(PromptRating), nullable=True)
    response = Column(Text, nullable=False)
    time_taken = Column(Float, nullable=False)
    created_at = Column(DateTime, nullable=False)
    session_id = Column(String(80), nullable=False)
    meta = Column(JSON)


class IntermediateStep(Base):
    __tablename__ = "intermediate_step"
    id = Column(Integer, primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompt.id"), nullable=False)
    intermediate_prompt = Column(Text, nullable=False)
    intermediate_response = Column(Text, nullable=False)
    meta = Column(JSON)

    def __repr__(self):
        return f"Prompt(id={self.id}, name={self.name}, created_by={self.created_by}, dag={self.dag}, meta={self.meta})"


class Template(Base):
    __tablename__ = "template"
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    dag = Column(JSON, nullable=False)
    description = Column(Text)
    meta = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dag": self.dag,
            "description": self.description,
            "meta": self.meta,
        }

    def __repr__(self):
        return f"Template(id={self.id}, name={self.name}, description={self.description}, dag={self.dag}, meta={self.meta})"


Base.metadata.create_all(bind=engine)
