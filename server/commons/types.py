from dataclasses import dataclass
from typing import Dict, Any, List

from database import Prompt as PromptModel


@dataclass
class CFPromptResult:
    result: str
    thought: list[dict[str, Any]]
    num_tokens: int
    prompt_id: int
    prompt: PromptModel
