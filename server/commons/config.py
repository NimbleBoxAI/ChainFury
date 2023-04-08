import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE = "sqlite:///./chain.db"
engine = create_engine(
    DATABASE, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Database opened successfully")
Base = declarative_base()
os.environ["JWT_SECRET"] = "my_secret"
jwt_secret = os.environ.get("JWT_SECRET", "my_secret")
