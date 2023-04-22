from commons.config import get_logger

logger = get_logger("cf_plugins")


class EventType:
    pass


class Event:
    def __init__(self, event_type: str):
        self.event_type = event_type


# All the things now are for the plugin builders to implement


class CFPluginMetadata:
    def __init__(self, name: str, version: str, plugin_class: type):
        self.name = name
        self.version = version
        self.plugin_class = plugin_class

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name}=={self.version}>"


class CFPlugin:
    def __init__(self):
        pass

    def handle(self, event: Event) -> None:
        raise NotImplementedError("handle method not implemented")
