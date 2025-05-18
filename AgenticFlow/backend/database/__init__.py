"""
Database package for AgenticFlow.

This package contains database models and initialization code.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
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

# Create scoped session factory for thread-local sessions
ScopedSession = scoped_session(SessionLocal)

def get_db():
    """
    Dependency function that yields a database session.
    
    Yields:
        Session: A database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize the database by creating all tables."""
    from .models_new import Base
    Base.metadata.create_all(bind=engine)

def drop_db():
    """Drop all database tables."""
    from .models_new import Base
    Base.metadata.drop_all(bind=engine)

def recreate_db():
    """Recreate the database by dropping and recreating all tables."""
    drop_db()
    init_db()

# Import models to ensure they are registered with SQLAlchemy
from .models_new import (
    User,
    Token,
    Email,
    Attachment,
    EmailAnalysis,
    SocialPost
)
