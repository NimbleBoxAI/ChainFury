from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response

from sqlalchemy.orm import Session
from typing import Annotated

from chainfury_server import database
from chainfury_server.commons.utils import get_prompt_intermediate_data
from chainfury_server.commons.utils import get_user_from_jwt, verify_user

intermediate_steps_router = APIRouter(prefix="", tags=["intermediate_steps"])


@intermediate_steps_router.get("/{chatbot_id}/prompt/{prompt_id}/intermediate_steps", status_code=200)
def get_intermediate_steps(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    prompt_id: int,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # get intermediate steps
    intermediate_steps = get_prompt_intermediate_data(db, prompt_id)
    if intermediate_steps is None:
        resp.status_code = 404
        return {"msg": "prompt not found"}
    return {"data": intermediate_steps}
