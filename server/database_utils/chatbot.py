from sqlalchemy.orm import Session

from database import ChatBot


def get_chatbot(db: Session, chatbot_id: int) -> ChatBot:
    row = db.query(ChatBot).filter(ChatBot.id == chatbot_id).first()

    if row is None:
        raise ValueError(f"Chatbot with id {chatbot_id} does not exist")

    return row
