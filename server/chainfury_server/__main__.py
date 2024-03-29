# Copyright © 2023- Frello Technology Private Limited

import os
import dotenv
import fire, uvicorn
from typing import List
import importlib

_dotenv_fp = os.getenv("CFS_DOTENV", ".env")
if os.path.exists(_dotenv_fp):
    dotenv.load_dotenv(_dotenv_fp)


def main(
    host: str = "0.0.0.0",
    port: int = 8000,
    pre: List[str] = [],
    post: List[str] = [],
):
    """
    Starts the server with the given configuration

    Args:
        host (str, optional): Host to run the server on. Defaults to "
        port (int, optional): Port to run the server on. Defaults to 8000.
        pre (List[str], optional): List of modules to load before the server is imported. Defaults to [].
        post (List[str], optional): List of modules to load after the server is imported. Defaults to [].
    """
    # WARNING: ensure that nothing is being imported in the utils from chainfury_server
    from chainfury.cli import CLI
    from chainfury_server.utils import logger
    from chainfury_server.version import __version__ as cfs_version

    logger.info(
        f"{CLI.info}\n"
        f"Starting ChainFury server ...\n"
        f"       Host: {host}\n"
        f"       Port: {port}\n"
        f"        Pre: {pre}\n"
        f"       Post: {post}\n"
        f"  cf_server: {cfs_version}"
    )

    # load all things you need to preload the modules
    for mod in pre:
        logger.info(f"Pre Loading {mod}")
        importlib.import_module(mod)

    # server setup happens here
    from chainfury_server.app import app

    # load anything after the server is loaded, this is cool for
    for mod in post:
        logger.info(f"Post Loading {mod}")
        importlib.import_module(mod)

    # Here you go ...
    uvicorn.run(app, host=host, port=int(port))


if __name__ == "__main__":
    fire.Fire(main)
