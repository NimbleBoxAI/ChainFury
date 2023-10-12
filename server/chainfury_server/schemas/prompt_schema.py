from pydantic import BaseModel
from typing import List, Dict, Any


class PromptBody(BaseModel):
    session_id: str
    chat_history: List[str] = []
    data: Dict[str, Any] = dict()
    new_message: str = ""
