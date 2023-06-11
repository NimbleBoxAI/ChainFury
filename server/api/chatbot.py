import database
from datetime import datetime
from typing import Annotated, List
from database import ChatBot, User, ChatBotTypes
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header, Request, Response
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user, get_user_id_from_jwt
from commons import config as c

logger = c.get_logger(__name__)

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatBotDetails(BaseModel):
    name: str
    dag: dict
    id: str = ""
    created_at: datetime = None  # type: ignore
    engine: str = ""
    update_keys: List[str] = []


# C: POST /chatbot/
@chatbot_router.post("/", status_code=201)
def create_chatbot(
    token: Annotated[str, Header()],
    req: Request,
    resp: Response,
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
        return {"message": f"Invalid engine '{chatbot_data.engine}'"}

    # actually create
    chatbot = ChatBot(
        name=chatbot_data.name,
        created_by=user.id,
        dag=chatbot_data.dag,
        engine=chatbot_data.engine,
        created_at=datetime.now(),
    )
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)
    return chatbot.to_dict()


# R: GET /chatbot/{id}
@chatbot_router.get("/{id}", status_code=200)
def get_chatbot(
    token: Annotated[str, Header()],
    req: Request,
    resp: Response,
    id: str,
    db: Session = Depends(database.fastapi_db_session),
):
    chatbot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}
    return chatbot.to_dict()


# U: PUT /chatbot/{id}
@chatbot_router.put("/{id}", status_code=200)
def update_chatbot(
    token: Annotated[str, Header()],
    req: Request,
    resp: Response,
    id: str,
    chatbot_data: ChatBotDetails,
    db: Session = Depends(database.fastapi_db_session),
):
    if not len(chatbot_data.update_keys):
        resp.status_code = 400
        return {"message": "No keys to update"}

    unq_keys = set(chatbot_data.update_keys)
    valid_keys = {"name", "description", "dag"}
    if not unq_keys.issubset(valid_keys):
        resp.status_code = 400
        return {"message": f"Invalid keys {unq_keys.difference(valid_keys)}"}

    chatbot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}

    for field in unq_keys:
        if field == "name":
            chatbot.name = chatbot_data.name
        elif field == "description":
            chatbot.description = chatbot_data.description
        elif field == "dag":
            chatbot.dag = chatbot_data.dag

    db.commit()
    db.refresh(chatbot)
    return chatbot


# D: DELETE /chatbot/{id}
@chatbot_router.delete("/{id}", status_code=200)
def delete_chatbot(
    token: Annotated[str, Header()], req: Request, resp: Response, id: str, db: Session = Depends(database.fastapi_db_session)
):
    chatbot = db.query(ChatBot).filter(ChatBot.id == id, ChatBot.deleted_at == None).first()
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}
    chatbot.deleted_at = datetime.now()
    db.commit()
    return {"message": "ChatBot deleted successfully"}


# L: GET /chatbot/
@chatbot_router.get("/", status_code=200)
def get_all_chatbots(
    token: Annotated[str, Header()],
    req: Request,
    resp: Response,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(database.fastapi_db_session),
):
    chatbots = db.query(ChatBot).filter(ChatBot.deleted_at == None).offset(skip).limit(limit).all()
    # return [chatbot.to_dict() for chatbot in chatbots]
    # ideally this is better solution, but for legacy reasons we are using the below one
    return {"msg": "success", "chatbots": [chatbot.to_dict() for chatbot in chatbots]}


#
# helpers
#


def db_chatbot_to_api_chatbot(ChatBot) -> ChatBotDetails:
    return ChatBotDetails(
        id=ChatBot.id,
        name=ChatBot.name,
        dag=ChatBot.dag,
        created_at=ChatBot.created_at,
        engine=ChatBot.engine,
    )
