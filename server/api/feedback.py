import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from commons.utils import update_chatbot_user_rating
from database_constants import PromptRating

feedback_router = APIRouter(prefix="", tags=["feedback"])


class FeedbackModel(BaseModel):
    score: PromptRating


@feedback_router.put("/feedback", status_code=200)
def post_chatbot_user_feedback(
    inputs: FeedbackModel,
    prompt_id: int,
    db: Session = Depends(database.fastapi_db_session),
):
    feedback = update_chatbot_user_rating(db, prompt_id, inputs.score)
    return {"message": "Chatbot user rating updated", "rating": inputs.score}
