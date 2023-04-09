import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE = "sqlite:///./chain.db"
engine = create_engine(DATABASE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("Database opened successfully")
Base = declarative_base()
Base.metadata.create_all(bind=engine)

JWT_SECRET = os.environ.get("JWT_SECRET", "my_secret")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", None)
