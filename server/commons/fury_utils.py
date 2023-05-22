import time
import traceback
from functools import partial
from fastapi import HTTPException
from typing import Tuple, List, Dict, Any

from database import ChatBot, Prompt, Session
from schemas.prompt_schema import Prompt as PromptSchema
from commons import config as c
from commons.types import CFPromptResult
from database_utils.prompt import create_prompt
from database_utils.intermediate_step import create_intermediate_steps, insert_intermediate_steps

from fury import Chain

logger = c.get_logger(__name__)


class FuryThoughts:
    def __init__(self, db, prompt_id):
        self.db = db
        self.prompt_id = prompt_id
        self.count = 0

    def __call__(self, thought):
        create_intermediate_steps(self.db, prompt_id=self.prompt_id, intermediate_response=thought["value"])
        self.count += 1


def get_prompt(chatbot: ChatBot, prompt: PromptSchema, db: Session, start: float) -> CFPromptResult:
    try:
        logger.debug("Adding prompt to database")
        prompt_row = create_prompt(db, chatbot.id, prompt.new_message, prompt.session_id)  # type: ignore

        # Create a Fury chain then run the chain while logging all the intermediate steps
        # prompt.chat_history
        chain = Chain.from_dict(chatbot.dag)  # type: ignore
        callback = FuryThoughts(db, prompt.session_id)
        mainline_out, full_ir = chain(prompt.new_message, thoughts_callback=callback)
        result = CFPromptResult(
            result=str(mainline_out),
            thought=[{"engine": "fury", "ir_steps": callback.count, "thoughts": list(full_ir.keys())}],
            num_tokens=1,
            prompt=prompt_row,
            prompt_id=prompt_row.id,  # type: ignore
        )

        # commit the prompt to DB
        prompt_row.response = result.result  # type: ignore
        prompt_row.time_taken = float(time.time() - start)  # type: ignore
        message = f"User: {prompt.new_message}\nBot: {result.result}"
        # prompt_row.gpt_rating = ask_for_rating(message)  #  type: ignore
        prompt_row.num_tokens = result.num_tokens  # type: ignore
        db.commit()

        # result["prompt_id"] = prompt_row.id
        logger.debug("Processed graph")
        return result

    except Exception as e:
        traceback.print_exc()
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
