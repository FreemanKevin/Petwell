from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from datetime import datetime
from app.core.config import settings
import pytz

# Create SQLAlchemy engine
engine = create_engine(settings.DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@event.listens_for(Session, 'before_flush')
def before_flush(session, flush_context, instances):
    """Convert datetime to UTC before saving to database"""
    for obj in session.new | session.dirty:
        for key, value in obj.__dict__.items():
            if isinstance(value, datetime):
                setattr(obj, key, value.astimezone(pytz.UTC))

def get_db() -> Generator[Session, None, None]:
    """
    Get database session.
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
