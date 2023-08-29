"""
Agent
=====

We follow registry pattern for models and actions.
"""

import copy
from uuid import uuid4
from typing import Any, List, Optional, Dict, Tuple

import jinja2

from chainfury.utils import logger
from chainfury.base import (
    func_to_vars,
    func_to_return_vars,
    extract_jinja_indices,
    get_value_by_keys,
    put_value_by_keys,
    Node,
    Model,
    Var,
)

# Models
# ------
# All the things below are for the models that are registered in the model registry, so that they can be used as inputs
# in the chain. There can be several models that can put as inputs in a single chatbot.


class ModelRegistry:
    """Model registry contains metadata for all the models that are provided in the components"""

    def __init__(self):
        self.models: Dict[str, Model] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_models: Dict[str, List[str]] = {}

    def has(self, id: str):
        """A helper function to check if a model is registered or not"""
        return id in self.models

    def register(self, model: Model):
        """Register a model in the registry

        Args:
            model (Model): Model to register
        """
        id = f"{model.id}"
        logger.debug(f"Registering model {id} at {id}")
        if id in self.models:
            raise Exception(f"Model {id} already registered")
        self.models[id] = model
        for tag in model.tags:
            self.tags_to_models[tag] = self.tags_to_models.get(tag, []) + [id]

    def get_tags(self) -> List[str]:
        """Get all the tags that are registered in the registry

        Returns:
            List[str]: List of tags
        """
        return list(self.tags_to_models.keys())

    def get_models(self, tag: str = "") -> Dict[str, Dict[str, Any]]:
        """Get all the models that are registered in the registry

        Args:
            tag (str, optional): Filter models by tag. Defaults to "".

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of models
        """
        items = {k: v.to_dict() for k, v in self.models.items()}
        if tag:
            items = {k: v for k, v in items.items() if tag in v.get("tags", [])}
        return items

    def get(self, id: str) -> Model:
        """Get a model from the registry

        Args:
            id (str): Id of the model

        Returns:
            Model: Model
        """
        self.counter[id] = self.counter.get(id, 0) + 1
        out = self.models.get(id, None)
        if out is None:
            raise ValueError(f"Model {id} not found")
        return out

    def get_count_for_model(self, id: str) -> int:
        """Get the number of times a model is used

        Args:
            id (str): Id of the model

        Returns:
            int: Number of times the model is used
        """
        return self.counter.get(id, 0)


model_registry = ModelRegistry()
"""
`model_registry` is a global variable that is used to register models. It is an instance of ModelRegistry class.
"""


# Programtic Actions Registry
# ---------------------------
# Programtic actions are nodes that are software 1.0 nodes, i.e. they are not trainable. They are used for things like
# calling an API, adding 2 numbers, etc. Since they are not trainable the only way to get those is the source code for
# the server.


class ProgramaticActionsRegistry:
    """Programatic actions registry contains metadata for all the programatic actions that are provided in the
    components"""

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_nodes: Dict[str, List[str]] = {}

    def register(
        self,
        fn: object,
        node_id: str,
        description: str,
        returns: List[str] = [],
        outputs=None,
        tags: List[str] = [],
    ) -> Node:
        """Register a programatic action in the registry

        Args:
            fn (object): Function to register
            node_id (str): Id of the node
            description (str): Description of the node
            returns (List[str], optional): List of returns. Defaults to [].
            outputs ([type], optional): [description]. Defaults to None.
            tags (List[str], optional): List of tags. Defaults to [].

        Raises:
            Exception: If the node is already registered

        Returns:
            Node: Node
        """
        logger.debug(f"Registering p-node '{node_id}'")
        if node_id in self.nodes:
            raise Exception(f"Node '{node_id}' already registered")
        if not outputs:
            assert len(returns), "If outputs is not provided then returns must be provided"
            outputs = {x: () for x in returns}
        else:
            assert len(outputs), "If returns is not provided then outputs must be provided"
        ops = func_to_return_vars(func=fn, returns=outputs)
        node = Node(
            id=node_id,
            type=Node.types.PROGRAMATIC,
            fn=fn,
            description=description,
            fields=func_to_vars(fn),
            outputs=ops,
            tags=tags,
        )
        self.nodes[node_id] = node
        for tag in tags:
            self.tags_to_nodes[tag] = self.tags_to_nodes.get(tag, []) + [node_id]
        return self.nodes[node_id]

    def get_tags(self) -> List[str]:
        """Get all the tags that are registered in the registry

        Returns:
            List[str]: List of tags
        """
        return list(self.tags_to_nodes.keys())

    def get_nodes(self, tag: str = "") -> Dict[str, Dict[str, Any]]:
        """Get all the nodes that are registered in the registry

        Args:
            tag (str, optional): Filter nodes by tag. Defaults to "".

        Returns:
            Dict[str, Dict[str, Any]]: Dictionary of nodes
        """
        items = {k: v.to_dict() for k, v in self.nodes.items()}
        if tag:
            items = {k: v for k, v in items.items() if tag in v.get("tags", [])}
        return items

    def get(self, node_id: str) -> Optional[Node]:
        """Get a node from the registry

        Args:
            node_id (str): Id of the node

        Returns:
            Node: Node
        """
        self.counter[node_id] = self.counter.get(node_id, 0) + 1
        out = self.nodes.get(node_id, None)
        if out is None:
            raise ValueError(f"p-node '{node_id}' not found")
        return copy.deepcopy(out)

    def get_count_for_nodes(self, node_id: str) -> int:
        """Get the number of times a node is used

        Args:
            node_id (str): Id of the node

        Returns:
            int: Number of times the node is used
        """
        return self.counter.get(node_id, 0)


programatic_actions_registry = ProgramaticActionsRegistry()
"""
`programatic_actions_registry` is a global variable that is used to register programatic nodes. It is an instance of
ProgramaticActionsRegistry class.
"""


# AI Actions Registry
# -------------------
# For everything that cannot be done by we have the AI powered actions Registry. This registry
# will not include all the things that are available to the outer service, but those that are
# hardcoded in the entire thing somewhere.


class AIAction:
    """This class is a callable for all the AI actions.

    Args:
        node_id (str): The id of the node
        model (Model): The model that is used for this action
        model_params (Dict[str, Any]): The parameters for the model
        fn (object): The function that is used for this action
    """

    # do not remove these from here it is used in base.py if you do then put in a third file
    JTYPE = "jinja-template"
    """constant for Jinja template type"""

    FUNC = "python-function"
    """constant for Python function type"""

    def __init__(self, node_id: str, model: Model, model_params: Dict[str, Any], fn: object, action_name: str):
        # do some basic checks that we can do before anything else like checking if model_params
        # is a subset of the model.vars
        fields = set(x.name for x in model.vars)
        mp_set = set(model_params.keys())
        if not mp_set.issubset(fields):
            raise Exception(f"Model params {mp_set} not a subset of {fields}")

        self.templates = []

        # since this is the AI action this is responsible for validating the function
        if type(fn) == dict:
            action_source = AIAction.JTYPE
            fields = []  # fields required for self.fields
            templates = []  # list of all the templates to be render with its position in fn
            fields_with_locations = extract_jinja_indices(fn)
            for field in fields_with_locations:
                fields.extend(field[1])
                obj = get_value_by_keys(fn, field[0])
                if not obj:
                    raise ValueError(f"Field {field[0]} not found in {fn}, but was extraced. There is a bug in get_value_by_keys function")
                templates.append((obj, jinja2.Template(obj), field[0]))

            # set values
            self.templates = templates
        else:
            assert type(fn) == type(func_to_return_vars), "`fn` can either be a function or a string"
            action_source = AIAction.FUNC
            fields = func_to_vars(fn)

        self.node_id = node_id
        self.model = model
        self.model_params = model_params
        self.fn = fn
        self.action_name = action_name
        self.action_source = action_source
        self.fields = fields

    def to_dict(self, no_vars: bool = False) -> Dict[str, Any]:
        """Serialize the AIAction object to a dict."""
        return {
            "node_id": self.node_id,
            "model": self.model.to_dict(no_vars=no_vars),
            "model_params": self.model_params,
            "fn": self.fn,
            "action_name": self.action_name,
            "action_source": self.action_source,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        """Deserialize the AIAction object from a dict."""
        return cls(
            node_id=data["node_id"],
            model=model_registry.get(data["model"]["id"]),
            model_params=data["model_params"],
            fn=data["fn"],
            action_name=data.get("action_name", data["node_id"]),
        )

    def __call__(self, **data: Dict[str, Any]) -> Tuple[Any, Optional[Exception]]:
        """This is a callable that takes in all the arguments that the underlying models take.

        Args:
            **data (Dict[str, Any]): The data that is passed to the model

        Returns:
            Tuple[Any, Optional[Exception]]: The output of the model and the exception if any
        """

        # check for keys even before calling any API or something
        # we need to create a sub dict that only contains the fields that are needed by the preprocessor
        # function and pass the rest of the data to the model call
        _data = {}
        for f in self.fields:
            if f.required and f.name not in data:
                raise Exception(f"Field '{f.name}' is required in {self.node_id} but not present")
            if f.name in data:
                _data[f.name] = data.pop(f.name)

        if self.action_source == AIAction.FUNC:
            try:
                fn_out = self.fn(**_data)  # type: ignore
                if self.action_source == AIAction.FUNC and not type(fn_out) == dict:
                    raise Exception(f"AI Action preprocessor for {self.node_id} did not return a dict but {type(fn_out)}")
            except Exception as e:
                return "", e
        elif self.action_source == AIAction.JTYPE:
            fn_out = copy.deepcopy(self.fn)
            for raw, t, keys in self.templates:
                value = t.render(**_data)
                put_value_by_keys(fn_out, keys, value)

        # print(">> model_params:", self.model_params)
        # print(">> preprocessor:", fn_out)
        model_final_params = {**self.model_params}
        model_final_params.update(data)
        model_final_params.update(fn_out)  # type: ignore
        out, err = self.model(model_final_params)
        if err != None:
            return "", err

        return out, err


class AIActionsRegistry:
    """This class is a registry for all the AI actions."""

    DB_REGISTER = "db"

    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_nodes: Dict[str, List[str]] = {}

    def to_action(
        self,
        action_name: str,
        model_id: str,
        model_params: Dict[str, Any],
        fn: object,
        outputs: Dict[str, Any],
        node_id: str = "",
        description: str = "",
    ) -> Node:
        """
        function to create an "Action" aka. `chainfury.Node`.

        **NOTE:** If you do not pass `node_id` then this will create a `uudi4`. This behaviour is important when dev
        wants to play with the action without commiting it anywhere.

        Args:
            model_id (str): The model id that is to be used for this action
            model_params (Dict[str, Any]): The model params that are to be used for this action
            fn (object): The function that is to be used as a preprocessor for this action
            outputs: This is a dict like `{'x': (-1, 'b', 'c')}`, if provided function returns a dictionary with key `x`
              and value automatically extracted from the model output at location `(-1, 'b', 'c')`.
            node_id (str, optional): The node id for this action. Defaults to "".
            description (str, optional): The description for this action. Defaults to "".

        Returns:
            Node: The node object that can be used to create a chain
        """
        node_id = node_id or str(uuid4())
        model = model_registry.get(model_id)
        if model is None:
            raise Exception(f"Model {model_id} not found")
        ai_action = AIAction(
            node_id=node_id,
            model=model,
            model_params=model_params,
            fn=fn,
            action_name=action_name,
        )
        if not outputs:
            output_field = func_to_return_vars(func=ai_action.__call__, returns={"model_output": ()})
        else:
            output_field = [Var(type="string", name=k, loc=loc) for k, loc in outputs.items()]
        node = Node(
            id=node_id,
            fn=ai_action,
            type=Node.types.AI,
            description=description,
            fields=ai_action.fields + model.vars,
            outputs=output_field,
        )
        return node

    def register(
        self,
        node_id: str,
        model_id: str,
        model_params: Dict[str, Any],
        fn: object,
        outputs: Dict[str, Any],
        action_name: str = "",
        description: str = "",
        tags: List[str] = [],
    ) -> Node:
        """
        This function will register this action in the local AI registry so it is accesible everywhere. Use this when
        you are hosting your own chainfury server and want to serve private functions not available in the public DB.
        If you are using this just for your local usecase and have no interest in the serving capabilities then
        use `to_action` instead.

        **NOTE:** If you do not pass `node_id` then this will create a `uudi4`. This behaviour is important when dev
        wants to play with the action without commiting it anywhere.

        Args:
            node_id (str): The node id for this action
            model_id (str): The model id that is to be used for this action
            model_params (Dict[str, Any]): The model params that are to be used for this action
            fn (object): The function that is to be used as a preprocessor for this action
            outputs: This is a dict like `{'x': (-1, 'b', 'c')}`, if provided function returns a dictionary with key `x`
                and value automatically extracted from the model output at location `(-1, 'b', 'c')`.
            description (str, optional): The description for this action. Defaults to "".
            tags (List[str], optional): The tags for this action. Defaults to [].
        """
        logger.debug(f"Registering ai-node '{node_id}'")
        if node_id != AIActionsRegistry.DB_REGISTER and node_id in self.nodes:
            raise ValueError(f"ai-node '{node_id}' already exists")
        node = self.to_action(
            action_name=action_name or node_id,
            node_id=node_id,
            model_id=model_id,
            model_params=model_params,
            fn=fn,
            outputs=outputs,
            description=description,
        )

        # this node can be registered in DB
        if node_id == AIActionsRegistry.DB_REGISTER:
            pass

        # this is just the server instance register
        else:
            self.nodes[node_id] = node
            for tag in tags:
                self.tags_to_nodes[tag] = self.tags_to_nodes.get(tag, []) + [node_id]
        return node

    def register_node(self, node: Node) -> Node:
        logger.debug(f"Registering ai-node '{node.id}'")
        if node.id in self.nodes:
            raise ValueError(f"ai-node '{node.id}' already exists")
        self.nodes[node.id] = node
        for tag in node.tags:
            self.tags_to_nodes[tag] = self.tags_to_nodes.get(tag, []) + [node.id]
        return node

    def unregister(self, node_id: str):
        """Unregister an ai-node

        Args:
            node_id (str): The node id for this action

        Raises:
            ValueError: If the node is not found
        """
        logger.debug(f"Unregistering ai-node '{node_id}'")
        node = self.nodes.pop(node_id, None)
        if node is None:
            raise ValueError(f"ai-node '{node_id}' not found")
        for tag, nodes in self.tags_to_nodes.items():
            if node_id in nodes:
                nodes.remove(node_id)
                if not nodes:
                    self.tags_to_nodes.pop(tag)
                break

    def get_tags(self) -> List[str]:
        """Get all the tags that are registered

        Returns:
            List[str]: The list of tags
        """
        return list(self.tags_to_nodes.keys())

    def get_nodes(self, tag: str = "") -> Dict[str, Dict[str, Any]]:
        """Get all the nodes that are registered

        Args:
            tag (str, optional): The tag to filter the nodes. Defaults to "".

        Returns:
            Dict[str, Dict[str, Any]]: The dict of nodes
        """
        items = {k: v.to_dict() for k, v in self.nodes.items()}
        if tag:
            items = {k: v for k, v in items.items() if tag in v.get("tags", [])}
        return items

    def get(self, node_id: str) -> Optional[Node]:
        """Get the node for the given node id

        Args:
            node_id (str): The node id for this action

        Returns:
            Optional[Node]: The node object
        """
        self.counter[node_id] = self.counter.get(node_id, 0) + 1
        out = self.nodes.get(node_id, None)
        if out is None:
            raise ValueError(f"ai-node '{node_id}' not found")
        return Node.from_dict(copy.deepcopy(out.to_dict()))

    def get_count_for_nodes(self, node_id: str) -> int:
        """Get number of times a particular node is called

        Args:
            node_id (str): The node id for this action

        Returns:
            int: The number of times the node is called
        """
        return self.counter.get(node_id, 0)


ai_actions_registry = AIActionsRegistry()
"""
`ai_actions_registry` is a global instance of `AIActionsRegistry` class. This is used to register and unregister
`AIAction` instances. This is used by the server to serve the registered actions.
"""

DEFAULT_MEMORY_CONSTANTS = {
    "openai-embedding": {
        "embedding_model_key": "input_strings",
        "embedding_model_params": {
            "model": "text-embedding-ada-002",
        },
        "translation_layer": {
            "embeddings": ["data", "*", "embedding"],
        },
    }
}


class Memory:
    """Class to wrap the DB functions as a callable.

    Args:
        node_id (str): The id of the node
        fn (object): The function that is used for this action
        vector_key (str): The key for the vector in the DB
        read_mode (bool, optional): If the function is a read function, if `False` then this is a write function.
    """

    fields_model = [
        Var(name="items", type=[Var(type="string"), Var(type="array", items=[Var(type="string")])], required=True),
        Var(name="embedding_model", type="string", required=True),
        Var(name="embedding_model_params", type="object", additionalProperties=Var(type="string")),
        Var(name="embedding_model_key", type="string"),
        Var(name="translation_layer", type="object", additionalProperties=Var(type="string")),
    ]
    """These are the fields that are used to map the input items to the embedding model, do not use directly"""

    def __init__(self, node_id: str, fn: object, vector_key: str, read_mode: bool = False):
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
                raise Exception(f"Field '{f.name}' is required in {self.node_id} but not present")
            if f.name in data:
                model_fields[f.name] = data.pop(f.name)

        model_data = {**model_fields.get("embedding_model_params", {})}
        model_id = model_fields.pop("embedding_model")
        embedding_model_default_config = DEFAULT_MEMORY_CONSTANTS.get(model_id, {})
        if embedding_model_default_config:
            model_data = {**embedding_model_default_config.get("embedding_model_params", {}), **model_data}
            model_key = embedding_model_default_config.get("embedding_model_key", "items") or model_data.get("embedding_model_key")
            model_fields["translation_layer"] = model_fields.get("translation_layer") or embedding_model_default_config.get(
                "translation_layer"
            )
        else:
            req_keys = [x.name for x in self.fields_model[2:]]
            if not all([x in model_fields for x in req_keys]):
                raise Exception(f"Model {model_id} requires {req_keys} to be passed")
            model_key = model_fields.get("embedding_model_key")
            model_data = {**model_fields.get("embedding_model_params", {}), **model_data}
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
                raise Exception(f"Field '{f.name}' is required in {self.node_id} but not present")
            if f.name in data:
                db_data[f.name] = data.pop(f.name)
            if f.name in translated_data:
                db_data[f.name] = translated_data.pop(f.name)
        out, err = self.fn(**db_data)  # type: ignore
        return out, err


class MemoryRegistry:
    def __init__(self) -> None:
        self._memories = {}

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
