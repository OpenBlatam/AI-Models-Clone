"""
Application factory

This module provides functions to create and configure the FastAPI application.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI

from config.settings import settings
from utils.cache import cache_service
from utils.scalability.background_tasks import background_task_queue
from utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    logger.info("Starting Logistics AI Platform...")
    await cache_service.connect()
    await background_task_queue.start()
    logger.info("Application started successfully")
    
    yield
    
    logger.info("Shutting down Logistics AI Platform...")
    await background_task_queue.stop()
    await cache_service.disconnect()
    logger.info("Application shut down successfully")


def create_app() -> FastAPI:
    """Create and return FastAPI application instance"""
    return FastAPI(
        title="Logistics AI Platform API",
        description="Comprehensive freight forwarding and logistics management system - A Nowports clone",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

