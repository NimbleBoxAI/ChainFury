import jwt
import database
from database import User
from typing import Annotated
from passlib.hash import sha256_crypt
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from commons import config as c
from commons.utils import get_user_from_jwt


auth_router = APIRouter(prefix="", tags=["authentication"])

logger = c.get_logger(__name__)


class AuthModel(BaseModel):
    username: str
    password: str


@auth_router.post("/login", status_code=200)
def login(auth: AuthModel, db: Session = Depends(database.db_session)):
    user: User = db.query(User).filter(User.username == auth.username).first()  # type: ignore
    if user is not None and sha256_crypt.verify(auth.password, user.password):  # type: ignore
        token = jwt.encode(payload={"username": auth.username}, key=c.JWT_SECRET)
        response = {"msg": "success", "token": token}
    else:
        response = {"msg": "failed"}
    return response


@auth_router.post("/get_user_info", status_code=200)
def decode_token(token: Annotated[str, Header()]):
    username = None
    try:
        username = get_user_from_jwt(token)
    except Exception as e:
        logger.exception(e)
        response = {"msg": "failed"}
    response = {"msg": "success", "username": username}
    return response
