import json
import time
from datetime import datetime
from typing import Annotated, List, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from fastapi import Depends, Header
from fastapi.requests import Request
from fastapi.responses import Response, StreamingResponse

from chainfury_server import database as DB
from chainfury_server.commons import types as T
from chainfury_server.engines import call_engine


def create_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    chatbot_data: T.CreateChatbotRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ChatBotDetails, T.ApiResponse]:
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
    response = T.ChatBotDetails.from_db(chatbot)
    return response


def get_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ChatBotDetails, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB call
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(DB.ChatBot.id == id, DB.ChatBot.deleted_at == None).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")

    # return
    return T.ChatBotDetails.from_db(chatbot)


def update_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    chatbot_data: T.ChatBotDetails,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ChatBotDetails, T.ApiResponse]:
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
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(DB.ChatBot.id == id, DB.ChatBot.deleted_at == None).first()  # type: ignore
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
    return T.ChatBotDetails.from_db(chatbot)


def delete_chatbot(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    id: str,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB Call
    chatbot: DB.ChatBot = db.query(DB.ChatBot).filter(DB.ChatBot.id == id, DB.ChatBot.deleted_at == None).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return T.ApiResponse(message="ChatBot not found")
    chatbot.deleted_at = datetime.now()
    db.commit()

    # return
    return T.ApiResponse(message=f"ChatBot: '{chatbot.name}' ({chatbot.id}) deleted")


def list_chatbots(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ListChatbotsResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # DB Call
    chatbots: List[DB.ChatBot] = db.query(DB.ChatBot).filter(DB.ChatBot.deleted_at == None).filter(DB.ChatBot.created_by == user.id).offset(skip).limit(limit).all()  # type: ignore

    # return
    return T.ListChatbotsResponse(
        chatbots=[T.ChatBotDetails.from_db(chatbot) for chatbot in chatbots],
    )


def run_chain(
    req: Request,
    resp: Response,
    id: str,
    token: Annotated[str, Header()],
    prompt: T.PromptBody,
    stream: bool = False,
    as_task: bool = False,
    db: Session = Depends(DB.fastapi_db_session),
):
    """
    This is the master function to run any chain over the API. This can behave in a bunch of different formats like:
    - (default) this will wait for the entire chain to execute and return the response
    - if ``stream`` is passed it will give a streaming response with line by line JSON and last response containing ``"done":true``
    - if ``as_task`` is passed then a task ID is received and you can poll for the results at ``/chains/{id}/results`` this supercedes the ``stream``.
    """
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # query the db
    chatbot = db.query(DB.ChatBot).filter(DB.ChatBot.id == id, DB.ChatBot.deleted_at == None).first()  # type: ignore
    if not chatbot:
        resp.status_code = 404
        return {"message": "ChatBot not found"}
    st = time.time()
    result = call_engine(chatbot=chatbot, prompt=prompt, db=db, start=st, stream=stream, as_task=as_task)

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

    if stream:
        return StreamingResponse(
            content=_get_streaming_response(result),
        )
    else:
        return result.to_dict()  # type: ignore


def get_chain_metrics(
    req: Request,
    resp: Response,
    id: str,
    token: Annotated[str, Header()],
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # get all chatbots for the user
    # SELECT COUNT(*) FROM prompt p WHERE p.chabot_id = 'as123s'
    results = db.query(func.count()).filter(DB.Prompt.chatbot_id == id).all()  # type: ignore
    return {"total_conversations": results[0][0]}
