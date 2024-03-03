# Copyright © 2023- Frello Technology Private Limited

import json
import time
from datetime import datetime, timedelta
from typing import Annotated, List, Union
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi.responses import Response, StreamingResponse
from fastapi import Depends, Header, Request, Response, HTTPException

import chainfury.types as T
import chainfury_server.database as DB
from chainfury_server.utils import Env
from chainfury_server.engine import FuryEngine


def create_chain(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_data: T.ApiCreateChainRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiChain, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate chatbot
    if not chatbot_data.name:
        resp.status_code = 400
        return T.ApiResponse(message="Name not specified")
    if chatbot_data.dag:
        for n in chatbot_data.dag.nodes:
            if len(n.id) > Env.CFS_MAXLEN_CF_NDOE():
                raise HTTPException(
                    status_code=400,
                    detail=f"Node ID length cannot be more than {Env.CFS_MAXLEN_CF_NDOE()}",
                )

    # DB call
    dag = chatbot_data.dag.model_dump() if chatbot_data.dag else {}
    chatbot = DB.ChatBot(
        name=chatbot_data.name,
        created_by=user.id,
        dag=dag,
        created_at=datetime.now(),
        description=chatbot_data.description,
    )  # type: ignore
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)

    # return
    return chatbot.to_ApiChain()


def get_chain(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    tag_id: str = "",
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiChain, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB call
    filters = [
        DB.ChatBot.id == id,
        DB.ChatBot.created_by == user.id,
        DB.ChatBot.deleted_at == None,
    ]
    if tag_id:
        filters.append(DB.ChatBot.tag_id == tag_id)
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(*filters).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")

    # return
    return chatbot.to_ApiChain()


def update_chain(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    chatbot_data: T.ApiChain,
    tag_id: str = "",
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiChain, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate chatbot update
    if not len(chatbot_data.update_keys):
        resp.status_code = 400
        return T.ApiResponse(message="No keys to update")

    unq_keys = set(chatbot_data.update_keys)
    valid_keys = {"name", "description", "dag"}
    if not unq_keys.issubset(valid_keys):
        resp.status_code = 400
        return T.ApiResponse(message=f"Invalid keys {unq_keys.difference(valid_keys)}")

    # DB Call
    filters = [
        DB.ChatBot.id == id,
        DB.ChatBot.created_by == user.id,
        DB.ChatBot.deleted_at == None,
    ]
    if tag_id:
        filters.append(DB.ChatBot.tag_id == tag_id)
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(*filters).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")

    for field in unq_keys:
        if field == "name":
            chatbot.name = chatbot_data.name  # type: ignore
        elif field == "description":
            chatbot.description = chatbot_data.description  # type: ignore
        elif field == "dag":
            chatbot.dag = chatbot_data.dag.dict()  # type: ignore
    db.commit()
    db.refresh(chatbot)

    # return
    return chatbot.to_ApiChain()


def delete_chain(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    tag_id: str = "",
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB Call
    filters = [
        DB.ChatBot.id == id,
        DB.ChatBot.created_by == user.id,
        DB.ChatBot.deleted_at == None,
    ]
    if tag_id:
        filters.append(DB.ChatBot.tag_id == tag_id)
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(*filters).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")
    chatbot.deleted_at = datetime.now()
    db.commit()

    # return
    return T.ApiResponse(message=f"ChatBot: '{chatbot.name}' ({chatbot.id}) deleted")


def list_chains(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    skip: int = 0,
    limit: int = 10,
    tag_id: str = "",
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiListChainsResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB Call
    filters = [
        DB.ChatBot.created_by == user.id,
        DB.ChatBot.deleted_at == None,
    ]
    if tag_id:
        filters.append(DB.ChatBot.tag_id == tag_id)
    chatbots: List[DB.ChatBot] = db.query(DB.ChatBot).filter(*filters).offset(skip).limit(limit).all()  # type: ignore

    # return
    return T.ApiListChainsResponse(
        chatbots=[chatbot.to_ApiChain() for chatbot in chatbots],
    )


def run_chain(
    req: Request,
    resp: Response,
    id: str,
    token: Annotated[str, Header()],
    prompt: T.ApiPromptBody,
    stream: bool = False,
    as_task: bool = False,
    store_ir: bool = False,
    store_io: bool = False,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[StreamingResponse, T.CFPromptResult, T.ApiResponse]:
    """
    This is the master function to run any chain over the API. This can behave in a bunch of different formats like:
    - (default) this will wait for the entire chain to execute and return the response
    - if ``stream`` is passed it will give a streaming response with line by line JSON and last response containing ``"done"`` key
    - if ``as_task`` is passed then a task ID is received and you can poll for the results at ``/chains/{id}/results`` this supercedes the ``stream``.
    """
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate input
    if not prompt.session_id:
        raise HTTPException(status_code=400, detail="Session ID not specified")
    if prompt.chat_history:
        raise HTTPException(status_code=400, detail="chat history is not supported yet")
    if prompt.new_message and prompt.data:
        raise HTTPException(
            status_code=400, detail="new_message and data cannot be passed together"
        )
    elif not prompt.new_message and not prompt.data:
        raise HTTPException(
            status_code=400, detail="new_message or data must be passed"
        )

    # DB call
    filters = [
        DB.ChatBot.id == id,
        DB.ChatBot.created_by == user.id,
        DB.ChatBot.deleted_at == None,
    ]
    chatbot = db.query(DB.ChatBot).filter(*filters).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")

    # call the engine
    engine = FuryEngine()

    if engine is None:
        raise HTTPException(status_code=400, detail=f"Invalid engine {chatbot.engine}")

    if as_task:
        # when run as a task this will return a task ID that will be submitted
        result = engine.submit(
            chatbot=chatbot,
            prompt=prompt,
            db=db,
            start=time.time(),
            store_ir=store_ir,
            store_io=store_io,
        )
        return result
    elif stream:

        def _get_streaming_response(result):
            for ir, done in result:
                if done:
                    ir.pop("result")
                    result = {**ir, "done": done}
                else:
                    if type(ir) == str:
                        result = {"main_out": ir}
                yield json.dumps(result) + "\n"

        streaming_result = engine.stream(
            chatbot=chatbot,
            prompt=prompt,
            db=db,
            start=time.time(),
            store_ir=store_ir,
            store_io=store_io,
        )
        return StreamingResponse(content=_get_streaming_response(streaming_result))
    else:
        result = engine.run(
            chatbot=chatbot,
            prompt=prompt,
            db=db,
            start=time.time(),
            store_ir=store_ir,
            store_io=store_io,
        )
        return result


def get_chain_metrics(
    req: Request,
    resp: Response,
    id: str,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB call
    results = db.query(func.count()).filter(DB.Prompt.chatbot_id == id).all()  # type: ignore
    metrics = {"total_conversations": results[0][0]}

    hourly_average_latency = (
        db.query(DB.Prompt)
        .filter(DB.Prompt.chatbot_id == id)  # type: ignore
        .filter(DB.Prompt.created_at >= datetime.now() - timedelta(hours=24))
        .with_entities(
            (func.substr(DB.Prompt.created_at, 1, 14)).label("hour"),
            func.avg(DB.Prompt.time_taken).label("avg_time_taken"),
        )
        .group_by((func.substr(DB.Prompt.created_at, 1, 14)))
        .all()
    )
    latency_per_hour = []
    for item in hourly_average_latency:
        created_datetime = item[0] + "00:00"
        latency_per_hour.append({"created_at": created_datetime, "time": item[1]})
    return {"metrics": metrics, "latencies": latency_per_hour}
