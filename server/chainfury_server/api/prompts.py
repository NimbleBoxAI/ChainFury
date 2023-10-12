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

from chainfury_server.schemas.prompt_schema import PromptBody
from chainfury_server.commons.utils import get_user_from_jwt
from chainfury_server.database import fastapi_db_session, ChatBotTypes, Prompt as PromptModel, IntermediateStep
from chainfury_server.database_constants import PromptRating
from chainfury_server.database_utils.chatbot import get_chatbot

from chainfury_server.engines import call_engine

# from chainfury_server.engines.langflow import get_prompt as get_prompt_lf, CFPromptResult

from chainfury_server.plugins import get_phandler, Event

# build router
router = APIRouter(tags=["prompts"])
# add docs to router
router.__doc__ = """
# Prompts API
"""

logger = logging.getLogger(__name__)


@router.get("/{chatbot_id}/prompt")
def get_prompt_list(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    user = get_user_from_jwt(token=token, db=db)

    # get prompts
    if limit < 1 or limit > 100:
        limit = 100
    offset = offset if offset > 0 else 0
    prompts = (
        db.query(PromptModel)  # type: ignore
        .filter(PromptModel.chatbot_id == chatbot_id)
        .order_by(PromptModel.created_at.desc())
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
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    user = get_user_from_jwt(token=token, db=db)

    prompt = db.query(PromptModel).filter(PromptModel.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    irsteps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()  # type: ignore
    if not irsteps:
        irsteps = []
    return {"prompt": prompt.to_dict(), "irsteps": [ir.to_dict() for ir in irsteps]}
