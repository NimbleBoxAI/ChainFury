import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")


def get_logger(name):
    temp_logger = logging.getLogger(name)
    temp_logger.setLevel(logging.DEBUG)
    return temp_logger


logger = get_logger(__name__)

DATABASE = "sqlite:///./chain.db"
engine = create_engine(DATABASE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
logger.info("Database opened successfully")

Base = declarative_base()
Base.metadata.create_all(bind=engine)

JWT_SECRET = os.environ.get("JWT_SECRET", "my_secret")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
