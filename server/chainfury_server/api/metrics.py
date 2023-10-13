from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Annotated
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header

from chainfury_server import database as DB

metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/{id}/metrics", status_code=200)
def get_chatbot_metrics(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    metric_type: str,
    db: Session = Depends(DB.fastapi_db_session),
):
    raise HTTPException(status_code=501)


@metrics_router.get("/metrics", status_code=200)
def get_all_chatbot_ratings(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get all chatbots for the user
    # SELECT c.id, COUNT(*)
    # FROM prompt p
    # JOIN chatbot c ON c.id = p.chatbot_id
    # WHERE c.created_by = 'bkyyqgln'
    # GROUP BY c.id;
    # db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()  # type: ignore
    results = (
        db.query(DB.Prompt.chatbot_id, func.count())  # type: ignore
        .filter(DB.ChatBot.created_by == user.id)
        .join(DB.ChatBot, DB.ChatBot.id == DB.Prompt.chatbot_id)
        .group_by(DB.Prompt.chatbot_id)
        .all()
    )
    metrics = [{k: {"total_conversations": v}} for (k, v) in results]
    return {"all_bot_metrics": metrics}
