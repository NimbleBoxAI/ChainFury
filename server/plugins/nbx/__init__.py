from plugins.base import CFPluginMetadata
from plugins.nbx.lmao import NimbleBoxPlugin

plugin_meta = CFPluginMetadata(
    name="nbx",
    version="0.1",
    plugin_class=NimbleBoxPlugin,
)
