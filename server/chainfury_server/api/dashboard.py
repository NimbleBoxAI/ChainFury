from fastapi import APIRouter, Depends, Header
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import Annotated

from chainfury_server.commons.utils import get_user_id_from_jwt
from chainfury_server import database
from chainfury_server.database_utils.dashboard import (
    get_chatbots_from_user_id,
    get_prompts_from_chatbot_id,
    get_prompts_with_chatbot_user_rating_from_chatbot_id,
    get_prompts_with_user_rating_from_chatbot_id,
    get_prompts_with_openai_rating_from_chatbot_id,
)
from chainfury_server.commons.utils import get_user_from_jwt, verify_user

dashboard_router = APIRouter(prefix="", tags=["dashboard"])


# @dashboard_router.get("/dashboard", status_code=200)
# def get_user_metrics_summary(
#     req: Request,
#     resp: Response,
#     token: Annotated[str, Header()],
#     db: Session = Depends(database.fastapi_db_session),
# ):
#     # validate user
#     username = get_user_from_jwt(token)
#     user = verify_user(db, username)

#     # get user metrics
#     user_metrics = []
#     total_conversations = 0
#     total_internal_feedback = 0
#     total_chatbot_user_feedback = 0
#     total_openAI_feedback = 0
#     chatbots = get_chatbots_from_user_id(db, user.id)
#     for chatbot in chatbots:
#         chatbot_id = chatbot.id
#         prompts = get_prompts_from_chatbot_id(db, chatbot_id)
#         total_conversations += len(prompts)
#         prompts_with_user_rating = get_prompts_with_user_rating_from_chatbot_id(db, chatbot_id)
#         total_internal_feedback += len(prompts_with_user_rating)
#         prompts_with_chatbot_user_rating = get_prompts_with_chatbot_user_rating_from_chatbot_id(db, chatbot_id)
#         total_chatbot_user_feedback += len(prompts_with_chatbot_user_rating)
#         prompts_with_openai_rating = get_prompts_with_openai_rating_from_chatbot_id(db, chatbot_id)
#         total_openAI_feedback += len(prompts_with_openai_rating)
#     total_chatbots = len(chatbots)
#     user_metrics.append(
#         {
#             "total_conversations": total_conversations,
#             "total_chatbots": total_chatbots,
#             "total_chatbot_user_feedback": total_chatbot_user_feedback,
#             "total_internal_feedback": total_internal_feedback,
#             "total_openAI_feedback": total_openAI_feedback,
#         }
#     )
#     return {"data": user_metrics}
