from datetime import datetime
from typing import Annotated, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from fastapi.requests import Request
from fastapi.responses import Response
from pydantic import BaseModel

from chainfury_server import database
from chainfury_server.database import ChatBot, User, ChatBotTypes
from chainfury_server.commons.utils import get_user_from_jwt, verify_user
from chainfury_server.commons.types import Dag
from chainfury_server.commons import config as c

logger = c.get_logger(__name__)

chatbot_router = APIRouter(tags=["chatbot"])


class ChatBotDetails(BaseModel):
    name: str
    dag: Dag = None  # type: ignore
    description: str = ""
    id: str = ""
    created_at: datetime = None  # type: ignore
    engine: str = ""
    update_keys: List[str] = []


# C: POST /chatbot/
@chatbot_router.post("/", status_code=201)
def create_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_data: ChatBotDetails,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # validate chatbot
    if not chatbot_data.name:
        resp.status_code = 400
        return {"message": "Name not specified"}

    if not chatbot_data.engine:
        resp.status_code = 400
        return {"message": "Engine not specified"}

    if chatbot_data.engine not in ChatBotTypes.all():
        resp.status_code = 400
        return {"message": f"Invalid engine should be one of {ChatBotTypes.all()}"}

    # actually create
    dag = chatbot_data.dag.dict() if chatbot_data.dag else {}
    chatbot = ChatBot(
        name=chatbot_data.name,
        created_by=user.id,
        dag=dag,
        engine=chatbot_data.engine,
        created_at=datetime.now(),
    )
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)
    return chatbot


# R: GET /chatbot/{id}
@chatbot_router.get("/{id}", status_code=200)
def get_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # query the db
    chatbot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}
    return chatbot


# U: PUT /chatbot/{id}
@chatbot_router.put("/{id}", status_code=200)
def update_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    chatbot_data: ChatBotDetails,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # validate chatbot update
    if not len(chatbot_data.update_keys):
        resp.status_code = 400
        return {"message": "No keys to update"}

    unq_keys = set(chatbot_data.update_keys)
    valid_keys = {"name", "description", "dag"}
    if not unq_keys.issubset(valid_keys):
        resp.status_code = 400
        return {"message": f"Invalid keys {unq_keys.difference(valid_keys)}"}

    # find and update
    chatbot: ChatBot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}

    for field in unq_keys:
        if field == "name":
            chatbot.name = chatbot_data.name  # type: ignore
        elif field == "description":
            chatbot.description = chatbot_data.description  # type: ignore
        elif field == "dag":
            chatbot.dag = chatbot_data.dag.dict()  # type: ignore

    db.commit()
    db.refresh(chatbot)
    return chatbot


# D: DELETE /chatbot/{id}
@chatbot_router.delete("/{id}", status_code=200)
def delete_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # find and delete
    chatbot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}
    chatbot.deleted_at = datetime.now()
    db.commit()
    return {"msg": f"ChatBot '{chatbot.id}' deleted successfully"}


# L: GET /chatbot/
@chatbot_router.get("/", status_code=200)
def list_chatbots(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # query the db
    chatbots = db.query(ChatBot).filter(ChatBot.deleted_at == None).filter(ChatBot.created_by == user.id).offset(skip).limit(limit).all()
    return {"chatbots": [chatbot.to_dict() for chatbot in chatbots]}
