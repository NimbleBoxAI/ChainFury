import database
from database import User
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

feedback_router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackModel(BaseModel):
    score: int


# @feedback_router.post("/chatbot/{id}/metrics/", status_code=200)
