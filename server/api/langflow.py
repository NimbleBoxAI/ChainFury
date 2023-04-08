import logging
from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from langflow.interface.run import process_graph
from langflow.interface.types import build_langchain_types_dict

# build router
router = APIRouter(prefix="/flow", tags=["flow"])
# add docs to router
router.__doc__ = """
# Flow API
"""

logger = logging.getLogger(__name__)


@router.get("/components")
def get_all():
    return build_langchain_types_dict()
