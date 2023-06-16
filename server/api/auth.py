import os
import jwt
import database
from database import User
from fastapi import HTTPException
from typing import Annotated
from passlib.hash import sha256_crypt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from commons import config as c
from commons.utils import get_user_from_jwt, get_user_id_from_jwt
from magic_admin import Magic

auth_router = APIRouter(prefix="", tags=["authentication"])

logger = c.get_logger(__name__)


class AuthModel(BaseModel):
    username: str
    password: str

class MagicAuthModel(BaseModel):
    token: str


class SignUpModal(BaseModel):
    username: str
    email: str
    password: str


@auth_router.post("/login", status_code=200)
def login(auth: AuthModel, db: Session = Depends(database.fastapi_db_session)):
    user: User = db.query(User).filter(User.username == auth.username).first()  # type: ignore
    if user is not None and sha256_crypt.verify(auth.password, user.password):  # type: ignore
        token = jwt.encode(payload={"username": auth.username, "userid": user.id}, key=c.JWT_SECRET)
        response = {"msg": "success", "token": token}
    else:
        response = {"msg": "failed"}
    return response

@auth_router.post("/magic-login", status_code=200)
def magic_login(auth: MagicAuthModel, db: Session = Depends(database.fastapi_db_session)):
    magic = Magic(api_secret_key=os.environ.get("MAGIC_API_SECRET_KEY", None))
    try:
        decoded = magic.User.get_metadata_by_token(auth.token)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail="Invalid token")
    email = decoded.data.get("email")
    user: User = db.query(User).filter(User.email == email).first()  # type: ignore
    if user is None:
        user: User = User(username=email, email=email, password="")  # type: ignore
        db.add(user)
        db.commit()
    token = jwt.encode(payload={"username": email, "userid": user.id}, key=c.JWT_SECRET)
    response = {"msg": "success", "token": token}
    return response


@auth_router.post("/get_user_info", status_code=200)
def decode_token(token: Annotated[str, Header()]):
    username = None
    userid = None
    try:
        username = get_user_from_jwt(token)
        userid = get_user_id_from_jwt(token)
    except Exception as e:
        logger.exception(e)
        response = {"msg": "failed"}
    response = {"msg": "success", "username": username, "user_id": userid}
    return response


@auth_router.post("/signup", status_code=200)
def sign_up(auth: SignUpModal, db: Session = Depends(database.fastapi_db_session)):
    user_exists = False
    email_exists = False
    user: User = db.query(User).filter(User.username == auth.username).first()  # type: ignore
    if user is not None:
        user_exists = True
    user: User = db.query(User).filter(User.email == auth.email).first()  # type: ignore
    if user is not None:
        email_exists = True
    if user_exists and email_exists:
        raise HTTPException(status_code=400, detail="Username and email already registered")
    elif user_exists:
        raise HTTPException(status_code=400, detail="Username is taken")
    elif email_exists:
        raise HTTPException(status_code=400, detail="Email already registered")
    if not user_exists and not email_exists:  # type: ignore
        user: User = User(username=auth.username, email=auth.email, password=sha256_crypt.hash(auth.password))  # type: ignore
        db.add(user)
        db.commit()
        token = jwt.encode(payload={"username": auth.username, "userid": user.id}, key=c.JWT_SECRET)
        response = {"msg": "success", "token": token}
    else:
        response = {"msg": "failed"}
    return response
