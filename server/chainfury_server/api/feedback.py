from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from typing import Annotated

from chainfury_server import database
from chainfury_server.commons.utils import update_chatbot_user_rating, get_user_from_jwt, verify_user
from chainfury_server.database_constants import PromptRating

feedback_router = APIRouter(tags=["feedback"])


class FeedbackModel(BaseModel):
    score: PromptRating


@feedback_router.put("/feedback", status_code=200)
def post_chatbot_user_feedback(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: FeedbackModel,
    prompt_id: int,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    feedback = update_chatbot_user_rating(db, prompt_id, inputs.score)
    return {"rating": inputs.score}
