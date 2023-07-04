from dataclasses import dataclass
from typing import Dict, Any, List, Optional

from pydantic import BaseModel


class FENode(BaseModel):
    class CFData(BaseModel):
        id: str
        type: str
        node: Dict[str, Any]
        value: Any = None

    class Position(BaseModel):
        x: float
        y: float

    id: str
    cf_id: str = ""  # this is the id of the node in the chainfury graph
    cf_data: Optional[CFData] = None  # this is the data of the node in the chainfury graph
    position: Position
    type: str
    width: int
    height: int
    selected: bool = None  # type: ignore
    position_absolute: Position = None  # type: ignore
    dragging: bool = None  # type: ignore
    data: dict = {}


class Edge(BaseModel):
    id: str
    source: str
    sourceHandle: str = ""
    target: str
    targetHandle: str = ""


class Dag(BaseModel):
    nodes: List[FENode]
    edges: List[Edge]
    sample: Dict[str, Any] = {}  # type: ignore
    main_in: str = ""
    main_out: str = ""
