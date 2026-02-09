"""
Workflow Engine - Motor de Workflows
Sistema de automatización de workflows y procesos de negocio
"""

import asyncio
import logging
import json
import uuid
from typing import List, Dict, Any, Optional, Callable, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import threading
import queue
import time

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """Estados de workflow"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskStatus(Enum):
    """Estados de tarea"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """Tipos de tarea"""
    SEARCH = "search"
    PROCESS_DOCUMENT = "process_document"
    SEND_NOTIFICATION = "send_notification"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"
    ANALYZE_DATA = "analyze_data"
    GENERATE_REPORT = "generate_report"
    CUSTOM = "custom"

class TriggerType(Enum):
    """Tipos de trigger"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    API_CALL = "api_call"
    FILE_UPLOAD = "file_upload"
    DATA_CHANGE = "data_change"

@dataclass
class WorkflowTrigger:
    """Trigger de workflow"""
    id: str
    type: TriggerType
    name: str
    description: str
    config: Dict[str, Any]
    enabled: bool = True
    created_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now(timezone.utc).isoformat()

@dataclass
class WorkflowTask:
    """Tarea de workflow"""
    id: str
    name: str
    description: str
    type: TaskType
    config: Dict[str, Any]
    inputs: List[str]
    outputs: List[str]
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    dependencies: List[str] = None
    condition: Optional[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []

@dataclass
class WorkflowExecution:
    """Ejecución de workflow"""
    id: str
    workflow_id: str
    status: WorkflowStatus
    started_at: str
    completed_at: Optional[str] = None
    triggered_by: str = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    task_executions: List[str] = None
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}
        if self.task_executions is None:
            self.task_executions = []

@dataclass
class TaskExecution:
    """Ejecución de tarea"""
    id: str
    task_id: str
    workflow_execution_id: str
    status: TaskStatus
    started_at: str
    completed_at: Optional[str] = None
    input_data: Dict[str, Any] = None
    output_data: Dict[str, Any] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    def __post_init__(self):
        if self.input_data is None:
            self.input_data = {}
        if self.output_data is None:
            self.output_data = {}

@dataclass
class Workflow:
    """Workflow"""
    id: str
    name: str
    description: str
    version: str
    status: WorkflowStatus
    triggers: List[WorkflowTrigger]
    tasks: List[WorkflowTask]
    task_graph: Dict[str, List[str]]  # Adjacency list
    variables: Dict[str, Any]
    created_at: str
    updated_at: str
    created_by: str
    
    def __post_init__(self):
        if self.variables is None:
            self.variables = {}

class WorkflowEngine:
    """
    Motor de workflows y automatización
    """
    
    def __init__(self):
        self.workflows: Dict[str, Workflow] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.task_executions: Dict[str, TaskExecution] = {}
        
        # Executor para tareas en paralelo
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Cola de workflows pendientes
        self.workflow_queue = queue.Queue()
        self.is_running = False
        self.worker_thread = None
        
        # Handlers de tareas
        self.task_handlers: Dict[TaskType, Callable] = {}
        
        # Configuraciones
        self.config = {
            "max_concurrent_executions": 5,
            "task_timeout": 300,
            "retry_delay": 5,
            "max_retries": 3
        }
        
        # Inicializar handlers por defecto
        self._initialize_default_handlers()
    
    async def initialize(self):
        """Inicializar motor de workflows"""
        try:
            logger.info("Inicializando motor de workflows...")
            
            # Iniciar worker thread
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._workflow_worker, daemon=True)
            self.worker_thread.start()
            
            # Crear workflows por defecto
            await self._create_default_workflows()
            
            logger.info("Motor de workflows inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando motor de workflows: {e}")
            raise
    
    def _initialize_default_handlers(self):
        """Inicializar handlers de tareas por defecto"""
        try:
            self.task_handlers[TaskType.SEARCH] = self._handle_search_task
            self.task_handlers[TaskType.PROCESS_DOCUMENT] = self._handle_process_document_task
            self.task_handlers[TaskType.SEND_NOTIFICATION] = self._handle_send_notification_task
            self.task_handlers[TaskType.EXPORT_DATA] = self._handle_export_data_task
            self.task_handlers[TaskType.IMPORT_DATA] = self._handle_import_data_task
            self.task_handlers[TaskType.ANALYZE_DATA] = self._handle_analyze_data_task
            self.task_handlers[TaskType.GENERATE_REPORT] = self._handle_generate_report_task
            
            logger.info("Handlers de tareas por defecto inicializados")
            
        except Exception as e:
            logger.error(f"Error inicializando handlers por defecto: {e}")
    
    async def _create_default_workflows(self):
        """Crear workflows por defecto"""
        try:
            # Workflow de procesamiento de documentos
            await self.create_workflow(
                name="Document Processing Workflow",
                description="Workflow automático para procesar documentos subidos",
                triggers=[
                    WorkflowTrigger(
                        id="file_upload_trigger",
                        type=TriggerType.FILE_UPLOAD,
                        name="File Upload Trigger",
                        description="Se activa cuando se sube un archivo",
                        config={"file_types": ["pdf", "docx", "txt", "md"]}
                    )
                ],
                tasks=[
                    WorkflowTask(
                        id="process_doc_task",
                        name="Process Document",
                        description="Procesar el documento subido",
                        type=TaskType.PROCESS_DOCUMENT,
                        config={"extract_text": True, "generate_embeddings": True},
                        inputs=["file_path"],
                        outputs=["document_id", "content", "metadata"]
                    ),
                    WorkflowTask(
                        id="notify_task",
                        name="Send Notification",
                        description="Notificar al usuario que el documento fue procesado",
                        type=TaskType.SEND_NOTIFICATION,
                        config={"notification_type": "document_processed"},
                        inputs=["document_id", "user_id"],
                        outputs=[],
                        dependencies=["process_doc_task"]
                    )
                ],
                task_graph={
                    "process_doc_task": ["notify_task"],
                    "notify_task": []
                },
                created_by="system"
            )
            
            # Workflow de análisis de datos
            await self.create_workflow(
                name="Data Analysis Workflow",
                description="Workflow para análisis automático de datos",
                triggers=[
                    WorkflowTrigger(
                        id="scheduled_analysis",
                        type=TriggerType.SCHEDULED,
                        name="Scheduled Analysis",
                        description="Se ejecuta diariamente a las 2 AM",
                        config={"cron": "0 2 * * *"}
                    )
                ],
                tasks=[
                    WorkflowTask(
                        id="analyze_data_task",
                        name="Analyze Data",
                        description="Analizar datos del sistema",
                        type=TaskType.ANALYZE_DATA,
                        config={"analysis_type": "comprehensive"},
                        inputs=[],
                        outputs=["analysis_results"]
                    ),
                    WorkflowTask(
                        id="generate_report_task",
                        name="Generate Report",
                        description="Generar reporte de análisis",
                        type=TaskType.GENERATE_REPORT,
                        config={"report_format": "pdf"},
                        inputs=["analysis_results"],
                        outputs=["report_path"],
                        dependencies=["analyze_data_task"]
                    ),
                    WorkflowTask(
                        id="notify_admin_task",
                        name="Notify Admin",
                        description="Notificar a administradores",
                        type=TaskType.SEND_NOTIFICATION,
                        config={"notification_type": "analysis_complete"},
                        inputs=["report_path"],
                        outputs=[],
                        dependencies=["generate_report_task"]
                    )
                ],
                task_graph={
                    "analyze_data_task": ["generate_report_task"],
                    "generate_report_task": ["notify_admin_task"],
                    "notify_admin_task": []
                },
                created_by="system"
            )
            
            logger.info("Workflows por defecto creados")
            
        except Exception as e:
            logger.error(f"Error creando workflows por defecto: {e}")
    
    async def create_workflow(self, name: str, description: str, 
                            triggers: List[WorkflowTrigger], tasks: List[WorkflowTask],
                            task_graph: Dict[str, List[str]], 
                            variables: Dict[str, Any] = None,
                            created_by: str = "system") -> Workflow:
        """Crear nuevo workflow"""
        try:
            workflow_id = str(uuid.uuid4())
            
            # Validar grafo de tareas
            if not self._validate_task_graph(tasks, task_graph):
                raise ValueError("Grafo de tareas inválido")
            
            # Crear workflow
            workflow = Workflow(
                id=workflow_id,
                name=name,
                description=description,
                version="1.0.0",
                status=WorkflowStatus.DRAFT,
                triggers=triggers,
                tasks=tasks,
                task_graph=task_graph,
                variables=variables or {},
                created_at=datetime.now(timezone.utc).isoformat(),
                updated_at=datetime.now(timezone.utc).isoformat(),
                created_by=created_by
            )
            
            # Almacenar workflow
            self.workflows[workflow_id] = workflow
            
            logger.info(f"Workflow creado: {name} ({workflow_id})")
            return workflow
            
        except Exception as e:
            logger.error(f"Error creando workflow: {e}")
            raise
    
    def _validate_task_graph(self, tasks: List[WorkflowTask], 
                           task_graph: Dict[str, List[str]]) -> bool:
        """Validar grafo de tareas"""
        try:
            # Verificar que todas las tareas están en el grafo
            task_ids = {task.id for task in tasks}
            graph_task_ids = set(task_graph.keys())
            
            for dependencies in task_graph.values():
                graph_task_ids.update(dependencies)
            
            if task_ids != graph_task_ids:
                return False
            
            # Verificar que no hay ciclos
            G = nx.DiGraph()
            for task_id, dependencies in task_graph.items():
                for dep in dependencies:
                    G.add_edge(dep, task_id)
            
            if not nx.is_directed_acyclic_graph(G):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validando grafo de tareas: {e}")
            return False
    
    async def execute_workflow(self, workflow_id: str, triggered_by: str = "manual",
                             input_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Ejecutar workflow"""
        try:
            # Verificar que el workflow existe
            if workflow_id not in self.workflows:
                raise ValueError(f"Workflow no encontrado: {workflow_id}")
            
            workflow = self.workflows[workflow_id]
            
            # Verificar que el workflow está activo
            if workflow.status != WorkflowStatus.ACTIVE:
                raise ValueError(f"Workflow no está activo: {workflow.status}")
            
            # Crear ejecución
            execution_id = str(uuid.uuid4())
            execution = WorkflowExecution(
                id=execution_id,
                workflow_id=workflow_id,
                status=WorkflowStatus.RUNNING,
                started_at=datetime.now(timezone.utc).isoformat(),
                triggered_by=triggered_by,
                input_data=input_data or {}
            )
            
            # Almacenar ejecución
            self.executions[execution_id] = execution
            
            # Agregar a la cola de ejecución
            self.workflow_queue.put(execution_id)
            
            logger.info(f"Workflow ejecutado: {workflow.name} ({execution_id})")
            return execution
            
        except Exception as e:
            logger.error(f"Error ejecutando workflow: {e}")
            raise
    
    def _workflow_worker(self):
        """Worker thread para procesar workflows"""
        while self.is_running:
            try:
                # Obtener workflow de la cola
                execution_id = self.workflow_queue.get(timeout=1)
                
                # Ejecutar workflow en un hilo separado
                asyncio.run_coroutine_threadsafe(
                    self._execute_workflow_async(execution_id),
                    asyncio.get_event_loop()
                )
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error en workflow worker: {e}")
    
    async def _execute_workflow_async(self, execution_id: str):
        """Ejecutar workflow de forma asíncrona"""
        try:
            execution = self.executions[execution_id]
            workflow = self.workflows[execution.workflow_id]
            
            # Crear ejecuciones de tareas
            task_executions = {}
            for task in workflow.tasks:
                task_execution = TaskExecution(
                    id=str(uuid.uuid4()),
                    task_id=task.id,
                    workflow_execution_id=execution_id,
                    status=TaskStatus.PENDING,
                    started_at=datetime.now(timezone.utc).isoformat(),
                    input_data={}
                )
                task_executions[task.id] = task_execution
                self.task_executions[task_execution.id] = task_execution
                execution.task_executions.append(task_execution.id)
            
            # Ejecutar tareas en orden topológico
            task_order = self._get_task_execution_order(workflow)
            
            for task_id in task_order:
                task = next(t for t in workflow.tasks if t.id == task_id)
                task_execution = task_executions[task_id]
                
                # Verificar dependencias
                if not self._check_task_dependencies(task, task_executions):
                    task_execution.status = TaskStatus.SKIPPED
                    continue
                
                # Ejecutar tarea
                await self._execute_task(task, task_execution, execution)
                
                # Si la tarea falló, marcar workflow como fallido
                if task_execution.status == TaskStatus.FAILED:
                    execution.status = WorkflowStatus.FAILED
                    execution.error_message = f"Tarea falló: {task.name}"
                    break
            
            # Marcar workflow como completado si no falló
            if execution.status == WorkflowStatus.RUNNING:
                execution.status = WorkflowStatus.COMPLETED
                execution.completed_at = datetime.now(timezone.utc).isoformat()
            
            logger.info(f"Workflow completado: {execution_id} - {execution.status}")
            
        except Exception as e:
            logger.error(f"Error ejecutando workflow {execution_id}: {e}")
            execution = self.executions[execution_id]
            execution.status = WorkflowStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc).isoformat()
    
    def _get_task_execution_order(self, workflow: Workflow) -> List[str]:
        """Obtener orden de ejecución de tareas"""
        try:
            G = nx.DiGraph()
            for task_id, dependencies in workflow.task_graph.items():
                for dep in dependencies:
                    G.add_edge(dep, task_id)
            
            return list(nx.topological_sort(G))
            
        except Exception as e:
            logger.error(f"Error obteniendo orden de tareas: {e}")
            return [task.id for task in workflow.tasks]
    
    def _check_task_dependencies(self, task: WorkflowTask, 
                               task_executions: Dict[str, TaskExecution]) -> bool:
        """Verificar dependencias de tarea"""
        try:
            for dep_id in task.dependencies:
                if dep_id not in task_executions:
                    return False
                
                dep_execution = task_executions[dep_id]
                if dep_execution.status != TaskStatus.COMPLETED:
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando dependencias: {e}")
            return False
    
    async def _execute_task(self, task: WorkflowTask, task_execution: TaskExecution,
                          workflow_execution: WorkflowExecution):
        """Ejecutar tarea individual"""
        try:
            task_execution.status = TaskStatus.RUNNING
            
            # Obtener handler de tarea
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"No hay handler para tipo de tarea: {task.type}")
            
            # Ejecutar tarea con timeout
            try:
                result = await asyncio.wait_for(
                    handler(task, task_execution, workflow_execution),
                    timeout=task.timeout_seconds
                )
                
                task_execution.output_data = result
                task_execution.status = TaskStatus.COMPLETED
                task_execution.completed_at = datetime.now(timezone.utc).isoformat()
                
            except asyncio.TimeoutError:
                task_execution.status = TaskStatus.FAILED
                task_execution.error_message = f"Tarea expiró después de {task.timeout_seconds} segundos"
                task_execution.completed_at = datetime.now(timezone.utc).isoformat()
            
        except Exception as e:
            logger.error(f"Error ejecutando tarea {task.name}: {e}")
            task_execution.status = TaskStatus.FAILED
            task_execution.error_message = str(e)
            task_execution.completed_at = datetime.now(timezone.utc).isoformat()
    
    # Handlers de tareas por defecto
    async def _handle_search_task(self, task: WorkflowTask, 
                                task_execution: TaskExecution,
                                workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de búsqueda"""
        try:
            query = task.config.get("query", "")
            limit = task.config.get("limit", 10)
            
            # Aquí integrarías con el motor de búsqueda
            # Por ahora, simular resultado
            result = {
                "query": query,
                "results": [
                    {"id": f"doc_{i}", "title": f"Document {i}", "score": 0.9 - i * 0.1}
                    for i in range(min(limit, 5))
                ],
                "total_results": limit
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de búsqueda: {e}")
            raise
    
    async def _handle_process_document_task(self, task: WorkflowTask,
                                          task_execution: TaskExecution,
                                          workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de procesamiento de documentos"""
        try:
            file_path = task_execution.input_data.get("file_path", "")
            
            # Aquí integrarías con el procesador de documentos
            # Por ahora, simular resultado
            result = {
                "document_id": str(uuid.uuid4()),
                "content": f"Contenido procesado de {file_path}",
                "metadata": {
                    "file_path": file_path,
                    "processed_at": datetime.now(timezone.utc).isoformat(),
                    "word_count": 1000
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de procesamiento: {e}")
            raise
    
    async def _handle_send_notification_task(self, task: WorkflowTask,
                                           task_execution: TaskExecution,
                                           workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de envío de notificaciones"""
        try:
            notification_type = task.config.get("notification_type", "general")
            user_id = task_execution.input_data.get("user_id", "system")
            
            # Aquí integrarías con el sistema de notificaciones
            # Por ahora, simular resultado
            result = {
                "notification_sent": True,
                "notification_type": notification_type,
                "user_id": user_id,
                "sent_at": datetime.now(timezone.utc).isoformat()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de notificaciones: {e}")
            raise
    
    async def _handle_export_data_task(self, task: WorkflowTask,
                                     task_execution: TaskExecution,
                                     workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de exportación de datos"""
        try:
            export_format = task.config.get("format", "json")
            
            # Aquí integrarías con el sistema de exportación
            # Por ahora, simular resultado
            result = {
                "export_path": f"/exports/export_{uuid.uuid4()}.{export_format}",
                "format": export_format,
                "exported_at": datetime.now(timezone.utc).isoformat(),
                "record_count": 1000
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de exportación: {e}")
            raise
    
    async def _handle_import_data_task(self, task: WorkflowTask,
                                     task_execution: TaskExecution,
                                     workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de importación de datos"""
        try:
            import_path = task_execution.input_data.get("import_path", "")
            
            # Aquí integrarías con el sistema de importación
            # Por ahora, simular resultado
            result = {
                "import_path": import_path,
                "imported_at": datetime.now(timezone.utc).isoformat(),
                "record_count": 500,
                "success_count": 450,
                "error_count": 50
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de importación: {e}")
            raise
    
    async def _handle_analyze_data_task(self, task: WorkflowTask,
                                      task_execution: TaskExecution,
                                      workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de análisis de datos"""
        try:
            analysis_type = task.config.get("analysis_type", "basic")
            
            # Aquí integrarías con el sistema de analytics
            # Por ahora, simular resultado
            result = {
                "analysis_type": analysis_type,
                "analyzed_at": datetime.now(timezone.utc).isoformat(),
                "insights": [
                    "Insight 1: Los usuarios buscan más por la mañana",
                    "Insight 2: Los documentos PDF son los más populares",
                    "Insight 3: La tasa de click-through ha aumentado 15%"
                ],
                "metrics": {
                    "total_searches": 10000,
                    "unique_users": 2500,
                    "avg_response_time": 0.5
                }
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de análisis: {e}")
            raise
    
    async def _handle_generate_report_task(self, task: WorkflowTask,
                                         task_execution: TaskExecution,
                                         workflow_execution: WorkflowExecution) -> Dict[str, Any]:
        """Handler para tarea de generación de reportes"""
        try:
            report_format = task.config.get("report_format", "pdf")
            analysis_results = task_execution.input_data.get("analysis_results", {})
            
            # Aquí integrarías con el generador de reportes
            # Por ahora, simular resultado
            result = {
                "report_path": f"/reports/report_{uuid.uuid4()}.{report_format}",
                "format": report_format,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "page_count": 10,
                "data_points": len(analysis_results.get("insights", []))
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error en handler de reportes: {e}")
            raise
    
    async def get_workflow_status(self, workflow_id: str) -> Optional[Workflow]:
        """Obtener estado de workflow"""
        return self.workflows.get(workflow_id)
    
    async def get_execution_status(self, execution_id: str) -> Optional[WorkflowExecution]:
        """Obtener estado de ejecución"""
        return self.executions.get(execution_id)
    
    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Obtener métricas del motor de workflows"""
        try:
            total_workflows = len(self.workflows)
            active_workflows = len([w for w in self.workflows.values() if w.status == WorkflowStatus.ACTIVE])
            total_executions = len(self.executions)
            
            # Contar ejecuciones por estado
            execution_status_counts = {}
            for execution in self.executions.values():
                status = execution.status.value
                execution_status_counts[status] = execution_status_counts.get(status, 0) + 1
            
            # Contar tareas por estado
            task_status_counts = {}
            for task_execution in self.task_executions.values():
                status = task_execution.status.value
                task_status_counts[status] = task_status_counts.get(status, 0) + 1
            
            return {
                "total_workflows": total_workflows,
                "active_workflows": active_workflows,
                "total_executions": total_executions,
                "execution_status_counts": execution_status_counts,
                "task_status_counts": task_status_counts,
                "queue_size": self.workflow_queue.qsize(),
                "is_running": self.is_running,
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de workflows: {e}")
            return {}
    
    async def shutdown(self):
        """Cerrar motor de workflows"""
        try:
            self.is_running = False
            
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            
            self.executor.shutdown(wait=True)
            
            logger.info("Motor de workflows cerrado")
            
        except Exception as e:
            logger.error(f"Error cerrando motor de workflows: {e}")


























