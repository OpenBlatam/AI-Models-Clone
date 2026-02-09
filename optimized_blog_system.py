from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from fastapi.responses import JSONResponse
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
from tensorboardX import SummaryWriter
import wandb
from database.base import Base, engine
from config import TENSORBOARD_LOG_DIR, WANDB_PROJECT, WANDB_RUN_NAME, WANDB_MODE


from typing import Any, List, Dict, Optional
import logging
import asyncio
@asynccontextmanager
async def lifespan(app) -> Any:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app.state.tb_writer = SummaryWriter(log_dir=TENSORBOARD_LOG_DIR)
    wandb.init(project=WANDB_PROJECT, name=WANDB_RUN_NAME, mode=WANDB_MODE)
    try:
        yield
    finally:
        app.state.tb_writer.close()

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
async def error_logging_middleware(request: Request, call_next) -> Any:
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    
    """error_logging_middleware function."""
try:
        response = await call_next(request)
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error in {__name__}: {e}")
        raise
    try:
        pass
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content: Dict[str, Any] = {"detail": "An unexpected error occurred. Please try again later."}
        ) 