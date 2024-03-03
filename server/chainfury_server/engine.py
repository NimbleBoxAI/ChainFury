# Copyright © 2023- Frello Technology Private Limited

import time
import json
import traceback
from uuid import uuid4
from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import Tuple, Dict, Any, Generator, Union

import chainfury.types as T
from chainfury import Chain
from chainfury.utils import SimplerTimes

import chainfury_server.database as DB
from chainfury_server.utils import logger


class FuryEngine:
    def run(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> T.CFPromptResult:
        if prompt.new_message and prompt.data:
            raise HTTPException(
                status_code=400, detail="prompt cannot have both new_message and data"
            )
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message if store_io else "", prompt.session_id)  # type: ignore

            # Create a Fury chain then run the chain while logging all the intermediate steps
            dag = T.Dag(**chatbot.dag)  # type: ignore
            chain = Chain.from_dag(dag, check_server=False)
            callback = FuryThoughts(db, prompt_row.id)
            if prompt.new_message:
                prompt.data = {chain.main_in: prompt.new_message}

            # call the chain
            mainline_out, full_ir = chain(
                data=prompt.data,
                thoughts_callback=callback,
                print_thoughts=False,
            )

            # store the full_ir in the DB.ChainLog
            if store_ir:
                # group the logs by node_id
                chain_logs_by_node = {}
                for k, v in full_ir.items():
                    node_id, varname = k.split("/")
                    chain_logs_by_node.setdefault(node_id, {"outputs": []})
                    chain_logs_by_node[node_id]["outputs"].append(
                        {
                            "name": varname,
                            "data": v,
                        }
                    )

                # iterate over node ids and create the logs
                for k, v in chain_logs_by_node.items():
                    db_chainlog = DB.ChainLog(
                        prompt_id=prompt_row.id,
                        created_at=SimplerTimes.get_now_datetime(),
                        node_id=k,
                        worker_id="cf_server",
                        message="step",
                        data=v,
                    )  # type: ignore
                    db.add(db_chainlog)
                db.commit()

            # create the result
            result = T.CFPromptResult(
                result=(
                    json.dumps(mainline_out)
                    if type(mainline_out) != str
                    else mainline_out
                ),
                prompt_id=prompt_row.id,  # type: ignore
            )

            # commit the prompt to DB
            if store_io:
                prompt_row.input_prompt = prompt.new_message  # type: ignore
                prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            db.commit()

            # result["prompt_id"] = prompt_row.id
            logger.debug("Processed graph")
            return result
        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e

    def stream(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> Generator[Tuple[Union[T.CFPromptResult, Dict[str, Any]], bool], None, None]:
        if prompt.new_message and prompt.data:
            raise HTTPException(
                status_code=400, detail="prompt cannot have both new_message and data"
            )
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message if store_io else "", prompt.session_id)  # type: ignore

            # Create a Fury chain then run the chain while logging all the intermediate steps
            dag = T.Dag(**chatbot.dag)  # type: ignore
            chain = Chain.from_dag(dag, check_server=False)
            callback = FuryThoughts(db, prompt_row.id)
            if prompt.new_message:
                prompt.data = {chain.main_in: prompt.new_message}

            # call the chain
            iterator = chain.stream(
                data=prompt.data,
                thoughts_callback=callback,
                print_thoughts=False,
            )
            # full_ir = {}
            mainline_out = ""
            for ir, done in iterator:
                if not done:
                    # full_ir.update(ir)
                    yield ir, False
                else:
                    mainline_out = ir
                    yield ir, False

                if store_ir:
                    # in case of stream, every item is a fundamentally a step
                    data = {
                        "outputs": [
                            {
                                "name": k.split("/")[-1],
                                "data": v,
                            }
                            for k, v in ir.items()
                        ]
                    }
                    k = next(iter(ir))[0].split("/")[0]
                    db_chainlog = DB.ChainLog(
                        prompt_id=prompt_row.id,
                        created_at=SimplerTimes.get_now_datetime(),
                        node_id=k,
                        worker_id="cf_server",
                        message="step",
                        data=data,
                    )  # type: ignore
                    db.add(db_chainlog)

            result = T.CFPromptResult(
                result=str(mainline_out),
                prompt_id=prompt_row.id,  # type: ignore
            )

            # commit the prompt to DB
            if store_io:
                prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            db.commit()

            logger.debug("Processed graph")
            yield result, True

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e

    def submit(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> T.CFPromptResult:
        if prompt.new_message and prompt.data:
            raise HTTPException(
                status_code=400, detail="prompt cannot have both new_message and data"
            )
        try:
            logger.debug("Adding prompt to database")
            prompt_row = create_prompt(db, chatbot.id, prompt.new_message if store_io else "", prompt.session_id)  # type: ignore

            # Create a Fury chain then run the chain while logging all the intermediate steps
            dag = T.Dag(**chatbot.dag)  # type: ignore
            chain = Chain.from_dag(dag, check_server=False)
            if prompt.new_message:
                prompt.data = {chain.main_in: prompt.new_message}

            # call the chain
            task_id: str = str(uuid4())
            result = T.CFPromptResult(
                result=f"Task '{task_id}' scheduled",
                prompt_id=prompt_row.id,
                task_id=task_id,
            )
            if store_io:
                prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            db.commit()

            return result

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e


# engine_registry.register(FuryEngine())

# helpers


class FuryThoughts:
    def __init__(self, db, prompt_id):
        self.db = db
        self.prompt_id = prompt_id
        self.count = 0

    def __call__(self, thought):
        intermediate_response = thought.get("value", "")
        if intermediate_response is None:
            intermediate_response = ""
        if type(intermediate_response) != str:
            intermediate_response = str(intermediate_response)
        # create_intermediate_steps(self.db, prompt_id=self.prompt_id, intermediate_response=intermediate_response)
        self.count += 1


def create_prompt(
    db: Session, chatbot_id: str, input_prompt: str, session_id: str
) -> DB.Prompt:
    db_prompt = DB.Prompt(
        chatbot_id=chatbot_id,
        input_prompt=input_prompt,
        created_at=SimplerTimes.get_now_datetime(),
        session_id=session_id,
    )  # type: ignore
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt
