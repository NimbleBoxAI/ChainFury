from fastapi import Depends, Header, HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from typing import Annotated
from sqlalchemy.orm import Session

import chainfury_server.database as DB
from chainfury_server.utils import logger
import chainfury.types as T


def list_prompts(
    token: Annotated[str, Header()],
    chain_id: str,
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
        .filter(DB.Prompt.chatbot_id == chain_id)
        .order_by(DB.Prompt.created_at.desc())  # type: ignore
        .limit(limit)
        .offset(offset)
        .all()
    )
    return {"prompts": [p.to_dict() for p in prompts]}


def get_prompt(
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get prompt
    prompt: DB.Prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")

    return {"prompt": prompt.to_dict()}


def delete_prompt(
    prompt_id: int,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # hard delete
    prompt: DB.Prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if not prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    db.delete(prompt)

    db.commit()
    return {"msg": f"Prompt: '{prompt_id}' deleted"}


def prompt_feedback(
    token: Annotated[str, Header()],
    inputs: T.ApiPromptFeedback,
    prompt_id: int,
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # store in the DB
    prompt: DB.Prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if prompt is not None:
        if prompt.user_rating is not None:
            raise HTTPException(
                status_code=400,
                detail=f"Chatbot user rating already exists",
            )
        prompt.user_rating = DB.PromptRating(inputs.score)
        db.commit()
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Unable to find the prompt",
        )
    return {"rating": prompt.user_rating}
