import os
import jwt
import json
import random, string
from datetime import datetime
from enum import Enum as EnumType
from fastapi import HTTPException
from passlib.hash import sha256_crypt
from dataclasses import dataclass, asdict
from typing import Dict, Any

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


def unique_string(table, row_reference, length=ID_LENGTH):
    """
    Gets Random Unique String for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_string = get_random_alphanumeric_string(length).lower()
    while db.query(table).filter(row_reference == random_string).limit(1).first() is not None:  # type: ignore
        random_string = get_random_alphanumeric_string(length).lower()

    return random_string


def unique_number(Table, row_reference, length=ID_LENGTH):
    """
    Gets Random Unique Number for Primary key and makes sure its unique for the table.
    """
    db = db_session()
    random_number = get_random_number(length)
    while db.query(Table).filter(row_reference == random_number).limit(1).first() is not None:  # type: ignore
        random_number = get_random_number(length)

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

    id: str = Column(String(8), default=lambda: unique_string(User, User.id), primary_key=True)
    email: str = Column(String(80), unique=True, nullable=False)
    username: str = Column(String(80), unique=True, nullable=False)
    password: str = Column(String(80), nullable=False)
    meta: Dict[str, Any] = Column(JSON)

    def __repr__(self):
        return f"User(id={self.id}, username={self.username}, meta={self.meta})"


class ChatBotTypes:
    LANGFLOW = "langflow"
    FURY = "fury"

    def all():  # type: ignore
        return [getattr(ChatBotTypes, attr) for attr in dir(ChatBotTypes) if not attr.startswith("__")]


class ChatBot(Base):
    __tablename__ = "chatbot"

    id: str = Column(
        String(8),
        default=lambda: unique_string(ChatBot, ChatBot.id),
        primary_key=True,
    )
    name: str = Column(String(80), unique=False)
    description: str = Column(Text, nullable=True)
    created_by: str = Column(String(8), ForeignKey("user.id"), nullable=False)
    dag: Dict[str, Any] = Column(JSON)
    meta: Dict[str, Any] = Column(JSON)
    engine: str = Column(String(80), nullable=False)
    tag_id: str = Column(String(80), nullable=True)
    created_at: datetime = Column(DateTime, nullable=False)
    deleted_at: datetime = Column(DateTime, nullable=True)

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

    id: int = Column(
        Integer,
        default=lambda: unique_number(Prompt, Prompt.id),
        primary_key=True,
    )
    chatbot_id: str = Column(String(8), ForeignKey("chatbot.id"), nullable=False)
    input_prompt: str = Column(Text, nullable=False)
    response: str = Column(Text, nullable=True)
    gpt_rating: str = Column(String(5), nullable=True)
    user_rating: int = Column(Enum(PromptRating), nullable=True)
    time_taken: float = Column(Float, nullable=True)
    num_tokens: int = Column(Integer, nullable=True)
    created_at: datetime = Column(DateTime, nullable=False)
    session_id: Dict[str, Any] = Column(String(80), nullable=False)
    meta: Dict[str, Any] = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "chatbot_id": self.chatbot_id,
            "input_prompt": self.input_prompt,
            "response": self.response,
            "gpt_rating": self.gpt_rating,
            "user_rating": self.user_rating,
            "time_taken": self.time_taken,
            "num_tokens": self.num_tokens,
            "created_at": self.created_at,
            "session_id": self.session_id,
            "meta": self.meta,
        }


class ChainLog(Base):
    __tablename__ = "chain_logs"

    id: str = Column(
        String(16),
        default=lambda: unique_string(ChainLog, ChainLog.id, 16),
        primary_key=True,
    )
    created_at: datetime = Column(DateTime, nullable=False)
    prompt_id: int = Column(Integer, ForeignKey("prompt.id"), nullable=False)
    node_id: str = Column(String(Env.CFS_MAX_NODE_ID_LEN()), nullable=False)
    worker_id: str = Column(String(Env.CF_MAX_WORKER_ID_LEN()), nullable=False)
    message: str = Column(Text, nullable=False)
    data: Dict[str, Any] = Column(JSON, nullable=True)


class Template(Base):
    __tablename__ = "template"

    id: int = Column(
        Integer,
        default=lambda: unique_number(Template, Template.id),
        primary_key=True,
    )
    name: str = Column(Text, nullable=False)
    dag: Dict[str, Any] = Column(JSON, nullable=False)
    description: str = Column(Text)
    meta: Dict[str, Any] = Column(JSON)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "dag": self.dag,
            "description": self.description,
            "meta": self.meta,
        }


Base.metadata.create_all(bind=engine)  # type: ignore

########
#
# JWT Helpers
#
########


@dataclass
class JWTPayload:
    username: str
    user_id: str

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
