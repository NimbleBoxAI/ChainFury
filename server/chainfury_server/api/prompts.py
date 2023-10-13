import time
import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from typing import Annotated, Any, Tuple, Dict
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dataclasses import dataclass, asdict

from chainfury_server import database as DB

# build router
router = APIRouter(tags=["prompts"])


@router.get("/{chatbot_id}/prompt")
def get_prompt_list(
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


@router.get("/{chatbot_id}/prompt/{prompt_id}")
def get_prompt(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    prompt_id: int,
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    irsteps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()  # type: ignore
    if not irsteps:
        irsteps = []
    return {"prompt": prompt.to_dict(), "irsteps": [ir.to_dict() for ir in irsteps]}
