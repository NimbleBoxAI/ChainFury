import database
from typing import Annotated
from database import ChatBot, User
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user, get_user_id_from_jwt
from commons import config as c

logger = c.get_logger(__name__)

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatBotModel(BaseModel):
    name: str
    dag: dict


@chatbot_router.post("/", status_code=200)
def create_chatbot(inputs: ChatBotModel, token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    username = get_user_from_jwt(token)
    verify_user(db, username)
    user_id = get_user_id_from_jwt(token)
    try:
        chatbot = ChatBot(name=inputs.name, created_by=user_id)
        if inputs.dag:
            # TODO: @yashbonde add dag check here
            chatbot.dag = inputs.dag  # type: ignore
        db.add(chatbot)
        db.commit()
        response = {"msg": "success", "chatbot": chatbot.to_dict()}
    except Exception as e:
        logger.exception(e)
        response = {"msg": "failed"}
    return response


# @chatbot_router.get("/", status_code=200)


@chatbot_router.put("/{id}", status_code=200)
def update_chatbot(id: str, token: Annotated[str, Header()], inputs: ChatBotModel, db: Session = Depends(database.fastapi_db_session)):
    verify_user(db, get_user_from_jwt(token))
    chatbot: ChatBot = db.query(ChatBot).filter(ChatBot.id == id and ChatBot.created_by == user.id).first()  # type: ignore
    # logger.debug(chatbot)
    if chatbot is not None:
        if inputs.name is not None:
            chatbot.name = inputs.name  # type: ignore
        if inputs.dag is not None:
            # TODO: @yashbonde add dag check here
            chatbot.dag = inputs.dag  # type: ignore
        db.commit()
        response = {"msg": "success"}
    else:
        response = {"msg": "failed"}
    return response


@chatbot_router.get("/", status_code=200)
def list_chatbots(token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    user: User = verify_user(db, get_user_from_jwt(token))
    chatbots = db.query(ChatBot).filter(ChatBot.created_by == user.id).all()
    # logger.debug(chatbots)
    response = {"msg": "success", "chatbots": [chatbot.to_dict() for chatbot in chatbots]}
    return response


# @chatbot_router.delete("/", status_code=200)
# def update_chatbot(inputs: ChatBotModel, db: Session = Depends(database.fastapi_db_session)):
