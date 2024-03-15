# Copyright © 2023- Frello Technology Private Limited

import os
from snowflake import SnowflakeGenerator

# WARNING: do not import anything from anywhere here, this is the place where chainfury_server starts.
#          importing anything can cause the --pre and --post flags to fail when starting server.

from chainfury.utils import (
    logger,
)  # keep this here, rest of package imports from this file


class Env:
    """
    Single namespace for all environment variables.
    """

    # once a lifetime secret
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")
    CFS_SECRETS_PASSWORD = lambda: os.getenv("CFS_SECRETS_PASSWORDs")

    # not once a lifetime but require DB changes, might as well not change these
    CFS_MAXLEN_CF_NODE = lambda: int(os.getenv("CFS_MAXLEN_CF_NODE", 80))
    CFS_MAXLEN_WORKER = lambda: int(os.getenv("CFS_MAXLEN_WORKER", 16))

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda: os.getenv("CFS_DATABASE", None)
    CFS_ALLOW_CORS_ORIGINS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_CORS_ORIGINS", "*").split(",")
    ]
    CFS_ALLOW_METHODS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_METHODS", "*").split(",")
    ]
    CFS_ALLOW_HEADERS = lambda: [
        x.strip() for x in os.getenv("CFS_ALLOW_HEADERS", "*").split(",")
    ]
    CFS_DISABLE_UI = lambda: os.getenv("CFS_DISABLE_UI", "0") == "1"
    CFS_DISABLE_DOCS = lambda: os.getenv("CFS_DISABLE_DOCS", "0") == "1"
    CFS_ENABLE_CELERY = lambda: os.getenv("CFS_ENABLE_CELERY", "0") == "1"


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)


class SFGen:
    CURRENT_EPOCH_START = 1705905900000  # UTC timezone
    """Start of the current epoch, used for generating snowflake ids"""

    def __init__(self, instance, epoch=CURRENT_EPOCH_START):
        self.gen = SnowflakeGenerator(instance, epoch=epoch)

    def __call__(self):
        return next(self.gen)
