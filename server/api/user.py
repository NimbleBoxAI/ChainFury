import database
from database import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

user_router = APIRouter("/user")

class ChangePasswordModel(BaseModel):
    username: str
    old_password: str
    new_password: str

@user_router.post("/test", status_code=200)
def test(db: Session = Depends(database.db_session)):
    response = {"msg": "success"}
    return response

@user_router.post("/change_password", status_code=200)
def test(inputs: ChangePasswordModel, db: Session = Depends(database.db_session)):
    user: User = User.query.filter((User.username == ChangePasswordModel.username) & (User.password == ChangePasswordModel.old_password)).first()
    if user is not None:
        user.password = ChangePasswordModel.new_password
        db.commit()
        response = {"msg": "success"}
    else:
        response = {"msg": "failed"}
    return response
