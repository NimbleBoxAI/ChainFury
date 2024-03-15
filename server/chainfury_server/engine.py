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

from celery import Celery

from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine


app = Celery()


@app.task(name="chainfury_server.engine.run_chain")
def run_chain(
    chatbot_id: str,
    prompt_id: str,
    prompt_data: Dict,
    store_ir: bool,
    store_io: bool,
    worker_id: str,
):
    start = SimplerTimes.get_now_fp64()

    # create the DB session
    sess = DB.get_local_session(
        create_engine(
            DB.db,
            poolclass=NullPool,
        )
    )
    db = sess()

    # get the db object
    chatbot = db.query(DB.ChatBot).filter(DB.ChatBot.id == chatbot_id).first()  # type: ignore
    prompt_row: DB.Prompt = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
    if prompt_row is None:
        time.sleep(2)
        prompt_row = db.query(DB.Prompt).filter(DB.Prompt.id == prompt_id).first()  # type: ignore
        if prompt_row is None:
            raise RuntimeError(f"Prompt {prompt_id} not found")

    # Create a Fury chain then run the chain while logging all the intermediate steps
    dag = T.Dag(**chatbot.dag)  # type: ignore
    chain = Chain.from_dag(dag, check_server=False)
    callback = FuryThoughtsCallback(db, prompt_row.id)

    # print(
    #     f"starting chain execution: [{prompt_row.meta.get('task_id')=}] [{worker_id=}]"
    # )
    iterator = chain.stream(
        data=prompt_data,
        thoughts_callback=callback,
        print_thoughts=False,
    )
    mainline_out = "<placeholder>"
    last_db = 0
    for ir, done in iterator:
        if done:
            mainline_out = ir
            break

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
            k = next(iter(ir)).split("/")[0]
            db_chainlog = DB.ChainLog(
                prompt_id=prompt_row.id,
                created_at=SimplerTimes.get_now_datetime(),
                node_id=k,
                worker_id=worker_id,
                message="step",
                data=data,
            )  # type: ignore
            db.add(db_chainlog)

            # update the DB every 5 seconds
            if time.time() - last_db > 5:
                db.commit()
                last_db = time.time()

    result = T.ChainResult(
        result=str(mainline_out),
        prompt_id=prompt_row.id,  # type: ignore
    )

    db_chainlog = DB.ChainLog(
        prompt_id=prompt_row.id,
        created_at=SimplerTimes.get_now_datetime(),
        node_id="end",
        worker_id=worker_id,
        message="completed",
    )  # type: ignore
    db.add(db_chainlog)

    # commit the prompt to DB
    if store_io:
        prompt_row.response = result.result  # type: ignore
    prompt_row.time_taken = float(time.time() - start)  # type: ignore

    # update the DB after sleeping a bit
    st = time.time() - last_db
    if st < 2:
        time.sleep(2 - st)  # be nice to the db
    db.commit()


class FuryEngine:
    def run(
        self,
        chatbot: DB.ChatBot,
        prompt: T.ApiPromptBody,
        db: Session,
        start: float,
        store_ir: bool,
        store_io: bool,
    ) -> T.ChainResult:
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
            callback = FuryThoughtsCallback(db, prompt_row.id)
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
            result = T.ChainResult(
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
    ) -> Generator[Tuple[Union[T.ChainResult, Dict[str, Any]], bool], None, None]:
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
            callback = FuryThoughtsCallback(db, prompt_row.id)
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
                    k = next(iter(ir)).split("/")[0]
                    db_chainlog = DB.ChainLog(
                        prompt_id=prompt_row.id,
                        created_at=SimplerTimes.get_now_datetime(),
                        node_id=k,
                        worker_id="cf_server",
                        message="step",
                        data=data,
                    )  # type: ignore
                    db.add(db_chainlog)

            result = T.ChainResult(
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
    ) -> T.ChainResult:
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
            worker_id = task_id.split("-")[0]

            db_chainlog = DB.ChainLog(
                prompt_id=prompt_row.id,
                created_at=SimplerTimes.get_now_datetime(),
                node_id="init",
                worker_id=worker_id,
                message=f"scheduling task {task_id}",
            )  # type: ignore
            db.add(db_chainlog)

            result = T.ChainResult(
                result=f"Task '{task_id}' scheduled",
                prompt_id=prompt_row.id,
                task_id=task_id,
            )
            if store_io:
                prompt_row.response = result.result  # type: ignore
            prompt_row.time_taken = float(time.time() - start)  # type: ignore
            prompt_row.meta = {"task_id": task_id}  # type: ignore

            app.send_task(
                "chainfury_server.engine.run_chain",
                queue="cfs",
                kwargs={
                    "chatbot_id": chatbot.id,
                    "prompt_id": prompt_row.id,
                    "prompt_data": prompt.data,
                    "store_ir": store_ir,
                    "store_io": store_io,
                    "worker_id": worker_id,
                },
                task_id=task_id,
                expires=600,  # 10 mins
                time_limit=240,  # 4 mins
                soft_time_limit=60,  # 1 min
            )

            db.commit()
            return result

        except Exception as e:
            traceback.print_exc()
            logger.exception(e)
            raise HTTPException(status_code=500, detail=str(e)) from e


# helpers


class FuryThoughtsCallback:
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
    db: Session,
    chatbot_id: str,
    input_prompt: str,
    session_id: str,
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
