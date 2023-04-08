from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from database import ChatBot, Prompt, IntermediateStep


def get_prompts(db: Session, chatbot_id: int) -> List[Prompt]:
    row = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id).all()
    return row


def create_prompt(db: Session, input_prompt: str, session_id=str) -> Prompt:
    db_prompt = Prompt(
        input_prompt=input_prompt,
        created_at=datetime.now(),
        session_id=session_id,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt
