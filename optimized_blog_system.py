from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from tensorboardX import SummaryWriter
import wandb
from database.base import Base, engine
from config import TENSORBOARD_LOG_DIR, WANDB_PROJECT, WANDB_RUN_NAME, WANDB_MODE


@asynccontextmanager
async def lifespan(app):
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
async def error_logging_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as exc:
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred. Please try again later."}
        ) 