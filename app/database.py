"""
Database configuration for Enhanced Blog System v27.0.0 REFACTORED
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool

from app.config import config

# Create database engine with optimization
engine = create_engine(
    config.database.url,
    poolclass=QueuePool,
    pool_size=config.database.pool_size,
    max_overflow=config.database.max_overflow,
    pool_timeout=config.database.pool_timeout,
    pool_recycle=config.database.pool_recycle,
    pool_pre_ping=True,
    echo=config.debug
)

# Create session factory with optimization
SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False
)

# Create scoped session for thread safety
db_session = scoped_session(SessionLocal)

# Create declarative base
Base = declarative_base()
Base.query = db_session.query_property()


def get_db():
    """Get database session with optimization"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database with optimization"""
    # Import all models to ensure they are registered
    from app.models import User, BlogPost
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully!")


def close_db():
    """Close database connections with optimization"""
    db_session.remove()
    engine.dispose()
    print("Database connections closed successfully!") 