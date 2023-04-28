import os
import dill
import time
import json
import tempfile
import traceback
from hashlib import sha256
from typing import Any, Dict, List
from dataclasses import dataclass
from fastapi import HTTPException

from sqlalchemy.orm import Session
from schemas.prompt_schema import Prompt
from database_utils.chatbot import get_chatbot
from database_utils.prompt import create_prompt
from database import Prompt as PromptModel

from fury.base import logger, Dag


@dataclass
class CFPromptResult:
    result: str
    thought: list[dict[str, Any]]
    num_tokens: int
    prompt_id: int
    prompt: PromptModel


PREFIX = "cfCache"


# lf
def save_cache(hash_val: str, chat_data, clean_old_cache_files: bool):
    cache_path = os.path.join(tempfile.gettempdir(), f"{PREFIX}_{hash_val}.dill")
    with open(cache_path, "wb") as cache_file:
        dill.dump(chat_data, cache_file)

    if clean_old_cache_files:
        for file in os.listdir(tempfile.gettempdir()):
            if file.startswith(PREFIX) and file != f"{PREFIX}_{hash_val}.dill":
                os.remove(os.path.join(tempfile.gettempdir(), file))


# lf
def load_cache(hash_val):
    cache_path = os.path.join(tempfile.gettempdir(), f"{PREFIX}_{hash_val}.dill")
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as cache_file:
            return dill.load(cache_file)


# lf -> cf
def get_result_and_thought_using_graph(langchain_object, message: str):
    """Get result and thought from extracted json"""
    num_of_tokens = len(message.split())
    try:
        if hasattr(langchain_object, "verbose"):
            langchain_object.verbose = True
        chat_input = None
        memory_key = ""
        if hasattr(langchain_object, "memory") and langchain_object.memory is not None:
            memory_key = langchain_object.memory.memory_key

        for key in langchain_object.input_keys:
            if key not in [memory_key, "chat_history"]:
                chat_input = {key: message}

        if hasattr(langchain_object, "return_intermediate_steps"):
            langchain_object.return_intermediate_steps = True

        fix_memory_inputs(langchain_object)

        from langchain.callbacks import get_openai_callback

        with get_openai_callback() as cb:
            output = langchain_object(chat_input)
            logger.debug(f"Total tokens {cb.total_tokens}")
            num_of_tokens = cb.total_tokens

        intermediate_steps = output.get("intermediate_steps", []) if isinstance(output, dict) else []
        result = output.get(langchain_object.output_keys[0]) if isinstance(output, dict) else output
        if intermediate_steps:
            thought = format_intermediate_steps(intermediate_steps)
        else:
            thought = []

    except Exception as exc:
        traceback.print_exc()
        raise ValueError(f"Error: {str(exc)}") from exc
    return result, thought, num_of_tokens


# cf
def process_graph(data_graph: Dict[str, Any]):
    """
    Process graph by extracting input variables and replacing ZeroShotPrompt
    with PromptTemplate,then run the graph and return the result and thought.
    """
    logger.debug("Loading langchain object")
    message = data_graph.pop("message", "")
    is_first_message = len(data_graph.get("chatHistory", [])) == 0

    # load langchain object
    dag = Dag.from_dict(data_graph)
    dag_hash = dag.hash()
    if is_first_message:
        langchain_object = dag.build()
    else:
        logger.debug("Loading langchain object from cache")
        langchain_object = load_cache(dag_hash)

    logger.debug("Loaded langchain object")
    if langchain_object is None:
        raise ValueError("There was an error loading the langchain_object. Please, check all the nodes and try again.")

    # Generate result and thought
    logger.debug("Generating result and thought")
    result, thought = get_result_and_thought_using_graph(langchain_object, message)
    logger.debug("Generated result and thought")

    # Save langchain_object to cache
    # We have to save it here because if the
    # memory is updated we need to keep the new values
    logger.debug("Saving langchain object to cache")
    save_cache(dag_hash, langchain_object, is_first_message)
    logger.debug("Saved langchain object to cache")
    return {"result": str(result), "thought": thought.strip()}


# cf
def get_prompt(chatbot_id: str, prompt: Prompt, db: Session) -> CFPromptResult:
    try:
        # start timer
        start = time.time()
        chatbot = get_chatbot(db, chatbot_id)
        logger.debug("Adding prompt to database")
        prompt_row = create_prompt(db, chatbot_id, prompt.new_message, prompt.session_id)

        _result, thought, num_tokens = process_graph(prompt.new_message, prompt.chat_history, chatbot.dag)
        result = CFPromptResult(result=str(_result), thought=thought, num_tokens=num_tokens, prompt=prompt_row, prompt_id=prompt_row.id)  # type: ignore

        prompt_row.response = result.result  # type: ignore
        prompt_row.time_taken = float(time.time() - start)  # type: ignore
        # insert_intermediate_steps(db, prompt_row.id, result.thought)

        message = f"User: {prompt.new_message}\nBot: {result.result}"
        # prompt_row.gpt_rating = ask_for_rating(message)
        prompt_row.num_tokens = result.num_tokens  # type: ignore
        db.commit()

        # result["prompt_id"] = prompt_row.id
        logger.debug("Processed graph")
        return result

    except Exception as e:
        traceback.print_exc()
        logger.exception(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
