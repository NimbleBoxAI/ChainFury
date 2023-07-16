import os
import json
from functools import partial

from chainfury_server.plugins.nbx.utils import logger

_nbx_token = os.environ.get("CF_NBX_TOKEN", "")
_nbx_workspace_id = os.environ.get("CF_NBX_WORKSPACE_ID", "")
_nbx_project_id = os.environ.get("CF_NBX_PROJECT_ID", "")

assert _nbx_project_id, "CF_NBX_PROJECT_ID not set"

_dp = f"{os.path.expanduser('~')}/.nbx"
_fp = f"{_dp}/secrets.json"
if not os.path.exists(_fp):
    logger.warning("NimbleBox secrets not found. Creating one...")
    assert _nbx_token, "CF_NBX_TOKEN not set"
    assert _nbx_workspace_id, "CF_NBX_WORKSPACE_ID not set"

    os.makedirs(_dp)
    with open(_fp) as f:
        f.write(
            json.dumps(
                {
                    "nbx_url": "https://app.rc.nimblebox.ai",
                    "access_token": _nbx_token,
                    "config.global.workspace_id": _nbx_workspace_id,
                }
            )
        )

from chainfury_server.plugins.base import CFPluginMetadata
from chainfury_server.plugins.nbx.lmao import NimbleBoxPlugin

plugin_meta = CFPluginMetadata(
    name="nbx",
    version="0.1",
    plugin_class=partial(
        NimbleBoxPlugin,
        project_id=_nbx_project_id,
    ),
)
