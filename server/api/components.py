import logging
from functools import lru_cache
from fastapi import APIRouter, Depends, Header, Request, Response
from typing import Annotated
from sqlalchemy.orm import Session

from commons.utils import get_user_from_jwt, verify_user

from database import fastapi_db_session

from fury.agent import model_registry

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
        "models": {"items": model_registry.get_models()},
    }


@components_router.get("/")
def get_components_resource_data(req: Request, token: Annotated[str, Header()], resp: Response):
    return {"components": list(_components().keys())}


@components_router.get("/{component_type}")
def list_components(
    req: Request, component_type: str, token: Annotated[str, Header()], resp: Response, db: Session = Depends(fastapi_db_session)
):
    # username = get_user_from_jwt(token)
    # verify_user(db, username)
    return _components().get(component_type, {"items": []})
