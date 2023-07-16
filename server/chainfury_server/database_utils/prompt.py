from datetime import datetime
from typing import List
from sqlalchemy.orm import Session

from chainfury_server.database import Prompt
from chainfury_server.commons import config as c

logger = c.get_logger(__name__)


def get_prompts(db: Session, chatbot_id: str) -> List[Prompt]:
    row = db.query(Prompt).filter(Prompt.chatbot_id == chatbot_id).all()
    return row


def create_prompt(db: Session, chatbot_id: str, input_prompt: str, session_id: str) -> Prompt:
    logger.info(f"Creating prompt for chatbot {chatbot_id} with input prompt {input_prompt}")
    db_prompt = Prompt(
        chatbot_id=chatbot_id,
        input_prompt=input_prompt,
        created_at=datetime.now(),
        session_id=session_id,
    )
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt
