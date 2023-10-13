import os
import jwt
import json
import random, string
from enum import Enum as EnumType
from fastapi import HTTPException
from passlib.hash import sha256_crypt
from dataclasses import dataclass, asdict

from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, scoped_session, sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, JSON, Text, Float, DateTime, Enum, create_engine

from chainfury_server.utils import logger, Env, folder, joinp

########
#
# Init things
#
########

Base = declarative_base()

ID_LENGTH = 8

db = Env.CFS_DATABASE("")
if not db:
    # create a sqlite in the chainfury directory
    cf_folder = os.path.expanduser("~/cf")
    os.makedirs(cf_folder, exist_ok=True)
    db = "sqlite:///" + cf_folder + "/cfs.db"
    logger.warning(f"No database passed will connect to local SQLite: {db}")
    engine = create_engine(
        db,
        connect_args={
            "check_same_thread": False,
        },
    )
else:
    logger.info(f"Using via database URL")
    engine = create_engine(
        db,
        poolclass=QueuePool,
        pool_size=10,
        pool_recycle=30,
        pool_pre_ping=True,
    )


########
#
# Helper Functions
#
########


def get_random_alphanumeric_string(length) -> str:
    letters_and_digits = string.ascii_letters + string.digits
    result_str = "".join((random.choice(letters_and_digits) for i in range(length)))
    return result_str


def get_random_number(length) -> int:
    smallest_number = 10 ** (length - 1)
    largest_number = (10**length) - 1
    random_numbers = random.randint(smallest_number, largest_number)
    return random_numbers


def get_local_session() -> sessionmaker:
    logger.debug("Database opened successfully")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


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


def unique_string(table, row_reference):
    """
    Gets Random Unique String for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_string = get_random_alphanumeric_string(ID_LENGTH).lower()
    while db.query(table).filter(row_reference == random_string).limit(1).first() is not None:  # type: ignore
        random_string = get_random_alphanumeric_string(ID_LENGTH).lower()

    return random_string


def unique_number(Table, row_reference):
    """
    Gets Random Unique Number for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_number = get_random_number(ID_LENGTH)
    while db.query(Table).filter(row_reference == random_number).limit(1).first() is not None:  # type: ignore
        random_number = get_random_number(ID_LENGTH)

    return random_number


def add_default_user():
    admin_password = sha256_crypt.hash("admin")
    db = db_session()
    try:
        db.add(User(username="admin", password=admin_password, email="admin@admin.com", meta=""))  # type: ignore
        db.commit()
    except IntegrityError as e:
        logger.info("Not adding default user")


def add_default_templates():
    db = db_session()
    try:
        ex_folder = joinp(folder(__file__), "examples")
        # with open("./examples/index.json") as f:
        with open(joinp(ex_folder, "index.json")) as f:
            data = json.load(f)
        for template_data in data:
            template = db.query(Template).filter_by(id=template_data["id"]).first()
            if template:
                template.name = template_data["name"]
                template.description = template_data["description"]
                # with open("./examples/" + template_data["dag"]) as f:
                with open(joinp(ex_folder, template_data["dag"])) as f:
                    dag = json.load(f)
                template.dag = dag
            else:
                # with open("./examples/" + template_data["dag"]) as f:
                with open(joinp(ex_folder, template_data["dag"])) as f:
                    dag = json.load(f)
                template = Template(
                    id=template_data["id"],
                    name=template_data["name"],
                    description=template_data["description"],
                    dag=dag,
                )  # type: ignore
                db.add(template)
        db.commit()
    except IntegrityError as e:
        logger.info("Not adding default templates")


########
#
# Tables
#
########


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

    def all():  # type: ignore
        return [getattr(ChatBotTypes, attr) for attr in dir(ChatBotTypes) if not attr.startswith("__")]


class ChatBot(Base):
    __tablename__ = "chatbot"

    id = Column(
        String(8),
        default=lambda: unique_string(ChatBot, ChatBot.id),
        primary_key=True,
    )
    name = Column(String(80), unique=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(8), ForeignKey("user.id"), nullable=False)
    dag = Column(JSON)
    meta = Column(JSON)
    engine = Column(String(80), nullable=False)
    tag_id = Column(String(80), nullable=True)
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
            "engine": self.engine,
            "tag_id": self.tag_id,
            "created_at": self.created_at,
            "deleted_at": self.deleted_at,
        }

    def __repr__(self):
        return f"ChatBot(id={self.id}, name={self.name}, created_by={self.created_by}, dag={self.dag}, meta={self.meta})"


class PromptRating(EnumType):
    """Enum to know how the conversation went with chat."""

    UNRATED = 0
    SAD = 1
    NEUTRAL = 2
    HAPPY = 3


class Prompt(Base):
    __tablename__ = "prompt"

    id = Column(
        Integer,
        default=lambda: unique_number(Prompt, Prompt.id),
        primary_key=True,
    )
    chatbot_id = Column(String(8), ForeignKey("chatbot.id"), nullable=False)
    input_prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=True)
    gpt_rating = Column(String(5), nullable=True)
    user_rating = Column(Enum(PromptRating), nullable=True)
    chatbot_user_rating = Column(Enum(PromptRating), nullable=True)
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

    id = Column(
        Integer,
        default=lambda: unique_number(Template, Template.id),
        primary_key=True,
    )
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


# A fury action is an AI powered node that can be used in a fury chain it is the DB equivalent of fury.Node


class FuryActions(Base):
    __tablename__ = "fury_actions"

    id: Column = Column(
        String(36),
        primary_key=True,
    )
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


Base.metadata.create_all(bind=engine)  # type: ignore

########
#
# JWT Helpers
#
########


@dataclass
class JWTPayload:
    username: str
    user_id: int

    def to_dict(self):
        return asdict(self)


def get_user_from_jwt(token, db: Session) -> User:
    try:
        payload = jwt.decode(token, key=Env.JWT_SECRET(), algorithms=["HS256"])
        payload = JWTPayload(
            username=payload.get("username", ""),
            user_id=payload.get("user_id", "") or payload.get("userid", ""),  # grandfather 'userid'
        )
    except Exception as e:
        logger.error("Could not decode JWT token")
        raise HTTPException(status_code=401, detail="Could not decode JWT token")

    logger.debug(f"Verifying user {payload.username}")
    return db.query(User).filter(User.username == payload.username).first()  # type: ignore
