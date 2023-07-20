from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Annotated
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from fastapi import APIRouter, Depends, Header

from chainfury_server import database
from chainfury_server.database_constants import PromptRating
from chainfury_server.commons.utils import (
    filter_prompts_by_date_range,
    get_user_score_metrics,
    get_chatbot_user_score_metrics,
    get_gpt_rating_metrics,
    get_hourly_latency_metrics,
)
from chainfury_server import database_constants as constants
from chainfury_server.commons.utils import get_user_from_jwt, verify_user, have_chatbot_access, get_user_id_from_jwt
from chainfury_server.database_utils.dashboard import get_chatbots_from_user_id, get_prompts_from_chatbot_id

metrics_router = APIRouter(tags=["metrics"])


# @metrics_router.get("/{id}/prompts", status_code=200)
# def get_chatbot_prompts(
#     req: Request,
#     resp: Response,
#     token: Annotated[str, Header()],
#     id: str,
#     db: Session = Depends(database.fastapi_db_session),
#     from_date: str = None,  # type: ignore
#     to_date: str = None,  # type: ignore
#     page: int = 1,
#     page_size: int = 10,
#     sort_by: str = constants.SORT_BY_CREATED_AT,
#     sort_order: str = constants.SORT_ORDER_DESC,
# ):
#     # validate user
#     username = get_user_from_jwt(token)
#     user = verify_user(db, username)

#     if from_date is None:
#         parsed_from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
#     else:
#         parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
#     if to_date is None:
#         parsed_to_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
#     else:
#         parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)

#     if parsed_to_date < parsed_from_date:
#         raise HTTPException(status_code=400, detail="Invalid date range")

#     metrics = filter_prompts_by_date_range(
#         db,
#         id,
#         parsed_from_date,
#         parsed_to_date,
#         page,
#         page_size,
#         sort_by,
#         sort_order,
#     )  # type: ignore

#     if metrics is None:
#         resp.status_code = 404
#         return {"msg": "Metrics for the chatbot with id {id} not found"}
#     return {"data": metrics}


@metrics_router.get("/{id}/metrics", status_code=200)
def get_chatbot_metrics(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    metric_type: str,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    metrics = None
    is_chatbot_creator = have_chatbot_access(db, chatbot_id=id, user_id=user.id)  # type: ignore
    if is_chatbot_creator is False:
        resp.status_code = 401
        return {"msg": "Unauthorized access"}

    if metric_type == constants.LATENCY_METRIC:
        metrics = get_hourly_latency_metrics(db, id)

    elif metric_type == constants.USER_SCORE_METRIC:
        metrics = get_chatbot_user_score_metrics(db, id)

    elif metric_type == constants.INTERNAL_REVIEW_SCORE_METRIC:
        metrics = get_user_score_metrics(db, id)

    elif metric_type == constants.GPT_REVIEW_SCORE_METRIC:
        metrics = get_gpt_rating_metrics(db, id)
    # elif metric_type == "cost":
    #     metrics = get_cost_metrics(db, id)

    if metrics is None:
        resp.status_code = 404
        return {"msg": f"Metrics for the chatbot with id {id} not found"}
    return {"data": metrics}


@metrics_router.get("/metrics", status_code=200)
def get_all_chatbot_ratings(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(database.fastapi_db_session),
):
    #     - Average user rating per bot
    #     - Average developer rating per bot
    #     - Average openai rating per bot
    #     - Total no. of ratings per bot
    #     - number of good/neutral/bad rating per bot
    #     - rise or fall of prompt ratings in the last 24 hours

    # bots | user rating average | open api rating average | developer rating average (you) | last 24 hours |
    # ----------------------------------------------------------------------------------------------------
    # bot1 |       1.135         |         2.67          |             2.07                 |      /\  24 %
    # bot2 |       1.114         |         2.75          |             1.05                 |      \/.  10%

    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # get all chatbots for the user
    metrics = []
    chatbots = get_chatbots_from_user_id(db, user.id)  # type: ignore
    for chatbot in chatbots:
        chatbot_user_ratings = []
        developer_ratings = []
        openai_ratings = []
        bot_metrics = {}
        total_tokens_processed = 0
        total_chatbot_conversations = 0
        sum_chatbot_user_ratings = 0
        sum_developer_ratings = 0
        sum_openai_ratings = 0
        avg_chatbot_user_ratings = 0
        avg_developer_ratings = 0
        avg_openai_ratings = 0
        total_ratings = 0
        total_chatbot_user_ratings = 0
        total_developer_ratings = 0
        total_openai_ratings = 0
        chatbot_id = chatbot.id
        prompts = get_prompts_from_chatbot_id(db, chatbot_id)
        for prompt in prompts:
            if prompt.chatbot_user_rating is not None:
                chatbot_user_ratings.append(PromptRating(prompt.chatbot_user_rating).value)
                sum_chatbot_user_ratings += PromptRating(prompt.chatbot_user_rating).value
                total_chatbot_user_ratings += 1
            if prompt.user_rating is not None:
                developer_ratings.append(PromptRating(prompt.user_rating).value)
                sum_developer_ratings += PromptRating(prompt.user_rating).value
                total_developer_ratings += 1
            if prompt.gpt_rating is not None:
                openai_ratings.append(int(prompt.gpt_rating))
                sum_openai_ratings += int(prompt.gpt_rating)
                total_openai_ratings += 1
            if prompt.num_tokens is not None:
                total_tokens_processed += prompt.num_tokens
        total_chatbot_conversations += len(prompts)

        sum_of_all_ratings = sum_chatbot_user_ratings + sum_developer_ratings + sum_openai_ratings
        total_ratings = total_chatbot_user_ratings + total_developer_ratings + total_openai_ratings
        avg_rating = 0 if total_ratings == 0 else sum_of_all_ratings / total_ratings

        avg_chatbot_user_ratings = 0 if total_chatbot_user_ratings == 0 else sum_chatbot_user_ratings / total_chatbot_user_ratings
        avg_developer_ratings = 0 if total_developer_ratings == 0 else sum_developer_ratings / total_developer_ratings
        avg_openai_ratings = 0 if total_openai_ratings == 0 else sum_openai_ratings / total_openai_ratings

        bot_metrics = {
            "total_conversations": total_chatbot_conversations,
            "total_tokens_processed": total_tokens_processed,
            "no_of_conversations_rated_by_developer": len(developer_ratings),
            "no_of_conversations_rated_by_end_user": len(chatbot_user_ratings),
            "no_of_conversations_rated_by_openai": len(openai_ratings),
            "average_rating": avg_rating,
            "average_chatbot_user_ratings": avg_chatbot_user_ratings,
            "average_developer_ratings": avg_developer_ratings,
            "average_openai_ratings": avg_openai_ratings,
        }
        metrics.append({chatbot_id: bot_metrics})
    return {"all_bot_metrics": metrics}
