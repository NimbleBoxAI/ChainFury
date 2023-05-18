import logging
from functools import lru_cache
from fastapi import APIRouter, Depends, Header, Request, Response
from typing import Annotated
from sqlalchemy.orm import Session

from commons.utils import get_user_from_jwt, verify_user

from database import fastapi_db_session

from fury.agent import model_registry, programatic_actions_registry, ai_actions_registry

# build router
components_router = APIRouter(prefix="/components", tags=["components"])
# add docs to router
components_router.__doc__ = """
# Components API
"""

logger = logging.getLogger(__name__)


@lru_cache(1)
def _components():
    return {
        "models": model_registry.get_models(),
        "programs": programatic_actions_registry.get_nodes(),
        "ai_actions": ai_actions_registry.get_nodes(),
    }


@components_router.get("/")
def get_components_resource_data(
    req: Request, token: Annotated[str, Header()], resp: Response
):
    return {"components": list(_components().keys())}


@components_router.get("/{component_type}")
def list_components(
    req: Request,
    component_type: str,
    token: Annotated[str, Header()],
    resp: Response,
    db: Session = Depends(fastapi_db_session),
):
    # username = get_user_from_jwt(token)
    # verify_user(db, username)
    return _components().get(component_type, {"items": []})


@components_router.get("/{component_type}/{component_id}")
def get_component(
    req: Request,
    component_type: str,
    component_id: str,
    token: Annotated[str, Header()],
    resp: Response,
    db: Session = Depends(fastapi_db_session),
):
    # username = get_user_from_jwt(token)
    # verify_user(db, username)
    if component_type == "models":
        model = model_registry.get(component_id)
        if model is None:
            resp.status_code = 404
            return {}
        return model.to_dict()
    elif component_type == "programs":
        node = programatic_actions_registry.get(component_id)
        if node is None:
            resp.status_code = 404
            return {}
        return node.to_dict()
    resp.status_code = 404
    return {}
