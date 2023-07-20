from typing import List, Dict, Any, Union, Callable
from sqlalchemy.orm import Session

from chainfury_server.commons.config import get_logger

# from chainfury_server.database import PluginKeyValue

logger = get_logger("cf_plugins")


class EventType:
    PROCESS_PROMPT = "process_prompt"


class Event:
    types = EventType

    def __init__(self, event_type: str, data: Any = {}):
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


# # One day, some day
# def __get_db() -> Session:
#     return Session()
#
# class CFPluginKV:
#     __plugin_name = ""
#     def write(self, key: str, value: str) -> str:
#         db = __get_db()
#         k = self.__plugin_name + "/" + key
#         db.merge(PluginKeyValue(key=k, value=value))
#         return key


class CFPlugin:
    def __init__(self):
        pass

    def handle(self, event: Event):
        raise NotImplementedError("handle method not implemented")
