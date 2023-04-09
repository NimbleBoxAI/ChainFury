import traceback
import time
from langflow.interface.run import fix_memory_inputs, load_langchain_object, save_cache
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database_utils.chatbot import get_chatbot
from database_utils.intermediate_step import insert_intermediate_steps
from database_utils.prompt import create_prompt
from schemas.prompt_schema import Prompt
from server.api.gpt_rating import ask_for_rating


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

        output = langchain_object(chat_input)
        intermediate_steps = output.get("intermediate_steps", []) if isinstance(output, dict) else []
        result = output.get(langchain_object.output_keys[0]) if isinstance(output, dict) else output
        if intermediate_steps:
            thought = format_intermediate_steps(intermediate_steps)
        else:
            thought = []

    except Exception as exc:
        traceback.print_exc()
        raise ValueError(f"Error: {str(exc)}") from exc
    return result, thought


def process_graph(message, chat_history, data_graph):
    """
    Process graph by extracting input variables and replacing ZeroShotPrompt
    with PromptTemplate,then run the graph and return the result and thought.
    """
    # Load langchain object
    print("Loading langchain object")
    is_first_message = len(chat_history) == 0
    computed_hash, langchain_object = load_langchain_object(data_graph, is_first_message)
    print("Loaded langchain object")

    if langchain_object is None:
        # Raise user facing error
        raise ValueError("There was an error loading the langchain_object. Please, check all the nodes and try again.")

    # Generate result and thought
    print("Generating result and thought")
    result, thought = get_result_and_thought_using_graph(langchain_object, message)
    print("Generated result and thought")

    # Save langchain_object to cache
    # We have to save it here because if the
    # memory is updated we need to keep the new values
    print("Saving langchain object to cache")
    save_cache(computed_hash, langchain_object, is_first_message)
    print("Saved langchain object to cache")
    return {"result": str(result), "thought": thought}


def get_prompt(chatbot_id: int, prompt: Prompt, db: Session):
    try:
        # start timer
        start = time.time()
        chatbot = get_chatbot(db, chatbot_id)
        print("Adding prompt to database")
        prompt_row = create_prompt(db, chatbot_id, prompt.new_message, prompt.session_id)

        result = process_graph(prompt.new_message, prompt.chat_history, chatbot.dag)

        prompt_row.response = result["result"]
        prompt_row.time_taken = float(time.time() - start)  # type: ignore
        insert_intermediate_steps(db, prompt_row.id, result["thought"])  # type: ignore
        prompt_row.gpt_rating = ask_for_rating()  #  type: ignore
        db.commit()

        result["prompt_id"] = prompt_row.id
        print("Processed graph")
        return result

    except Exception as e:
        import traceback

        traceback.print_exc()
        # print(e)
        raise HTTPException(status_code=500, detail=str(e)) from e
