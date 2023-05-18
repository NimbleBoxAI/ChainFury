"""
# Agent

This file contains methods and functions that are used to create an agent, i.e.
- model registry
- memory registry
- functional node registry
"""

import traceback
from functools import lru_cache
from typing import Any, List, Optional, Union, Dict, Tuple

from fury.base import (
    logger,
    func_to_template_fields,
    func_to_return_template_fields,
    Node,
    Model,
    ModelTags,
    Chain,
)

"""
## Models

All the things below are for the models that are registered in the model registry, so that they can be used as inputs
in the chain. There can be several models that can put as inputs in a single chatbot.
"""


class ModelRegistry:
    tags_types = ModelTags

    def __init__(self):
        self.models: Dict[str, Model] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_models: Dict[str, List[str]] = {}

    def has(self, model_id: str):
        return model_id in self.models

    def register(
        self,
        fn: object,
        collection_name: str,
        model_id: str,
        description: str,
        tags: List[str] = [],
    ):
        id = f"{model_id}"
        logger.info(f"Registering model {model_id} at {id}")
        if id in self.models:
            raise Exception(f"Model {model_id} already registered")
        self.models[id] = Model(
            collection_name=collection_name,
            model_id=model_id,
            fn=fn,
            description=description,
            template_fields=func_to_template_fields(fn),
            tags=tags,
        )
        for tag in tags:
            self.tags_to_models[tag] = self.tags_to_models.get(tag, []) + [id]

    def get_tags(self) -> List[str]:
        return list(self.tags_to_models.keys())

    def get_models(self, tag: str = "") -> List[Dict[str, Any]]:
        return [{k: v.to_dict()} for k, v in self.models.items()]

    def get(self, model_id: str) -> Optional[Model]:
        self.counter[model_id] = self.counter.get(model_id, 0) + 1
        out = self.models.get(model_id, None)
        if out is None:
            logger.warning(f"Model {model_id} not found")
        return out

    def get_count_for_model(self, model_id: str) -> int:
        return self.counter.get(model_id, 0)


model_registry = ModelRegistry()


"""
## Programtic Actions Registry

Programtic actions are nodes that are software 1.0 nodes, i.e. they are not trainable. They are used for things like
calling an API, adding 2 numbers, etc. Since they are not trainable the only way to get those is the source code for
the server.
"""


class ProgramaticActionsRegistry:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_nodes: Dict[str, List[str]] = {}

    def register(
        self,
        fn: object,
        node_id: str,
        description: str,
        returns: List[str],
        tags: List[str] = [],
    ):
        logger.info(f"Registering p-node '{node_id}'")
        if node_id in self.nodes:
            raise Exception(f"Node '{node_id}' already registered")
        self.nodes[node_id] = Node(
            id=node_id,
            type=Node.types.PROGRAMATIC,
            fn=fn,
            description=description,
            fields=func_to_template_fields(fn),
            output=func_to_return_template_fields(func=fn, returns=returns),
        )
        for tag in tags:
            self.tags_to_nodes[tag] = self.tags_to_nodes.get(tag, []) + [node_id]

    def get_tags(self) -> List[str]:
        return list(self.tags_to_nodes.keys())

    def get_nodes(self, tag: str = "") -> List[Dict[str, Any]]:
        return [{k: v.to_dict()} for k, v in self.nodes.items()]

    def get(self, node_id: str) -> Optional[Node]:
        self.counter[node_id] = self.counter.get(node_id, 0) + 1
        out = self.nodes.get(node_id, None)
        if out is None:
            logger.warning(f"p-node '{node_id}' not found")
        return out

    def get_count_for_nodes(self, node_id: str) -> int:
        return self.counter.get(node_id, 0)


programatic_actions_registry = ProgramaticActionsRegistry()


"""
## AI Actions Registry

For everything that cannot be done by we have the AI powered actions Registry. This registry
will not include all the things that are available to the outer service, but those that are
hardcoded in the entire thing somewhere.
"""


class AIAction:
    def __init__(
        self, node_id: str, model: Model, model_params: Dict[str, Any], fn: object
    ):
        # do some basic checks that we can do before anything else like checking if model_params
        # is a subset of the model.template_fields
        fields = set(x.name for x in model.template_fields)
        mp_set = set(model_params.keys())
        if not mp_set.issubset(fields):
            raise Exception(f"Model params {mp_set} not a subset of {fields}")

        self.node_id = node_id
        self.model = model
        self.model_params = model_params
        self.fn = fn
        self.fields = func_to_template_fields(fn)

    def __call__(self, **data: Dict[str, Any]) -> Tuple[Any, Optional[Exception]]:
        # we can check again if the incoming keys in the message data are actualyl present in the fields
        # or not for the model
        try:
            # we need to create a sub dict that only contains the fields that are needed by the preprocessor
            # function and pass the rest of the data to the model call
            _data = {}
            for f in self.fields:
                if f.required and f.name not in data:
                    raise Exception(
                        f"Field {f.name} is required in {self.node_id} but not present"
                    )
                if f.name in data:
                    _data[f.name] = data.pop(f.name)

            fn_out = self.fn(**_data)  # type: ignore
            if not type(fn_out) == dict:
                raise Exception(
                    f"AI Action preprocessor for {self.node_id} did not return a dict but {type(fn_out)}"
                )
        except Exception as e:
            return "", e

        # print(">> model_params:", self.model_params)
        # print(">> preprocessor:", fn_out)
        model_final_params = {**self.model_params}
        model_final_params.update(data)
        model_final_params.update(fn_out)
        # print(model_final_params)
        out, err = self.model(model_final_params)
        if err != None:
            return "", err
        return out, err


class AIActionsRegistry:
    def __init__(self):
        self.nodes: Dict[str, Node] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_nodes: Dict[str, List[str]] = {}

    def register(
        self,
        node_id: str,
        description: str,
        model_id: str,
        model_params: Dict[str, Any],
        fn: object = None,
        tags: List[str] = [],
    ):
        logger.info(f"Registering ai-node '{node_id}'")
        model = model_registry.get(model_id)
        if model is None:
            raise Exception(f"Model {model_id} not found")
        ai_action = AIAction(
            node_id=node_id,
            model=model,
            model_params=model_params,
            fn=fn,
        )
        self.nodes[node_id] = Node(
            id=node_id,
            fn=ai_action,
            type=Node.types.AI,
            description=description,
            fields=ai_action.fields + model.template_fields,
            output=func_to_return_template_fields(
                func=ai_action.__call__, returns=["model_output"]
            ),
        )
        for tag in tags:
            self.tags_to_nodes[tag] = self.tags_to_nodes.get(tag, []) + [node_id]

    def get_tags(self) -> List[str]:
        return list(self.tags_to_nodes.keys())

    def get_nodes(self, tag: str = "") -> List[Dict[str, Any]]:
        return [{k: v.to_dict()} for k, v in self.nodes.items()]

    def get(self, node_id: str) -> Optional[Node]:
        self.counter[node_id] = self.counter.get(node_id, 0) + 1
        out = self.nodes.get(node_id, None)
        if out is None:
            logger.warning(f"ai-node '{node_id}' not found")
        return out

    def get_count_for_nodes(self, node_id: str) -> int:
        return self.counter.get(node_id, 0)


ai_actions_registry = AIActionsRegistry()

# class Memory:
#     def __init__(self, memory_id):
#         self.node = Node(id=f"cf-memory-{memory_id}", type=Node.types.MEMORY)

#     # user can subclass this and override the following functions
#     def get(self, key: str):
#         ...

#     def put(self, key: str, value: Any):
#         ...


# # the main class, user can either subclass this or prvide the chain
# class Agent:
#     def __init__(self, models: List[Model], chain: Chain):
#         self.models = models
#         self.chain = chain

#     def __call__(self, user_input: Any):
#         return self.chain(user_input)


# # we LRU cache this to save time on ser / deser
# @lru_cache(128)
# def get_agent(models: List[Model], chain: Chain) -> Agent:
#     return Agent(
#         models=models,
#         chain=chain,
#     )


if __name__ == "__main__":
    pass
