from commons.utils import get_user_from_jwt
from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session
from typing import Annotated

import database
from database_utils.dashboard import (
    get_chatbots_from_username,
    get_prompts_from_chatbot_id,
    get_prompts_with_chatbot_user_rating_from_chatbot_id,
    get_prompts_with_user_rating_from_chatbot_id,
    get_prompts_with_openai_rating_from_chatbot_id,
)

dashboard_router = APIRouter(prefix="", tags=["dashboard"])


@dashboard_router.get("/dashboard", status_code=200)
def get_user_metrics_summary(token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    user_metrics = []
    total_conversations = 0
    total_internal_feedback = 0
    total_chatbot_user_feedback = 0
    total_openAI_feedback = 0
    username = get_user_from_jwt(token)
    chatbots = get_chatbots_from_username(username)

    for chatbot in chatbots:
        chatbot_id = chatbot.id
        prompts = get_prompts_from_chatbot_id(chatbot_id)
        total_conversations += len(prompts)
        prompts_with_user_rating = get_prompts_with_user_rating_from_chatbot_id(chatbot_id)
        total_internal_feedback += len(prompts_with_user_rating)
        prompts_with_chatbot_user_rating = get_prompts_with_chatbot_user_rating_from_chatbot_id(chatbot_id)
        total_chatbot_user_feedback += len(prompts_with_chatbot_user_rating)
        prompts_with_openai_rating = get_prompts_with_openai_rating_from_chatbot_id(chatbot_id)
        total_openAI_feedback += len(prompts_with_openai_rating)
    total_chatbots = len(chatbots)
    user_metrics.append(
        {
            "total_conversations": total_conversations,
            "total_chatbots": total_chatbots,
            "total_chatbot_user_feedback": total_chatbot_user_feedback,
            "total_internal_feedback": total_internal_feedback,
            "total_openAI_feedback": total_openAI_feedback,
        }
    )
    return {"msg": "success", "data": user_metrics}
