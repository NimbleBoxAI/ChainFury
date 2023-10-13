from sqlalchemy.orm import Session
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from typing import Annotated

from chainfury_server import database as DB


feedback_router = APIRouter(tags=["feedback"])


class FeedbackModel(BaseModel):
    score: DB.PromptRating


@feedback_router.put("/feedback", status_code=200)
def post_chatbot_user_feedback(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: FeedbackModel,
    prompt_id: int,
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # store in the DB
    prompt: DB.Prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()  # type: ignore
    if prompt is not None:
        if prompt.chatbot_user_rating is not DB.PromptRating.UNRATED:
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
