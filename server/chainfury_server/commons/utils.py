import os
import jwt
import json
from fastapi import HTTPException
from passlib.hash import sha256_crypt
from dataclasses import dataclass, asdict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from chainfury_server.database import db_session, User, Template
from chainfury_server.commons import config as c

logger = c.get_logger(__name__)


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
        ex_folder = joinp(folder(folder(__file__)), "examples")
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


@dataclass
class JWTPayload:
    username: str
    user_id: int

    def to_dict(self):
        return asdict(self)


def get_user_from_jwt(token, db: Session) -> User:
    try:
        payload = jwt.decode(token, key=c.Env.JWT_SECRET(), algorithms=["HS256"])
        payload = JWTPayload(
            username=payload.get("username", ""),
            user_id=payload.get("user_id", "") or payload.get("userid", ""),
        )
    except Exception as e:
        logger.exception("Could not decode JWT token")
        raise HTTPException(status_code=401, detail="Could not decode JWT token")

    logger.debug(f"Verifying user {payload.username}")
    return db.query(User).filter(User.username == payload.username).first()  # type: ignore


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)
