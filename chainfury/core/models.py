# Copyright © 2023- Frello Technology Private Limited

"""
Models
======

All things required in a model.
"""

import random
from typing import Any, List, Dict

from chainfury.base import Model
from chainfury.utils import logger


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
        id = model.id
        logger.debug(f"Registering model {id} at {id}")
        if id in self.models:
            raise Exception(f"Model {id} already registered")
        self.models[id] = model
        for tag in model.tags:
            self.tags_to_models[tag] = self.tags_to_models.get(tag, []) + [id]
        return model

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

    def get_any_model(self) -> Model:
        return random.choice(list(self.models.values()))


model_registry = ModelRegistry()
"""
`model_registry` is a global variable that is used to register models. It is an instance of ModelRegistry class.
"""
