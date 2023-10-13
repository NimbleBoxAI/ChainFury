from sqlalchemy.orm import Session
from typing import Generator, Tuple, Union, Dict, Any

from datetime import datetime
from sqlalchemy.orm import Session

from chainfury_server.database import Prompt, ChatBot
from chainfury_server.commons.types import CFPromptResult, PromptBody


class EngineInterface(object):
    def __call__(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float, stream: bool = False, as_task: bool = False):
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        if as_task:
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
        """
        This is the main entry point for the engine. It should return a CFPromptResult.
        """
        raise NotImplementedError("Subclass this and implement submit()")


class EngineRegistry:
    def __init__(self) -> None:
        self._engines = {}

    def register(self, engine: EngineInterface, name: str):
        self._engines[name] = engine

    def get(self, name: str) -> EngineInterface:
        return self._engines[name]


engine_registry = EngineRegistry()


def create_prompt(db: Session, chatbot_id: str, input_prompt: str, session_id: str) -> Prompt:
    db_prompt = Prompt(
        chatbot_id=chatbot_id,
        input_prompt=input_prompt,
        created_at=datetime.now(),
        session_id=session_id,
    )  # type: ignore
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt
