import chainfury_server.commons.config as c
from typing import List, Dict
from functools import lru_cache

from chainfury_server.plugins.loader import get_plugin_by_name
from chainfury_server.plugins.base import logger, Event, CFPlugin


class PluginHandler:
    def __init__(self, plugin_names: List[str]):
        self.plugins: Dict[str, CFPlugin] = {}
        for plugin_name in plugin_names:
            logger.info(f"Loading plugin {plugin_name}")
            cf_plugin_meta = get_plugin_by_name(plugin_name)
            cls = cf_plugin_meta.plugin_class()
            try:
                assert isinstance(cls, CFPlugin)
            except AssertionError:
                logger.error(f"Plugin {plugin_name} is not a valid CFPlugin")
                raise
            self.plugins[plugin_name] = cls

    def __repr__(self) -> str:
        return f"<PluginHandler: {self.plugins.keys()}>"

    def handle(self, event: Event):
        for pname, ph in self.plugins.items():
            try:
                ph.handle(event)
            except Exception as e:
                logger.error(f"Error handling event {event.event_type} with plugin {pname}")


@lru_cache(1)
def get_phandler() -> PluginHandler:
    pluginHandler = PluginHandler(c.PluginsConfig.plugins_list)
    logger.info(f"Setting up plugin handler... {pluginHandler}")
    return pluginHandler
