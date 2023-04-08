from enum import Enum


class PromptRating(Enum):
    """Enum to know how the conversation went with chat."""

    SAD = 1
    NEUTRAL = 2
    HAPPY = 3


SORT_BY_TIME_TAKEN = "time_taken"
SORT_BY_USER_RATING = "user_rating"
SORT_BY_CHATBOT_USER_RATING = "chatbot_user_rating"
SORT_BY_GPT_RATING = "gpt_rating"
SORT_BY_CREATED_AT = "created_at"
SORT_ORDER_ASC = "asc"
SORT_ORDER_DESC = "desc"
