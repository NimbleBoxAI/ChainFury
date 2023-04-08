from pydantic import BaseModel
from typing import List


class PromptSchema(BaseModel):
    chat_history: List[str]
    session_id: str
    new_message: str
