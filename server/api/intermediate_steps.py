from http.client import HTTPException
import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import DateTime
import datetime
from commons.utils import get_prompt_intermediate_data
import database_constants as constants

intermediate_steps_router = APIRouter(prefix="", tags=["intermediate_steps"])


@intermediate_steps_router.get(
    "/chatbot/{id}/prompt/{prompt_id}/intermediate_steps", status_code=200
)
def get_intermediate_steps(
    id: int,
    prompt_id: int,
    db: Session = Depends(database.db_session),
):
    intermediate_steps = get_prompt_intermediate_data(prompt_id)
    if intermediate_steps is not None:
        response = {"msg": "success", "data": intermediate_steps}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Intermediate steps for the prompt with id {prompt_id} not found",
        )
    return response
