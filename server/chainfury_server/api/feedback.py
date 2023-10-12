from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated

from chainfury_server import database
from chainfury_server import database_constants as constants
from chainfury_server.commons.utils import get_user_from_jwt
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
    user = get_user_from_jwt(token=token, db=db)

    # store in the DB
    prompt = db.query(database.Prompt).filter(database.Prompt.id == prompt_id).first()  # type: ignore
    if prompt is not None:
        if prompt.chatbot_user_rating is not constants.PromptRating.UNRATED:
            raise HTTPException(
                status_code=400,
                detail=f"Chatbot user rating already exists",
            )
        prompt.chatbot_user_rating = inputs.score
        db.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
    return {"rating": prompt.chatbot_user_rating}
