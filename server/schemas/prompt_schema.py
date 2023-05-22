from pydantic import BaseModel
from typing import List


class Prompt(BaseModel):
    chat_history: List[str] = []
    session_id: str
    new_message: str
