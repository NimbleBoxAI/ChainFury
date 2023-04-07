from enum import Enum


class PromptRating(Enum):
    """Enum to know how the conversation went with chat."""

    SAD = 1
    NEUTRAL = 2
    HAPPY = 3
