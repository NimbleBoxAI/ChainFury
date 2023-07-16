from typing import Annotated
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from passlib.hash import sha256_crypt
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel

from chainfury_server import database
from chainfury_server.database import User
from chainfury_server.commons.utils import get_user_from_jwt, verify_user

user_router = APIRouter(prefix="/user", tags=["user"])


class ChangePasswordModel(BaseModel):
    username: str
    old_password: str
    new_password: str


@user_router.post("/change_password", status_code=200)
def change_password(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: ChangePasswordModel,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    if user is None:
        resp.status_code = 404
        return {"msg": "user not found"}

    if sha256_crypt.verify(inputs.old_password, user.password):  # type: ignore
        password = sha256_crypt.hash(inputs.new_password)
        user.password = password  # type: ignore
        db.commit()
        response = {"msg": "success"}
        return response
    else:
        resp.status_code = 400
        return {"msg": "old password is incorrect"}
