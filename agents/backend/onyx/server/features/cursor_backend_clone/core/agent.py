"""
Cursor Agent - Agente principal 24/7
=====================================

Agente persistente que escucha y ejecuta comandos desde Cursor.
"""

import asyncio
import logging
from enum import Enum
from typing import Optional, Dict, Any, List, Callable
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime

# Usar orjson para JSON más rápido
try:
    import orjson as json
except ImportError:
    import json  # Fallback a json estándar

# Usar structlog para logging estructurado
try:
    import structlog
    logger = structlog.get_logger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Estados del agente"""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class AgentConfig:
    """Configuración del agente"""
    check_interval: float = 1.0  # Segundos entre checks
    max_concurrent_tasks: int = 5
    task_timeout: float = 300.0  # 5 minutos
    auto_restart: bool = True
    persistent_storage: bool = True
    storage_path: str = "./data/agent_state.json"
    command_file: Optional[str] = None  # Archivo para recibir comandos
    watch_directory: Optional[str] = None  # Directorio a monitorear


@dataclass
class Task:
    """Tarea a ejecutar"""
    id: str
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    status: str = "pending"
    result: Optional[str] = None
    error: Optional[str] = None


class CursorAgent:
    """Agente principal que escucha y ejecuta comandos"""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.status = AgentStatus.IDLE
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.running = False
        self._listener_task: Optional[asyncio.Task] = None
        self._executor_task: Optional[asyncio.Task] = None
        self._callbacks: List[Callable] = []
        
        # Estado persistente
        self._state_file = self.config.storage_path
        
        # Sistema de notificaciones y métricas
        try:
            from .notifications import NotificationManager, NotificationLevel
            from .metrics import MetricsCollector
            self.notifications = NotificationManager()
            self.metrics = MetricsCollector()
        except ImportError:
            self.notifications = None
            self.metrics = None
        
        # Rate limiter
        try:
            from .rate_limiter import TaskRateLimiter
            self.rate_limiter = TaskRateLimiter(
                max_tasks_per_minute=60,
                max_concurrent_tasks=self.config.max_concurrent_tasks
            )
        except ImportError:
            self.rate_limiter = None
        
        # Plugin manager
        try:
            from .plugins import PluginManager
            self.plugin_manager = PluginManager(self)
        except ImportError:
            self.plugin_manager = None
        
        # Scheduler
        try:
            from .scheduler import TaskScheduler
            self.scheduler = TaskScheduler(self)
        except ImportError:
            self.scheduler = None
        
        # Backup manager
        try:
            from .backup import BackupManager
            self.backup_manager = BackupManager(self)
        except ImportError:
            self.backup_manager = None
        
        # Cache
        try:
            from .cache import CommandCache
            self.command_cache = CommandCache()
        except ImportError:
            self.command_cache = None
        
        # Template manager
        try:
            from .templates import TemplateManager
            self.template_manager = TemplateManager()
        except ImportError:
            self.template_manager = None
        
        # Validator
        try:
            from .validators import CommandValidator
            self.validator = CommandValidator()
        except ImportError:
            self.validator = None
        
        # Event bus
        try:
            from .event_bus import EventBus, EventType
            self.event_bus = EventBus()
        except ImportError:
            self.event_bus = None
        
        # Cluster manager
        try:
            from .cluster import ClusterManager
            self.cluster_manager = ClusterManager(self)
        except ImportError:
            self.cluster_manager = None
        
        # Config manager
        try:
            from .config_manager import ConfigManager
            config_path = Path(self.config.storage_path).parent / "config.json"
            self.config_manager = ConfigManager(str(config_path))
        except ImportError:
            self.config_manager = None
        
        # Alert manager
        try:
            from .alerting import AlertManager
            self.alert_manager = AlertManager(self)
        except ImportError:
            self.alert_manager = None
        
        # AI Processor
        try:
            from .ai_processor import AIProcessor
            self.ai_processor = AIProcessor(use_local=True)
        except ImportError:
            self.ai_processor = None
        
        # Embeddings
        try:
            from .embeddings import EmbeddingStore
            self.embedding_store = EmbeddingStore()
        except ImportError:
            self.embedding_store = None
        
        # Pattern Learner
        try:
            from .pattern_learner import PatternLearner
            self.pattern_learner = PatternLearner()
        except ImportError:
            self.pattern_learner = None
        
    async def start(self) -> None:
        """Iniciar el agente"""
        if self.status == AgentStatus.RUNNING:
            logger.warning("Agent is already running")
            return
            
        logger.info("🚀 Starting Cursor Agent 24/7...")
        self.running = True
        self.status = AgentStatus.RUNNING
        
        # Inicializar componentes de IA
        if self.ai_processor:
            await self.ai_processor.initialize()
        if self.embedding_store:
            await self.embedding_store.initialize()
        if self.pattern_learner:
            await self.pattern_learner.load()
        
        # Cargar estado persistente si existe
        if self.config.persistent_storage:
            await self._load_state()
        
        # Iniciar listener y executor
        self._listener_task = asyncio.create_task(self._listen_loop())
        self._executor_task = asyncio.create_task(self._executor_loop())
        
        # Iniciar plugins
        if self.plugin_manager:
            await self.plugin_manager.start_all()
        
        # Iniciar scheduler
        if self.scheduler:
            await self.scheduler.start()
        
        # Iniciar backup automático
        if self.backup_manager:
            await self.backup_manager.start_auto_backup()
        
        # Iniciar cluster manager
        if self.cluster_manager:
            await self.cluster_manager.start()
        
        # Iniciar alert manager
        if self.alert_manager:
            await self.alert_manager.start()
        
        logger.info("✅ Agent started successfully")
        await self._notify_callbacks("started")
        
        # Publicar evento
        if self.event_bus:
            await self.event_bus.publish(
                self.event_bus.EventType.AGENT_STARTED,
                {"agent_id": id(self)},
                source="agent"
            )
        
        # Notificación y métrica
        if self.notifications:
            await self.notifications.notify(
                "Agent Started",
                "Cursor Agent 24/7 is now running",
                level=self.notifications.NotificationLevel.SUCCESS
            )
        if self.metrics:
            self.metrics.increment("agent_starts")
            self.metrics.set_gauge("agent_running", 1.0)
        
    async def stop(self) -> None:
        """Detener el agente"""
        if self.status == AgentStatus.STOPPED:
            return
            
        logger.info("🛑 Stopping Cursor Agent...")
        self.running = False
        self.status = AgentStatus.STOPPED
        
        # Cancelar tareas
        if self._listener_task:
            self._listener_task.cancel()
        if self._executor_task:
            self._executor_task.cancel()
            
        # Esperar a que terminen
        await asyncio.gather(
            self._listener_task,
            self._executor_task,
            return_exceptions=True
        )
        
        # Detener componentes
        if self.alert_manager:
            await self.alert_manager.stop()
        
        if self.cluster_manager:
            await self.cluster_manager.stop()
        
        if self.scheduler:
            await self.scheduler.stop()
        
        if self.backup_manager:
            await self.backup_manager.stop_auto_backup()
        
        if self.plugin_manager:
            await self.plugin_manager.stop_all()
        
        # Publicar evento
        if self.event_bus:
            await self.event_bus.publish(
                self.event_bus.EventType.AGENT_STOPPED,
                {"agent_id": id(self)},
                source="agent"
            )
        
        # Guardar estado
        if self.config.persistent_storage:
            await self._save_state()
            
        logger.info("✅ Agent stopped")
        await self._notify_callbacks("stopped")
        
        # Notificación y métrica
        if self.notifications:
            await self.notifications.notify(
                "Agent Stopped",
                "Cursor Agent 24/7 has been stopped",
                level=self.notifications.NotificationLevel.INFO
            )
        if self.metrics:
            self.metrics.increment("agent_stops")
            self.metrics.set_gauge("agent_running", 0.0)
        
    async def pause(self) -> None:
        """Pausar el agente"""
        if self.status == AgentStatus.RUNNING:
            self.status = AgentStatus.PAUSED
            logger.info("⏸️ Agent paused")
            await self._notify_callbacks("paused")
            
    async def resume(self) -> None:
        """Reanudar el agente"""
        if self.status == AgentStatus.PAUSED:
            self.status = AgentStatus.RUNNING
            logger.info("▶️ Agent resumed")
            await self._notify_callbacks("resumed")
            
    async def add_task(self, command: str) -> str:
        """Agregar una tarea al queue"""
        # Validar comando
        if self.validator:
            validation = self.validator.validate(command)
            if not validation.valid:
                raise ValueError(f"Command validation failed: {', '.join(validation.errors)}")
            if validation.warnings:
                logger.warning(f"Command warnings: {', '.join(validation.warnings)}")
            # Sanitizar comando
            command = self.validator.sanitize(command)
        
        # Verificar rate limit
        if self.rate_limiter:
            if not await self.rate_limiter.can_add_task():
                raise Exception("Rate limit exceeded. Too many tasks.")
            await self.rate_limiter.add_task()
        
        task_id = f"task_{datetime.now().timestamp()}_{len(self.tasks)}"
        task = Task(
            id=task_id,
            command=command,
            status="pending"
        )
        
        self.tasks[task_id] = task
        await self.task_queue.put(task)
        
        logger.info(f"📝 Task added: {task_id} - {command[:50]}...")
        
        # Métricas
        if self.metrics:
            self.metrics.increment("tasks_added")
            self.metrics.set_gauge("tasks_pending", sum(1 for t in self.tasks.values() if t.status == "pending"))
        
        # Notificar plugins
        if self.plugin_manager:
            await self.plugin_manager.notify_task_added(task_id, command)
        
        # Publicar evento
        if self.event_bus:
            await self.event_bus.publish(
                self.event_bus.EventType.TASK_ADDED,
                {"task_id": task_id, "command": command[:100]},
                source="agent"
            )
        
        return task_id
        
    async def get_status(self) -> Dict[str, Any]:
        """Obtener estado del agente"""
        status = {
            "status": self.status.value,
            "running": self.running,
            "tasks_total": len(self.tasks),
            "tasks_pending": sum(1 for t in self.tasks.values() if t.status == "pending"),
            "tasks_running": sum(1 for t in self.tasks.values() if t.status == "running"),
            "tasks_completed": sum(1 for t in self.tasks.values() if t.status == "completed"),
            "tasks_failed": sum(1 for t in self.tasks.values() if t.status == "failed"),
        }
        
        # Agregar métricas si están disponibles
        if self.metrics:
            status["metrics"] = self.metrics.get_summary()
        
        # Agregar notificaciones si están disponibles
        if self.notifications:
            status["notifications"] = self.notifications.get_stats()
        
        return status
        
    async def get_tasks(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Obtener lista de tareas"""
        tasks_list = list(self.tasks.values())
        tasks_list.sort(key=lambda x: x.timestamp, reverse=True)
        
        return [
            {
                "id": task.id,
                "command": task.command,
                "status": task.status,
                "timestamp": task.timestamp.isoformat(),
                "result": task.result,
                "error": task.error,
            }
            for task in tasks_list[:limit]
        ]
        
    def on_event(self, callback: Callable) -> None:
        """Registrar callback para eventos"""
        self._callbacks.append(callback)
        
    async def _notify_callbacks(self, event: str) -> None:
        """Notificar callbacks de eventos"""
        for callback in self._callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f"Error in callback: {e}")
                
    async def _listen_loop(self) -> None:
        """Loop principal que escucha comandos"""
        logger.info("👂 Starting command listener...")
        
        # Inicializar file watcher
        from .file_watcher import FileWatcher
        
        # Determinar archivo de comandos
        if self.config.command_file:
            command_file = Path(self.config.command_file)
        else:
            command_file = Path(self.config.storage_path).parent / "commands.txt"
        
        self.file_watcher = FileWatcher(
            command_file=str(command_file) if command_file else None,
            watch_dir=self.config.watch_directory
        )
        self.file_watcher.set_callback(self._on_command_received)
        await self.file_watcher.start()
        
        if command_file:
            logger.info(f"📝 Listening for commands in: {command_file}")
            logger.info(f"💡 Write commands to: {command_file}")
        elif self.config.watch_directory:
            logger.info(f"📁 Monitoring directory: {self.config.watch_directory}")
        
        while self.running:
            try:
                await asyncio.sleep(self.config.check_interval)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in listener loop: {e}")
                if not self.config.auto_restart:
                    break
                await asyncio.sleep(5)
        
        # Detener file watcher
        if hasattr(self, 'file_watcher'):
            await self.file_watcher.stop()
    
    async def _on_command_received(self, command: str) -> None:
        """Callback cuando se recibe un comando"""
        if command and command.strip():
            logger.info(f"📨 Command received: {command[:50]}...")
            await self.add_task(command.strip())
                
    async def _executor_loop(self) -> None:
        """Loop que ejecuta tareas"""
        logger.info("⚙️ Starting task executor...")
        
        active_tasks: Dict[str, asyncio.Task] = {}
        
        while self.running:
            try:
                # Procesar tareas pendientes
                if len(active_tasks) < self.config.max_concurrent_tasks:
                    try:
                        task = await asyncio.wait_for(
                            self.task_queue.get(),
                            timeout=0.5
                        )
                        
                        if task.status == "pending":
                            task.status = "running"
                            task_executor = asyncio.create_task(
                                self._execute_task(task)
                            )
                            active_tasks[task.id] = task_executor
                            
                    except asyncio.TimeoutError:
                        pass
                
                # Limpiar tareas completadas
                completed = []
                for task_id, exec_task in active_tasks.items():
                    if exec_task.done():
                        completed.append(task_id)
                        
                for task_id in completed:
                    del active_tasks[task_id]
                    
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in executor loop: {e}")
                await asyncio.sleep(1)
                
        # Esperar a que terminen todas las tareas activas
        if active_tasks:
            await asyncio.gather(*active_tasks.values(), return_exceptions=True)
            
    async def _execute_task(self, task: Task) -> None:
        """Ejecutar una tarea"""
        start_time = datetime.now()
        success = False
        
        try:
            logger.info(f"🔨 Executing task: {task.id}")
            
            # Procesar comando con IA si está disponible
            processed_command = None
            if self.ai_processor:
                try:
                    processed_command = await self.ai_processor.process_command(task.command)
                    logger.debug(f"🤖 AI processed command: intent={processed_command.intent}, confidence={processed_command.confidence:.2f}")
                    
                    # Si hay código extraído, usarlo
                    if processed_command.extracted_code:
                        task.command = processed_command.extracted_code
                except Exception as e:
                    logger.debug(f"AI processing failed: {e}")
            
            # Predecir éxito con pattern learner
            if self.pattern_learner:
                try:
                    success_prob, pattern_info = await self.pattern_learner.predict_success(task.command)
                    logger.debug(f"📊 Success probability: {success_prob:.2f}")
                except Exception as e:
                    logger.debug(f"Pattern prediction failed: {e}")
            
            # Agregar a embeddings si está disponible
            if self.embedding_store:
                try:
                    await self.embedding_store.add(
                        f"task_{task.id}",
                        task.command,
                        metadata={"task_id": task.id, "timestamp": task.timestamp.isoformat()}
                    )
                except Exception as e:
                    logger.debug(f"Embedding storage failed: {e}")
            
            # Verificar caché si está disponible
            cached_result = None
            if self.command_cache:
                cached_result = await self.command_cache.get_result(task.command)
                if cached_result:
                    logger.debug(f"💾 Using cached result for task {task.id}")
                    result = cached_result
                else:
                    # Ejecutar comando real
                    from .task_executor import TaskExecutor
                    executor = TaskExecutor(timeout=self.config.task_timeout)
                    exec_result = await executor.execute(task.command, task.id)
                    
                    if exec_result.success:
                        result = exec_result.output
                        # Guardar en caché
                        if self.command_cache and result:
                            await self.command_cache.set_result(task.command, result)
                    else:
                        raise Exception(exec_result.error or "Execution failed")
            else:
                # Ejecutar comando real sin caché
                from .task_executor import TaskExecutor
                executor = TaskExecutor(timeout=self.config.task_timeout)
                exec_result = await executor.execute(task.command, task.id)
                
                if exec_result.success:
                    result = exec_result.output
                else:
                    raise Exception(exec_result.error or "Execution failed")
            
            task.status = "completed"
            task.result = result
            success = True
            
            # Resumir resultado con IA si es muy largo
            if self.ai_processor and len(result) > 1000:
                try:
                    summarized = await self.ai_processor.summarize_result(result, max_length=500)
                    task.result = summarized
                except Exception as e:
                    logger.debug(f"Result summarization failed: {e}")
            
            # Registrar en pattern learner
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.pattern_learner:
                try:
                    await self.pattern_learner.record_command(
                        task.command,
                        success=True,
                        execution_time=execution_time,
                        result=result
                    )
                except Exception as e:
                    logger.debug(f"Pattern recording failed: {e}")
            
            logger.info(f"✅ Task completed: {task.id}")
            await self._notify_callbacks(f"task_completed:{task.id}")
            
            # Notificación y métricas
            if self.notifications:
                await self.notifications.notify(
                    "Task Completed",
                    f"Task {task.id[:8]}... completed successfully",
                    level=self.notifications.NotificationLevel.SUCCESS,
                    metadata={"task_id": task.id, "command": task.command[:50]}
                )
            if self.metrics:
                self.metrics.increment("tasks_completed")
                self.metrics.set_gauge("tasks_completed_total", sum(1 for t in self.tasks.values() if t.status == "completed"))
            
            # Rate limiter
            if self.rate_limiter:
                await self.rate_limiter.complete_task()
            
            # Notificar plugins
            if self.plugin_manager:
                await self.plugin_manager.notify_task_completed(task.id, result)
            
            # Publicar evento
            if self.event_bus:
                await self.event_bus.publish(
                    self.event_bus.EventType.TASK_COMPLETED,
                    {"task_id": task.id, "result": result[:200]},
                    source="agent"
                )
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"❌ Task failed: {task.id} - {e}")
            
            # Registrar fallo en pattern learner
            execution_time = (datetime.now() - start_time).total_seconds()
            if self.pattern_learner:
                try:
                    await self.pattern_learner.record_command(
                        task.command,
                        success=False,
                        execution_time=execution_time,
                        result=None
                    )
                except Exception as e2:
                    logger.debug(f"Pattern recording failed: {e2}")
            
            await self._notify_callbacks(f"task_failed:{task.id}")
            
            # Notificación y métricas
            if self.notifications:
                await self.notifications.notify(
                    "Task Failed",
                    f"Task {task.id[:8]}... failed: {str(e)[:100]}",
                    level=self.notifications.NotificationLevel.ERROR,
                    metadata={"task_id": task.id, "error": str(e), "command": task.command[:50]}
                )
            if self.metrics:
                self.metrics.increment("tasks_failed")
                self.metrics.set_gauge("tasks_failed_total", sum(1 for t in self.tasks.values() if t.status == "failed"))
            
            # Rate limiter
            if self.rate_limiter:
                await self.rate_limiter.complete_task()
            
            # Notificar plugins
            if self.plugin_manager:
                await self.plugin_manager.notify_task_failed(task.id, str(e))
            
            # Publicar evento
            if self.event_bus:
                await self.event_bus.publish(
                    self.event_bus.EventType.TASK_FAILED,
                    {"task_id": task.id, "error": str(e)[:200]},
                    source="agent"
                )
            
    async def _save_state(self) -> None:
        """Guardar estado persistente"""
        try:
            from pathlib import Path
            Path(self._state_file).parent.mkdir(parents=True, exist_ok=True)
            
            state = {
                "status": self.status.value,
                "tasks": {
                    task_id: {
                        "id": task.id,
                        "command": task.command,
                        "status": task.status,
                        "timestamp": task.timestamp.isoformat(),
                        "result": task.result,
                        "error": task.error,
                    }
                    for task_id, task in self.tasks.items()
                }
            }
            
            # Usar orjson si está disponible (más rápido)
            if hasattr(json, 'dumps'):
                # orjson
                with open(self._state_file, 'wb') as f:
                    f.write(json.dumps(state, option=json.OPT_INDENT_2))
            else:
                # json estándar
                with open(self._state_file, 'w') as f:
                    json.dump(state, f, indent=2)
                
            logger.info(f"💾 State saved to {self._state_file}")
            
        except Exception as e:
            logger.error(f"Error saving state: {e}")
            
    async def _load_state(self) -> None:
        """Cargar estado persistente"""
        try:
            from pathlib import Path
            
            if not Path(self._state_file).exists():
                return
                
            # Usar orjson si está disponible (más rápido)
            if hasattr(json, 'loads'):
                # orjson
                with open(self._state_file, 'rb') as f:
                    state = json.loads(f.read())
            else:
                # json estándar
                with open(self._state_file, 'r') as f:
                    state = json.load(f)
                
            # Restaurar tareas
            for task_id, task_data in state.get("tasks", {}).items():
                task = Task(
                    id=task_data["id"],
                    command=task_data["command"],
                    timestamp=datetime.fromisoformat(task_data["timestamp"]),
                    status=task_data["status"],
                    result=task_data.get("result"),
                    error=task_data.get("error"),
                )
                self.tasks[task_id] = task
                
            logger.info(f"📂 State loaded from {self._state_file}")
            
        except Exception as e:
            logger.error(f"Error loading state: {e}")

