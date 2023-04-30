from functools import lru_cache
from typing import Any, List, Optional, Union, Dict

from fury.base import func_to_template_fields, Node, logger, TemplateField


class Model:
    def __init__(self, collection_name, model_id, fn: callable, description, template_fields: List[TemplateField], tags=[]):
        self.collection_name = collection_name
        self.model_id = model_id
        self.fn = fn
        self.description = description
        self.template_fields = template_fields
        self.tags = tags

    def to_dict(self):
        return {
            "collection_name": self.collection_name,
            "model_id": self.model_id,
            "description": self.description,
            "tags": self.tags,
            "template_fields": [x.to_dict() for x in self.template_fields],
        }


class ModelTags:
    LLM = "llm"
    OPENSOURCE = "opensource"
    GPT = "gpt"
    VISION = "vision"


class ModelRegistry:
    tags_types = ModelTags

    def __init__(self):
        self.models: Dict[str, Node] = {}
        self.counter: Dict[str, int] = {}
        self.tags_to_models: Dict[str, List[str]] = {}

    def register(self, fn: callable, collection_name: str, model_id: str, description: str, tags: List[str] = []):
        id = f"cf-model-{model_id}"
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
            self.tags_to_models[tag] = self.tags_to_models.get(tag, []) + [
                id,
            ]

    def get_tags(self) -> List[str]:
        return list(self.tags_to_models.keys())

    def get_models(self, tag: str = "") -> List[Dict[str, Any]]:
        return [{k: v.to_dict()} for k, v in self.models.items()]

    def get(self, model_id: str) -> Optional[Node]:
        self.counter[model_id] = self.counter.get(model_id, 0) + 1
        out = self.models.get(model_id, None)
        if out is None:
            logger.warning(f"Model {model_id} not found")
        return out

    def get_count_for_model(self, model_id: str) -> int:
        return self.counter.get(model_id, 0)


model_registry = ModelRegistry()


class Memory:
    def __init__(self, memory_id):
        self.node = Node(id=f"cf-memory-{memory_id}", type=Node.types.MEMORY)

    # user can subclass this and override the following functions
    def get(self, key: str):
        ...

    def put(self, key: str, value: Any):
        ...


class Chain:
    def __init__(self, agent: "Agent"):
        # so the chain can access all the underlying elements of Agent including:
        # - models
        # - memories
        self.agent = Agent

    # user can subclass this and override the __call__
    def __call__(self):
        ...


# the main class, user can either subclass this or prvide the chain
class Agent:
    def __init__(self, models: List[Model], memories: List[Memory], chain: Chain):
        self.models = models
        self.memories = memories
        self.chain = chain

    def __call__(self, user_input: Any):
        return self.chain(user_input)


if __name__ == "__main__":
    pass
