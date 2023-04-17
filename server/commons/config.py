import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

API_URL = "/api/v1"


def get_logger(name):
    temp_logger = logging.getLogger(name)
    temp_logger.setLevel(logging.DEBUG)
    return temp_logger


logger = get_logger(__name__)


DATABASE = "sqlite:///./chain.db"
if os.environ.get("DATABASE_URL", None) is not None:
    logger.info("Using DATABASE_URL")
    DATABASE = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Database opened successfully")

Base = declarative_base()

JWT_SECRET = os.environ.get("JWT_SECRET", "my_secret")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
