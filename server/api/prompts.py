import logging

from fastapi import APIRouter, Depends, Header
from typing import Annotated
from pydantic import BaseModel
from schemas.prompt_schema import Prompt
from sqlalchemy.orm import Session

from commons.utils import get_user_from_jwt, verify_user

from commons.langflow_utils import get_prompt
from commons.utils import update_internal_user_rating
from database import fastapi_db_session
from database_constants import PromptRating


# build router
router = APIRouter(tags=["prompts"])
# add docs to router
router.__doc__ = """
# Prompts API
"""

logger = logging.getLogger(__name__)


@router.post("/chatbot/{chatbot_id}/prompt")
def process_prompt(chatbot_id: str, prompt: Prompt, db: Session = Depends(fastapi_db_session)):
    return get_prompt(chatbot_id, prompt, db)


class InternalFeedbackModel(BaseModel):
    score: PromptRating


@router.put("/chatbot/{chatbot_id}/prompt")
def update_internal_user_feedback(
    inputs: InternalFeedbackModel, prompt_id: int, token: Annotated[str, Header()], db: Session = Depends(fastapi_db_session)
):
    username = get_user_from_jwt(token)
    verify_user(username)
    feedback = update_internal_user_rating(prompt_id, inputs.score)
    return {"message": "Internal user rating updated", "rating": inputs.score}
