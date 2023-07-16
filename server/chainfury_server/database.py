from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Text, Float, DateTime, Enum
from sqlalchemy.orm import Session
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from chainfury_server.database_constants import PromptRating, ID_LENGTH
from chainfury_server.commons.config import Base, get_local_session, engine
from chainfury_server.database_utils import general_utils


def db_session() -> Session:  # type: ignore
    session_factory = sessionmaker(bind=engine)
    session_class = scoped_session(session_factory)
    # now all calls to session_class() will create a thread-local session_class
    try:
        return session_class()
    finally:
        session_class.remove()


def fastapi_db_session():
    sess_cls = get_local_session()
    db = sess_cls()
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


class ChatBotTypes:
    LANGFLOW = "langflow"
    FURY = "fury"

    def all():
        return [getattr(ChatBotTypes, attr) for attr in dir(ChatBotTypes) if not attr.startswith("__")]


class ChatBot(Base):
    __tablename__ = "chatbot"

    id = Column(String(8), default=lambda: unique_string(ChatBot, ChatBot.id), primary_key=True)
    name = Column(String(80), unique=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(8), ForeignKey("user.id"), nullable=False)
    dag = Column(JSON)
    meta = Column(JSON)
    engine = Column(String(80), nullable=False)
    created_at = Column(DateTime, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
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

    def to_dict(self):
        return {
            "id": self.id,
            "chatbot_id": self.chatbot_id,
            "input_prompt": self.input_prompt,
            "response": self.response,
            "gpt_rating": self.gpt_rating,
            "user_rating": self.user_rating,
            "chatbot_user_rating": self.chatbot_user_rating,
            "time_taken": self.time_taken,
            "num_tokens": self.num_tokens,
            "created_at": self.created_at,
            "session_id": self.session_id,
            "meta": self.meta,
        }


class IntermediateStep(Base):
    __tablename__ = "intermediate_step"
    id = Column(
        String(8),
        default=lambda: unique_string(IntermediateStep, IntermediateStep.id),
        primary_key=True,
    )
    prompt_id = Column(Integer, ForeignKey("prompt.id"), nullable=False)
    intermediate_prompt = Column(Text, nullable=False)
    intermediate_response = Column(Text, nullable=False)
    response_json = Column(JSON, nullable=True)
    meta = Column(JSON)
    created_at = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "intermediate_prompt": self.intermediate_prompt,
            "intermediate_response": self.intermediate_response,
            "response_json": self.response_json,
            "meta": self.meta,
            "created_at": self.created_at,
        }

    def __repr__(self):
        return f"IntermediateStep(id={self.id}, prompt_id={self.prompt_id}, intermediate_prompt={self.intermediate_prompt}, intermediate_response={self.intermediate_response}, response_json={self.response_json}, meta={self.meta}, created_at={self.created_at})"


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


# A fury action is an AI powered node that can be used in a fury chain it is the DB equivalent of fury.Node


class FuryActions(Base):
    __tablename__ = "fury_actions"
    id: Column = Column(String(36), primary_key=True)
    created_by: str = Column(String(8), ForeignKey("user.id"), nullable=False)
    type: str = Column(String(80), nullable=False)  # the AI Action type
    name: str = Column(String(80), unique=False)
    description: str = Column(String(80))
    fields: list[dict] = Column(JSON)
    fn: dict = Column(JSON)
    outputs: list[dict] = Column(JSON)
    tags: list[str] = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "created_by": self.created_by,
            "type": self.type,
            "name": self.name,
            "description": self.description,
            "fields": self.fields,
            "fn": self.fn,
            "outputs": self.outputs,
            "tags": self.tags,
        }

    def update_from_dict(self, data: dict):
        self.name = data.get("name", self.name)
        self.description = data.get("description", self.description)
        self.fields = data.get("fields", self.fields)
        self.fn = data.get("fn", self.fn)
        self.outputs = data.get("outputs", self.outputs)
        self.tags = data.get("tags", self.tags)


Base.metadata.create_all(bind=engine)
