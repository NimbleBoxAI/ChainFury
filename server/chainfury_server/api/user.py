from typing import Annotated
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from passlib.hash import sha256_crypt
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel

from chainfury_server import database as DB

user_router = APIRouter(tags=["user"])


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
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    if sha256_crypt.verify(inputs.old_password, user.password):
        password = sha256_crypt.hash(inputs.new_password)
        user.password = password  # type: ignore
        db.commit()
        response = {"msg": "success"}
        return response
    else:
        resp.status_code = 400
        return {"msg": "old password is incorrect"}
