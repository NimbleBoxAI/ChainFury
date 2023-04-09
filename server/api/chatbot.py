import database
from typing import Annotated
from database import ChatBot
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user

chatbot_router = APIRouter(prefix="/chatbot", tags=["chatbot"])


class ChatBotModel(BaseModel):
    name: str = None
    dag: dict = None


@chatbot_router.post("/", status_code=200)
def create_chatbot(inputs: ChatBotModel, token: Annotated[str, Header()], db: Session = Depends(database.db_session)):
    username = get_user_from_jwt(token)
    verify_user(username)
    try:
        chatbot = ChatBot(name=inputs.name, created_by=username, dag=inputs.dag)
        db.add(chatbot)
        db.commit()
        response = {"msg": "success", "chatbot": chatbot.to_dict()}
    except Exception as e:
        print(e)
        response = {"msg": "failed"}
    return response


# @chatbot_router.get("/", status_code=200)


@chatbot_router.put("/{id}", status_code=200)
def update_chatbot(id: int, token: Annotated[str, Header()], inputs: ChatBotModel, db: Session = Depends(database.db_session)):
    verify_user(get_user_from_jwt(token))
    chatbot: ChatBot = db.query(ChatBot).filter(ChatBot.id == id).first()  # type: ignore
    print(chatbot)
    if chatbot is not None:
        if inputs.name is not None:
            chatbot.name = inputs.name
        if inputs.dag is not None:
            chatbot.dag = inputs.dag
        db.commit()
        response = {"msg": "success"}
    else:
        response = {"msg": "failed"}
    return response


@chatbot_router.get("/", status_code=200)
def list_chatbots(token: Annotated[str, Header()], db: Session = Depends(database.db_session)):
    verify_user(get_user_from_jwt(token))
    chatbots = db.query(ChatBot).all()
    print(chatbots)
    response = {"msg": "success", "chatbots": [chatbot.to_dict() for chatbot in chatbots]}
    return response


# @chatbot_router.delete("/", status_code=200)
# def update_chatbot(inputs: ChatBotModel, db: Session = Depends(database.db_session)):
