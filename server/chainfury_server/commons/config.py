from typing import List


# Things that are user definable: user will configure this file below manually or pass via the CLI
class PluginsConfig:
    plugins_list: List[str] = []  # "echo" is a good starting point
