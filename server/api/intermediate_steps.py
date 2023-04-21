from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated

import database
from commons.utils import get_prompt_intermediate_data
from commons.utils import get_user_from_jwt, verify_user

intermediate_steps_router = APIRouter(prefix="", tags=["intermediate_steps"])


@intermediate_steps_router.get("/chatbot/{id}/prompt/{prompt_id}/intermediate_steps", status_code=200)
def get_intermediate_steps(
    id: str,
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(database.fastapi_db_session),
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
