import os
import logging

# from chainfury_server.database import db_session, User, Template


def get_logger(name) -> logging.Logger:
    temp_logger = logging.getLogger(name)
    temp_logger.setLevel(logging.INFO)
    return temp_logger


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = get_logger("cf_server")  # type: ignore


class Env:
    """
    Single namespace for all environment variables.

    * CFS_DATABASE: database connection string
    * JWT_SECRET: secret for JWT tokens
    """

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda x: os.getenv("CFS_DATABASE", x)
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")


def folder(x: str) -> str:
    """get the folder of this file path"""
    return os.path.split(os.path.abspath(x))[0]


def joinp(x: str, *args) -> str:
    """convienience function for os.path.join"""
    return os.path.join(x, *args)
