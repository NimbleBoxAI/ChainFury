import database
from typing import Annotated
from database import Template
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from fastapi.requests import Request
from fastapi.responses import Response
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user

template_router = APIRouter(prefix="", tags=["template"])


class TemplateModel(BaseModel):
    name: str
    dag: dict
    description: str = "No description provided"


@template_router.get("/templates", status_code=200)
def get_all_templates(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    templates = db.query(Template).all()
    return {"templates": [template.to_dict() for template in templates]}


@template_router.get("/template/{id}", status_code=200)
def get_template_by_id(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: int,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    template: Template = db.query(Template).filter(Template.id == id).first()  # type: ignore
    return {"template": template.to_dict()}


@template_router.post("/template", status_code=200)
def create_template(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: TemplateModel,
    db: Session = Depends(database.fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    template = Template(name=inputs.name, description=inputs.description, dag=inputs.dag)
    db.add(template)
    db.commit()
    return {"template": template.to_dict()}
