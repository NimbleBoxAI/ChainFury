from http.client import HTTPException
import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import DateTime
from datetime import datetime
from commons.utils import (
    filter_prompts_by_date_range,
    get_user_score_metrics,
    get_chatbot_user_score_metrics,
    get_gpt_rating_metrics,
    get_hourly_latency_metrics,
)
import database_constants as constants
from typing import Annotated
from commons.utils import get_user_from_jwt, verify_user

metrics_router = APIRouter(prefix="", tags=["metrics"])


@metrics_router.get("/chatbot/{id}/prompts", status_code=200)
def get_chatbot_metrics(
    id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(database.db_session),
    from_date: str = None,
    to_date: str = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = constants.SORT_BY_CREATED_AT,
    sort_order: str = constants.SORT_ORDER_DESC,
):
    username = get_user_from_jwt(token)
    verify_user(username)
    if from_date is None:
        parsed_from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        parsed_from_date = datetime.strptime(from_date, "%Y-%m-%d")
    if to_date is None:
        parsed_to_date = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    else:
        parsed_to_date = datetime.strptime(to_date, "%Y-%m-%d") + datetime.timedelta(days=1)

    if parsed_to_date < parsed_from_date:
        raise HTTPException(status_code=400, detail="Invalid date range")
    metrics = filter_prompts_by_date_range(
        id,
        parsed_from_date,
        parsed_to_date,
        page,
        page_size,
        sort_by,
        sort_order,
    )
    if metrics is not None:
        response = {"msg": "success", "data": metrics}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Metrics for the chatbot with id {id} not found",
        )
    return response


@metrics_router.get("/chatbot/{id}/metrics", status_code=200)
def get_chatbot_metrics(
    id: int,
    metric_type: str,
    token: Annotated[str, Header()],
    db: Session = Depends(database.db_session),
):
    username = get_user_from_jwt(token)
    verify_user(username)
    metrics = None
    if metric_type == constants.LATENCY_METRIC:
        metrics = get_hourly_latency_metrics(id)
    # elif metric_type == "cost":
    #     metrics = get_cost_metrics(id)
    elif metric_type == constants.USER_SCORE_METRIC:
        metrics = get_user_score_metrics(id)
    elif metric_type == constants.INTERNAL_REVIEW_SCORE_METRIC:
        metrics = get_chatbot_user_score_metrics(id)
    elif metric_type == constants.GPT_REVIEW_SCORE_METRIC:
        metrics = get_gpt_rating_metrics(id)
    if metrics is not None:
        response = {"msg": "success", "data": metrics}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Metrics for the chatbot with id {id} not found",
        )
    return response
