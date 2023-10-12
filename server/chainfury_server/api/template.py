from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from fastapi.requests import Request
from fastapi.responses import Response
from pydantic import BaseModel

from chainfury_server import database
from chainfury_server.database import Template
from chainfury_server.commons.utils import get_user_from_jwt

template_router = APIRouter(tags=["template"])


class TemplateModel(BaseModel):
    name: str
    dag: dict
    description: str = "No description provided"


@template_router.get("/", status_code=200)
def get_all_templates(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    user = get_user_from_jwt(token=token, db=db)

    templates = db.query(Template).all()
    template_list = []
    for t in templates:
        data = t.to_dict()
        if "main_in" in data:
            template_list.append(data)
    return {"templates": resp}
