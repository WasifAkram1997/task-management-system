"""
Database connection and session management for task_db
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import get_settings

settings = get_settings()

#Crete engine
engine = create_engine(
    settings.get_database_url(),
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.DEBUG
)

#Session factory
SessionLocal = sessionmaker(
    autoflush=False,
    autocommit= False,
    bind=engine
)


#Base class for models
Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in database"""
    Base.metadata.create_all(bind=engine)