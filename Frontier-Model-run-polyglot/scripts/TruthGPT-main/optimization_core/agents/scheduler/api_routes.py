"""
OpenClaw Scheduler -- FastAPI endpoints.

Exposes endpoints for managing scheduled agent tasks at runtime.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class TaskCreateRequest(BaseModel):
    task_id: str = Field(..., description="Unique task identifier.")
    user_id: str = Field("default", description="User context for the agent.")
    prompt: str = Field(..., description="Prompt the agent will execute.")
    interval_seconds: float = Field(60, description="Interval between runs (seconds).")
    repeat: bool = Field(True, description="Whether the task repeats.")
    max_runs: int = Field(0, description="Max number of executions (0 = unlimited).")


class TaskStatus(BaseModel):
    task_id: str
    user_id: str
    prompt: str
    interval: float
    repeat: bool
    runs: int
    cancelled: bool


def create_scheduler_router(scheduler: "AgentScheduler") -> APIRouter:  # noqa: F821
    """Build an APIRouter for managing scheduled tasks."""

    router = APIRouter(
        prefix="/v1/scheduler",
        tags=["Scheduler"],
    )

    @router.post("/tasks")
    async def create_task(req: TaskCreateRequest):
        """Register a new scheduled task."""
        if req.repeat:
            scheduler.add_recurring(
                task_id=req.task_id,
                user_id=req.user_id,
                prompt=req.prompt,
                interval_seconds=req.interval_seconds,
                max_runs=req.max_runs,
            )
        else:
            scheduler.add_delayed(
                task_id=req.task_id,
                user_id=req.user_id,
                prompt=req.prompt,
                delay_seconds=req.interval_seconds,
            )
        return {"ok": True, "task_id": req.task_id}

    @router.get("/tasks")
    async def list_tasks():
        """List all registered tasks."""
        return scheduler.list_tasks()

    @router.delete("/tasks/{task_id}")
    async def cancel_task(task_id: str):
        """Cancel a scheduled task."""
        success = scheduler.cancel(task_id)
        return {"ok": success, "task_id": task_id}

    @router.post("/start")
    async def start_scheduler():
        """Start all registered tasks."""
        await scheduler.start()
        return {"ok": True, "message": "Scheduler started."}

    @router.post("/stop")
    async def stop_scheduler():
        """Stop all running tasks."""
        await scheduler.stop()
        return {"ok": True, "message": "Scheduler stopped."}

    return router
