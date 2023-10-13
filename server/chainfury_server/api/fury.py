import traceback
from uuid import uuid4
from functools import lru_cache
from sqlalchemy.orm import Session
from typing import Annotated, Union
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Header, Request, Response, Query, HTTPException

from chainfury.agent import model_registry, programatic_actions_registry, ai_actions_registry, memory_registry
from chainfury.base import Node

import chainfury_server.database as DB
import chainfury.types as T
from chainfury_server.utils import logger

# build router
fury_router = APIRouter(tags=["fury"])


@lru_cache(1)
def _components(to_dict: bool = False):
    _MODEL = "models"
    _PROGRAMATIC = "programatic_actions"
    _BUILTIN_AI = "builtin_ai"
    _MEMORY = "memory"

    return {
        _MODEL: model_registry.get_models(),
        _PROGRAMATIC: programatic_actions_registry.get_nodes(),
        _BUILTIN_AI: ai_actions_registry.get_nodes(),
        _MEMORY: memory_registry.get_nodes(),
    }


#
# Components API: this is used for models, actions_p and builtin_ai
#


def get_component(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    component_type: str,
    component_id: str,
    db: Session = Depends(DB.fastapi_db_session),
):
    user = DB.get_user_from_jwt(token=token, db=db)

    if component_type not in _components():
        resp.status_code = 404
        return T.ApiResponse(message="Component type not found")

    comps = _components()[component_type]
    item = comps.get(component_id, None)
    if not item:
        resp.status_code = 404
        return {}
    return item


#
# Fury Actions specific APIs
#


# C - Create a new FuryAction
def create_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_action: T.ApiAction,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiAction, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate action
    node = validate_action(fury_action, resp)

    # insert into db
    try:
        _node = node.to_dict()
        _node["created_by"] = user.id
        _node["name"] = fury_action.name
        fury_action_data = DB.FuryActions(**_node)
        db.add(fury_action_data)
        db.commit()
        db.refresh(fury_action_data)
        return fury_action_data  # TODO: @yashbonde - this is a bug, it should return the fury_action
    except IntegrityError:
        resp.status_code = 409
        return T.ApiResponse(message="FuryAction already exists")
    except Exception as e:
        logger.exception(traceback.format_exc())
        resp.status_code = 500
        return T.ApiResponse(message="Internal server error")


# R - Retrieve a FuryAction by ID
def get_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_id: str,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiAction, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # read from db
    fury_action = db.query(DB.FuryActions).get(fury_id)
    if not fury_action:
        resp.status_code = 404
        return T.ApiResponse(message="FuryAction not found")
    return fury_action  # TODO: @yashbonde - this is a bug, it should return the fury_action


# U - Update an existing FuryAction
def update_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_id: str,
    fury_action: T.ApiActionUpdateRequest,
    db: Session = Depends(DB.fastapi_db_session),
) -> Union[T.ApiAction, T.ApiResponse]:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # validate fields
    if not len(fury_action.update_fields):
        resp.status_code = 400
        return T.ApiResponse(message="No update fields provided")

    unq_fields = set(fury_action.update_fields)
    valid_fields = {"name", "description", "tags", "fn"}
    if not unq_fields.issubset(valid_fields):
        resp.status_code = 400
        return T.ApiResponse(message=f"Invalid update fields provided {unq_fields - valid_fields}")
    for field in unq_fields:
        if not getattr(fury_action, field):
            resp.status_code = 400
            return T.ApiResponse(message=f"Field {field} cannot be empty")

    # create update dict
    update_dict = {}
    node = None
    for field in unq_fields:
        if field == "name":
            update_dict["name"] = fury_action.name

        elif field == "description":
            update_dict["description"] = fury_action.description

        elif field == "tags":
            update_dict["tags"] = fury_action.tags

        elif field == "fn":
            node = validate_action(fury_action, resp)
            update_dict.update(node.to_dict())

    # find object
    fury_action_db: DB.FuryActions = db.query(DB.FuryActions).get(fury_id)
    if not fury_action_db:
        resp.status_code = 404
        return T.ApiResponse(message="FuryAction not found")

    # update object
    try:
        fury_action_db.update_from_dict(update_dict)
        db.commit()
        db.refresh(fury_action_db)
    except Exception as e:
        logger.exception(traceback.format_exc())
        resp.status_code = 500
        return T.ApiResponse(message="Internal server error")
    return fury_action_db  # TODO: @yashbonde - this is a bug, it should return the fury_action


# D - Delete a FuryAction by ID
def delete_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_id: str,
    db: Session = Depends(DB.fastapi_db_session),
) -> T.ApiResponse:
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # delete from db
    fury_action = db.query(DB.FuryActions).get(fury_id)
    if not fury_action:
        resp.status_code = 404
        return T.ApiResponse(message="FuryAction not found")
    db.delete(fury_action)
    db.commit()
    return T.ApiResponse(message="FuryAction deleted successfully")


# L - List all DB.FuryActions
def list_actions(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=25),
    db: Session = Depends(DB.fastapi_db_session),
):
    # validate user
    user = DB.get_user_from_jwt(token=token, db=db)

    # read from db
    fury_actions = db.query(DB.FuryActions).offset(offset).limit(limit).all()  # type: ignore
    return fury_actions


#
# helper functions
#


def validate_action(fury_action: Union[T.ApiAction, T.ApiActionUpdateRequest], resp: Response) -> Node:
    # if the function is to be updated then perform the full validation same as when creating a new action
    if len(fury_action.outputs) != 1:
        raise HTTPException(status_code=400, detail=f"Only one output must be provided when modifying the function")

    try:
        fury_action.outputs = fury_action.outputs[0].dict()  # type: ignore
        fury_action.outputs = {fury_action.outputs["name"]: fury_action.outputs["loc"]}  # type: ignore
    except Exception as e:
        logger.exception(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Cannot parse function: {e}")

    try:
        node: Node = ai_actions_registry.to_action(
            action_name=fury_action.name,
            node_id=str(uuid4()),
            model_id=fury_action.fn.model_id,
            model_params=fury_action.fn.model_params,
            fn=fury_action.fn.fn,
            outputs=fury_action.outputs,
            description=fury_action.description,
        )
    except Exception as e:
        logger.exception(traceback.format_exc())
        raise HTTPException(status_code=400, detail=f"Cannot parse function: {e}")

    return node  # type: ignore
