import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from commons.utils import get_prompt_from_prompt_id
from http.client import HTTPException

feedback_router = APIRouter(prefix="", tags=["feedback"])


class FeedbackModel(BaseModel):
    score: int


@feedback_router.post("/feedback", status_code=200)
def post_internal_user_feedback(
    inputs: FeedbackModel,
    prompt_id: int,
    db: Session = Depends(database.db_session),
):

    prompt = get_prompt_from_prompt_id(prompt_id)
    if prompt is not None:
        prompt.user_rating = inputs.score
        db.commit()
        response = {"msg": "success"}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
    return response
