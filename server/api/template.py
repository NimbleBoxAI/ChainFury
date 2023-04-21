import database
from typing import Annotated
from database import Template
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, Header
from pydantic import BaseModel
from commons.utils import get_user_from_jwt, verify_user

template_router = APIRouter(prefix="", tags=["template"])


class TemplateModel(BaseModel):
    name: str
    dag: dict
    description: str = "No description provided"


@template_router.get("/templates", status_code=200)
def get_all_templates(token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    verify_user(db, get_user_from_jwt(token))
    templates = db.query(Template).all()
    response = {"msg": "success", "templates": [template.to_dict() for template in templates]}
    return response


@template_router.get("/template/{id}", status_code=200)
def get_template_by_id(id: int, token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    verify_user(db, get_user_from_jwt(token))
    template: Template = db.query(Template).filter(Template.id == id).first()  # type: ignore
    response = {"msg": "success", "template": template.to_dict()}
    return response


@template_router.post("/template", status_code=200)
def create_template(inputs: TemplateModel, token: Annotated[str, Header()], db: Session = Depends(database.fastapi_db_session)):
    verify_user(db, get_user_from_jwt(token))
    template = Template(name=inputs.name, description=inputs.description, dag=inputs.dag)
    db.add(template)
    db.commit()
    response = {"msg": "success", "template": template.to_dict()}
    return response
