from sqlalchemy.orm import Session
from fastapi import HTTPException

from chainfury_server.database import ChatBot


def get_chatbot(db: Session, chatbot_id: str) -> ChatBot:
    row = db.query(ChatBot).filter(ChatBot.id == chatbot_id).first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail=f"Chatbot with id {chatbot_id} not found",
        )

    return row
