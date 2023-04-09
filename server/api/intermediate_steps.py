from http.client import HTTPException
import database
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import DateTime
import datetime
from commons.utils import get_prompt_intermediate_data
import database_constants as constants
from typing import Annotated
from commons.utils import get_user_from_jwt, verify_user

intermediate_steps_router = APIRouter(prefix="", tags=["intermediate_steps"])


@intermediate_steps_router.get("/chatbot/{id}/prompt/{prompt_id}/intermediate_steps", status_code=200)
def get_intermediate_steps(
    id: int,
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(database.db_session),
):
    username = get_user_from_jwt(token)
    verify_user(username)
    intermediate_steps = get_prompt_intermediate_data(prompt_id)
    if intermediate_steps is not None:
        response = {"msg": "success", "data": intermediate_steps}
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Intermediate steps for the prompt with id {prompt_id} not found",
        )
    return response
