import database
from typing import Annotated
from database import ChatBot
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatBotModel(BaseModel):
    name: str
    dag: dict


@chatbot_router.post("/", status_code=200)
def create_chatbot(inputs: ChatBotModel, token: Annotated[str, Header()], db: Session = Depends(database.db_session)):
    username = get_user_from_jwt(token)
    verify_user(username)
    try:
        chatbot = ChatBot(name=inputs.name, created_by=username, dag=inputs.dag)
        db.add(chatbot)
        db.commit()
        response = {"msg": "success"}
    except Exception as e:
        print(e)
        response = {"msg": "failed"}
    return response


# @chatbot_router.get("/", status_code=200)


@chatbot_router.put("/{id}", status_code=200)
def update_chatbot(inputs: ChatBotModel, db: Session = Depends(database.db_session)):
    chatbot: ChatBot = db.query(ChatBot).filter(ChatBot.id == id).first()
    if chatbot is not None:
        # chatbot.
        db.commit()
        response = {"msg": "success"}
    else:
        response = {"msg": "failed"}
    return response


# @chatbot_router.delete("/", status_code=200)
# def update_chatbot(inputs: ChatBotModel, db: Session = Depends(database.db_session)):
