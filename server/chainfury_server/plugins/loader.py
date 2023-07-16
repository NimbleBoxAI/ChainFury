import os
import sys
from importlib.util import spec_from_file_location, module_from_spec

from chainfury_server.plugins.base import CFPluginMetadata, logger

#
name_to_module = {}
prefix = os.path.dirname(__file__).split("/")[-1]
for f in os.listdir(os.path.dirname(__file__)):
    _fp = prefix + "/" + f
    if os.path.isdir(_fp):
        if "__init__.py" in os.listdir(_fp):
            name_to_module[f] = _fp

logger.info(f"{name_to_module}")


#


def load_module_from_path(mod_name, fn_name, file_path):
    logger.debug(f"Loding module: '{fn_name}' from '{file_path}' storing as '{mod_name}")
    spec = spec_from_file_location(fn_name, file_path)
    foo = module_from_spec(spec)
    sys.modules[mod_name] = foo
    spec.loader.exec_module(foo)
    fn = getattr(foo, fn_name)
    return fn


def get_plugin_by_name(plugin_name: str) -> CFPluginMetadata:
    if plugin_name in name_to_module:
        module_path = name_to_module[plugin_name]
    else:
        raise Exception(f"Plugin '{plugin_name}' not found")

    try:
        plugin_meta = load_module_from_path(
            mod_name=plugin_name.replace("/", "."), fn_name="plugin_meta", file_path=module_path + "/__init__.py"
        )
        return plugin_meta
    except Exception as e:
        raise Exception(f"Could not fine 'plugin_meta' in plugin: '{plugin_name}' | error: {e}")
