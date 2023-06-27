from dataclasses import dataclass
from typing import Dict, Any, List

from database import Prompt as PromptModel
from pydantic import BaseModel

from chainfury.types import Dag, Node, Edge


@dataclass
class CFPromptResult:
    result: str
    thought: list[dict[str, Any]]
    num_tokens: int
    prompt_id: int
    prompt: PromptModel
