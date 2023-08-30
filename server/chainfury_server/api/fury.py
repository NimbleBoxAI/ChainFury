import logging
import traceback
from uuid import uuid4
from functools import lru_cache
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Annotated, Dict, Any, Union
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Depends, Header, Request, Response, Query

from chainfury.agent import model_registry, programatic_actions_registry, ai_actions_registry, memory_registry
from chainfury.base import Node

from chainfury_server.database import fastapi_db_session, FuryActions
from chainfury_server.commons.utils import get_user_from_jwt, verify_user

# build router
fury_router = APIRouter(tags=["fury"])

# add docs to router
fury_router.__doc__ = """
# Fury API

Fury API contains the following:
- ability to get the list of components or get a specific component (`/components/...`)
- ability to CRUDL fury actions (`/actions/...`)
"""

logger = logging.getLogger(__name__)

_MODEL = "models"
_PROGRAMATIC = "programatic_actions"
_ACTION_AI = "ai_actions"
_BUILTIN_AI = "builtin_ai"
_MEMORY = "memory"


@lru_cache(1)
def _components(to_dict: bool = False):
    return {
        _MODEL: model_registry.get_models(),
        _PROGRAMATIC: programatic_actions_registry.get_nodes(),
        _BUILTIN_AI: ai_actions_registry.get_nodes(),
        _MEMORY: memory_registry.get_nodes(),
    }


@fury_router.get("/")
def list_components_types(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    return {"components": list(_components().keys()), "actions": [_ACTION_AI]}


#
# Components API: this is used for models, actions_p and builtin_ai
#


# L
@fury_router.get("/components/{component_type}")
def list_components(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    component_type: str,
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    if component_type not in _components():
        resp.status_code = 404
        return {"error": "Component type not found"}
    return _components()[component_type]


# R
@fury_router.get("/components/{component_type}/{component_id}")
def get_component(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    component_type: str,
    component_id: str,
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    if component_type not in _components():
        resp.status_code = 404
        return {"error": "Component type not found"}

    comps = _components()[component_type]
    item = comps.get(component_id, None)
    if not item:
        resp.status_code = 404
        return {}
    return item


#
# Fury Actions specific APIs
#


# Pydantic model for creating a FuryAction
class ActionRequest(BaseModel):
    class FnModel(BaseModel):
        model_id: str = Field(description="The model ID taken from the /components/models API.")
        model_params: dict = Field(description="The model parameters JSON.")
        fn: dict = Field(description="The function JSON.")

    class OutputModel(BaseModel):
        type: str = Field(description="The type of the output.")
        name: str = Field(description="The name of the output.")
        loc: list[str] = Field(description="The location of the output in the JSON.")

    name: str = Field(description="The name of the action.")
    description: str = Field(description="The description of the action.")
    tags: list[str] = Field(default=[], description="The tags for the action.")
    fn: FnModel = Field(description="The function details for the action.")
    outputs: list[OutputModel] = Field(description="The output details for the action.")


class ActionUpdateRequest(BaseModel):
    name: str = Field(default="", description="The name of the action.")
    description: str = Field(default="", description="The description of the action.")
    tags: list[str] = Field(default=[], description="The tags for the action.")
    fn: ActionRequest.FnModel = Field(default=None, description="The function details for the action.")
    outputs: list[ActionRequest.OutputModel] = Field([], description="The output details for the action.")
    update_fields: list[str] = Field(description="The fields to update.")


# C - Create a new FuryAction
@fury_router.post("/actions/")
def create_fury_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_action: ActionRequest,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # validate action
    node, modified_resp = validate_action(fury_action, resp)
    if modified_resp is not None:
        return modified_resp.body

    # insert into db
    try:
        _node = node.to_dict()
        _node["created_by"] = user.id
        _node["name"] = fury_action.name
        fury_action_data = FuryActions(**_node)
        db.add(fury_action_data)
        db.commit()
        db.refresh(fury_action_data)
    except IntegrityError:
        resp.status_code = 409
        return {"error": "FuryAction already exists"}
    except Exception as e:
        logger.exception(traceback.format_exc())
        resp.status_code = 500
        return {"error": "Internal server error"}

    return fury_action_data


# R - Retrieve a FuryAction by ID
@fury_router.get("/actions/{fury_action_id}")
def get_fury_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_action_id: str,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # read from db
    fury_action = db.query(FuryActions).get(fury_action_id)
    if not fury_action:
        resp.status_code = 404
        return {"error": "FuryAction not found"}
    return fury_action


# U - Update an existing FuryAction
@fury_router.put("/actions/{fury_action_id}")
def update_fury_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_action_id: str,
    fury_action: ActionUpdateRequest,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # validate fields
    if not len(fury_action.update_fields):
        resp.status_code = 400
        return {"error": "No update fields provided"}

    unq_fields = set(fury_action.update_fields)
    valid_fields = {"name", "description", "tags", "fn"}
    if not unq_fields.issubset(valid_fields):
        resp.status_code = 400
        return {"error": f"Invalid update fields provided {unq_fields - valid_fields}"}
    for field in unq_fields:
        if not getattr(fury_action, field):
            resp.status_code = 400
            return {"error": f"Field {field} cannot be empty"}

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
            node, modified_resp = validate_action(fury_action, resp)
            if modified_resp is not None:
                return modified_resp.body
            update_dict.update(node.to_dict())

    # find object
    fury_action_db: FuryActions = db.query(FuryActions).get(fury_action_id)
    if not fury_action_db:
        resp.status_code = 404
        return {"error": "FuryAction not found"}

    # update object
    try:
        fury_action_db.update_from_dict(update_dict)
        db.commit()
        db.refresh(fury_action_db)
    except Exception as e:
        logger.exception(traceback.format_exc())
        resp.status_code = 500
        return {"error": "Internal server error"}
    return fury_action_db


# D - Delete a FuryAction by ID
@fury_router.delete("/actions/{fury_action_id}")
def delete_fury_action(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    fury_action_id: str,
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # delete from db
    fury_action = db.query(FuryActions).get(fury_action_id)
    if not fury_action:
        resp.status_code = 404
        return {"error": "FuryAction not found"}
    db.delete(fury_action)
    db.commit()
    return {"msg": "FuryAction deleted successfully"}


# L - List all FuryActions
@fury_router.get("/actions/")
def list_fury_actions(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    offset: int = Query(0, ge=0),
    limit: int = Query(25, ge=1, le=25),
    db: Session = Depends(fastapi_db_session),
):
    # validate user
    username = get_user_from_jwt(token)
    user = verify_user(db, username)

    # read from db
    fury_actions = db.query(FuryActions).offset(offset).limit(limit).all()
    return fury_actions


#
# helper functions
#


def validate_action(fury_action: Union[ActionRequest, ActionUpdateRequest], resp: Response) -> tuple[Node, Response]:
    # if the function is to be updated then perform the full validation same as when creating a new action
    if len(fury_action.outputs) != 1:
        resp.status_code = 400
        resp.body = {"error": "Only one output must be provided when modifying the function"}  # type: ignore
        return None, resp  # type: ignore

    try:
        fury_action.outputs = fury_action.outputs[0].dict()  # type: ignore
        fury_action.outputs = {fury_action.outputs["name"]: fury_action.outputs["loc"]}  # type: ignore
    except Exception as e:
        logger.exception(traceback.format_exc())
        resp.status_code = 400
        resp.body = {"error": f"Cannot parse outputs: {e}"}  # type: ignore
        return None, resp  # type: ignore

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
        resp.status_code = 400
        resp.body = {"error": str(e)}  # type: ignore
        return None, resp  # type: ignore

    return node, None  # type: ignore
