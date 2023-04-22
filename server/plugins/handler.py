from typing import List

from plugins.loader import get_plugin_by_name
from plugins.base import logger, Event


class PluginHandler:
    def __init__(self, plugin_names: List[str]):
        self.plugins = {}
        for plugin_name in plugin_names:
            logger.info(f"Loading plugin {plugin_name}")
            cf_plugin_meta = get_plugin_by_name(plugin_name)
            cls = cf_plugin_meta.plugin_class()
            self.plugins[plugin_names] = cls

    def handle(self, event: Event):
        for plugin in self.plugins.values():
            plugin.handle(event)
