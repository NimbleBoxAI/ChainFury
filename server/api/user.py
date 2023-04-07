import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

user_router = APIRouter("/user")

@user_router.post("/test", status_code=200)
def test(db: Session = Depends(database.db_session)):
    response = {"msg": "success"}
    return response
