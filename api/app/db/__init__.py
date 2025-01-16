from .base import Base
from .session import engine, SessionLocal, get_db

# Create tables
Base.metadata.create_all(bind=engine)

__all__ = ["Base", "engine", "SessionLocal", "get_db"]
