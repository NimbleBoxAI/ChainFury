from sqlalchemy.orm import Session
from typing import Generator, Tuple, Union, Dict, Any

from chainfury_server.database import ChatBot
from chainfury_server.commons.types import CFPromptResult
from chainfury_server.schemas.prompt_schema import PromptBody


class EngineInterface(object):
    def __call__(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float, stream: bool = False):
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        if stream:
            return self.stream(chatbot, prompt, db, start)
        else:
            return self.run(chatbot, prompt, db, start)

    def run(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float) -> CFPromptResult:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement run()")

    def stream(
        self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float
    ) -> Generator[Tuple[Union[CFPromptResult, Dict[str, Any]], bool], None, None]:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement run_streaming()")


class EngineRegistry:
    def __init__(self) -> None:
        self._engines = {}

    def register(self, engine: EngineInterface, name: str):
        self._engines[name] = engine

    def get(self, name: str) -> EngineInterface:
        return self._engines[name]


engine_registry = EngineRegistry()
