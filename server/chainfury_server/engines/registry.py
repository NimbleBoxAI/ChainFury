from sqlalchemy.orm import Session
from typing import Generator, Tuple, Union, Dict, Any

from chainfury_server.database import ChatBot
from chainfury_server.commons.types import CFPromptResult
from chainfury_server.schemas.prompt_schema import PromptBody


class EngineInterface(object):
    def __call__(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float, stream: bool = False, task: bool = False):
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        if task:
            return self.submit(chatbot=chatbot, prompt=prompt, db=db, start=start)
        elif stream:
            return self.stream(chatbot=chatbot, prompt=prompt, db=db, start=start)
        else:
            return self.run(chatbot=chatbot, prompt=prompt, db=db, start=start)

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
        raise NotImplementedError("Subclass this and implement stream()")

    def submit(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float) -> CFPromptResult:
        raise NotImplementedError("Subclass this and implement submit()")


class EngineRegistry:
    def __init__(self) -> None:
        self._engines = {}

    def register(self, engine: EngineInterface, name: str):
        self._engines[name] = engine

    def get(self, name: str) -> EngineInterface:
        return self._engines[name]


engine_registry = EngineRegistry()
