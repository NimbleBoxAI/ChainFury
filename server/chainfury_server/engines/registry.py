from sqlalchemy.orm import Session
from typing import Generator, Tuple, Union, Dict, Any, Optional

import chainfury_server.database as DB
import chainfury.types as T


class EngineInterface(object):
    @property
    def engine_name(self) -> str:
        raise NotImplementedError("Subclass this and implement engine_name")

    def run(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> T.CFPromptResult:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement run()")

    def stream(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> Generator[Tuple[Union[T.CFPromptResult, Dict[str, Any]], bool], None, None]:
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement stream()")

    def submit(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> T.CFPromptResult:
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
