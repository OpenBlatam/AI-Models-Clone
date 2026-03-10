"""
OpenClaw -- Agent Task Scheduler.

Allows agents to be triggered on a schedule (cron-like) or after a delay.
Uses ``asyncio`` tasks for lightweight in-process scheduling.

For production, integrate with Celery, APScheduler, or a cloud scheduler.
"""

import asyncio
import logging
import time
import json
from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ScheduledTask:
    """Represents a single scheduled agent task."""

    task_id: str
    user_id: str
    prompt: str
    interval_seconds: float
    repeat: bool = True
    max_runs: int = 0  # 0 = unlimited
    last_run_time: Optional[float] = field(default=None, repr=True)
    _run_count: int = field(default=0, repr=False)
    _cancelled: bool = field(default=False, repr=False)

    def cancel(self) -> None:
        self._cancelled = True


class AgentScheduler:
    """
    In-process task scheduler for OpenClaw agents.

    Usage::

        from agents.client import AgentClient
        from agents.scheduler import AgentScheduler

        client = AgentClient()
        scheduler = AgentScheduler(client)

        # Run a prompt every 60 seconds
        scheduler.add_recurring("daily_report", "user1",
                                "Generate a summary of today's metrics",
                                interval_seconds=60)

        # Run a prompt once after 10 seconds
        scheduler.add_delayed("welcome", "user2",
                              "Send a welcome message",
                              delay_seconds=10)

        await scheduler.start()
    """

    def __init__(self, agent_client: Any, persistence_path: str = "scheduler_registry.json") -> None:
        self.agent_client = agent_client
        self.persistence_path = Path(persistence_path)
        self.tasks: Dict[str, ScheduledTask] = {}
        self._on_result: Optional[Callable] = None
        
        # Load persisted tasks
        self._load_tasks()
        
        # In-process backup
        self._running_tasks: Dict[str, asyncio.Task] = {}
        
        try:
            from apscheduler.schedulers.asyncio import AsyncIOScheduler
            self.scheduler_engine = AsyncIOScheduler()
            self.has_apscheduler = True
        except ImportError:
            self.scheduler_engine = None
            self.has_apscheduler = False
            logger.warning("APScheduler no encontrado. Usando fallback de asyncio. 'pip install apscheduler'")

    def on_result(self, callback: Callable) -> None:
        """Register a callback ``(task_id, result) -> None`` for task results."""
        self._on_result = callback

    # ------------------------------------------------------------------
    # Task registration
    # ------------------------------------------------------------------

    def add_recurring(
        self,
        task_id: str,
        user_id: str,
        prompt: str,
        interval_seconds: float = 60,
        max_runs: int = 0,
    ) -> ScheduledTask:
        """Add a recurring task that fires every ``interval_seconds``."""
        task = ScheduledTask(
            task_id=task_id,
            user_id=user_id,
            prompt=prompt,
            interval_seconds=interval_seconds,
            repeat=True,
            max_runs=max_runs,
        )
        self.tasks[task_id] = task
        self._save_tasks()
        logger.info("Recurring task registered: %s (every %ss)", task_id, interval_seconds)
        
        if self.scheduler_engine and self.scheduler_engine.state == 1: # running
            self._schedule_job(task)
            
        return task

    def add_delayed(
        self,
        task_id: str,
        user_id: str,
        prompt: str,
        delay_seconds: float = 10,
    ) -> ScheduledTask:
        """Add a one-shot task that fires after ``delay_seconds``."""
        task = ScheduledTask(
            task_id=task_id,
            user_id=user_id,
            prompt=prompt,
            interval_seconds=delay_seconds,
            repeat=False,
            max_runs=1,
        )
        self.tasks[task_id] = task
        self._save_tasks()
        logger.info("Delayed task registered: %s (in %ss)", task_id, delay_seconds)
        
        if self.scheduler_engine and self.scheduler_engine.state == 1:
            self._schedule_job(task)
            
        return task

    def cancel(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        task = self.tasks.get(task_id)
        if task:
            task.cancel()
            if self.has_apscheduler and self.scheduler_engine:
                try:
                    self.scheduler_engine.remove_job(task_id)
                except Exception:
                    pass
            else:
                asyncio_task = self._running_tasks.get(task_id)
                if asyncio_task:
                    asyncio_task.cancel()
            
            self._save_tasks()
            logger.info("Task cancelled: %s", task_id)
            return True
        return False

    def list_tasks(self) -> List[Dict[str, Any]]:
        """Return a summary of all registered tasks."""
        return [
            {
                "task_id": t.task_id,
                "user_id": t.user_id,
                "prompt": t.prompt[:50],
                "interval": t.interval_seconds,
                "repeat": t.repeat,
                "runs": t._run_count,
                "cancelled": t._cancelled,
            }
            for t in self.tasks.values()
        ]

    # ------------------------------------------------------------------
    # Execution
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start all registered tasks using APScheduler or asyncio fallback."""
        if self.has_apscheduler and self.scheduler_engine:
            if self.scheduler_engine.state == 0:
                self.scheduler_engine.start()
            for task in self.tasks.values():
                if not task._cancelled:
                    self._schedule_job(task)
            logger.info("APScheduler started with %d tasks", len(self.tasks))
        else:
            # Fallback
            for task_id, task in self.tasks.items():
                if task_id not in self._running_tasks and not task._cancelled:
                    # Calculate initial delay for resumed tasks
                    initial_delay = task.interval_seconds
                    if task.last_run_time:
                        elapsed = time.time() - task.last_run_time
                        initial_delay = max(0.1, task.interval_seconds - elapsed)
                    
                    self._running_tasks[task_id] = asyncio.create_task(
                        self._run_loop(task, initial_delay=initial_delay)
                    )
            logger.info("Asyncio Fallback Scheduler started.")

    async def stop(self) -> None:
        """Cancel all running tasks and stop the scheduler."""
        for task in self.tasks.values():
            task.cancel()
            
        if self.has_apscheduler and self.scheduler_engine:
            self.scheduler_engine.shutdown(wait=False)
        else:
            for asyncio_task in self._running_tasks.values():
                asyncio_task.cancel()
            self._running_tasks.clear()
        
        logger.info("Scheduler stopped.")

    def _schedule_job(self, task: ScheduledTask) -> None:
        # APScheduler Integration Logic
        from datetime import datetime, timedelta
        
        # Calculate next run date based on last_run_time if available
        next_run = None
        if task.last_run_time:
            next_run = datetime.fromtimestamp(task.last_run_time) + timedelta(seconds=task.interval_seconds)
            if next_run < datetime.now():
                next_run = datetime.now() + timedelta(seconds=0.1) # Run almost immediately if overdue

        if task.repeat:
            self.scheduler_engine.add_job(
                self._execute_task,
                'interval',
                seconds=task.interval_seconds,
                id=task.task_id,
                args=[task],
                next_run_time=next_run,
                replace_existing=True
            )
        else:
            run_date = next_run or (datetime.now() + timedelta(seconds=task.interval_seconds))
            self.scheduler_engine.add_job(
                self._execute_task,
                'date',
                run_date=run_date,
                id=task.task_id,
                args=[task],
                replace_existing=True
            )

    async def _execute_task(self, task: ScheduledTask) -> None:
        """Wrapper to execute and record task runs."""
        if task._cancelled:
            return
            
        task._run_count += 1
        task.last_run_time = time.time()
        self._save_tasks()
        
        logger.info("Executing scheduled task '%s' (run #%d)", task.task_id, task._run_count)

        try:
            result = await self.agent_client.run(user_id=task.user_id, prompt=task.prompt)
            if self._on_result:
                self._on_result(task.task_id, result)
        except Exception as e:
            logger.exception("Task '%s' failed: %s", task.task_id, str(e))

        if task.max_runs > 0 and task._run_count >= task.max_runs:
            logger.info("Task '%s' reached max runs (%d)", task.task_id, task.max_runs)
            self.cancel(task.task_id)

    async def _run_loop(self, task: ScheduledTask, initial_delay: Optional[float] = None) -> None:
        """Fallback internal loop that executes a scheduled task via asyncio."""
        try:
            delay = initial_delay if initial_delay is not None else task.interval_seconds
            await asyncio.sleep(delay)

            while not task._cancelled:
                await self._execute_task(task)

                if not task.repeat or task._cancelled:
                    break

                await asyncio.sleep(task.interval_seconds)

        except asyncio.CancelledError:
            logger.info("Task '%s' was cancelled.", task.task_id)
            raise

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_tasks(self) -> None:
        """Serialize current tasks to a JSON file."""
        try:
            data = {}
            for tid, t in self.tasks.items():
                if not t._cancelled:
                    data[tid] = asdict(t)
            
            with open(self.persistence_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error("Failed to save scheduler registry: %s", e)

    def _load_tasks(self) -> None:
        """Load tasks from the registry file."""
        if not self.persistence_path.exists():
            return
            
        try:
            with open(self.persistence_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for tid, t_data in data.items():
                    task = ScheduledTask(**t_data)
                    self.tasks[tid] = task
            logger.info("Restored %d tasks from persistence.", len(self.tasks))
        except Exception as e:
            logger.error("Failed to load scheduler registry: %s", e)
