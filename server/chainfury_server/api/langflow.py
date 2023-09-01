from fastapi import APIRouter, Request, Response, Header
from typing import Annotated
from functools import lru_cache

from chainfury_server.commons import config as c

logger = c.get_logger(__name__)


# build router
router = APIRouter(prefix="", tags=["flow"])

@lru_cache()
def _get_lf_components():
    try:
        from langflow.interface.types import build_langchain_types_dict
    except ImportError:
        logger.error("langflow not installed")
        return {}
    return build_langchain_types_dict()

@router.get("/components")
def get_lf_components(
    req: Request,
    resp: Response,
    token: Annotated[str, Header()],
):
    return _get_lf_components()
