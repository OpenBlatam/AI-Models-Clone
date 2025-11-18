"""
Enhanced database configuration with connection pooling and optimization
"""
from typing import AsyncGenerator, Optional, Dict, Any
from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text, event
from sqlalchemy.pool import QueuePool
import asyncio
import logging
from contextlib import asynccontextmanager
import time

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Global database engine and session factory
_engine: Optional[AsyncEngine] = None
_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


def create_database_engine() -> AsyncEngine:
    """Create optimized database engine with connection pooling."""
    global _engine
    
    if _engine is not None:
        return _engine
    
    # Database URL with connection pooling parameters
    database_url = settings.DATABASE_URL
    
    # Engine configuration for optimal performance
    engine_kwargs = {
        "echo": settings.DEBUG,
        "echo_pool": settings.DEBUG,
        "poolclass": QueuePool,
        "pool_size": settings.DB_POOL_SIZE,
        "max_overflow": settings.DB_MAX_OVERFLOW,
        "pool_pre_ping": True,
        "pool_recycle": settings.DB_POOL_RECYCLE,
        "connect_args": {
            "command_timeout": 30,
            "server_settings": {
                "application_name": settings.PROJECT_NAME,
                "jit": "off",  # Disable JIT for better performance in some cases
            }
        }
    }
    
    _engine = create_async_engine(database_url, **engine_kwargs)
    
    # Add event listeners for monitoring
    setup_engine_event_listeners(_engine)
    
    logger.info(f"Database engine created with pool_size={settings.DB_POOL_SIZE}")
    return _engine


def setup_engine_event_listeners(engine: AsyncEngine) -> None:
    """Setup event listeners for database monitoring."""
    
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set database pragmas for optimal performance."""
        if "sqlite" in str(engine.url):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            cursor.close()
    
    @event.listens_for(engine.sync_engine, "checkout")
    def receive_checkout(dbapi_connection, connection_record, connection_proxy):
        """Log connection checkout."""
        logger.debug("Database connection checked out")
    
    @event.listens_for(engine.sync_engine, "checkin")
    def receive_checkin(dbapi_connection, connection_record):
        """Log connection checkin."""
        logger.debug("Database connection checked in")


def create_session_factory() -> async_sessionmaker[AsyncSession]:
    """Create database session factory."""
    global _session_factory
    
    if _session_factory is not None:
        return _session_factory
    
    engine = create_database_engine()
    
    _session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False
    )
    
    logger.info("Database session factory created")
    return _session_factory


async def init_db() -> None:
    """Initialize database with tables and indexes."""
    try:
        engine = create_database_engine()
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Create indexes for better performance
        await create_performance_indexes(engine)
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def create_performance_indexes(engine: AsyncEngine) -> None:
    """Create performance indexes for better query performance."""
    try:
        async with engine.begin() as conn:
            # Create indexes for common queries
            indexes = [
                # User indexes
                "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
                "CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active)",
                
                # Document indexes
                "CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents(updated_at)",
                "CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status)",
                
                # Organization indexes
                "CREATE INDEX IF NOT EXISTS idx_organizations_created_at ON organizations(created_at)",
                "CREATE INDEX IF NOT EXISTS idx_organizations_is_active ON organizations(is_active)",
                
                # Collaboration indexes
                "CREATE INDEX IF NOT EXISTS idx_collaborations_document_id ON collaborations(document_id)",
                "CREATE INDEX IF NOT EXISTS idx_collaborations_user_id ON collaborations(user_id)",
                "CREATE INDEX IF NOT EXISTS idx_collaborations_created_at ON collaborations(created_at)",
            ]
            
            for index_sql in indexes:
                try:
                    await conn.execute(text(index_sql))
                except Exception as e:
                    logger.warning(f"Failed to create index: {e}")
        
        logger.info("Performance indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create performance indexes: {e}")
        # Don't raise here as indexes are optional


async def close_db() -> None:
    """Close database connections."""
    global _engine, _session_factory
    
    if _engine:
        await _engine.dispose()
        _engine = None
        logger.info("Database engine disposed")
    
    _session_factory = None


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session with proper error handling."""
    session_factory = create_session_factory()
    session = session_factory()
    
    try:
        yield session
        await session.commit()
    except Exception as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    finally:
        await session.close()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting database session."""
    async with get_db_session() as session:
        yield session


async def execute_raw_query(query: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """Execute raw SQL query."""
    session_factory = create_session_factory()
    async with session_factory() as session:
        try:
            result = await session.execute(text(query), params or {})
            await session.commit()
            return result
        except Exception as e:
            await session.rollback()
            logger.error(f"Raw query execution failed: {e}")
            raise


async def get_database_metrics() -> Dict[str, Any]:
    """Get database performance metrics."""
    try:
        engine = create_database_engine()
        
        # Get connection pool metrics
        pool = engine.pool
        pool_metrics = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid()
        }
        
        # Get database-specific metrics
        async with engine.begin() as conn:
            # PostgreSQL specific metrics
            if "postgresql" in str(engine.url):
                result = await conn.execute(text("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active_connections,
                        count(*) FILTER (WHERE state = 'idle') as idle_connections
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """))
                db_metrics = result.fetchone()
                
                return {
                    "pool_metrics": pool_metrics,
                    "database_metrics": {
                        "total_connections": db_metrics[0] if db_metrics else 0,
                        "active_connections": db_metrics[1] if db_metrics else 0,
                        "idle_connections": db_metrics[2] if db_metrics else 0
                    }
                }
        
        return {"pool_metrics": pool_metrics}
        
    except Exception as e:
        logger.error(f"Failed to get database metrics: {e}")
        return {"error": str(e)}


async def optimize_database() -> Dict[str, Any]:
    """Optimize database performance."""
    try:
        engine = create_database_engine()
        optimization_results = {}
        
        async with engine.begin() as conn:
            # PostgreSQL specific optimizations
            if "postgresql" in str(engine.url):
                # Update table statistics
                await conn.execute(text("ANALYZE"))
                optimization_results["analyze"] = "completed"
                
                # Vacuum if needed (be careful in production)
                if settings.ENVIRONMENT != "production":
                    await conn.execute(text("VACUUM"))
                    optimization_results["vacuum"] = "completed"
        
        logger.info("Database optimization completed")
        return optimization_results
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        return {"error": str(e)}


async def check_database_health() -> Dict[str, Any]:
    """Check database health and connectivity."""
    try:
        engine = create_database_engine()
        
        # Test basic connectivity
        start_time = time.time()
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        response_time = time.time() - start_time
        
        # Get connection pool status
        pool = engine.pool
        pool_healthy = pool.checkedin() > 0 or pool.size() > 0
        
        return {
            "status": "healthy",
            "response_time_ms": response_time * 1000,
            "pool_healthy": pool_healthy,
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Database transaction decorator
def with_transaction(func):
    """Decorator for database transactions."""
    async def wrapper(*args, **kwargs):
        session_factory = create_session_factory()
        async with session_factory() as session:
            try:
                # Inject session into function arguments
                if 'db' in kwargs:
                    kwargs['db'] = session
                else:
                    # Find the first AsyncSession argument
                    for i, arg in enumerate(args):
                        if isinstance(arg, AsyncSession):
                            args = list(args)
                            args[i] = session
                            break
                    else:
                        kwargs['db'] = session
                
                result = await func(*args, **kwargs)
                await session.commit()
                return result
                
            except Exception as e:
                await session.rollback()
                logger.error(f"Transaction failed in {func.__name__}: {e}")
                raise
            finally:
                await session.close()
    
    return wrapper


# Batch operations helper
async def batch_insert(model_class, data_list: list, batch_size: int = 1000) -> int:
    """Insert data in batches for better performance."""
    session_factory = create_session_factory()
    async with session_factory() as session:
        try:
            total_inserted = 0
            
            for i in range(0, len(data_list), batch_size):
                batch = data_list[i:i + batch_size]
                session.add_all([model_class(**item) for item in batch])
                await session.flush()
                total_inserted += len(batch)
            
            await session.commit()
            logger.info(f"Batch inserted {total_inserted} records")
            return total_inserted
            
        except Exception as e:
            await session.rollback()
            logger.error(f"Batch insert failed: {e}")
            raise
        finally:
            await session.close()


# Connection health monitoring
async def monitor_connections() -> Dict[str, Any]:
    """Monitor database connections."""
    try:
        engine = create_database_engine()
        pool = engine.pool
        
        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Connection monitoring failed: {e}")
        return {"error": str(e)}