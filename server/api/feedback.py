import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from commons.utils import get_prompt_from_prompt_id, update_user_rating
from database_constants import PromptRating

feedback_router = APIRouter(prefix="", tags=["feedback"])


class FeedbackModel(BaseModel):
    score: PromptRating


@feedback_router.post("/feedback", status_code=200)
def post_internal_user_feedback(
    inputs: FeedbackModel,
    prompt_id: int,
    db: Session = Depends(database.db_session),
):

    prompt = get_prompt_from_prompt_id(prompt_id)
    if prompt is not None:
        feedback = update_user_rating(prompt_id, inputs.score)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
