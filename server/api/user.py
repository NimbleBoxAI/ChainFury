import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query

router = APIRouter()

@router.post("/test", status_code=200)
def test(db: Session = Depends(database.db_session)):
    response = {"msg": "success"}
    return response