import database
from typing import Annotated
from database import User
from fastapi import HTTPException
from sqlalchemy.orm import Session
from passlib.hash import sha256_crypt
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user

user_router = APIRouter(prefix="/user", tags=["user"])


class ChangePasswordModel(BaseModel):
    username: str
    old_password: str
    new_password: str


@user_router.post("/change_password", status_code=200)
def change_password(inputs: ChangePasswordModel, token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    username = get_user_from_jwt(token)
    verify_user(username)
    user: User = db.query(User).filter(User.username == inputs.username).first()  # type: ignore
    if sha256_crypt.verify(inputs.old_password, user.password):  # type: ignore
        password = sha256_crypt.hash(inputs.new_password)
        user.password = password  # type: ignore
        db.commit()
        response = {"msg": "success"}
        return response
    else:
        raise HTTPException(status_code=400, detail="You have entered the wrong password")
