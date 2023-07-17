from fastapi import APIRouter

from chainfury_server.commons import config as c

logger = c.get_logger(__name__)


# build router
router = APIRouter(prefix="", tags=["flow"])


@router.get("/components")
def get_all():
    try:
        from langflow.interface.types import build_langchain_types_dict
    except ImportError:
        logger.error("langflow not installed")
        return {}
    return build_langchain_types_dict()
