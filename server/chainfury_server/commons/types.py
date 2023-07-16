from dataclasses import dataclass
from typing import Dict, Any, List

from pydantic import BaseModel

from chainfury_server.database import Prompt as PromptModel
from chainfury.types import Dag, FENode, Edge


@dataclass
class CFPromptResult:
    result: str
    thought: list[dict[str, Any]]
    num_tokens: int
    prompt_id: int
    prompt: PromptModel

    def to_dict(self):
        return {
            "result": self.result,
            "thought": self.thought,
            "num_tokens": self.num_tokens,
            "prompt_id": self.prompt_id,
        }
