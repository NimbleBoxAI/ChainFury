import time
import traceback
from typing import Any, Dict, Generator, List, Tuple, Union
from fastapi import HTTPException
from sqlalchemy.orm import Session

try:
    from langflow.interface.run import fix_memory_inputs, load_langchain_object

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


def langflow_is_available() -> bool:
    return _AVAILABLE


from chainfury_server.commons import config as c
from chainfury_server.database_utils.intermediate_step import insert_intermediate_steps
from chainfury_server.database_utils.prompt import create_prompt
from chainfury_server.commons.gpt_rating import ask_for_rating
from chainfury_server.engines.registry import EngineInterface, ChatBot, PromptBody, Session, CFPromptResult, engine_registry

logger = c.get_logger(__name__)

# main


class LangflowEngine(EngineInterface):
    def run(self, chatbot: ChatBot, prompt: PromptBody, db: Session, start: float):
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message, prompt.session_id)

            _result, thought, num_tokens = process_graph(prompt.new_message, prompt.chat_history, chatbot.dag)
            result = CFPromptResult(result=str(_result), thought=thought, num_tokens=num_tokens, prompt=prompt_row, prompt_id=prompt_row.id)  # type: ignore

            prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            insert_intermediate_steps(db, prompt_row.id, result.thought)  # type: ignore

            message = f"User: {prompt.new_message}\nBot: {result.result}"
            prompt_row.gpt_rating = ask_for_rating(message)  #  type: ignore
            prompt_row.num_tokens = result.num_tokens  # type: ignore
            db.commit()

            # result["prompt_id"] = prompt_row.id
            logger.debug("Processed graph")
            return result

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e


engine_registry.register(LangflowEngine(), "langflow")

# helpers


def format_intermediate_steps(intermediate_steps):
    formatted_chain = []
    for step in intermediate_steps:
        action = step[0]
        observation = step[1]

        formatted_chain.append(
            {
                "action": action.tool,
                "action_input": action.tool_input,
                "observation": observation,
            }
        )
    return formatted_chain


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


def process_graph(message: str, chat_history: List[str], data_graph):
    """
    Process graph by extracting input variables and replacing ZeroShotPrompt
    with PromptTemplate,then run the graph and return the result and thought.
    """
    # Load langchain object
    logger.debug("Loading langchain object")
    is_first_message = len(chat_history) == 0
    computed_hash, langchain_object = load_langchain_object(data_graph, True)
    logger.debug("Loaded langchain object")

    if langchain_object is None:
        # Raise user facing error
        raise ValueError("There was an error loading the langchain_object. Please, check all the nodes and try again.")

    # Generate result and thought
    logger.debug("Generating result and thought")
    result, thought, num_tokens = get_result_and_thought_using_graph(langchain_object, message)
    logger.debug("Generated result and thought")

    # Save langchain_object to cache
    # We have to save it here because if the
    # memory is updated we need to keep the new values
    logger.debug("Saving langchain object to cache")
    # save_cache(computed_hash, langchain_object, is_first_message)
    logger.debug("Saved langchain object to cache")
    # return {"result": str(result), "thought": thought, "num_tokens": num_tokens}
    return str(result), thought, num_tokens
