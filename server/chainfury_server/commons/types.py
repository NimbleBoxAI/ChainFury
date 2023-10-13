from datetime import datetime
from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

from chainfury_server import database as DB
from chainfury.types import Dag, FENode, Edge


@dataclass
class CFPromptResult:
    result: str
    thought: List[Dict[str, Any]] = field(default_factory=[])  # type: ignore
    num_tokens: int = 0
    prompt_id: int = 0
    prompt: Optional[DB.Prompt] = None
    task_id: str = ""

    def to_dict(self):
        return {
            "result": self.result,
            "thought": self.thought,
            "num_tokens": self.num_tokens,
            "prompt_id": self.prompt_id,
            "task_id": self.task_id,
        }


class ApiResponse(BaseModel):
    message: str


class PromptBody(BaseModel):
    session_id: str
    chat_history: List[str] = []
    data: Dict[str, Any] = dict()
    new_message: str = ""


class ChatBotDetails(BaseModel):
    name: str
    dag: Optional[Dag] = None
    description: Optional[str] = None
    id: str = ""
    created_at: Optional[datetime] = None
    engine: str = ""
    update_keys: List[str] = []

    @classmethod
    def from_db(cls, chatbot: DB.ChatBot):
        return cls(
            name=chatbot.name,
            dag=chatbot.dag,
            description=chatbot.description,
            id=chatbot.id,
            created_at=chatbot.created_at,
            engine=chatbot.engine,
        )


class CreateChatbotRequest(BaseModel):
    name: str
    engine: str
    dag: Optional[Dag] = None
    description: str = ""


class ListChatbotsResponse(BaseModel):
    chatbots: List[ChatBotDetails]


class ActionRequest(BaseModel):
    class FnModel(BaseModel):
        model_id: str = Field(description="The model ID taken from the /components/models API.")
        model_params: dict = Field(description="The model parameters JSON.")
        fn: dict = Field(description="The function JSON.")

    class OutputModel(BaseModel):
        type: str = Field(description="The type of the output.")
        name: str = Field(description="The name of the output.")
        loc: list[str] = Field(description="The location of the output in the JSON.")

    name: str = Field(description="The name of the action.")
    description: str = Field(description="The description of the action.")
    tags: list[str] = Field(default=[], description="The tags for the action.")
    fn: FnModel = Field(description="The function details for the action.")
    outputs: list[OutputModel] = Field(description="The output details for the action.")


class ActionUpdateRequest(BaseModel):
    name: str = Field(default="", description="The name of the action.")
    description: str = Field(default="", description="The description of the action.")
    tags: list[str] = Field(default=[], description="The tags for the action.")
    fn: ActionRequest.FnModel = Field(default=None, description="The function details for the action.")
    outputs: list[ActionRequest.OutputModel] = Field([], description="The output details for the action.")
    update_fields: list[str] = Field(description="The fields to update.")
