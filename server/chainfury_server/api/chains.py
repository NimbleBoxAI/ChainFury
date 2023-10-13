import json
import time
from datetime import datetime
from typing import Annotated, List, Union
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from fastapi.responses import Response, StreamingResponse
from fastapi import Depends, Header, Request, Response, HTTPException

import chainfury.types as T

import chainfury_server.database as DB
from chainfury_server.engines import engine_registry


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

    if not chatbot_data.engine:
        resp.status_code = 400
        return T.ApiResponse(message="Engine not specified")

    if chatbot_data.engine not in DB.ChatBotTypes.all():
        resp.status_code = 400
        return T.ApiResponse(message=f"Invalid engine should be one of {DB.ChatBotTypes.all()}")

    # DB call
    dag = chatbot_data.dag.dict() if chatbot_data.dag else {}
    chatbot = DB.ChatBot(
        name=chatbot_data.name,
        created_by=user.id,
        dag=dag,
        engine=chatbot_data.engine,
        created_at=datetime.now(),
        description=chatbot_data.description,
    )  # type: ignore
    db.add(chatbot)
    db.commit()
    db.refresh(chatbot)

    # return
    response = T.ApiChain(**chatbot.to_dict())
    return response


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
    chatbot = db.query(DB.ChatBot).filter(*filters).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")

    # return
    return T.ApiChain(**chatbot.to_dict())


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
    return T.ApiChain(**chatbot.to_dict())


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
        chatbots=[T.ApiChain(**chatbot.to_dict()) for chatbot in chatbots],
    )


def run_chain(
    req: Request,
    resp: Response,
    id: str,
    token: Annotated[str, Header()],
    prompt: T.ApiPromptBody,
    stream: bool = False,
    as_task: bool = False,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[StreamingResponse, T.CFPromptResult, T.ApiResponse]:
    """
    This is the master function to run any chain over the API. This can behave in a bunch of different formats like:
    - (default) this will wait for the entire chain to execute and return the response
    - if ``stream`` is passed it will give a streaming response with line by line JSON and last response containing ``"done":true``
    - if ``as_task`` is passed then a task ID is received and you can poll for the results at ``/chains/{id}/results`` this supercedes the ``stream``.
    """
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

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
    engine = engine_registry.get(chatbot.engine)
    if engine is None:
        raise HTTPException(status_code=400, detail=f"Invalid engine {chatbot.engine}")

    #
    if as_task:
        result = engine.submit(chatbot=chatbot, prompt=prompt, db=db, start=time.time())
        return result
    elif stream:

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

        streaming_result = engine.stream(chatbot=chatbot, prompt=prompt, db=db, start=time.time())
        return StreamingResponse(content=_get_streaming_response(streaming_result))
    else:
        result = engine.run(chatbot=chatbot, prompt=prompt, db=db, start=time.time())
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
    return {"total_conversations": results[0][0]}
