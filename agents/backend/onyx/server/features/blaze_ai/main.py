"""
Main application entry point for the Blaze AI module.

This module demonstrates how to use the refactored Blaze AI module
with FastAPI and provides a complete example application.
"""

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yaml
from pathlib import Path

from . import create_modular_ai, get_logger
from .api.router import router as blaze_ai_router
from .core.interfaces import CoreConfig


def load_config(config_path: str = "config.yaml") -> CoreConfig:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return CoreConfig(**config_data)
    except FileNotFoundError:
        logger = get_logger("main")
        logger.warning(f"Config file {config_path} not found, using defaults")
        return CoreConfig()
    except Exception as e:
        logger = get_logger("main")
        logger.error(f"Error loading config: {e}")
        return CoreConfig()


def create_app(config: CoreConfig) -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Blaze AI API",
        description="Advanced AI Module for Content Generation and Analysis",
        version="2.0.0",
        docs_url="/docs" if config.api.enable_docs else None,
        redoc_url="/redoc" if config.api.enable_docs else None
    )
    
    # Add CORS middleware
    if config.api.enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.security.allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    # Include Blaze AI router
    app.include_router(blaze_ai_router, prefix=config.api.api_prefix)
    
    # Add startup and shutdown events
    @app.on_event("startup")
    async def startup_event():
        logger = get_logger("main")
        logger.info("Starting Blaze AI application...")
        
        # Initialize the AI module
        try:
            ai = create_modular_ai(config=config)
            app.state.ai = ai
            logger.info("Blaze AI module initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Blaze AI module: {e}")
            raise
    
    @app.on_event("shutdown")
    async def shutdown_event():
        logger = get_logger("main")
        logger.info("Shutting down Blaze AI application...")
        
        # Shutdown the AI module
        if hasattr(app.state, 'ai'):
            try:
                await app.state.ai.shutdown()
                logger.info("Blaze AI module shutdown successfully")
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
    
    return app


async def main():
    """Main application entry point."""
    # Load configuration
    config = load_config()
    
    # Setup logging
    from .utils.logging import setup_logging
    setup_logging(
        level=config.log_level.value,
        log_file=config.log_file
    )
    
    logger = get_logger("main")
    logger.info("Initializing Blaze AI application...")
    
    # Create FastAPI app
    app = create_app(config)
    
    # Start server
    logger.info(f"Starting server on {config.api.host}:{config.api.port}")
    config_dict = uvicorn.Config(
        app=app,
        host=config.api.host,
        port=config.api.port,
        workers=config.api.workers,
        log_level=config.log_level.value.lower()
    )
    
    server = uvicorn.Server(config_dict)
    await server.serve()


if __name__ == "__main__":
    asyncio.run(main())
