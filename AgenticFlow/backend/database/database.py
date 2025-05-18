"""
Database configuration and session management.

This module provides database connection and session management for the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os

from config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def get_db() -> Session:
    """
    Get a database session.
    
    Yields:
        Session: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_context():
    """
    Context manager for database sessions.
    
    Yields:
        Session: A database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables."""
    from database import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables."""
    from database import models  # noqa: F401
    Base.metadata.drop_all(bind=engine)

def recreate_db():
    """Recreate the database by dropping and recreating all tables."""
    drop_db()
    init_db()
