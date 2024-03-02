# Copyright © 2023- Frello Technology Private Limited

"""
Actions
=======

All actions that the AI can do.
"""

from typing import Any, List, Optional, Dict

from chainfury.base import (
    Node,
    func_to_return_vars,
    func_to_vars,
    Var,
    get_value_by_keys,
)
from chainfury.utils import logger
from chainfury.core.models import model_registry


class Memory:
    """Class to wrap the DB functions as a callable.

    Args:
        node_id (str): The id of the node
        fn (object): The function that is used for this action
        vector_key (str): The key for the vector in the DB
        read_mode (bool, optional): If the function is a read function, if `False` then this is a write function.
    """

    fields_model = [
        Var(
            name="items",
            type=[Var(type="string"), Var(type="array", items=[Var(type="string")])],
            required=True,
        ),
        Var(name="embedding_model", type="string", required=True),
        Var(
            name="embedding_model_params",
            type="object",
            additionalProperties=Var(type="string"),
        ),
        Var(name="embedding_model_key", type="string"),
        Var(
            name="translation_layer",
            type="object",
            additionalProperties=Var(type="string"),
        ),
    ]
    """These are the fields that are used to map the input items to the embedding model, do not use directly"""

    def __init__(
        self, node_id: str, fn: object, vector_key: str, read_mode: bool = False
    ):
        self.node_id = node_id
        self.fn = fn
        self.vector_key = vector_key
        self.read_mode = read_mode
        self.fields_fn = func_to_vars(fn)
        self.fields = self.fields_fn + self.fields_model

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the Memory object to a dict."""
        return {
            "node_id": self.node_id.split("-")[0],
            "vector_key": self.vector_key,
            "read_mode": self.read_mode,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Deserialize the Memory object from a dict."""
        read_mode = data["read_mode"]
        if read_mode:
            fn = memory_registry.get_read(data["node_id"])
        else:
            fn = memory_registry.get_write(data["node_id"])

        # here we do return Memory type but instead of creating one we use a previously existing Node and return
        # the fn for the Node which is ultimately this precise Memory object
        return fn.fn  # type: ignore

    def __call__(self, **data: Dict[str, Any]) -> Any:
        # the first thing we have to do is get the data for the model. This is actually a very hard problem because this
        # function needs to call some other arbitrary function where we know the inputs to this function "items" but we
        # do not know which variable to pass this to in the undelying model's function. Thus we need to take in a huge
        # amount of things as more inputs ("embedding_model_key", "embedding_model_params"). Then we don't even know
        # what the inputs to the underlying DB functionbare going to be, in which case we also need to add things like
        # the translation that needs to be done ("translation_layer"). This makes the number of inputs a lot but
        # ultimately is required to do the job for robust-ness. Which is why we provide a default for openai-embedding
        # model. For any other model user will need to pass all the information.
        model_fields: Dict[str, Any] = {}
        for f in self.fields_model:
            if f.required and f.name not in data:
                raise Exception(
                    f"Field '{f.name}' is required in {self.node_id} but not present"
                )
            if f.name in data:
                model_fields[f.name] = data.pop(f.name)

        model_data = {**model_fields.get("embedding_model_params", {})}
        model_id = model_fields.pop("embedding_model")

        # TODO: @yashbonde - clean this mess up
        # DEFAULT_MEMORY_CONSTANTS = {
        #     "openai-embedding": {
        #         "embedding_model_key": "input_strings",
        #         "embedding_model_params": {
        #             "model": "text-embedding-ada-002",
        #         },
        #         "translation_layer": {
        #             "embeddings": ["data", "*", "embedding"],
        #         },
        #     }
        # }
        # embedding_model_default_config = DEFAULT_MEMORY_CONSTANTS.get(model_id, {})
        # if embedding_model_default_config:
        #     model_data = {
        #         **embedding_model_default_config.get("embedding_model_params", {}),
        #         **model_data,
        #     }
        #     model_key = embedding_model_default_config.get(
        #         "embedding_model_key", "items"
        #     ) or model_data.get("embedding_model_key")
        #     model_fields["translation_layer"] = model_fields.get(
        #         "translation_layer"
        #     ) or embedding_model_default_config.get("translation_layer")
        # else:

        req_keys = [x.name for x in self.fields_model[2:]]
        if not all([x in model_fields for x in req_keys]):
            raise Exception(f"Model {model_id} requires {req_keys} to be passed")
        model_key = model_fields.get("embedding_model_key")
        model_data = {
            **model_fields.get("embedding_model_params", {}),
            **model_data,
        }
        model_data[model_key] = model_fields.pop("items")  # type: ignore
        model = model_registry.get(model_id)
        embeddings, err = model(model_data=model_data)
        if err:
            logger.error(f"error: {err}")
            logger.error(f"traceback: {embeddings}")
            raise err

        # now that we have all the embeddings ready we now need to translate it to be fed into the DB function
        translated_data = {}
        for k, v in model_fields.get("translation_layer", {}).items():
            translated_data[k] = get_value_by_keys(embeddings, v)

        # create the dictionary to call the underlying function
        db_data = {}
        for f in self.fields_fn:
            if f.required and not (f.name in data or f.name in translated_data):
                raise Exception(
                    f"Field '{f.name}' is required in {self.node_id} but not present"
                )
            if f.name in data:
                db_data[f.name] = data.pop(f.name)
            if f.name in translated_data:
                db_data[f.name] = translated_data.pop(f.name)
        out, err = self.fn(**db_data)  # type: ignore
        return out, err


class MemoryRegistry:
    def __init__(self) -> None:
        self._memories: Dict[str, Node] = {}

    def register_write(
        self,
        component_name: str,
        fn: object,
        outputs: Dict[str, Any],
        vector_key: str,
        description: str = "",
        tags: List[str] = [],
    ) -> Node:
        node_id = f"{component_name}-write"
        mem_fn = Memory(node_id=node_id, fn=fn, vector_key=vector_key, read_mode=False)
        output_fields = func_to_return_vars(fn, returns=outputs)
        node = Node(
            id=node_id,
            fn=mem_fn,
            type=Node.types.MEMORY,
            fields=mem_fn.fields,
            outputs=output_fields,
            description=description,
            tags=tags,
        )
        self._memories[node_id] = node
        return node

    def register_read(
        self,
        component_name: str,
        fn: object,
        outputs: Dict[str, Any],
        vector_key: str,
        description: str = "",
        tags: List[str] = [],
    ) -> Node:
        node_id = f"{component_name}-read"
        mem_fn = Memory(node_id=node_id, fn=fn, vector_key=vector_key, read_mode=True)
        output_fields = func_to_return_vars(fn, returns=outputs)
        node = Node(
            id=node_id,
            fn=mem_fn,
            type=Node.types.MEMORY,
            fields=mem_fn.fields,
            outputs=output_fields,
            description=description,
            tags=tags,
        )
        self._memories[node_id] = node
        return node

    def get_write(self, node_id: str) -> Optional[Node]:
        out = self._memories.get(node_id + "-write", None)
        if out is None:
            raise ValueError(f"Memory '{node_id}' not found")
        return out

    def get_read(self, node_id: str) -> Optional[Node]:
        out = self._memories.get(node_id + "-read", None)
        if out is None:
            raise ValueError(f"Memory '{node_id}' not found")
        return out

    def get_nodes(self):
        return {k: v.to_dict() for k, v in self._memories.items()}


memory_registry = MemoryRegistry()
"""
`memory_registry` is a global instance of MemoryRegistry class. This is used to register and unregister Memory instances.
This is what the user should use when they want to use the memory elements in their chain.
"""
