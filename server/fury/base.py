import json
from hashlib import sha256
from typing import Any, Union, Optional, Dict, List
from collections import deque, defaultdict

from commons.config import get_logger

logger = get_logger("fury-core")


class TemplateField:
    def __init__(
        self,
        required: bool = False,
        placeholder: str = "",
        show: bool = True,
        multiline: bool = False,
        value: Any = None,
        password: bool = False,
        name: str = "",
        type: str = "str",
        is_list: bool = False,
        suffixes: list[str] = [],
        file_types: list[str] = [],
        content: Union[str, None] = None,
        options: list[str] = [],
        display_name: Optional[str] = None,
        **kwargs,
    ):
        self.type = type
        self.required = required
        self.placeholder = placeholder
        self.is_list = is_list
        self.show = show
        self.multiline = multiline
        self.value = value
        self.suffixes = suffixes
        self.file_types = file_types
        self.content = content
        self.password = password
        self.options = options
        self.name = name
        self.display_name = display_name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(
            type=data.get("type", "str"),
            required=data.get("required", False),
            placeholder=data.get("placeholder", ""),
            is_list=data.get("list", False),
            show=data.get("show", True),
            multiline=data.get("multiline", False),
            value=data.get("value", None),
            suffixes=data.get("suffixes", []),
            file_types=data.get("fileTypes", []),
            content=data.get("content", None),
            password=data.get("password", False),
            options=data.get("options", []),
            name=data.get("name", ""),
            display_name=data.get("display_name", None),
        )

    def __repr__(self) -> str:
        return f"TemplateField('{self.type}', '{self.name}', '{self.password}')"

    def to_dict(self):
        data = {
            "required": self.required,
            "placeholder": self.placeholder,
            "is_list": self.is_list,
            "show": self.show,
            "multiline": self.multiline,
            "value": self.value,
            "suffixes": self.suffixes,
            "file_types": self.file_types,
            # self.fileTypes = file_types
            "content": self.content,
            "password": self.password,
            "options": self.options,
            "name": self.name,
            "display_name": self.display_name,
            "type": self.type,
            "list": self.is_list,
        }
        return data

    def process_field(self, key: str, value: Dict[str, Any], name: Optional[str] = None) -> None:
        _type = value["type"]

        # Remove 'Optional' wrapper
        if "Optional" in _type:
            _type = _type.replace("Optional[", "")[:-1]

        # Check for list type
        if "List" in _type:
            _type = _type.replace("List[", "")[:-1]
            self.is_list = True

        # Replace 'Mapping' with 'dict'
        if "Mapping" in _type:
            _type = _type.replace("Mapping", "dict")

        # Change type from str to Tool
        self.field_type = "Tool" if key in {"allowed_tools"} else self.field_type

        self.field_type = "int" if key in {"max_value_length"} else self.field_type

        # Show or not field
        self.show = bool((self.required and key not in ["input_variables"]) or key in FORCE_SHOW_FIELDS or "api_key" in key)

        # Add password field
        self.password = any(text in key.lower() for text in {"password", "token", "api", "key"})

        # Add multline
        self.multiline = key in {
            "suffix",
            "prefix",
            "template",
            "examples",
            "code",
            "headers",
        }

        # Replace dict type with str
        if "dict" in self.field_type.lower():
            self.field_type = "code"

        if key == "dict_":
            self.field_type = "file"
            self.suffixes = [".json", ".yaml", ".yml"]
            self.file_types = ["json", "yaml", "yml"]

        # Replace default value with actual value
        if "default" in value:
            self.value = value["default"]

        if key == "headers":
            self.value = """{'Authorization':
            'Bearer <token>'}"""

        # Add options to openai
        if name == "OpenAI" and key == "model_name":
            self.options = constants.OPENAI_MODELS
            self.is_list = True
        elif name == "ChatOpenAI" and key == "model_name":
            self.options = constants.CHAT_OPENAI_MODELS
            self.is_list = True


class NodeConnection:
    def __init__(self, id: str, name: str = "", required: bool = False, description: str = ""):
        self.id = id
        self.name = name
        self.required = required
        self.description = description


class Node:
    def __init__(
        self,
        id: str,
        type: str,
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

    def __repr__(self) -> str:
        out = (
            f"CFNode('{self.id}', '{self.type}', fields: ["  # {len(self.fields)}, inputs:{len(self.inputs)}, outputs:{len(self.outputs)})"
        )
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


class Dag:
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
