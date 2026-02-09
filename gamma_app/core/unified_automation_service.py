"""
Unified Automation Service - Consolidated automation functionality
Combines workflow, scheduling, orchestration, and automation services
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime, timedelta
import croniter
from collections import defaultdict, deque
import networkx as nx
import yaml
import pickle
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task Status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Task Priority"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class WorkflowStatus(Enum):
    """Workflow Status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ScheduleType(Enum):
    """Schedule Type"""
    ONCE = "once"
    INTERVAL = "interval"
    CRON = "cron"
    EVENT = "event"

@dataclass
class Task:
    """Task Definition"""
    id: str
    name: str
    description: str
    function: str
    parameters: Dict[str, Any]
    dependencies: List[str] = field(default_factory=list)
    priority: TaskPriority = TaskPriority.MEDIUM
    timeout: int = 300
    retry_count: int = 3
    retry_delay: int = 60
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Workflow:
    """Workflow Definition"""
    id: str
    name: str
    description: str
    tasks: List[Task]
    status: WorkflowStatus = WorkflowStatus.DRAFT
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Schedule:
    """Schedule Definition"""
    id: str
    name: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    workflow_id: str
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

class UnifiedAutomationService:
    """
    Unified Automation Service - Consolidated automation functionality
    Handles workflows, task scheduling, orchestration, and automation
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.workflows: Dict[str, Workflow] = {}
        self.schedules: Dict[str, Schedule] = {}
        self.task_registry: Dict[str, Callable] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_history: deque = deque(maxlen=10000)
        self.workflow_graphs: Dict[str, nx.DiGraph] = {}
        
        # Execution engine
        self.executor = ThreadPoolExecutor(max_workers=config.get("max_workers", 10))
        self.scheduler_running = False
        
        # Task queues by priority
        self.task_queues = {
            TaskPriority.CRITICAL: deque(),
            TaskPriority.HIGH: deque(),
            TaskPriority.MEDIUM: deque(),
            TaskPriority.LOW: deque()
        }
        
        logger.info("UnifiedAutomationService initialized")
    
    async def register_task_function(self, name: str, function: Callable) -> bool:
        """Register a task function"""
        try:
            self.task_registry[name] = function
            logger.info(f"Task function {name} registered")
            return True
        except Exception as e:
            logger.error(f"Error registering task function {name}: {e}")
            return False
    
    async def create_workflow(self, name: str, description: str, tasks: List[Dict[str, Any]]) -> str:
        """Create a new workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Create tasks
            workflow_tasks = []
            for task_data in tasks:
                task = Task(
                    id=str(uuid.uuid4()),
                    name=task_data["name"],
                    description=task_data.get("description", ""),
                    function=task_data["function"],
                    parameters=task_data.get("parameters", {}),
                    dependencies=task_data.get("dependencies", []),
                    priority=TaskPriority(task_data.get("priority", 2)),
                    timeout=task_data.get("timeout", 300),
                    retry_count=task_data.get("retry_count", 3),
                    retry_delay=task_data.get("retry_delay", 60)
                )
                workflow_tasks.append(task)
            
            # Create workflow
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                tasks=workflow_tasks
            )
            
            # Build dependency graph
            await self._build_workflow_graph(workflow)
            
            self.workflows[workflow_id] = workflow
            logger.info(f"Workflow {name} created with ID {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def _build_workflow_graph(self, workflow: Workflow):
        """Build dependency graph for workflow"""
        try:
            graph = nx.DiGraph()
            
            # Add nodes (tasks)
            for task in workflow.tasks:
                graph.add_node(task.id, task=task)
            
            # Add edges (dependencies)
            for task in workflow.tasks:
                for dep_id in task.dependencies:
                    graph.add_edge(dep_id, task.id)
            
            # Check for cycles
            if not nx.is_directed_acyclic_graph(graph):
                raise ValueError("Workflow contains circular dependencies")
            
            self.workflow_graphs[workflow.id] = graph
            logger.info(f"Workflow graph built for {workflow.id}")
            
        except Exception as e:
            logger.error(f"Error building workflow graph: {e}")
            raise
    
    async def execute_workflow(self, workflow_id: str, parameters: Dict[str, Any] = None) -> str:
        """Execute a workflow"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow {workflow_id} not found")
            
            workflow = self.workflows[workflow_id]
            workflow.status = WorkflowStatus.ACTIVE
            workflow.started_at = datetime.now()
            
            # Create execution context
            execution_id = str(uuid.uuid4())
            context = {
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "parameters": parameters or {},
                "results": {},
                "started_at": datetime.now()
            }
            
            # Execute workflow
            asyncio.create_task(self._execute_workflow_async(workflow, context))
            
            logger.info(f"Workflow {workflow_id} execution started with ID {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {e}")
            raise
    
    async def _execute_workflow_async(self, workflow: Workflow, context: Dict[str, Any]):
        """Execute workflow asynchronously"""
        try:
            graph = self.workflow_graphs[workflow.id]
            completed_tasks = set()
            
            while len(completed_tasks) < len(workflow.tasks):
                # Find ready tasks
                ready_tasks = []
                for task in workflow.tasks:
                    if task.id in completed_tasks:
                        continue
                    
                    # Check if all dependencies are completed
                    dependencies_met = all(
                        dep_id in completed_tasks 
                        for dep_id in task.dependencies
                    )
                    
                    if dependencies_met:
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # Check for deadlock
                    remaining_tasks = [
                        task for task in workflow.tasks 
                        if task.id not in completed_tasks
                    ]
                    if remaining_tasks:
                        logger.error(f"Workflow {workflow.id} deadlocked")
                        workflow.status = WorkflowStatus.FAILED
                        return
                    break
                
                # Execute ready tasks in parallel
                tasks_to_execute = []
                for task in ready_tasks:
                    task.status = TaskStatus.RUNNING
                    task.started_at = datetime.now()
                    
                    # Add to appropriate queue
                    self.task_queues[task.priority].append(task)
                    
                    # Execute task
                    task_coroutine = self._execute_task(task, context)
                    tasks_to_execute.append(task_coroutine)
                
                # Wait for tasks to complete
                if tasks_to_execute:
                    results = await asyncio.gather(*tasks_to_execute, return_exceptions=True)
                    
                    for i, result in enumerate(results):
                        task = ready_tasks[i]
                        if isinstance(result, Exception):
                            task.status = TaskStatus.FAILED
                            task.error = str(result)
                            logger.error(f"Task {task.name} failed: {result}")
                        else:
                            task.status = TaskStatus.COMPLETED
                            task.result = result
                            task.completed_at = datetime.now()
                            context["results"][task.id] = result
                            logger.info(f"Task {task.name} completed")
                        
                        completed_tasks.add(task.id)
                        self.task_history.append(task)
            
            # Mark workflow as completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
            logger.info(f"Workflow {workflow.id} completed")
            
        except Exception as e:
            logger.error(f"Error executing workflow {workflow.id}: {e}")
            workflow.status = WorkflowStatus.FAILED
    
    async def _execute_task(self, task: Task, context: Dict[str, Any]) -> Any:
        """Execute a single task"""
        try:
            if task.function not in self.task_registry:
                raise ValueError(f"Task function {task.function} not registered")
            
            function = self.task_registry[task.function]
            
            # Prepare parameters
            params = task.parameters.copy()
            params.update(context.get("parameters", {}))
            params["context"] = context
            
            # Execute with timeout
            result = await asyncio.wait_for(
                self._run_task_function(function, params),
                timeout=task.timeout
            )
            
            return result
            
        except asyncio.TimeoutError:
            raise Exception(f"Task {task.name} timed out after {task.timeout} seconds")
        except Exception as e:
            # Retry logic
            if task.retry_count > 0:
                task.retry_count -= 1
                task.status = TaskStatus.RETRYING
                await asyncio.sleep(task.retry_delay)
                return await self._execute_task(task, context)
            else:
                raise
    
    async def _run_task_function(self, function: Callable, params: Dict[str, Any]) -> Any:
        """Run task function in thread pool"""
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, function, **params)
            return result
        except Exception as e:
            logger.error(f"Error running task function: {e}")
            raise
    
    async def create_schedule(self, 
                            name: str,
                            schedule_type: ScheduleType,
                            schedule_config: Dict[str, Any],
                            workflow_id: str) -> str:
        """Create a new schedule"""
        try:
            schedule_id = str(uuid.uuid4())
            
            # Calculate next run time
            next_run = await self._calculate_next_run(schedule_type, schedule_config)
            
            schedule = Schedule(
                id=schedule_id,
                name=name,
                schedule_type=schedule_type,
                schedule_config=schedule_config,
                workflow_id=workflow_id,
                next_run=next_run
            )
            
            self.schedules[schedule_id] = schedule
            
            # Start scheduler if not running
            if not self.scheduler_running:
                asyncio.create_task(self._run_scheduler())
            
            logger.info(f"Schedule {name} created with ID {schedule_id}")
            return schedule_id
            
        except Exception as e:
            logger.error(f"Error creating schedule: {e}")
            raise
    
    async def _calculate_next_run(self, schedule_type: ScheduleType, config: Dict[str, Any]) -> datetime:
        """Calculate next run time for schedule"""
        try:
            now = datetime.now()
            
            if schedule_type == ScheduleType.ONCE:
                return config.get("run_at", now)
            
            elif schedule_type == ScheduleType.INTERVAL:
                interval = config.get("interval_seconds", 3600)
                return now + timedelta(seconds=interval)
            
            elif schedule_type == ScheduleType.CRON:
                cron_expr = config.get("cron_expression", "0 * * * *")
                cron = croniter.croniter(cron_expr, now)
                return cron.get_next(datetime)
            
            elif schedule_type == ScheduleType.EVENT:
                # Event-based schedules don't have predictable next runs
                return None
            
            return now
            
        except Exception as e:
            logger.error(f"Error calculating next run: {e}")
            return datetime.now()
    
    async def _run_scheduler(self):
        """Run the scheduler loop"""
        try:
            self.scheduler_running = True
            logger.info("Scheduler started")
            
            while self.scheduler_running:
                now = datetime.now()
                
                # Check for due schedules
                for schedule in self.schedules.values():
                    if not schedule.enabled:
                        continue
                    
                    if schedule.next_run and schedule.next_run <= now:
                        # Execute scheduled workflow
                        asyncio.create_task(self._execute_scheduled_workflow(schedule))
                        
                        # Calculate next run
                        schedule.last_run = now
                        schedule.next_run = await self._calculate_next_run(
                            schedule.schedule_type, 
                            schedule.schedule_config
                        )
                
                # Sleep for 1 minute
                await asyncio.sleep(60)
                
        except Exception as e:
            logger.error(f"Error in scheduler: {e}")
        finally:
            self.scheduler_running = False
            logger.info("Scheduler stopped")
    
    async def _execute_scheduled_workflow(self, schedule: Schedule):
        """Execute a scheduled workflow"""
        try:
            logger.info(f"Executing scheduled workflow {schedule.workflow_id}")
            await self.execute_workflow(schedule.workflow_id)
        except Exception as e:
            logger.error(f"Error executing scheduled workflow: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        try:
            if workflow_id not in self.workflows:
                return {"error": "Workflow not found"}
            
            workflow = self.workflows[workflow_id]
            
            # Get task statuses
            task_statuses = {}
            for task in workflow.tasks:
                task_statuses[task.id] = {
                    "name": task.name,
                    "status": task.status.value,
                    "started_at": task.started_at.isoformat() if task.started_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "error": task.error
                }
            
            return {
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "created_at": workflow.created_at.isoformat(),
                "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
                "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
                "tasks": task_statuses,
                "total_tasks": len(workflow.tasks),
                "completed_tasks": len([t for t in workflow.tasks if t.status == TaskStatus.COMPLETED]),
                "failed_tasks": len([t for t in workflow.tasks if t.status == TaskStatus.FAILED])
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return {"error": str(e)}
    
    async def get_schedule_status(self, schedule_id: str) -> Dict[str, Any]:
        """Get schedule status"""
        try:
            if schedule_id not in self.schedules:
                return {"error": "Schedule not found"}
            
            schedule = self.schedules[schedule_id]
            
            return {
                "schedule_id": schedule_id,
                "name": schedule.name,
                "schedule_type": schedule.schedule_type.value,
                "enabled": schedule.enabled,
                "last_run": schedule.last_run.isoformat() if schedule.last_run else None,
                "next_run": schedule.next_run.isoformat() if schedule.next_run else None,
                "workflow_id": schedule.workflow_id
            }
            
        except Exception as e:
            logger.error(f"Error getting schedule status: {e}")
            return {"error": str(e)}
    
    async def pause_workflow(self, workflow_id: str) -> bool:
        """Pause a workflow"""
        try:
            if workflow_id in self.workflows:
                self.workflows[workflow_id].status = WorkflowStatus.PAUSED
                return True
            return False
        except Exception as e:
            logger.error(f"Error pausing workflow: {e}")
            return False
    
    async def resume_workflow(self, workflow_id: str) -> bool:
        """Resume a paused workflow"""
        try:
            if workflow_id in self.workflows:
                self.workflows[workflow_id].status = WorkflowStatus.ACTIVE
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming workflow: {e}")
            return False
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel a workflow"""
        try:
            if workflow_id in self.workflows:
                workflow = self.workflows[workflow_id]
                workflow.status = WorkflowStatus.FAILED
                
                # Cancel running tasks
                for task in workflow.tasks:
                    if task.status == TaskStatus.RUNNING:
                        task.status = TaskStatus.CANCELLED
                
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling workflow: {e}")
            return False
    
    async def export_workflow(self, workflow_id: str, format: str = "json") -> str:
        """Export workflow definition"""
        try:
            if workflow_id not in self.workflows:
                raise ValueError("Workflow not found")
            
            workflow = self.workflows[workflow_id]
            
            if format == "json":
                return json.dumps({
                    "id": workflow.id,
                    "name": workflow.name,
                    "description": workflow.description,
                    "tasks": [
                        {
                            "name": task.name,
                            "description": task.description,
                            "function": task.function,
                            "parameters": task.parameters,
                            "dependencies": task.dependencies,
                            "priority": task.priority.value,
                            "timeout": task.timeout,
                            "retry_count": task.retry_count,
                            "retry_delay": task.retry_delay
                        }
                        for task in workflow.tasks
                    ]
                }, indent=2)
            
            elif format == "yaml":
                return yaml.dump({
                    "name": workflow.name,
                    "description": workflow.description,
                    "tasks": [
                        {
                            "name": task.name,
                            "description": task.description,
                            "function": task.function,
                            "parameters": task.parameters,
                            "dependencies": task.dependencies,
                            "priority": task.priority.value,
                            "timeout": task.timeout,
                            "retry_count": task.retry_count,
                            "retry_delay": task.retry_delay
                        }
                        for task in workflow.tasks
                    ]
                }, default_flow_style=False)
            
            else:
                raise ValueError(f"Unsupported export format: {format}")
                
        except Exception as e:
            logger.error(f"Error exporting workflow: {e}")
            return ""
    
    async def get_automation_statistics(self) -> Dict[str, Any]:
        """Get automation statistics"""
        try:
            total_workflows = len(self.workflows)
            active_workflows = len([w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE])
            total_schedules = len(self.schedules)
            active_schedules = len([s for s in self.schedules.values() if s.enabled])
            
            # Task statistics
            total_tasks = sum(len(w.tasks) for w in self.workflows.values())
            completed_tasks = len([t for t in self.task_history if t.status == TaskStatus.COMPLETED])
            failed_tasks = len([t for t in self.task_history if t.status == TaskStatus.FAILED])
            
            return {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "total_schedules": total_schedules,
                "active_schedules": active_schedules,
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "failed_tasks": failed_tasks,
                "success_rate": (completed_tasks / (completed_tasks + failed_tasks) * 100) if (completed_tasks + failed_tasks) > 0 else 0,
                "registered_functions": len(self.task_registry),
                "scheduler_running": self.scheduler_running
            }
            
        except Exception as e:
            logger.error(f"Error getting automation statistics: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for automation service"""
        try:
            stats = await self.get_automation_statistics()
            
            return {
                "status": "healthy",
                "total_workflows": stats.get("total_workflows", 0),
                "active_workflows": stats.get("active_workflows", 0),
                "total_schedules": stats.get("total_schedules", 0),
                "scheduler_running": stats.get("scheduler_running", False),
                "registered_functions": stats.get("registered_functions", 0),
                "executor_active": not self.executor._shutdown
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    async def shutdown(self):
        """Shutdown the automation service"""
        try:
            self.scheduler_running = False
            self.executor.shutdown(wait=True)
            logger.info("Automation service shutdown complete")
        except Exception as e:
            logger.error(f"Error shutting down automation service: {e}")


























