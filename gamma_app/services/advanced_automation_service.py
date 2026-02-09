"""
Advanced Automation Service with Intelligent Workflow Management
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Callable, Coroutine
from dataclasses import dataclass, field
from enum import Enum
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import traceback

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class TaskStatus(Enum):
    """Task status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    RETRYING = "retrying"

class TaskPriority(Enum):
    """Task priority"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class WorkflowStatus(Enum):
    """Workflow status"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TriggerType(Enum):
    """Trigger types"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT = "event"
    WEBHOOK = "webhook"
    API = "api"
    CONDITION = "condition"

@dataclass
class TaskDefinition:
    """Task definition"""
    id: str
    name: str
    description: str
    task_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 3
    retry_delay: float = 1.0
    timeout: Optional[int] = None
    priority: TaskPriority = TaskPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TaskInstance:
    """Task instance"""
    id: str
    task_definition_id: str
    workflow_id: str
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowDefinition:
    """Workflow definition"""
    id: str
    name: str
    description: str
    version: str
    tasks: List[TaskDefinition] = field(default_factory=list)
    triggers: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkflowInstance:
    """Workflow instance"""
    id: str
    workflow_definition_id: str
    status: WorkflowStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    variables: Dict[str, Any] = field(default_factory=dict)
    task_instances: List[TaskInstance] = field(default_factory=list)
    current_task: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AutomationRule:
    """Automation rule"""
    id: str
    name: str
    description: str
    trigger_conditions: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    enabled: bool = True
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)

class AdvancedAutomationService:
    """Advanced Automation Service with Intelligent Workflow Management"""
    
    def __init__(self):
        self.workflow_definitions = {}
        self.workflow_instances = {}
        self.task_definitions = {}
        self.task_instances = {}
        self.automation_rules = {}
        self.task_executors = {}
        self.workflow_queue = asyncio.Queue()
        self.task_queue = asyncio.Queue()
        self.rule_queue = asyncio.Queue()
        self.execution_graphs = {}
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.process_pool = ProcessPoolExecutor(max_workers=4)
        
        # Initialize default task executors
        self._initialize_task_executors()
        
        # Start background tasks
        self._start_background_tasks()
        
        logger.info("Advanced Automation Service initialized")
    
    def _initialize_task_executors(self):
        """Initialize default task executors"""
        try:
            # Built-in task executors
            self.task_executors = {
                'http_request': self._execute_http_request,
                'data_transform': self._execute_data_transform,
                'file_operation': self._execute_file_operation,
                'database_query': self._execute_database_query,
                'email_send': self._execute_email_send,
                'webhook_trigger': self._execute_webhook_trigger,
                'ai_generation': self._execute_ai_generation,
                'content_processing': self._execute_content_processing,
                'notification_send': self._execute_notification_send,
                'data_validation': self._execute_data_validation,
                'custom_script': self._execute_custom_script,
                'parallel_execution': self._execute_parallel_execution,
                'conditional_branch': self._execute_conditional_branch,
                'loop_execution': self._execute_loop_execution,
                'delay_execution': self._execute_delay_execution
            }
            
            logger.info(f"Initialized {len(self.task_executors)} task executors")
            
        except Exception as e:
            logger.error(f"Error initializing task executors: {e}")
    
    def _start_background_tasks(self):
        """Start background processing tasks"""
        try:
            # Start workflow processor
            asyncio.create_task(self._process_workflows())
            
            # Start task processor
            asyncio.create_task(self._process_tasks())
            
            # Start rule processor
            asyncio.create_task(self._process_rules())
            
            logger.info("Background tasks started")
            
        except Exception as e:
            logger.error(f"Error starting background tasks: {e}")
    
    async def _process_workflows(self):
        """Process workflow instances"""
        try:
            while True:
                try:
                    workflow_instance = await asyncio.wait_for(self.workflow_queue.get(), timeout=1.0)
                    await self._execute_workflow(workflow_instance)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing workflow: {e}")
                    
        except Exception as e:
            logger.error(f"Error in workflow processor: {e}")
    
    async def _process_tasks(self):
        """Process task instances"""
        try:
            while True:
                try:
                    task_instance = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                    await self._execute_task(task_instance)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing task: {e}")
                    
        except Exception as e:
            logger.error(f"Error in task processor: {e}")
    
    async def _process_rules(self):
        """Process automation rules"""
        try:
            while True:
                try:
                    rule_event = await asyncio.wait_for(self.rule_queue.get(), timeout=1.0)
                    await self._evaluate_rules(rule_event)
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    logger.error(f"Error processing rules: {e}")
                    
        except Exception as e:
            logger.error(f"Error in rule processor: {e}")
    
    async def create_workflow(self, workflow_def: WorkflowDefinition) -> str:
        """Create a new workflow definition"""
        try:
            workflow_id = str(uuid.uuid4())
            workflow_def.id = workflow_id
            workflow_def.created_at = datetime.utcnow()
            workflow_def.updated_at = datetime.utcnow()
            
            # Validate workflow
            await self._validate_workflow(workflow_def)
            
            # Build execution graph
            await self._build_execution_graph(workflow_def)
            
            # Store workflow definition
            self.workflow_definitions[workflow_id] = workflow_def
            
            # Store task definitions
            for task_def in workflow_def.tasks:
                self.task_definitions[task_def.id] = task_def
            
            logger.info(f"Workflow created: {workflow_id}")
            
            return workflow_id
            
        except Exception as e:
            logger.error(f"Error creating workflow: {e}")
            raise
    
    async def _validate_workflow(self, workflow_def: WorkflowDefinition):
        """Validate workflow definition"""
        try:
            # Check for circular dependencies
            graph = nx.DiGraph()
            
            for task_def in workflow_def.tasks:
                graph.add_node(task_def.id)
                for dep in task_def.dependencies:
                    graph.add_edge(dep, task_def.id)
            
            if not nx.is_directed_acyclic_graph(graph):
                raise ValueError("Workflow contains circular dependencies")
            
            # Validate task definitions
            for task_def in workflow_def.tasks:
                if task_def.task_type not in self.task_executors:
                    raise ValueError(f"Unknown task type: {task_def.task_type}")
            
            logger.info("Workflow validation passed")
            
        except Exception as e:
            logger.error(f"Error validating workflow: {e}")
            raise
    
    async def _build_execution_graph(self, workflow_def: WorkflowDefinition):
        """Build execution graph for workflow"""
        try:
            graph = nx.DiGraph()
            
            for task_def in workflow_def.tasks:
                graph.add_node(task_def.id, task=task_def)
                for dep in task_def.dependencies:
                    graph.add_edge(dep, task_def.id)
            
            self.execution_graphs[workflow_def.id] = graph
            
            logger.info(f"Execution graph built for workflow: {workflow_def.id}")
            
        except Exception as e:
            logger.error(f"Error building execution graph: {e}")
            raise
    
    async def start_workflow(self, workflow_id: str, variables: Dict[str, Any] = None) -> str:
        """Start a workflow instance"""
        try:
            if workflow_id not in self.workflow_definitions:
                raise ValueError(f"Workflow not found: {workflow_id}")
            
            workflow_def = self.workflow_definitions[workflow_id]
            
            if not workflow_def.enabled:
                raise ValueError(f"Workflow disabled: {workflow_id}")
            
            # Create workflow instance
            instance_id = str(uuid.uuid4())
            workflow_instance = WorkflowInstance(
                id=instance_id,
                workflow_definition_id=workflow_id,
                status=WorkflowStatus.ACTIVE,
                created_at=datetime.utcnow(),
                started_at=datetime.utcnow(),
                variables=variables or {}
            )
            
            # Create task instances
            for task_def in workflow_def.tasks:
                task_instance = TaskInstance(
                    id=str(uuid.uuid4()),
                    task_definition_id=task_def.id,
                    workflow_id=instance_id,
                    status=TaskStatus.PENDING,
                    priority=task_def.priority,
                    created_at=datetime.utcnow(),
                    parameters=task_def.parameters.copy()
                )
                
                workflow_instance.task_instances.append(task_instance)
                self.task_instances[task_instance.id] = task_instance
            
            # Store workflow instance
            self.workflow_instances[instance_id] = workflow_instance
            
            # Add to execution queue
            await self.workflow_queue.put(workflow_instance)
            
            logger.info(f"Workflow started: {instance_id}")
            
            return instance_id
            
        except Exception as e:
            logger.error(f"Error starting workflow: {e}")
            raise
    
    async def _execute_workflow(self, workflow_instance: WorkflowInstance):
        """Execute a workflow instance"""
        try:
            workflow_def = self.workflow_definitions[workflow_instance.workflow_definition_id]
            execution_graph = self.execution_graphs[workflow_instance.workflow_definition_id]
            
            # Find ready tasks
            ready_tasks = await self._find_ready_tasks(workflow_instance, execution_graph)
            
            # Execute ready tasks
            for task_instance in ready_tasks:
                await self.task_queue.put(task_instance)
            
            # Check if workflow is complete
            if await self._is_workflow_complete(workflow_instance):
                workflow_instance.status = WorkflowStatus.COMPLETED
                workflow_instance.completed_at = datetime.utcnow()
                workflow_instance.execution_time = (
                    workflow_instance.completed_at - workflow_instance.started_at
                ).total_seconds()
                
                logger.info(f"Workflow completed: {workflow_instance.id}")
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            workflow_instance.status = WorkflowStatus.FAILED
            workflow_instance.error_message = str(e)
    
    async def _find_ready_tasks(self, workflow_instance: WorkflowInstance, execution_graph: nx.DiGraph) -> List[TaskInstance]:
        """Find tasks ready for execution"""
        try:
            ready_tasks = []
            
            for task_instance in workflow_instance.task_instances:
                if task_instance.status != TaskStatus.PENDING:
                    continue
                
                # Check dependencies
                task_def = self.task_definitions[task_instance.task_definition_id]
                dependencies_met = True
                
                for dep_id in task_def.dependencies:
                    dep_instance = next(
                        (ti for ti in workflow_instance.task_instances if ti.task_definition_id == dep_id),
                        None
                    )
                    
                    if not dep_instance or dep_instance.status != TaskStatus.COMPLETED:
                        dependencies_met = False
                        break
                
                if dependencies_met:
                    ready_tasks.append(task_instance)
            
            return ready_tasks
            
        except Exception as e:
            logger.error(f"Error finding ready tasks: {e}")
            return []
    
    async def _is_workflow_complete(self, workflow_instance: WorkflowInstance) -> bool:
        """Check if workflow is complete"""
        try:
            for task_instance in workflow_instance.task_instances:
                if task_instance.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking workflow completion: {e}")
            return False
    
    async def _execute_task(self, task_instance: TaskInstance):
        """Execute a task instance"""
        try:
            task_def = self.task_definitions[task_instance.task_definition_id]
            
            # Update task status
            task_instance.status = TaskStatus.RUNNING
            task_instance.started_at = datetime.utcnow()
            
            # Get task executor
            executor = self.task_executors.get(task_def.task_type)
            if not executor:
                raise ValueError(f"Task executor not found: {task_def.task_type}")
            
            # Execute task
            start_time = time.time()
            
            try:
                result = await executor(task_instance, task_def)
                task_instance.result = result
                task_instance.status = TaskStatus.COMPLETED
                
            except Exception as e:
                task_instance.error_message = str(e)
                task_instance.status = TaskStatus.FAILED
                
                # Retry if possible
                if task_instance.retry_count < task_def.retry_count:
                    task_instance.retry_count += 1
                    task_instance.status = TaskStatus.RETRYING
                    
                    # Schedule retry
                    await asyncio.sleep(task_def.retry_delay * (2 ** task_instance.retry_count))
                    await self.task_queue.put(task_instance)
                    return
            
            # Update execution time
            task_instance.execution_time = time.time() - start_time
            task_instance.completed_at = datetime.utcnow()
            
            # Continue workflow execution
            workflow_instance = self.workflow_instances[task_instance.workflow_id]
            await self.workflow_queue.put(workflow_instance)
            
            logger.info(f"Task completed: {task_instance.id}")
            
        except Exception as e:
            logger.error(f"Error executing task: {e}")
            task_instance.status = TaskStatus.FAILED
            task_instance.error_message = str(e)
    
    # Task Executors
    async def _execute_http_request(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute HTTP request task"""
        try:
            import httpx
            
            url = task_def.parameters.get('url')
            method = task_def.parameters.get('method', 'GET')
            headers = task_def.parameters.get('headers', {})
            data = task_def.parameters.get('data')
            timeout = task_def.parameters.get('timeout', 30)
            
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data
                )
                
                return {
                    'status_code': response.status_code,
                    'headers': dict(response.headers),
                    'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                }
                
        except Exception as e:
            logger.error(f"Error executing HTTP request: {e}")
            raise
    
    async def _execute_data_transform(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute data transformation task"""
        try:
            import pandas as pd
            
            data = task_def.parameters.get('data')
            transform_type = task_def.parameters.get('transform_type')
            
            if transform_type == 'json_to_csv':
                df = pd.json_normalize(data)
                return df.to_csv(index=False)
            
            elif transform_type == 'csv_to_json':
                df = pd.read_csv(data)
                return df.to_dict('records')
            
            elif transform_type == 'filter':
                df = pd.DataFrame(data)
                filter_condition = task_def.parameters.get('filter_condition')
                return df.query(filter_condition).to_dict('records')
            
            else:
                return data
                
        except Exception as e:
            logger.error(f"Error executing data transform: {e}")
            raise
    
    async def _execute_file_operation(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute file operation task"""
        try:
            import aiofiles
            import shutil
            
            operation = task_def.parameters.get('operation')
            source_path = task_def.parameters.get('source_path')
            target_path = task_def.parameters.get('target_path')
            
            if operation == 'copy':
                shutil.copy2(source_path, target_path)
                return {'status': 'copied', 'source': source_path, 'target': target_path}
            
            elif operation == 'move':
                shutil.move(source_path, target_path)
                return {'status': 'moved', 'source': source_path, 'target': target_path}
            
            elif operation == 'delete':
                import os
                os.remove(source_path)
                return {'status': 'deleted', 'path': source_path}
            
            elif operation == 'read':
                async with aiofiles.open(source_path, 'r') as f:
                    content = await f.read()
                return {'content': content, 'path': source_path}
            
            elif operation == 'write':
                content = task_def.parameters.get('content')
                async with aiofiles.open(target_path, 'w') as f:
                    await f.write(content)
                return {'status': 'written', 'path': target_path}
            
            else:
                raise ValueError(f"Unknown file operation: {operation}")
                
        except Exception as e:
            logger.error(f"Error executing file operation: {e}")
            raise
    
    async def _execute_database_query(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute database query task"""
        try:
            # This would integrate with the database service
            query = task_def.parameters.get('query')
            connection_string = task_def.parameters.get('connection_string')
            
            # Placeholder implementation
            return {'query': query, 'result': 'placeholder'}
            
        except Exception as e:
            logger.error(f"Error executing database query: {e}")
            raise
    
    async def _execute_email_send(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute email send task"""
        try:
            # This would integrate with the email service
            to = task_def.parameters.get('to')
            subject = task_def.parameters.get('subject')
            body = task_def.parameters.get('body')
            
            # Placeholder implementation
            return {'status': 'sent', 'to': to, 'subject': subject}
            
        except Exception as e:
            logger.error(f"Error executing email send: {e}")
            raise
    
    async def _execute_webhook_trigger(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute webhook trigger task"""
        try:
            # This would integrate with the webhook service
            url = task_def.parameters.get('url')
            data = task_def.parameters.get('data')
            
            # Placeholder implementation
            return {'status': 'triggered', 'url': url}
            
        except Exception as e:
            logger.error(f"Error executing webhook trigger: {e}")
            raise
    
    async def _execute_ai_generation(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute AI generation task"""
        try:
            # This would integrate with the AI service
            prompt = task_def.parameters.get('prompt')
            model = task_def.parameters.get('model')
            
            # Placeholder implementation
            return {'generated_text': f'Generated content for: {prompt}'}
            
        except Exception as e:
            logger.error(f"Error executing AI generation: {e}")
            raise
    
    async def _execute_content_processing(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute content processing task"""
        try:
            # This would integrate with the content service
            content_id = task_def.parameters.get('content_id')
            operation = task_def.parameters.get('operation')
            
            # Placeholder implementation
            return {'status': 'processed', 'content_id': content_id, 'operation': operation}
            
        except Exception as e:
            logger.error(f"Error executing content processing: {e}")
            raise
    
    async def _execute_notification_send(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute notification send task"""
        try:
            # This would integrate with the notification service
            message = task_def.parameters.get('message')
            channel = task_def.parameters.get('channel')
            
            # Placeholder implementation
            return {'status': 'sent', 'channel': channel}
            
        except Exception as e:
            logger.error(f"Error executing notification send: {e}")
            raise
    
    async def _execute_data_validation(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute data validation task"""
        try:
            data = task_def.parameters.get('data')
            validation_rules = task_def.parameters.get('validation_rules')
            
            # Placeholder implementation
            return {'valid': True, 'data': data}
            
        except Exception as e:
            logger.error(f"Error executing data validation: {e}")
            raise
    
    async def _execute_custom_script(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute custom script task"""
        try:
            script = task_def.parameters.get('script')
            language = task_def.parameters.get('language', 'python')
            
            # Placeholder implementation
            return {'result': 'Custom script executed'}
            
        except Exception as e:
            logger.error(f"Error executing custom script: {e}")
            raise
    
    async def _execute_parallel_execution(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute parallel execution task"""
        try:
            tasks = task_def.parameters.get('tasks', [])
            
            # Execute tasks in parallel
            results = await asyncio.gather(*[
                self._execute_task(task) for task in tasks
            ], return_exceptions=True)
            
            return {'results': results}
            
        except Exception as e:
            logger.error(f"Error executing parallel execution: {e}")
            raise
    
    async def _execute_conditional_branch(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute conditional branch task"""
        try:
            condition = task_def.parameters.get('condition')
            true_branch = task_def.parameters.get('true_branch')
            false_branch = task_def.parameters.get('false_branch')
            
            # Evaluate condition
            if condition:
                return {'branch': 'true', 'next_task': true_branch}
            else:
                return {'branch': 'false', 'next_task': false_branch}
            
        except Exception as e:
            logger.error(f"Error executing conditional branch: {e}")
            raise
    
    async def _execute_loop_execution(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute loop execution task"""
        try:
            loop_condition = task_def.parameters.get('loop_condition')
            loop_body = task_def.parameters.get('loop_body')
            max_iterations = task_def.parameters.get('max_iterations', 100)
            
            results = []
            iteration = 0
            
            while loop_condition and iteration < max_iterations:
                result = await self._execute_task(loop_body)
                results.append(result)
                iteration += 1
            
            return {'results': results, 'iterations': iteration}
            
        except Exception as e:
            logger.error(f"Error executing loop execution: {e}")
            raise
    
    async def _execute_delay_execution(self, task_instance: TaskInstance, task_def: TaskDefinition) -> Any:
        """Execute delay execution task"""
        try:
            delay_seconds = task_def.parameters.get('delay_seconds', 1)
            
            await asyncio.sleep(delay_seconds)
            
            return {'status': 'delayed', 'delay_seconds': delay_seconds}
            
        except Exception as e:
            logger.error(f"Error executing delay execution: {e}")
            raise
    
    async def create_automation_rule(self, rule: AutomationRule) -> str:
        """Create automation rule"""
        try:
            rule_id = str(uuid.uuid4())
            rule.id = rule_id
            rule.created_at = datetime.utcnow()
            
            self.automation_rules[rule_id] = rule
            
            logger.info(f"Automation rule created: {rule_id}")
            
            return rule_id
            
        except Exception as e:
            logger.error(f"Error creating automation rule: {e}")
            raise
    
    async def trigger_rule_evaluation(self, event_data: Dict[str, Any]):
        """Trigger rule evaluation"""
        try:
            await self.rule_queue.put(event_data)
            
        except Exception as e:
            logger.error(f"Error triggering rule evaluation: {e}")
    
    async def _evaluate_rules(self, event_data: Dict[str, Any]):
        """Evaluate automation rules"""
        try:
            for rule in self.automation_rules.values():
                if not rule.enabled:
                    continue
                
                # Check trigger conditions
                if await self._check_trigger_conditions(rule.trigger_conditions, event_data):
                    # Execute actions
                    await self._execute_rule_actions(rule.actions, event_data)
                    
                    logger.info(f"Rule executed: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error evaluating rules: {e}")
    
    async def _check_trigger_conditions(self, conditions: List[Dict[str, Any]], event_data: Dict[str, Any]) -> bool:
        """Check trigger conditions"""
        try:
            for condition in conditions:
                field = condition.get('field')
                operator = condition.get('operator')
                value = condition.get('value')
                
                event_value = event_data.get(field)
                
                if operator == 'equals':
                    if event_value != value:
                        return False
                elif operator == 'not_equals':
                    if event_value == value:
                        return False
                elif operator == 'greater_than':
                    if event_value <= value:
                        return False
                elif operator == 'less_than':
                    if event_value >= value:
                        return False
                elif operator == 'contains':
                    if value not in str(event_value):
                        return False
                elif operator == 'not_contains':
                    if value in str(event_value):
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking trigger conditions: {e}")
            return False
    
    async def _execute_rule_actions(self, actions: List[Dict[str, Any]], event_data: Dict[str, Any]):
        """Execute rule actions"""
        try:
            for action in actions:
                action_type = action.get('type')
                
                if action_type == 'start_workflow':
                    workflow_id = action.get('workflow_id')
                    variables = action.get('variables', {})
                    await self.start_workflow(workflow_id, variables)
                
                elif action_type == 'send_notification':
                    # This would integrate with notification service
                    pass
                
                elif action_type == 'trigger_webhook':
                    # This would integrate with webhook service
                    pass
                
                elif action_type == 'custom_action':
                    # Execute custom action
                    pass
            
        except Exception as e:
            logger.error(f"Error executing rule actions: {e}")
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        try:
            if workflow_id not in self.workflow_instances:
                return None
            
            workflow_instance = self.workflow_instances[workflow_id]
            
            return {
                'id': workflow_instance.id,
                'workflow_definition_id': workflow_instance.workflow_definition_id,
                'status': workflow_instance.status.value,
                'created_at': workflow_instance.created_at.isoformat(),
                'started_at': workflow_instance.started_at.isoformat() if workflow_instance.started_at else None,
                'completed_at': workflow_instance.completed_at.isoformat() if workflow_instance.completed_at else None,
                'execution_time': workflow_instance.execution_time,
                'error_message': workflow_instance.error_message,
                'task_count': len(workflow_instance.task_instances),
                'completed_tasks': len([t for t in workflow_instance.task_instances if t.status == TaskStatus.COMPLETED]),
                'failed_tasks': len([t for t in workflow_instance.task_instances if t.status == TaskStatus.FAILED])
            }
            
        except Exception as e:
            logger.error(f"Error getting workflow status: {e}")
            return None
    
    async def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task status"""
        try:
            if task_id not in self.task_instances:
                return None
            
            task_instance = self.task_instances[task_id]
            
            return {
                'id': task_instance.id,
                'task_definition_id': task_instance.task_definition_id,
                'workflow_id': task_instance.workflow_id,
                'status': task_instance.status.value,
                'priority': task_instance.priority.value,
                'created_at': task_instance.created_at.isoformat(),
                'started_at': task_instance.started_at.isoformat() if task_instance.started_at else None,
                'completed_at': task_instance.completed_at.isoformat() if task_instance.completed_at else None,
                'execution_time': task_instance.execution_time,
                'retry_count': task_instance.retry_count,
                'error_message': task_instance.error_message,
                'result': task_instance.result
            }
            
        except Exception as e:
            logger.error(f"Error getting task status: {e}")
            return None
    
    async def cancel_workflow(self, workflow_id: str) -> bool:
        """Cancel workflow execution"""
        try:
            if workflow_id not in self.workflow_instances:
                return False
            
            workflow_instance = self.workflow_instances[workflow_id]
            
            if workflow_instance.status in [WorkflowStatus.COMPLETED, WorkflowStatus.FAILED, WorkflowStatus.CANCELLED]:
                return False
            
            workflow_instance.status = WorkflowStatus.CANCELLED
            workflow_instance.completed_at = datetime.utcnow()
            
            # Cancel pending tasks
            for task_instance in workflow_instance.task_instances:
                if task_instance.status == TaskStatus.PENDING:
                    task_instance.status = TaskStatus.CANCELLED
            
            logger.info(f"Workflow cancelled: {workflow_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling workflow: {e}")
            return False
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Automation Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'workflows': {
                    'definitions': len(self.workflow_definitions),
                    'instances': len(self.workflow_instances),
                    'active_instances': len([w for w in self.workflow_instances.values() if w.status == WorkflowStatus.ACTIVE])
                },
                'tasks': {
                    'definitions': len(self.task_definitions),
                    'instances': len(self.task_instances),
                    'pending_tasks': len([t for t in self.task_instances.values() if t.status == TaskStatus.PENDING]),
                    'running_tasks': len([t for t in self.task_instances.values() if t.status == TaskStatus.RUNNING])
                },
                'automation': {
                    'rules': len(self.automation_rules),
                    'active_rules': len([r for r in self.automation_rules.values() if r.enabled])
                },
                'queues': {
                    'workflow_queue_size': self.workflow_queue.qsize(),
                    'task_queue_size': self.task_queue.qsize(),
                    'rule_queue_size': self.rule_queue.qsize()
                },
                'executors': {
                    'task_executors': len(self.task_executors),
                    'thread_pool_workers': self.thread_pool._max_workers,
                    'process_pool_workers': self.process_pool._max_workers
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Automation Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























