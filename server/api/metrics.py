from http.client import HTTPException
import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import DateTime
import datetime
from commons.utils import filter_prompts_by_date_range
import database_constants as constants

metrics_router = APIRouter(prefix="", tags=["metrics"])


@metrics_router.get("/chatbot/{id}/metrics", status_code=200)
def get_chatbot_metrics(
    id: int,
    db: Session = Depends(database.db_session),
    from_date: str | None = None,
    to_date: str | None = None,
    page: int = 1,
    page_size: int = 10,
    sort_by: str = constants.SORT_BY_CREATED_AT,
    sort_order: str = constants.SORT_ORDER_DESC,
):
    if from_date is None:
        from_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if to_date is None:
        to_date = datetime.now().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )

    parsed_from_date = datetime.datetime.strptime(from_date, "%Y-%m-%d")
    parsed_to_date = datetime.datetime.strptime(
        to_date, "%Y-%m-%d"
    ) + datetime.timedelta(days=1)

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
