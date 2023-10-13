import os
import logging

# WARNING: do not import anything from anywhere here, this is the place where chainfury_server starts.
#          importing anything can cause the --pre and --post flags to fail when starting server.

from chainfury.utils import logger  # keep this here, rest of package imports from this file


class Env:
    """
    Single namespace for all environment variables.

    * CFS_DATABASE: database connection string
    * JWT_SECRET: secret for JWT tokens
    """

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda x: os.getenv("CFS_DATABASE", x)
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")
    CFS_MAX_NODE_ID_LEN = lambda: int(os.getenv("CFS_MAX_NODE_ID_LEN", 80))
    CF_MAX_WORKER_ID_LEN = lambda: int(os.getenv("CF_MAX_WORKER_ID_LEN", 16))


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)
