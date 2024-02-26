# Copyright © 2023- Frello Technology Private Limited

import os
import importlib

from chainfury.utils import logger
from chainfury.utils import folder, joinp


all_items = set()
for p in os.listdir(folder(__file__)):
    if p.startswith("_") or p in ["functional", "ai_actions"]:
        continue
    if os.path.isdir(joinp(folder(__file__), p)):
        mod = importlib.import_module(f"chainfury.components.{p}")
        logger.debug(f"Adding file: {mod.__file__}")
        all_items.add(p)
all_items = list(all_items)

# do this after the above components are loaded
from chainfury.components.functional import *
