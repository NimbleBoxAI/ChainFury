from fastapi import APIRouter
from langflow.interface.types import build_langchain_types_dict

from chainfury_server.commons import config as c

logger = c.get_logger(__name__)


# build router
router = APIRouter(prefix="/flow", tags=["flow"])
# add docs to router
router.__doc__ = """
# Flow API
"""


@router.get("/components")
def get_all():
    return build_langchain_types_dict()
