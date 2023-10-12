from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Annotated
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header

from chainfury_server import database

# from chainfury_server.commons.utils import (
#     filter_prompts_by_date_range,
#     get_user_score_metrics,
#     get_chatbot_user_score_metrics,
#     get_gpt_rating_metrics,
#     get_hourly_latency_metrics,
# )
from chainfury_server import database_constants as constants
from chainfury_server.commons.utils import get_user_from_jwt

metrics_router = APIRouter(tags=["metrics"])


@metrics_router.get("/{id}/metrics", status_code=200)
def get_chatbot_metrics(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    metric_type: str,
    db: Session = Depends(database.fastapi_db_session),
):
    raise HTTPException(status_code=501)


@metrics_router.get("/metrics", status_code=200)
def get_all_chatbot_ratings(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    user = get_user_from_jwt(token=token, db=db)

    # get all chatbots for the user
    # SELECT c.id, COUNT(*)
    # FROM prompt p
    # JOIN chatbot c ON c.id = p.chatbot_id
    # WHERE c.created_by = 'bkyyqgln'
    # GROUP BY c.id;
    # db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()  # type: ignore
    results = (
        db.query(database.Prompt.chatbot_id, func.count())  # type: ignore
        .filter(database.ChatBot.created_by == user.id)
        .join(database.ChatBot, database.ChatBot.id == database.Prompt.chatbot_id)
        .group_by(database.Prompt.chatbot_id)
        .all()
    )
    metrics = [{k: {"total_conversations": v}} for (k, v) in results]
    return {"all_bot_metrics": metrics}
