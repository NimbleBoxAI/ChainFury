import time
import json
import logging

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse
from typing import Annotated, Any, Tuple, Dict
from pydantic import BaseModel
from schemas.prompt_schema import Prompt
from sqlalchemy.orm import Session
from dataclasses import dataclass

from commons.utils import get_user_from_jwt, verify_user

from commons.langflow_utils import get_prompt as get_prompt_lf, CFPromptResult
from commons.fury_utils import get_prompt as get_prompt_fury, get_streaming_prompt
from commons.utils import update_internal_user_rating
from database import fastapi_db_session, ChatBotTypes, Prompt as PromptModel, IntermediateStep
from database_constants import PromptRating
from database_utils.chatbot import get_chatbot

from plugins import get_phandler, Event

# build router
router = APIRouter(tags=["prompts"])
# add docs to router
router.__doc__ = """
# Prompts API
"""

logger = logging.getLogger(__name__)


@router.get("/chatbot/{chatbot_id}/prompt")
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
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # get prompts
    if limit < 1 or limit > 100:
        limit = 100
    offset = offset if offset > 0 else 0
    prompts = db.query(PromptModel).filter(PromptModel.chatbot_id == chatbot_id).limit(limit).offset(offset).all()
    return {"prompts": [p.to_dict() for p in prompts]}


@router.post("/chatbot/{chatbot_id}/prompt")
def process_prompt(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    prompt: Prompt,
    stream: bool = False,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # call the engine
    result = call_engine(chatbot_id=chatbot_id, prompt=prompt, db=db, stream=stream)

    # # manage any callbacks
    # ph = get_phandler()
    # ph.handle(Event(event_type=Event.types.PROCESS_PROMPT, data=result))

    def _get_streaming_response(result):
        for ir, done in result:
            if done:
                ir.pop("result")
                result = {**ir, "done": done}
            else:
                if type(ir) == str:
                    ir = {"main_out": ir}
                result = {**ir, "done": done}
            yield json.dumps(result) + "\n"

    if stream:
        return StreamingResponse(
            content=_get_streaming_response(result),
        )
    else:
        out = result.__dict__
        out.pop("prompt")
        return out


class InternalFeedbackModel(BaseModel):
    score: PromptRating


@router.put("/chatbot/{chatbot_id}/prompt")
def update_internal_user_feedback(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    inputs: InternalFeedbackModel,
    prompt_id: int,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    feedback = update_internal_user_rating(db, prompt_id, inputs.score)
    return {"msg": "Internal user rating updated", "rating": inputs.score}


@router.get("/chatbot/{chatbot_id}/prompt/{prompt_id}")
def get_prompt(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_id: str,
    prompt_id: int,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    prompt = db.query(PromptModel).filter(PromptModel.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    irsteps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()
    if not irsteps:
        irsteps = []
    return {"prompt": prompt.to_dict(), "irsteps": [ir.to_dict() for ir in irsteps]}


@router.delete("/chatbot/{chatbot_id}/prompt/{prompt_id}")
def delete_prompt(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    prompt_id: int,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # hard delete
    prompt = db.query(PromptModel).filter(PromptModel.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)

    # now delete all the intermediate steps
    ir_steps = db.query(IntermediateStep).filter(IntermediateStep.prompt_id == prompt.session_id).all()
    for ir in ir_steps:
        db.delete(ir)

    db.commit()
    return {"msg": f"Prompt: '{prompt_id}' deleted"}


#
# helper
#


def call_engine(chatbot_id: str, prompt: Prompt, db: Session, stream: bool) -> CFPromptResult:
    start = time.time()
    chatbot = get_chatbot(db, chatbot_id)
    if chatbot.engine == ChatBotTypes.LANGFLOW:
        if stream:
            raise HTTPException(status_code=404, detail=f"Streaming not supported for engine: {chatbot.engine}")
        result = get_prompt_lf(chatbot, prompt, db, start)
        return result
    elif chatbot.engine == ChatBotTypes.FURY:
        if stream:
            result = get_streaming_prompt(chatbot, prompt, db, start)
        else:
            result = get_prompt_fury(chatbot, prompt, db, start)
        return result

    raise HTTPException(status_code=404, detail=f"Invalid chatbot type: {chatbot.type}")
