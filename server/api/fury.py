import logging
from functools import lru_cache
from fastapi import APIRouter, Depends, Header, Request, Response
from typing import Annotated, Dict, Any
from sqlalchemy.orm import Session

from commons.utils import get_user_from_jwt, verify_user

from database import fastapi_db_session

from fury.agent import model_registry, programatic_actions_registry, ai_actions_registry

# build router
fury_router = APIRouter(prefix="/fury", tags=["fury"])

# add docs to router
fury_router.__doc__ = """
# Fury API

Fury API contains the following:
- ability to CRUDL fury chain
- ability to 
"""

logger = logging.getLogger(__name__)

_MODEL = "models"
_PROGRAMATIC = "actions_p"
_BUILTIN_AI = "builtin_ai"
_ACTION_AI = "action_ai"


@lru_cache(1)
def _components():
    return {
        _MODEL: model_registry.get_models(),
        _PROGRAMATIC: programatic_actions_registry.get_nodes(),
        _BUILTIN_AI: ai_actions_registry.get_nodes(),
    }


#
# Components API
#


@fury_router.get("/components")
def get_components_resource_data(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    verify_user(db, username)
    return {"components": list(_components().keys()) + [_ACTION_AI]}


@fury_router.get("/components/{component_type}")
def list_components(
    req: Request,
    resp: Response,
    component_type: str,
    token: Annotated[str, Header()],
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    verify_user(db, username)

    if component_type in _components():
        return _components()[component_type]

    if component_type != _ACTION_AI:
        resp.status_code = 404
        return []


@fury_router.get("/components/{component_type}/{component_id}")
def get_component(
    req: Request,
    resp: Response,
    component_type: str,
    component_id: str,
    token: Annotated[str, Header()],
    db: Session = Depends(fastapi_db_session),
):
    username = get_user_from_jwt(token)
    verify_user(db, username)

    if component_type in _components():
        comps = _components()[component_type]
        item = list(filter(lambda x: x.id == component_id, comps))
        item = comps.get(component_id)
        if item is None:
            resp.status_code = 404
            return {}
        return item.to_dict()

    if component_type != _ACTION_AI:
        resp.status_code = 404
        return []
