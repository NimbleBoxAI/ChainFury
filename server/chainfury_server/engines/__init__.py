from sqlalchemy.orm import Session

from chainfury_server.database import ChatBot
from chainfury_server.engines.registry import EngineInterface, EngineRegistry, engine_registry
from chainfury_server.commons.types import PromptBody

# add engines here
from chainfury_server.engines.langflow import LangflowEngine
from chainfury_server.engines.fury import FuryEngine


def call_engine(
    chatbot: ChatBot,
    prompt: PromptBody,
    db: Session,
    start: float,
    stream: bool,
    as_task: bool,
):
    return engine_registry.get(chatbot.engine)(
        chatbot=chatbot,
        prompt=prompt,
        db=db,
        start=start,
        stream=stream,
        as_task=as_task,
    )
