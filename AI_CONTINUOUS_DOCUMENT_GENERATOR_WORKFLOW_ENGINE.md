# Motor de Flujo de Trabajo: IA Generadora Continua de Documentos

## Resumen

Este documento define un motor de flujo de trabajo avanzado que orquesta la generación continua de documentos, gestiona dependencias entre documentos, y automatiza procesos de revisión y aprobación.

## 1. Arquitectura del Motor de Flujo de Trabajo

### 1.1 Componentes Principales

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        DOCUMENT WORKFLOW CHAIN ENGINE                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   WORKFLOW      │  │   DEPENDENCY    │  │   EXECUTION     │                │
│  │   DEFINER       │  │   MANAGER       │  │   ENGINE        │                │
│  │                 │  │                 │  │                 │                │
│  │ • Templates     │  │ • Dependencies  │  │ • Parallel      │                │
│  │ • Rules         │  │ • Ordering      │  │   Execution     │                │
│  │ • Conditions    │  │ • Validation    │  │ • Error         │                │
│  │ • Triggers      │  │ • Resolution    │  │   Handling      │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐                │
│  │   STATE         │  │   NOTIFICATION  │  │   PERSISTENCE   │                │
│  │   MANAGER       │  │   SYSTEM        │  │   LAYER         │                │
│  │                 │  │                 │  │                 │                │
│  │ • State         │  │ • Email         │  │ • Workflow      │                │
│  │   Tracking      │  │ • Slack         │  │   Storage       │                │
│  │ • Transitions   │  │ • Webhooks      │  │ • State         │                │
│  │ • History       │  │ • Dashboard     │  │   Persistence   │                │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 2. Modelos de Datos del Flujo de Trabajo

### 2.1 Definición de Flujo de Trabajo

```python
# app/models/workflow.py
from enum import Enum
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime
import uuid

class WorkflowStatus(Enum):
    """Estados del flujo de trabajo"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskStatus(Enum):
    """Estados de las tareas"""
    PENDING = "pending"
    READY = "ready"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"

class TaskType(Enum):
    """Tipos de tareas"""
    DOCUMENT_GENERATION = "document_generation"
    QUALITY_CHECK = "quality_check"
    REDUNDANCY_ANALYSIS = "redundancy_analysis"
    COHERENCE_VALIDATION = "coherence_validation"
    USER_REVIEW = "user_review"
    APPROVAL = "approval"
    NOTIFICATION = "notification"
    CUSTOM = "custom"

class TriggerType(Enum):
    """Tipos de triggers"""
    MANUAL = "manual"
    SCHEDULED = "scheduled"
    EVENT_BASED = "event_based"
    CONDITIONAL = "conditional"
    WEBHOOK = "webhook"

@dataclass
class WorkflowTask:
    """Tarea individual en el flujo de trabajo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    task_type: TaskType = TaskType.DOCUMENT_GENERATION
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 1
    dependencies: List[str] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    retry_count: int = 0
    max_retries: int = 3
    timeout_seconds: int = 300
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowCondition:
    """Condición para ejecución de tareas"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    condition_type: str = "expression"  # expression, threshold, custom
    expression: str = ""  # Python expression
    parameters: Dict[str, Any] = field(default_factory=dict)
    negate: bool = False

@dataclass
class WorkflowTrigger:
    """Trigger para iniciar flujo de trabajo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    trigger_type: TriggerType = TriggerType.MANUAL
    conditions: List[WorkflowCondition] = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

@dataclass
class WorkflowDefinition:
    """Definición completa de un flujo de trabajo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    version: str = "1.0.0"
    tasks: List[WorkflowTask] = field(default_factory=list)
    triggers: List[WorkflowTrigger] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

@dataclass
class WorkflowInstance:
    """Instancia de ejecución de un flujo de trabajo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_definition_id: str = ""
    name: str = ""
    status: WorkflowStatus = WorkflowStatus.PENDING
    variables: Dict[str, Any] = field(default_factory=dict)
    task_instances: List[WorkflowTask] = field(default_factory=list)
    current_task_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    created_by: Optional[str] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class WorkflowExecutionLog:
    """Log de ejecución del flujo de trabajo"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workflow_instance_id: str = ""
    task_id: Optional[str] = None
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
```

## 3. Motor de Flujo de Trabajo

### 3.1 Clase Principal del Motor

```python
# app/services/workflow_engine.py
import asyncio
import logging
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime, timedelta
import json
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..models.workflow import *
from ..models.generation import ContinuousGenerationRequest
from ..models.document import GeneratedDocument, DocumentType
from ..services.generator import ContinuousDocumentGenerator
from ..services.redundancy_detector import ContentRedundancyDetector
from ..services.quality import QualityValidator
from ..core.database import get_database
from ..core.notifications import NotificationService

logger = logging.getLogger(__name__)

class DocumentWorkflowChainEngine:
    """
    Motor de flujo de trabajo para generación continua de documentos
    """
    
    def __init__(self):
        self.db = get_database()
        self.notification_service = NotificationService()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.active_instances: Dict[str, WorkflowInstance] = {}
        self.task_handlers: Dict[TaskType, Callable] = {
            TaskType.DOCUMENT_GENERATION: self._handle_document_generation,
            TaskType.QUALITY_CHECK: self._handle_quality_check,
            TaskType.REDUNDANCY_ANALYSIS: self._handle_redundancy_analysis,
            TaskType.COHERENCE_VALIDATION: self._handle_coherence_validation,
            TaskType.USER_REVIEW: self._handle_user_review,
            TaskType.APPROVAL: self._handle_approval,
            TaskType.NOTIFICATION: self._handle_notification,
            TaskType.CUSTOM: self._handle_custom_task
        }
        
    async def create_workflow_definition(
        self, 
        definition: WorkflowDefinition
    ) -> str:
        """
        Crea una nueva definición de flujo de trabajo
        """
        try:
            # Validar definición
            await self._validate_workflow_definition(definition)
            
            # Guardar en base de datos
            definition_id = await self._save_workflow_definition(definition)
            
            logger.info(f"Workflow definition created: {definition_id}")
            return definition_id
            
        except Exception as e:
            logger.error(f"Error creating workflow definition: {e}")
            raise
    
    async def execute_workflow(
        self, 
        workflow_definition_id: str,
        variables: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> str:
        """
        Ejecuta un flujo de trabajo
        """
        try:
            # Obtener definición
            definition = await self._get_workflow_definition(workflow_definition_id)
            if not definition:
                raise ValueError(f"Workflow definition not found: {workflow_definition_id}")
            
            # Crear instancia
            instance = WorkflowInstance(
                workflow_definition_id=workflow_definition_id,
                name=f"{definition.name} - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
                variables=variables or {},
                created_by=created_by
            )
            
            # Clonar tareas
            instance.task_instances = [
                WorkflowTask(
                    id=str(uuid.uuid4()),
                    name=task.name,
                    description=task.description,
                    task_type=task.task_type,
                    priority=task.priority,
                    dependencies=task.dependencies.copy(),
                    parameters=task.parameters.copy(),
                    max_retries=task.max_retries,
                    timeout_seconds=task.timeout_seconds
                )
                for task in definition.tasks
            ]
            
            # Guardar instancia
            instance_id = await self._save_workflow_instance(instance)
            instance.id = instance_id
            
            # Agregar a instancias activas
            self.active_instances[instance_id] = instance
            
            # Ejecutar en background
            asyncio.create_task(self._execute_workflow_instance(instance))
            
            logger.info(f"Workflow execution started: {instance_id}")
            return instance_id
            
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise
    
    async def _execute_workflow_instance(self, instance: WorkflowInstance):
        """
        Ejecuta una instancia de flujo de trabajo
        """
        try:
            instance.status = WorkflowStatus.RUNNING
            instance.started_at = datetime.now()
            await self._update_workflow_instance(instance)
            
            await self._log_workflow_event(
                instance.id, 
                "INFO", 
                f"Workflow execution started: {instance.name}"
            )
            
            # Ejecutar tareas en orden de dependencias
            while True:
                # Encontrar tareas listas para ejecutar
                ready_tasks = await self._get_ready_tasks(instance)
                
                if not ready_tasks:
                    # Verificar si todas las tareas están completadas
                    if all(task.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED, TaskStatus.CANCELLED] 
                           for task in instance.task_instances):
                        instance.status = WorkflowStatus.COMPLETED
                        instance.completed_at = datetime.now()
                        await self._update_workflow_instance(instance)
                        
                        await self._log_workflow_event(
                            instance.id, 
                            "INFO", 
                            f"Workflow completed successfully: {instance.name}"
                        )
                        break
                    else:
                        # Hay tareas pendientes pero ninguna está lista
                        failed_tasks = [task for task in instance.task_instances 
                                      if task.status == TaskStatus.FAILED]
                        if failed_tasks:
                            instance.status = WorkflowStatus.FAILED
                            instance.error_message = f"Failed tasks: {[t.name for t in failed_tasks]}"
                            await self._update_workflow_instance(instance)
                            
                            await self._log_workflow_event(
                                instance.id, 
                                "ERROR", 
                                f"Workflow failed: {instance.error_message}"
                            )
                            break
                        else:
                            # Esperar un poco y reintentar
                            await asyncio.sleep(1)
                            continue
                
                # Ejecutar tareas listas en paralelo
                await self._execute_ready_tasks(instance, ready_tasks)
                
        except Exception as e:
            instance.status = WorkflowStatus.FAILED
            instance.error_message = str(e)
            await self._update_workflow_instance(instance)
            
            await self._log_workflow_event(
                instance.id, 
                "ERROR", 
                f"Workflow execution failed: {str(e)}",
                {"traceback": traceback.format_exc()}
            )
            
            logger.error(f"Workflow execution failed: {e}")
        finally:
            # Remover de instancias activas
            if instance.id in self.active_instances:
                del self.active_instances[instance.id]
    
    async def _get_ready_tasks(self, instance: WorkflowInstance) -> List[WorkflowTask]:
        """
        Obtiene tareas listas para ejecutar
        """
        ready_tasks = []
        
        for task in instance.task_instances:
            if task.status != TaskStatus.PENDING:
                continue
            
            # Verificar dependencias
            dependencies_met = True
            for dep_id in task.dependencies:
                dep_task = next((t for t in instance.task_instances if t.id == dep_id), None)
                if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                    dependencies_met = False
                    break
            
            if dependencies_met:
                task.status = TaskStatus.READY
                ready_tasks.append(task)
        
        return ready_tasks
    
    async def _execute_ready_tasks(
        self, 
        instance: WorkflowInstance, 
        ready_tasks: List[WorkflowTask]
    ):
        """
        Ejecuta tareas listas en paralelo
        """
        # Agrupar tareas por prioridad
        tasks_by_priority = {}
        for task in ready_tasks:
            if task.priority not in tasks_by_priority:
                tasks_by_priority[task.priority] = []
            tasks_by_priority[task.priority].append(task)
        
        # Ejecutar por prioridad (mayor prioridad primero)
        for priority in sorted(tasks_by_priority.keys(), reverse=True):
            tasks = tasks_by_priority[priority]
            
            # Ejecutar tareas de la misma prioridad en paralelo
            futures = []
            for task in tasks:
                future = asyncio.create_task(self._execute_task(instance, task))
                futures.append(future)
            
            # Esperar a que todas las tareas de esta prioridad terminen
            await asyncio.gather(*futures, return_exceptions=True)
    
    async def _execute_task(self, instance: WorkflowInstance, task: WorkflowTask):
        """
        Ejecuta una tarea individual
        """
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            await self._update_task_instance(instance.id, task)
            
            await self._log_workflow_event(
                instance.id, 
                "INFO", 
                f"Task started: {task.name}",
                {"task_id": task.id, "task_type": task.task_type.value}
            )
            
            # Obtener handler para el tipo de tarea
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                raise ValueError(f"No handler found for task type: {task.task_type}")
            
            # Ejecutar tarea con timeout
            result = await asyncio.wait_for(
                handler(instance, task),
                timeout=task.timeout_seconds
            )
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now()
            task.result = result
            await self._update_task_instance(instance.id, task)
            
            await self._log_workflow_event(
                instance.id, 
                "INFO", 
                f"Task completed: {task.name}",
                {"task_id": task.id, "result": result}
            )
            
        except asyncio.TimeoutError:
            task.status = TaskStatus.FAILED
            task.error_message = f"Task timeout after {task.timeout_seconds} seconds"
            await self._update_task_instance(instance.id, task)
            
            await self._log_workflow_event(
                instance.id, 
                "ERROR", 
                f"Task timeout: {task.name}",
                {"task_id": task.id, "timeout": task.timeout_seconds}
            )
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            await self._update_task_instance(instance.id, task)
            
            await self._log_workflow_event(
                instance.id, 
                "ERROR", 
                f"Task failed: {task.name}",
                {"task_id": task.id, "error": str(e), "traceback": traceback.format_exc()}
            )
            
            # Reintentar si es posible
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.PENDING
                task.started_at = None
                task.completed_at = None
                task.error_message = None
                await self._update_task_instance(instance.id, task)
                
                await self._log_workflow_event(
                    instance.id, 
                    "INFO", 
                    f"Task retry {task.retry_count}/{task.max_retries}: {task.name}",
                    {"task_id": task.id}
                )
    
    # Handlers de tareas específicas
    async def _handle_document_generation(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para generación de documentos
        """
        # Obtener parámetros de la tarea
        query = task.parameters.get("query", "")
        document_types = task.parameters.get("document_types", [])
        max_documents = task.parameters.get("max_documents", 5)
        
        # Crear petición de generación
        request = ContinuousGenerationRequest(
            query=query,
            document_types=[DocumentType(dt) for dt in document_types],
            max_documents=max_documents,
            context=instance.variables.get("context", {})
        )
        
        # Generar documentos
        generator = ContinuousDocumentGenerator()
        async with generator:
            documents = await generator.generate_continuous_documents(request)
        
        # Guardar documentos en variables de la instancia
        instance.variables["generated_documents"] = [
            {
                "id": doc.id,
                "title": doc.title,
                "type": doc.type.value,
                "content": doc.content,
                "quality_score": doc.quality_score,
                "coherence_score": doc.coherence_score
            }
            for doc in documents
        ]
        
        return {
            "documents_generated": len(documents),
            "document_ids": [doc.id for doc in documents],
            "average_quality": sum(doc.quality_score for doc in documents) / len(documents),
            "average_coherence": sum(doc.coherence_score for doc in documents) / len(documents)
        }
    
    async def _handle_quality_check(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para verificación de calidad
        """
        documents = instance.variables.get("generated_documents", [])
        if not documents:
            raise ValueError("No documents found for quality check")
        
        quality_threshold = task.parameters.get("quality_threshold", 0.7)
        failed_documents = []
        
        for doc in documents:
            if doc["quality_score"] < quality_threshold:
                failed_documents.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "quality_score": doc["quality_score"]
                })
        
        if failed_documents:
            instance.variables["quality_check_failed"] = True
            instance.variables["failed_documents"] = failed_documents
        else:
            instance.variables["quality_check_passed"] = True
        
        return {
            "total_documents": len(documents),
            "failed_documents": len(failed_documents),
            "quality_threshold": quality_threshold,
            "failed_document_details": failed_documents
        }
    
    async def _handle_redundancy_analysis(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para análisis de redundancia
        """
        documents = instance.variables.get("generated_documents", [])
        if not documents:
            raise ValueError("No documents found for redundancy analysis")
        
        # Convertir a objetos ContentItem
        from ..services.redundancy_detector import ContentItem, ContentType
        
        content_items = []
        for doc in documents:
            content_item = ContentItem(
                id=doc["id"],
                content=doc["content"],
                content_type=ContentType.DOCUMENT,
                metadata={"title": doc["title"], "type": doc["type"]}
            )
            content_items.append(content_item)
        
        # Analizar redundancia
        detector = ContentRedundancyDetector()
        reports, optimized_docs = await detector.analyze_document_redundancy(content_items)
        
        # Actualizar variables
        instance.variables["redundancy_reports"] = [
            {
                "document_id": report.document_id,
                "similarity_score": report.similarity_score,
                "redundant_sections": len(report.redundant_sections),
                "recommendations": report.recommendations
            }
            for report in reports
        ]
        
        return {
            "total_reports": len(reports),
            "high_similarity_count": len([r for r in reports if r.similarity_score > 0.8]),
            "optimization_applied": len(optimized_docs) > 0
        }
    
    async def _handle_coherence_validation(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para validación de coherencia
        """
        documents = instance.variables.get("generated_documents", [])
        if not documents:
            raise ValueError("No documents found for coherence validation")
        
        coherence_threshold = task.parameters.get("coherence_threshold", 0.7)
        failed_documents = []
        
        for doc in documents:
            if doc["coherence_score"] < coherence_threshold:
                failed_documents.append({
                    "id": doc["id"],
                    "title": doc["title"],
                    "coherence_score": doc["coherence_score"]
                })
        
        if failed_documents:
            instance.variables["coherence_validation_failed"] = True
            instance.variables["coherence_failed_documents"] = failed_documents
        else:
            instance.variables["coherence_validation_passed"] = True
        
        return {
            "total_documents": len(documents),
            "failed_documents": len(failed_documents),
            "coherence_threshold": coherence_threshold,
            "failed_document_details": failed_documents
        }
    
    async def _handle_user_review(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para revisión de usuario
        """
        # Esta tarea requiere intervención manual
        # Se pausa el flujo hasta que el usuario complete la revisión
        
        review_required = task.parameters.get("review_required", True)
        if not review_required:
            return {"status": "skipped", "reason": "Review not required"}
        
        # Crear notificación para el usuario
        user_email = task.parameters.get("user_email")
        if user_email:
            await self.notification_service.send_review_notification(
                user_email,
                instance.id,
                task.id,
                instance.variables.get("generated_documents", [])
            )
        
        # Pausar el flujo de trabajo
        instance.status = WorkflowStatus.PAUSED
        await self._update_workflow_instance(instance)
        
        return {
            "status": "paused",
            "reason": "Waiting for user review",
            "notification_sent": user_email is not None
        }
    
    async def _handle_approval(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para aprobación
        """
        # Verificar si hay documentos que requieren aprobación
        quality_failed = instance.variables.get("quality_check_failed", False)
        coherence_failed = instance.variables.get("coherence_validation_failed", False)
        
        if quality_failed or coherence_failed:
            # Requiere aprobación manual
            approver_email = task.parameters.get("approver_email")
            if approver_email:
                await self.notification_service.send_approval_notification(
                    approver_email,
                    instance.id,
                    task.id,
                    {
                        "quality_failed": quality_failed,
                        "coherence_failed": coherence_failed,
                        "failed_documents": instance.variables.get("failed_documents", []),
                        "coherence_failed_documents": instance.variables.get("coherence_failed_documents", [])
                    }
                )
            
            # Pausar el flujo de trabajo
            instance.status = WorkflowStatus.PAUSED
            await self._update_workflow_instance(instance)
            
            return {
                "status": "paused",
                "reason": "Waiting for approval",
                "approval_required": True,
                "notification_sent": approver_email is not None
            }
        else:
            # Aprobación automática
            instance.variables["approved"] = True
            return {
                "status": "approved",
                "reason": "Automatic approval - all checks passed"
            }
    
    async def _handle_notification(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para notificaciones
        """
        notification_type = task.parameters.get("type", "completion")
        recipients = task.parameters.get("recipients", [])
        
        if not recipients:
            return {"status": "skipped", "reason": "No recipients specified"}
        
        # Enviar notificación
        await self.notification_service.send_workflow_notification(
            recipients,
            notification_type,
            instance,
            task.parameters.get("message", "")
        )
        
        return {
            "status": "sent",
            "recipients": len(recipients),
            "type": notification_type
        }
    
    async def _handle_custom_task(
        self, 
        instance: WorkflowInstance, 
        task: WorkflowTask
    ) -> Dict[str, Any]:
        """
        Handler para tareas personalizadas
        """
        # Ejecutar función personalizada
        custom_function = task.parameters.get("function")
        if not custom_function:
            raise ValueError("No custom function specified")
        
        # Aquí se podría ejecutar código Python personalizado
        # Por seguridad, esto debería estar restringido en producción
        try:
            # Ejemplo de ejecución de función personalizada
            result = eval(custom_function, {"instance": instance, "task": task})
            return {"result": result, "status": "completed"}
        except Exception as e:
            raise ValueError(f"Custom function execution failed: {e}")
    
    # Métodos de persistencia
    async def _save_workflow_definition(self, definition: WorkflowDefinition) -> str:
        """Guarda definición de flujo de trabajo"""
        # Implementar guardado en base de datos
        pass
    
    async def _get_workflow_definition(self, definition_id: str) -> Optional[WorkflowDefinition]:
        """Obtiene definición de flujo de trabajo"""
        # Implementar consulta a base de datos
        pass
    
    async def _save_workflow_instance(self, instance: WorkflowInstance) -> str:
        """Guarda instancia de flujo de trabajo"""
        # Implementar guardado en base de datos
        pass
    
    async def _update_workflow_instance(self, instance: WorkflowInstance):
        """Actualiza instancia de flujo de trabajo"""
        # Implementar actualización en base de datos
        pass
    
    async def _update_task_instance(self, instance_id: str, task: WorkflowTask):
        """Actualiza instancia de tarea"""
        # Implementar actualización en base de datos
        pass
    
    async def _log_workflow_event(
        self, 
        instance_id: str, 
        level: str, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        """Registra evento del flujo de trabajo"""
        log = WorkflowExecutionLog(
            workflow_instance_id=instance_id,
            level=level,
            message=message,
            details=details or {}
        )
        # Implementar guardado de log
        pass
    
    async def _validate_workflow_definition(self, definition: WorkflowDefinition):
        """Valida definición de flujo de trabajo"""
        if not definition.name:
            raise ValueError("Workflow name is required")
        
        if not definition.tasks:
            raise ValueError("Workflow must have at least one task")
        
        # Validar dependencias
        task_ids = {task.id for task in definition.tasks}
        for task in definition.tasks:
            for dep_id in task.dependencies:
                if dep_id not in task_ids:
                    raise ValueError(f"Task {task.name} has invalid dependency: {dep_id}")
    
    # Métodos de consulta
    async def get_workflow_instances(
        self, 
        status: Optional[WorkflowStatus] = None,
        limit: int = 100
    ) -> List[WorkflowInstance]:
        """Obtiene instancias de flujo de trabajo"""
        # Implementar consulta a base de datos
        pass
    
    async def get_workflow_instance(self, instance_id: str) -> Optional[WorkflowInstance]:
        """Obtiene instancia específica de flujo de trabajo"""
        # Implementar consulta a base de datos
        pass
    
    async def cancel_workflow(self, instance_id: str) -> bool:
        """Cancela un flujo de trabajo"""
        if instance_id in self.active_instances:
            instance = self.active_instances[instance_id]
            instance.status = WorkflowStatus.CANCELLED
            await self._update_workflow_instance(instance)
            return True
        return False
    
    async def pause_workflow(self, instance_id: str) -> bool:
        """Pausa un flujo de trabajo"""
        if instance_id in self.active_instances:
            instance = self.active_instances[instance_id]
            instance.status = WorkflowStatus.PAUSED
            await self._update_workflow_instance(instance)
            return True
        return False
    
    async def resume_workflow(self, instance_id: str) -> bool:
        """Reanuda un flujo de trabajo pausado"""
        # Implementar reanudación
        pass
```

## 4. Plantillas de Flujo de Trabajo

### 4.1 Plantilla Básica de Generación

```python
# app/templates/workflows/basic_generation.py
from app.models.workflow import *

def create_basic_generation_workflow() -> WorkflowDefinition:
    """
    Crea un flujo de trabajo básico para generación de documentos
    """
    workflow = WorkflowDefinition(
        name="Basic Document Generation",
        description="Flujo básico para generación de documentos con validación de calidad",
        version="1.0.0"
    )
    
    # Tarea 1: Generación de documentos
    generation_task = WorkflowTask(
        name="Generate Documents",
        description="Generar documentos basados en la petición del usuario",
        task_type=TaskType.DOCUMENT_GENERATION,
        priority=1,
        parameters={
            "query": "{{user_query}}",
            "document_types": ["{{document_types}}"],
            "max_documents": "{{max_documents}}"
        }
    )
    
    # Tarea 2: Verificación de calidad
    quality_task = WorkflowTask(
        name="Quality Check",
        description="Verificar calidad de los documentos generados",
        task_type=TaskType.QUALITY_CHECK,
        priority=2,
        dependencies=[generation_task.id],
        parameters={
            "quality_threshold": 0.7
        }
    )
    
    # Tarea 3: Análisis de redundancia
    redundancy_task = WorkflowTask(
        name="Redundancy Analysis",
        description="Analizar redundancia entre documentos",
        task_type=TaskType.REDUNDANCY_ANALYSIS,
        priority=2,
        dependencies=[generation_task.id],
        parameters={
            "similarity_threshold": 0.8
        }
    )
    
    # Tarea 4: Validación de coherencia
    coherence_task = WorkflowTask(
        name="Coherence Validation",
        description="Validar coherencia entre documentos",
        task_type=TaskType.COHERENCE_VALIDATION,
        priority=2,
        dependencies=[generation_task.id],
        parameters={
            "coherence_threshold": 0.7
        }
    )
    
    # Tarea 5: Aprobación
    approval_task = WorkflowTask(
        name="Approval",
        description="Aprobar documentos generados",
        task_type=TaskType.APPROVAL,
        priority=3,
        dependencies=[quality_task.id, redundancy_task.id, coherence_task.id],
        parameters={
            "approver_email": "{{approver_email}}"
        }
    )
    
    # Tarea 6: Notificación
    notification_task = WorkflowTask(
        name="Send Notification",
        description="Enviar notificación de finalización",
        task_type=TaskType.NOTIFICATION,
        priority=4,
        dependencies=[approval_task.id],
        parameters={
            "type": "completion",
            "recipients": ["{{user_email}}"],
            "message": "Document generation completed successfully"
        }
    )
    
    workflow.tasks = [
        generation_task,
        quality_task,
        redundancy_task,
        coherence_task,
        approval_task,
        notification_task
    ]
    
    # Trigger manual
    manual_trigger = WorkflowTrigger(
        name="Manual Trigger",
        trigger_type=TriggerType.MANUAL,
        enabled=True
    )
    
    workflow.triggers = [manual_trigger]
    
    return workflow
```

### 4.2 Plantilla Avanzada con Revisión

```python
# app/templates/workflows/advanced_review.py
def create_advanced_review_workflow() -> WorkflowDefinition:
    """
    Crea un flujo de trabajo avanzado con revisión de usuario
    """
    workflow = WorkflowDefinition(
        name="Advanced Document Generation with Review",
        description="Flujo avanzado con generación, validación y revisión de usuario",
        version="1.0.0"
    )
    
    # Tarea 1: Generación inicial
    initial_generation = WorkflowTask(
        name="Initial Generation",
        description="Generación inicial de documentos",
        task_type=TaskType.DOCUMENT_GENERATION,
        priority=1,
        parameters={
            "query": "{{user_query}}",
            "document_types": ["{{document_types}}"],
            "max_documents": "{{max_documents}}"
        }
    )
    
    # Tarea 2: Verificación de calidad
    quality_check = WorkflowTask(
        name="Quality Check",
        description="Verificación de calidad",
        task_type=TaskType.QUALITY_CHECK,
        priority=2,
        dependencies=[initial_generation.id],
        parameters={
            "quality_threshold": 0.8
        }
    )
    
    # Tarea 3: Revisión de usuario
    user_review = WorkflowTask(
        name="User Review",
        description="Revisión manual por parte del usuario",
        task_type=TaskType.USER_REVIEW,
        priority=3,
        dependencies=[quality_check.id],
        parameters={
            "user_email": "{{user_email}}",
            "review_required": True
        }
    )
    
    # Tarea 4: Generación mejorada (condicional)
    improved_generation = WorkflowTask(
        name="Improved Generation",
        description="Generación mejorada basada en feedback",
        task_type=TaskType.DOCUMENT_GENERATION,
        priority=4,
        dependencies=[user_review.id],
        parameters={
            "query": "{{improved_query}}",
            "document_types": ["{{document_types}}"],
            "max_documents": "{{max_documents}}",
            "improvement_feedback": "{{user_feedback}}"
        }
    )
    
    # Tarea 5: Validación final
    final_validation = WorkflowTask(
        name="Final Validation",
        description="Validación final de todos los documentos",
        task_type=TaskType.QUALITY_CHECK,
        priority=5,
        dependencies=[improved_generation.id],
        parameters={
            "quality_threshold": 0.9,
            "coherence_threshold": 0.8
        }
    )
    
    # Tarea 6: Notificación final
    final_notification = WorkflowTask(
        name="Final Notification",
        description="Notificación de finalización",
        task_type=TaskType.NOTIFICATION,
        priority=6,
        dependencies=[final_validation.id],
        parameters={
            "type": "completion",
            "recipients": ["{{user_email}}"],
            "message": "Document generation and review completed"
        }
    )
    
    workflow.tasks = [
        initial_generation,
        quality_check,
        user_review,
        improved_generation,
        final_validation,
        final_notification
    ]
    
    return workflow
```

## 5. API Endpoints para Flujo de Trabajo

### 5.1 Endpoints de Gestión

```python
# app/api/workflow_endpoints.py
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from ..models.workflow import *
from ..services.workflow_engine import DocumentWorkflowChainEngine

router = APIRouter(prefix="/api/workflow", tags=["Workflow Management"])

class WorkflowDefinitionRequest(BaseModel):
    name: str
    description: str
    tasks: List[Dict[str, Any]]
    triggers: List[Dict[str, Any]] = []
    variables: Dict[str, Any] = {}

class WorkflowExecutionRequest(BaseModel):
    workflow_definition_id: str
    variables: Dict[str, Any] = {}
    created_by: Optional[str] = None

class WorkflowInstanceResponse(BaseModel):
    id: str
    name: str
    status: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    progress: float = 0.0

@router.post("/definitions")
async def create_workflow_definition(
    request: WorkflowDefinitionRequest,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Crea una nueva definición de flujo de trabajo
    """
    try:
        # Convertir request a WorkflowDefinition
        definition = WorkflowDefinition(
            name=request.name,
            description=request.description,
            tasks=[WorkflowTask(**task) for task in request.tasks],
            triggers=[WorkflowTrigger(**trigger) for trigger in request.triggers],
            variables=request.variables
        )
        
        definition_id = await engine.create_workflow_definition(definition)
        
        return {
            "success": True,
            "definition_id": definition_id,
            "message": "Workflow definition created successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute")
async def execute_workflow(
    request: WorkflowExecutionRequest,
    background_tasks: BackgroundTasks,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Ejecuta un flujo de trabajo
    """
    try:
        instance_id = await engine.execute_workflow(
            request.workflow_definition_id,
            request.variables,
            request.created_by
        )
        
        return {
            "success": True,
            "instance_id": instance_id,
            "message": "Workflow execution started"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances")
async def get_workflow_instances(
    status: Optional[str] = None,
    limit: int = 100,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Obtiene instancias de flujo de trabajo
    """
    try:
        workflow_status = WorkflowStatus(status) if status else None
        instances = await engine.get_workflow_instances(workflow_status, limit)
        
        return {
            "success": True,
            "instances": [
                {
                    "id": instance.id,
                    "name": instance.name,
                    "status": instance.status.value,
                    "created_at": instance.created_at.isoformat(),
                    "started_at": instance.started_at.isoformat() if instance.started_at else None,
                    "completed_at": instance.completed_at.isoformat() if instance.completed_at else None,
                    "progress": len([t for t in instance.task_instances if t.status == TaskStatus.COMPLETED]) / len(instance.task_instances) if instance.task_instances else 0
                }
                for instance in instances
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/instances/{instance_id}")
async def get_workflow_instance(
    instance_id: str,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Obtiene una instancia específica de flujo de trabajo
    """
    try:
        instance = await engine.get_workflow_instance(instance_id)
        if not instance:
            raise HTTPException(status_code=404, detail="Workflow instance not found")
        
        return {
            "success": True,
            "instance": {
                "id": instance.id,
                "name": instance.name,
                "status": instance.status.value,
                "variables": instance.variables,
                "tasks": [
                    {
                        "id": task.id,
                        "name": task.name,
                        "status": task.status.value,
                        "started_at": task.started_at.isoformat() if task.started_at else None,
                        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                        "error_message": task.error_message,
                        "result": task.result
                    }
                    for task in instance.task_instances
                ],
                "created_at": instance.created_at.isoformat(),
                "started_at": instance.started_at.isoformat() if instance.started_at else None,
                "completed_at": instance.completed_at.isoformat() if instance.completed_at else None
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/cancel")
async def cancel_workflow(
    instance_id: str,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Cancela un flujo de trabajo
    """
    try:
        success = await engine.cancel_workflow(instance_id)
        
        if success:
            return {
                "success": True,
                "message": "Workflow cancelled successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Workflow instance not found or not cancellable")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/pause")
async def pause_workflow(
    instance_id: str,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Pausa un flujo de trabajo
    """
    try:
        success = await engine.pause_workflow(instance_id)
        
        if success:
            return {
                "success": True,
                "message": "Workflow paused successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Workflow instance not found or not pausable")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/instances/{instance_id}/resume")
async def resume_workflow(
    instance_id: str,
    engine: DocumentWorkflowChainEngine = Depends()
):
    """
    Reanuda un flujo de trabajo pausado
    """
    try:
        success = await engine.resume_workflow(instance_id)
        
        if success:
            return {
                "success": True,
                "message": "Workflow resumed successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Workflow instance not found or not resumable")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/templates")
async def get_workflow_templates():
    """
    Obtiene plantillas de flujo de trabajo disponibles
    """
    templates = [
        {
            "id": "basic_generation",
            "name": "Basic Document Generation",
            "description": "Flujo básico para generación de documentos con validación de calidad",
            "tasks": [
                "Generate Documents",
                "Quality Check",
                "Redundancy Analysis",
                "Coherence Validation",
                "Approval",
                "Send Notification"
            ]
        },
        {
            "id": "advanced_review",
            "name": "Advanced Generation with Review",
            "description": "Flujo avanzado con generación, validación y revisión de usuario",
            "tasks": [
                "Initial Generation",
                "Quality Check",
                "User Review",
                "Improved Generation",
                "Final Validation",
                "Final Notification"
            ]
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    }
```

## 6. Conclusión

El **Motor de Flujo de Trabajo de Documentos** proporciona:

### 🎯 **Características Principales**
- **Orquestación Completa** - Gestiona todo el proceso de generación
- **Dependencias Inteligentes** - Ejecuta tareas en el orden correcto
- **Ejecución Paralela** - Optimiza el rendimiento
- **Manejo de Errores** - Reintentos automáticos y recuperación
- **Estados Persistentes** - Mantiene el estado entre reinicios

### 🔧 **Funcionalidades Avanzadas**
- **Tareas Personalizadas** - Extensibilidad completa
- **Condiciones Dinámicas** - Lógica de negocio flexible
- **Notificaciones** - Comunicación automática
- **Revisión de Usuario** - Integración humana
- **Aprobaciones** - Control de calidad

### 📊 **Beneficios del Sistema**
- **Automatización Completa** - Reduce intervención manual
- **Trazabilidad Total** - Logs detallados de ejecución
- **Escalabilidad** - Maneja múltiples flujos simultáneos
- **Flexibilidad** - Plantillas reutilizables
- **Confiabilidad** - Manejo robusto de errores

Este motor transforma la generación de documentos de un proceso manual en un flujo de trabajo automatizado, inteligente y confiable.


















