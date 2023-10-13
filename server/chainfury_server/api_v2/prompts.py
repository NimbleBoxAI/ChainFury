import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from typing import Annotated
from sqlalchemy.orm import Session

from chainfury_server import database as DB
from chainfury_server.commons.utils import logger


# build router
router = APIRouter(tags=["prompts"])
# add docs to router
router.__doc__ = """
# Prompts API
"""


def list_prompts(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get prompts
    if limit < 1 or limit > 100:
        limit = 100
    offset = offset if offset > 0 else 0
    prompts = (
        db.query(DB.Prompt)  # type: ignore
        .filter(DB.Prompt.chatbot_id == chatbot_id)
        .order_by(DB.Prompt.created_at.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )
    return {"prompts": [p.to_dict() for p in prompts]}


def get_prompt(
    req: Request,
    resp: Response,
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get prompt
    prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    irsteps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()  # type: ignore
    if not irsteps:
        irsteps = []
    return {"prompt": prompt.to_dict(), "irsteps": [ir.to_dict() for ir in irsteps]}


def delete_prompt(
    req: Request,
    resp: Response,
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # hard delete
    prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)

    # now delete all the intermediate steps
    ir_steps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()  # type: ignore
    for ir in ir_steps:
        db.delete(ir)

    db.commit()
    return {"msg": f"Prompt: '{prompt_id}' deleted"}