import jwt
import database
from database import User
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel
from commons.config import jwt_secret
from commons.utils import get_user_from_jwt

auth_router = APIRouter(prefix="", tags=["authentication"])

class AuthModel(BaseModel):
    username: str = None
    password: str = None
    token: str = None

@auth_router.post("/login", status_code=200)
def login(auth: AuthModel, db: Session = Depends(database.db_session)):
    user: User = db.query(User).filter((User.username == auth.username) & (User.password == auth.password)).first()
    if user is not None:
        token = jwt.encode(
            payload={"username": auth.username},
            key=jwt_secret
        )
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
        print(e)
        response = {"msg": "failed"}
    response = {"msg": "success", "username": username}
    return response