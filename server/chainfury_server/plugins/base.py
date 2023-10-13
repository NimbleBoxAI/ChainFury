from typing import Dict, Any, Callable

from chainfury_server.commons.utils import logger


class EventType:
    PROCESS_PROMPT = "process_prompt"


class Event:
    types = EventType

    def __init__(self, event_type: str, data: Dict[str, Any] = {}):
        self.event_type = event_type
        self.data = data


# All the things now are for the plugin builders to implement


class CFPluginMetadata:
    def __init__(self, name: str, version: str, plugin_class: Callable):
        self.name = name
        self.version = version
        self.plugin_class = plugin_class

    def __repr__(self) -> str:
        return f"<CFPluginMetadata ({self.plugin_class.__name__}) {self.name}=={self.version}>"


class CFPlugin:
    def __init__(self):
        pass

    def handle(self, event: Event):
        raise NotImplementedError("handle method not implemented")
