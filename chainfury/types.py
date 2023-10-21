from datetime import datetime
from typing import Dict, Any, List, Optional

from pydantic import BaseModel, Field

# First is the set of types that are used in the chainfury itself


class FENode(BaseModel):
    """FENode is the node as required by the UI to render the node in the graph. If you do not care about the UI, you can
    populate either the ``cf_id`` or ``cf_data``."""

    class CFData(BaseModel):
        id: str
        type: str
        node: Dict[str, Any]
        value: Any = None

    cf_id: str = Field("", description="this is the id of the node in the chainfury graph")
    cf_data: Optional[CFData] = Field(None, description="this is the data of the node in the chainfury graph")

    class Position(BaseModel):
        x: float
        y: float

    id: str = Field(description="The ID of the node, this is ignored by engine")
    position: Position = Field(description="The position of the node in the graph")
    type: str = Field("FuryEngineNode", description="The FE type of node")
    width: int = Field(description="Width of the node card")
    height: int = Field(description="Height of the node card")
    selected: Optional[bool] = Field(None, description="Is this node selected")
    position_absolute: Optional[Position] = Field(None, description="The absolute position of the node")
    dragging: Optional[bool] = Field(None, description="Is this node draggable")
    data: Optional[Dict[str, Any]] = Field({}, description="Any extra data to be stored by the node")


class Edge(BaseModel):
    """This is one edge of the graph"""

    id: str = Field(description="The ID of the edge, this is ignored by engine")
    source: str = Field(description="The ID of the source node")
    sourceHandle: str = Field(description="The variable of the source node")
    target: str = Field(description="The ID of the target node")
    targetHandle: str = Field(description="The variable of the target node")


class Dag(BaseModel):
    """This is visual representation of the chain. JSON of this is stored in the DB."""

    nodes: List[FENode]
    edges: List[Edge]
    sample: Dict[str, Any] = Field(default_factory=dict)
    main_in: str = ""
    main_out: str = ""


class CFPromptResult(BaseModel):
    """This is a structured result of the prompt by the Chain. This is more useful for providing types on the server."""

    result: str
    prompt_id: int = 0
    task_id: str = ""


class ApiResponse(BaseModel):
    """This is the default response body of the API"""

    message: str


class ApiPromptBody(BaseModel):
    """This is the prompt for the API to run the chain"""

    session_id: str
    chat_history: List[str] = []
    data: Dict[str, Any] = dict()
    new_message: str = ""


class ApiChain(BaseModel):
    """This is the on-the-wire representation of the chain. This is used by the network to transfer chains"""

    name: str
    dag: Optional[Dag] = None
    description: Optional[str] = None
    id: str = ""
    created_at: Optional[datetime] = None
    engine: str = ""
    update_keys: List[str] = []


class ApiCreateChainRequest(BaseModel):
    """User request to create a new chain"""

    name: str
    engine: str
    dag: Optional[Dag] = None
    description: str = ""


class ApiListChainsResponse(BaseModel):
    """List of all the chains"""

    chatbots: List[ApiChain]


class ApiAction(BaseModel):
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


class ApiActionUpdateRequest(BaseModel):
    name: str = Field(default="", description="The name of the action.")
    description: str = Field(default="", description="The description of the action.")
    tags: list[str] = Field(default=[], description="The tags for the action.")
    fn: ApiAction.FnModel = Field(default=None, description="The function details for the action.")
    outputs: list[ApiAction.OutputModel] = Field([], description="The output details for the action.")
    update_fields: list[str] = Field(description="The fields to update.")


class ApiAuth(BaseModel):
    username: str
    password: str


class ApiSignUp(BaseModel):
    username: str
    email: str
    password: str


class ApiChangePassword(BaseModel):
    username: str
    old_password: str
    new_password: str


class ApiPromptFeedback(BaseModel):
    score: int
