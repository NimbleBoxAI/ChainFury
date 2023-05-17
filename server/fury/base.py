import json
import inspect
from hashlib import sha256
from typing import Any, Union, Optional, Dict, List, Tuple, Callable
from collections import deque, defaultdict

from commons.config import get_logger

logger = get_logger("fury-core")


class Secret(str):
    """This class just means that in TemplateField it will be taken as a password field"""


#
# TemplateFields: this is the base class for all the fields that the user can provide from the front end
#


class TemplateField:
    def __init__(
        self,
        type: Union[str, List["TemplateField"]],
        format: str = "",
        items: List["TemplateField"] = [],
        additionalProperties: Union[Dict, "TemplateField"] = {},
        password: bool = False,
        #
        required: bool = False,
        placeholder: str = "",
        show: bool = False,
        name: str = "",
    ):
        self.type = type
        self.format = format
        self.items = items or []
        self.additionalProperties = additionalProperties
        self.password = password
        #
        self.required = required
        self.placeholder = placeholder
        self.show = show
        self.name = name

    def __repr__(self) -> str:
        return (
            f"TemplateField(type={self.type}, format={self.format}, items={self.items}, additionalProperties={self.additionalProperties})"
        )

    def to_dict(self) -> Dict[str, Any]:
        d = {"type": self.type}
        if type(self.type) == list and len(self.type) and type(self.type[0]) == TemplateField:
            d["type"] = [x.to_dict() for x in self.type]
        if self.format:
            d["format"] = self.format
        if self.items:
            d["items"] = [item.to_dict() for item in self.items]
        if self.additionalProperties:
            if isinstance(self.additionalProperties, TemplateField):
                d["additionalProperties"] = self.additionalProperties.to_dict()
            else:
                d["additionalProperties"] = self.additionalProperties
        if self.password:
            d["password"] = self.password
        #
        if self.required:
            d["required"] = self.required
        if self.placeholder:
            d["placeholder"] = self.placeholder
        if self.show:
            d["show"] = self.show
        if self.name:
            d["name"] = self.name
        return d


def pyannotation_to_json_schema(x) -> TemplateField:
    if isinstance(x, type):
        if x == str:
            return TemplateField(type="string")
        elif x == int:
            return TemplateField(type="integer")
        elif x == float:
            return TemplateField(type="number")
        elif x == bool:
            return TemplateField(type="boolean")
        elif x == bytes:
            return TemplateField(type="string", format="byte")
        elif x == list:
            return TemplateField(type="array", items=[TemplateField(type="string")])
        elif x == dict:
            return TemplateField(type="object", additionalProperties=TemplateField(type="string"))
        elif x == Secret:
            return TemplateField(type="string", password=True)
        else:
            raise ValueError(f"i0: Unsupported type: {x}")
    elif isinstance(x, str):
        return TemplateField(type="string")
    elif hasattr(x, "__origin__") and hasattr(x, "__args__"):
        if x.__origin__ == list:
            return TemplateField(type="array", items=[pyannotation_to_json_schema(x.__args__[0])])
        elif x.__origin__ == dict:
            if len(x.__args__) == 2 and x.__args__[0] == str:
                return TemplateField(type="object", additionalProperties=pyannotation_to_json_schema(x.__args__[1]))
            else:
                raise ValueError(f"i2: Unsupported type: {x}")
        elif x.__origin__ == tuple:
            return TemplateField(type="array", items=[pyannotation_to_json_schema(arg) for arg in x.__args__])
        elif x.__origin__ == Union:
            # Unwrap union types with None type
            types = [arg for arg in x.__args__ if arg is not None]
            if len(types) == 1:
                return pyannotation_to_json_schema(types[0])
            else:
                return TemplateField(type=[pyannotation_to_json_schema(typ) for typ in types])
        else:
            print(x.__origin__)
            raise ValueError(f"i3: Unsupported type: {x}")
    elif isinstance(x, tuple):
        return TemplateField(type="array", items=[TemplateField(type="string"), pyannotation_to_json_schema(x[1])] * len(x))
    else:
        raise ValueError(f"i4: Unsupported type: {x}")


def func_to_template_fields(func) -> List[TemplateField]:
    """
    Extracts the signature of a function and converts it to an array of TemplateField objects.
    """
    signature = inspect.signature(func)
    fields = []
    for param in signature.parameters.values():
        schema = pyannotation_to_json_schema(param.annotation)
        schema.required = param.default is inspect.Parameter.empty
        schema.name = param.name
        schema.placeholder = str(param.default) if param.default is not inspect.Parameter.empty else ""
        if not schema.name.startswith("_"):
            schema.show = True
        fields.append(schema)
    return fields


#
# Node: Each box that is drag and dropped in the UI is a Node, it will tell what kind of things are
#       its inputs, outputs and fields that are shown in the UI. It can be of different types and
#       it only wraps teh
#


class NodeType:
    PROGRAMATIC = "programatic"
    LLM = "llm"


class NodeConnection:
    def __init__(self, id: str, name: str = "", required: bool = False, description: str = ""):
        self.id = id
        self.name = name
        self.required = required
        self.description = description


class Node:
    types = NodeType

    def __init__(
        self,
        id: str,
        type: str,
        fn: Callable = None,
        description: str = "",
        inputs: List[NodeConnection] = [],
        fields: List[TemplateField] = [],
        outputs: List[NodeConnection] = [],
    ):
        self.id = id
        self.type = type
        self.description = description
        self.inputs = inputs
        self.fields = fields
        self.outputs = outputs
        self.fn = fn

    def __repr__(self) -> str:
        out = f"CFNode('{self.id}', '{self.type}', fields: [{len(self.fields)}, inputs:{len(self.inputs)}, outputs:{len(self.outputs)})"
        for f in self.fields:
            out += f"\n      {f},"
        out += "])"
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any], use_langflow_dag: bool = True):
        # inputs = ([NodeConnection(**input) for input in data["inputs"]],)
        # fields=[TemplateField(**field) for field in data["fields"]],
        # outputs=[NodeConnection(**output) for output in data["outputs"]],
        if use_langflow_dag:
            node_data = data.get("data", {})
            # fields = [TemplateField.from_dict(x) .values()]
            fields = []
            for k, v in node_data.get("node", {}).get("template", {}).items():
                if type(v) == dict:
                    fields.append(TemplateField.from_dict(v))
        else:
            node_data = data
            fields = [TemplateField.from_dict(x) for x in node_data.get("template", [])]
        return cls(
            id=data.pop("id", ""),
            type=data.pop("type", ""),
            description=node_data.pop("description", ""),
            fields=fields,
        )

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "description": self.description,
            "fields": [field.to_dict() for field in self.fields],
        }


#
# Edge: Each connection between two boxes on the UI is called an Edge, it is only a dataclass without any methods.
#


class Edge:
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target

    def __repr__(self) -> str:
        return f"CFEdge('{self.source}', '{self.target}')"

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            source=data["source"],
            target=data["target"],
        )

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
        }


#
# Dag: An entire flow is called the Chain
#


class Chain:
    def __init__(
        self,
        nodes: List[Node] = [],
        edges: List[Edge] = [],
    ):
        self.nodes = nodes
        self.edges = edges

    def __repr__(self) -> str:
        # return f"CFDag(nodes: {len(self.nodes)}, edges: {len(self.edges)})"
        out = "CFDag(\n  nodes: ["
        for n in self.nodes:
            out += f"\n    {n},"
        out += "\n  ],\n  edges: ["
        for e in self.edges:
            out += f"\n    {e},"
        out += "\n  ]\n)"
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            nodes=[Node.from_dict(x) for x in data.get("nodes", [])],
            edges=[Edge.from_dict(x) for x in data.get("edges", [])],
        )

    def to_dict(self):
        return {
            "nodes": [x.to_dict() for x in self.nodes],
            "edges": [x.to_dict() for x in self.edges],
        }

    def hash(self) -> str:
        return sha256(json.dumps(self.to_dict).encode("utf-8")).hexdigest()

    def build(self):
        # this function builds the final langchain dag that will be executed, in order to determine the order of execution in a DAG
        # the algorithm is called 'topological sort'
        out = topological_sort(self.edges)
        print(out)


# helper functions


class NotDAGError(Exception):
    pass


def edge_array_to_adjacency_list(edges: List[Edge]):
    """Convert silk format dag edges to adjacency list format"""
    adjacency_lists = {}
    for edge in edges:
        src = edge.source
        dst = edge.target
        if src not in adjacency_lists:
            adjacency_lists[src] = []
        adjacency_lists[src].append(dst)
    return adjacency_lists


def adjacency_list_to_edge_map(adjacency_list) -> List[Edge]:
    """Convert adjacency list format to silk format dag edges"""
    edges = []
    for src, dsts in adjacency_list.items():
        for dst in dsts:
            edges.append(Edge(source=src, target=dst))
    return edges


def topological_sort(edges: List[Edge]) -> List[str]:
    """Topological sort of a DAG, raises NotDAGError if the graph is not a DAG"""
    adjacency_lists = edge_array_to_adjacency_list(edges)
    in_degree = defaultdict(int)
    for src, dsts in adjacency_lists.items():
        for dst in dsts:
            in_degree[dst] += 1

    # Add all nodes with no incoming edges to the queue
    queue = deque()
    for node in adjacency_lists:
        if in_degree[node] == 0:
            queue.append(node)

    # For each node, remove it from the graph and add it to the sorted list
    sorted_list = []
    edge_nodes_cntr = 0
    while queue:
        node = queue.popleft()
        sorted_list.append(node)
        neighbours = adjacency_lists.get(node, [])
        if not neighbours:
            edge_nodes_cntr += 1
        for neighbor in neighbours:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    # Check to see if all edges are removed
    if len(sorted_list) == len(adjacency_lists) + edge_nodes_cntr:
        return sorted_list
    else:
        raise NotDAGError("A cycle exists in the graph.")
