from sqlalchemy.orm import Session
from typing import Generator, Tuple, Union, Dict, Any, Optional

import chainfury_server.database as DB
import chainfury.types as T


class EngineInterface(object):
    @property
    def engine_name(self) -> str:
        raise NotImplementedError("Subclass this and implement engine_name")

    def __call__(
        self, chatbot: DB.ChatBot, prompt: T.ApiPromptBody, db: Session, start: float, stream: bool = False, as_task: bool = False
    ):
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        if as_task:
            return self.submit(chatbot=chatbot, prompt=prompt, db=db, start=start)
        elif stream:
            return self.stream(chatbot=chatbot, prompt=prompt, db=db, start=start)
        else:
            return self.run(chatbot=chatbot, prompt=prompt, db=db, start=start)

    def run(self, chatbot: DB.ChatBot, prompt: T.ApiPromptBody, db: Session, start: float) -> T.CFPromptResult:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement run()")

    def stream(
        self, chatbot: DB.ChatBot, prompt: T.ApiPromptBody, db: Session, start: float
    ) -> Generator[Tuple[Union[T.CFPromptResult, Dict[str, Any]], bool], None, None]:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement stream()")

    def submit(self, chatbot: DB.ChatBot, prompt: T.ApiPromptBody, db: Session, start: float) -> T.CFPromptResult:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement submit()")


class EngineRegistry:
    def __init__(self) -> None:
        self._engines = {}

    def register(self, engine: EngineInterface) -> None:
        self._engines[engine.engine_name] = engine

    def get(self, name: str) -> Optional[EngineInterface]:
        return self._engines.get(name)


engine_registry = EngineRegistry()
