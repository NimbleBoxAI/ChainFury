from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from commons.config import Base, SessionLocal, engine
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON, Text
from database_constants import PromptRating, ID_LENGTH
from sqlalchemy import Float, DateTime, Enum
from database_utils import general_utils


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


def unique_string(Table, row_reference):
    """
    Gets Random Unique String for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_string = general_utils.get_random_alphanumeric_string(ID_LENGTH).lower()
    while db.query(Table).filter(row_reference == random_string).limit(1).first() is not None:
        random_string = general_utils.get_random_alphanumeric_string(ID_LENGTH).lower()

    return random_string


def unique_number(Table, row_reference):
    """
    Gets Random Unique Number for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_number = general_utils.get_random_number(ID_LENGTH)
    while db.query(Table).filter(row_reference == random_number).limit(1).first() is not None:
        random_number = general_utils.get_random_number(ID_LENGTH)

    return random_number


class User(Base):
    __tablename__ = "user"

    id = Column(String(8), default=lambda: unique_string(User, User.id), primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    username = Column(String(80), unique=True, nullable=False)
    password = Column(String(80), nullable=False)
    meta = Column(JSON)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, meta={self.meta})"


class ChatBot(Base):
    __tablename__ = "chatbot"

    id = Column(String(8), default=lambda: unique_string(ChatBot, ChatBot.id), primary_key=True)
    name = Column(String(80), unique=True)
    created_by = Column(String(8), ForeignKey("user.id"), nullable=False)
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

    id = Column(Integer, default=lambda: unique_number(Prompt, Prompt.id), primary_key=True)
    chatbot_id = Column(String(8), ForeignKey("chatbot.id"), nullable=False)
    input_prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    gpt_rating = Column(String(5), nullable=True)
    user_rating = Column(Enum(PromptRating), nullable=True, default=PromptRating.UNRATED)
    chatbot_user_rating = Column(Enum(PromptRating), nullable=True, default=PromptRating.UNRATED)
    time_taken = Column(Float, nullable=True)
    num_tokens = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False)
    session_id = Column(String(80), nullable=False)
    meta = Column(JSON)


class IntermediateStep(Base):
    __tablename__ = "intermediate_step"
    id = Column(String(8), default=lambda: unique_string(IntermediateStep, IntermediateStep.id), primary_key=True)
    prompt_id = Column(Integer, ForeignKey("prompt.id"), nullable=False)
    intermediate_prompt = Column(Text, nullable=False)
    intermediate_response = Column(Text, nullable=False)
    meta = Column(JSON)

    def __repr__(self):
        return f"Prompt(id={self.id}, name={self.name}, created_by={self.created_by}, dag={self.dag}, meta={self.meta})"


class Template(Base):
    __tablename__ = "template"
    id = Column(Integer, default=lambda: unique_number(Template, Template.id), primary_key=True)
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


# A true plugin architecture allows for plugins to be able to CRUDL some state via a simple mechanism
# so that they can become more powerful, however we don't want to plugins to be very heavy on the DB
# thus the plugins must build a simple key-value based state management system.


# class PluginKeyValue(Base):
#     __tablename__ = "plugin_kv"
#     key = Column(String, primary_key=True)
#     value = Column(String, nullable=False)


# class Components(Base):
#     __tablename__ = "components"
#     id: str = Column(String(8), default=lambda: unique_string(Components, Components.id), primary_key=True)
#     name: str = Column(String(80), unique=True)
#     description: str = Column(String(80))
#     component_type: str = Column(String(80), nullable=False)
#     inputs: list[dict] = Column(JSON)
#     outputs: list[dict] = Column(JSON)
#     tags: list[str] = Column(JSON)


Base.metadata.create_all(bind=engine)
