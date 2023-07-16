from pydantic import BaseModel
from typing import List


class PromptBody(BaseModel):
    chat_history: List[str] = []
    session_id: str
    new_message: str
