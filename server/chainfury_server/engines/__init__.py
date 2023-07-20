from sqlalchemy.orm import Session

from chainfury_server.database import ChatBot
from chainfury_server.schemas.prompt_schema import PromptBody
from chainfury_server.engines.registry import EngineInterface, EngineRegistry, engine_registry

# add engines here
from chainfury_server.engines.langflow import LangflowEngine
from chainfury_server.engines.fury import FuryEngine


def call_engine(chatbot: ChatBot, prompt: PromptBody, db: Session, start: float, stream: bool = False):
    eng = engine_registry.get(chatbot.engine)  # type: ignore
    eng_result = eng(chatbot, prompt, db, start, stream)
    return eng_result
