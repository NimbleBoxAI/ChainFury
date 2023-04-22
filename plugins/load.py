import os

print("Loading plugins...", end="")
f_prefix = "plugins"
files = os.listdir(os.path.dirname(__file__))
plugin_name_to_module = dict()
name_to_module = lambda f: f.replace(".py", "")
for f in files:
    _folder = f_prefix + "/" + f
    if f.endswith(".py") and f not in ["__init__.py", "load.py"]:
        plugin_name_to_module[f] = name_to_module(f).replace(".py", "")
    elif os.path.isdir(_folder):
        # check if it has __init__.py
        if "__init__.py" in os.listdir(_folder):
            plugin_name_to_module[f] = f_prefix + "." + name_to_module(f)
print("Ok!")


def get_plugin_by_name(name: str):
    if name in plugin_name_to_module:
        return plugin_name_to_module[name]
    return None


if __name__ == "__main__":
    from pprint import pprint

    pprint(plugin_name_to_module)
