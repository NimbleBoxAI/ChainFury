import os
import logging
from typing import List
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

API_URL = "/api/v1"


def get_logger(name):
    temp_logger = logging.getLogger(name)
    temp_logger.setLevel(logging.DEBUG)
    return temp_logger


logger = get_logger(__name__)


class Env:
    """
    Single namespace for all environment variables.

    * CFS_DATABASE: database connection string
    * JWT_SECRET: secret for JWT tokens
    """

    # when you want to use chainfury as a client you need to set the following vars
    CFS_DATABASE = lambda x: os.getenv("CFS_DATABASE", x)
    JWT_SECRET = lambda: os.getenv("JWT_SECRET", "hajime-shimamoto")


db = Env.CFS_DATABASE("")
if not db:
    # create a sqlite in the chainfury directory
    cf_folder = os.path.expanduser("~/cf")
    os.makedirs(cf_folder, exist_ok=True)
    db = "sqlite:///" + cf_folder + "/cfs.db"
    logger.warning(f"No database passed will connect to local SQLite: {db}")
    engine = create_engine(
        db,
        connect_args={
            "check_same_thread": False,
        },
    )
else:
    logger.info(f"Using database: {db}")
    engine = create_engine(
        db,
        poolclass=QueuePool,
        pool_size=10,
        pool_recycle=30,
        pool_pre_ping=True,
    )


def get_local_session() -> sessionmaker:
    logger.debug("Database opened successfully")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


Base = declarative_base()


# Things that are user definable: user will configure this file below manually or pass via the CLI
class PluginsConfig:
    plugins_list: List[str] = []  # "echo" is a good starting point
