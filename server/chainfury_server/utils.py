# Copyright © 2023- Frello Technology Private Limited

import os
import logging

# WARNING: do not import anything from anywhere here, this is the place where chainfury_server starts.
#          importing anything can cause the --pre and --post flags to fail when starting server.

from chainfury.utils import (
    logger,
)  # keep this here, rest of package imports from this file


class Env:
    """
    Single namespace for all environment variables.

    * CFS_DATABASE: database connection string
    * JWT_SECRET: secret for JWT tokens
    """

    # once a lifetime secret
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda: os.getenv("CFS_DATABASE", None)
    CFS_MAXLEN_CF_NDOE = lambda: int(os.getenv("CFS_MAXLEN_CF_NDOE", 80))
    CFS_MAXLEN_WORKER = lambda: int(os.getenv("CFS_MAXLEN_WORKER", 16))
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


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)
