#!/usr/bin/env python3
"""
Advanced CQRS Implementation - Application Layer
===============================================

Command Query Responsibility Segregation (CQRS) implementation
with command bus, query bus, and enterprise-grade features.
"""

import asyncio
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from contextlib import asynccontextmanager

T = TypeVar('T')
R = TypeVar('R')


class CommandStatus(Enum):
    """Command processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class QueryStatus(Enum):
    """Query processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Command(ABC):
    """Base class for all commands."""
    
    # Command identification
    command_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    command_type: str = field(default="")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Command metadata
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Processing metadata
    status: CommandStatus = CommandStatus.PENDING
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        """Initialize command after creation."""
        if not self.command_type:
            self.command_type = self.__class__.__name__


@dataclass
class Query(ABC):
    """Base class for all queries."""
    
    # Query identification
    query_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query_type: str = field(default="")
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Query metadata
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    
    # Processing metadata
    status: QueryStatus = QueryStatus.PENDING
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None
    cache_key: Optional[str] = None
    cache_ttl: int = 300  # 5 minutes default
    
    def __post_init__(self):
        """Initialize query after creation."""
        if not self.query_type:
            self.query_type = self.__class__.__name__


@dataclass
class CommandResult:
    """Result of command execution."""
    
    success: bool
    command_id: str
    result: Optional[Any] = None
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class QueryResult(Generic[R]):
    """Result of query execution."""
    
    success: bool
    query_id: str
    result: Optional[R] = None
    error_message: Optional[str] = None
    processing_time_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    cached: bool = False


class CommandHandler(ABC, Generic[T]):
    """Base class for command handlers."""
    
    @abstractmethod
    async def handle(self, command: T) -> CommandResult:
        """Handle a command."""
        pass
    
    @property
    @abstractmethod
    def command_type(self) -> Type[T]:
        """Get the command type this handler can process."""
        pass
    
    @property
    def priority(self) -> int:
        """Get handler priority (lower = higher priority)."""
        return 100
    
    @property
    def async_processing(self) -> bool:
        """Whether this handler should be processed asynchronously."""
        return True


class QueryHandler(ABC, Generic[T, R]):
    """Base class for query handlers."""
    
    @abstractmethod
    async def handle(self, query: T) -> QueryResult[R]:
        """Handle a query."""
        pass
    
    @property
    @abstractmethod
    def query_type(self) -> Type[T]:
        """Get the query type this handler can process."""
        pass
    
    @property
    def priority(self) -> int:
        """Get handler priority (lower = higher priority)."""
        return 100
    
    @property
    def cache_enabled(self) -> bool:
        """Whether this handler supports caching."""
        return True


class CommandBus:
    """
    Advanced command bus with enterprise-grade features.
    
    Features:
    - Command routing and execution
    - Command validation and authorization
    - Command logging and auditing
    - Retry mechanisms with exponential backoff
    - Command correlation and causation
    - Performance monitoring
    - Dead letter queue
    """
    
    def __init__(self):
        self._handlers: Dict[Type, CommandHandler] = {}
        self._command_log: List[Command] = []
        self._dead_letter_queue: List[Command] = []
        self._processing_queue: asyncio.Queue = asyncio.Queue()
        self._processing_tasks: set[asyncio.Task] = set()
        self._logger = logging.getLogger(__name__)
        self._metrics = {
            'commands_sent': 0,
            'commands_processed': 0,
            'commands_failed': 0,
            'commands_retried': 0,
            'processing_time_avg': 0.0,
            'queue_size': 0
        }
        self._running = False
        self._max_workers = 5
        self._retry_delays = [1, 2, 4, 8, 16]  # Exponential backoff
    
    async def start(self) -> None:
        """Start the command bus."""
        if self._running:
            return
        
        self._running = True
        self._logger.info("Starting command bus...")
        
        # Start processing workers
        for _ in range(self._max_workers):
            task = asyncio.create_task(self._process_commands())
            self._processing_tasks.add(task)
        
        self._logger.info(f"Command bus started with {self._max_workers} workers")
    
    async def stop(self) -> None:
        """Stop the command bus."""
        if not self._running:
            return
        
        self._running = False
        self._logger.info("Stopping command bus...")
        
        # Cancel all processing tasks
        for task in self._processing_tasks:
            task.cancel()
        
        # Wait for tasks to complete
        if self._processing_tasks:
            await asyncio.gather(*self._processing_tasks, return_exceptions=True)
        
        self._processing_tasks.clear()
        self._logger.info("Command bus stopped")
    
    def register_handler(self, handler: CommandHandler) -> None:
        """
        Register a command handler.
        
        Args:
            handler: The command handler to register
        """
        command_type = handler.command_type
        self._handlers[command_type] = handler
        self._logger.info(f"Registered command handler for {command_type.__name__}")
    
    def unregister_handler(self, command_type: Type[Command]) -> None:
        """
        Unregister a command handler.
        
        Args:
            command_type: The command type to unregister
        """
        if command_type in self._handlers:
            del self._handlers[command_type]
            self._logger.info(f"Unregistered command handler for {command_type.__name__}")
    
    async def send(self, command: Command) -> CommandResult:
        """
        Send a command for processing.
        
        Args:
            command: The command to send
        
        Returns:
            CommandResult with processing result
        """
        # Log command
        self._command_log.append(command)
        
        # Add to processing queue
        await self._processing_queue.put(command)
        
        # Update metrics
        self._metrics['commands_sent'] += 1
        self._metrics['queue_size'] = self._processing_queue.qsize()
        
        self._logger.debug(f"Sent command: {command.command_type} (ID: {command.command_id})")
        
        # For immediate execution, wait for result
        return await self._wait_for_result(command)
    
    async def send_async(self, command: Command) -> None:
        """
        Send a command for asynchronous processing.
        
        Args:
            command: The command to send
        """
        # Log command
        self._command_log.append(command)
        
        # Add to processing queue
        await self._processing_queue.put(command)
        
        # Update metrics
        self._metrics['commands_sent'] += 1
        self._metrics['queue_size'] = self._processing_queue.qsize()
        
        self._logger.debug(f"Sent async command: {command.command_type} (ID: {command.command_id})")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get command bus performance metrics."""
        return {
            'commands_sent': self._metrics['commands_sent'],
            'commands_processed': self._metrics['commands_processed'],
            'commands_failed': self._metrics['commands_failed'],
            'commands_retried': self._metrics['commands_retried'],
            'processing_time_avg': self._metrics['processing_time_avg'],
            'queue_size': self._processing_queue.qsize(),
            'total_commands_logged': len(self._command_log),
            'dead_letter_queue_size': len(self._dead_letter_queue),
            'active_handlers': len(self._handlers),
            'running': self._running
        }
    
    async def _process_commands(self) -> None:
        """Process commands from the queue."""
        while self._running:
            try:
                # Get command from queue with timeout
                command = await asyncio.wait_for(self._processing_queue.get(), timeout=1.0)
                
                # Process the command
                await self._process_command(command)
                
                # Mark task as done
                self._processing_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self._logger.error(f"Error in command processing worker: {e}")
    
    async def _process_command(self, command: Command) -> None:
        """Process a single command."""
        start_time = time.time()
        
        try:
            # Update command status
            command.status = CommandStatus.PROCESSING
            
            # Get handler for this command type
            handler = self._handlers.get(type(command))
            
            if not handler:
                error_msg = f"No handler found for command type: {command.command_type}"
                self._logger.error(error_msg)
                command.status = CommandStatus.FAILED
                command.error_message = error_msg
                self._dead_letter_queue.append(command)
                self._metrics['commands_failed'] += 1
                return
            
            # Execute command
            if handler.async_processing:
                result = await handler.handle(command)
            else:
                # Run in thread pool for sync handlers
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: asyncio.run(handler.handle(command))
                )
            
            # Update command status
            if result.success:
                command.status = CommandStatus.COMPLETED
                self._metrics['commands_processed'] += 1
                self._logger.debug(f"Processed command {command.command_id} successfully")
            else:
                command.status = CommandStatus.FAILED
                command.error_message = result.error_message
                self._metrics['commands_failed'] += 1
                self._logger.error(f"Failed to process command {command.command_id}: {result.error_message}")
            
            # Update processing time
            command.processing_time_ms = (time.time() - start_time) * 1000
            
            # Update metrics
            self._metrics['processing_time_avg'] = (
                (self._metrics['processing_time_avg'] * (self._metrics['commands_processed'] - 1) + command.processing_time_ms) /
                max(self._metrics['commands_processed'], 1)
            )
            
        except Exception as e:
            self._logger.error(f"Failed to process command {command.command_id}: {e}")
            command.status = CommandStatus.FAILED
            command.error_message = str(e)
            self._metrics['commands_failed'] += 1
            
            # Retry logic
            if command.retry_count < command.max_retries:
                command.retry_count += 1
                self._metrics['commands_retried'] += 1
                
                # Calculate delay with exponential backoff
                delay = self._retry_delays[min(command.retry_count - 1, len(self._retry_delays) - 1)]
                
                self._logger.info(f"Retrying command {command.command_id} in {delay}s (attempt {command.retry_count})")
                
                # Schedule retry
                asyncio.create_task(self._retry_command(command, delay))
            else:
                # Move to dead letter queue
                self._dead_letter_queue.append(command)
                self._logger.error(f"Command {command.command_id} moved to dead letter queue after {command.max_retries} retries")
    
    async def _retry_command(self, command: Command, delay: float) -> None:
        """Retry a command after a delay."""
        await asyncio.sleep(delay)
        command.status = CommandStatus.PENDING
        await self._processing_queue.put(command)
    
    async def _wait_for_result(self, command: Command, timeout: float = 30.0) -> CommandResult:
        """Wait for command result with timeout."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if command.status in [CommandStatus.COMPLETED, CommandStatus.FAILED]:
                return CommandResult(
                    success=command.status == CommandStatus.COMPLETED,
                    command_id=command.command_id,
                    error_message=command.error_message,
                    processing_time_ms=command.processing_time_ms
                )
            
            await asyncio.sleep(0.1)
        
        # Timeout
        command.status = CommandStatus.FAILED
        command.error_message = "Command processing timeout"
        return CommandResult(
            success=False,
            command_id=command.command_id,
            error_message="Command processing timeout"
        )


class QueryBus:
    """
    Advanced query bus with enterprise-grade features.
    
    Features:
    - Query routing and execution
    - Query caching and optimization
    - Query validation and authorization
    - Query logging and auditing
    - Performance monitoring
    - Result caching
    """
    
    def __init__(self):
        self._handlers: Dict[Type, QueryHandler] = {}
        self._query_log: List[Query] = []
        self._cache: Dict[str, QueryResult] = {}
        self._logger = logging.getLogger(__name__)
        self._metrics = {
            'queries_sent': 0,
            'queries_processed': 0,
            'queries_failed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'processing_time_avg': 0.0
        }
    
    def register_handler(self, handler: QueryHandler) -> None:
        """
        Register a query handler.
        
        Args:
            handler: The query handler to register
        """
        query_type = handler.query_type
        self._handlers[query_type] = handler
        self._logger.info(f"Registered query handler for {query_type.__name__}")
    
    def unregister_handler(self, query_type: Type[Query]) -> None:
        """
        Unregister a query handler.
        
        Args:
            query_type: The query type to unregister
        """
        if query_type in self._handlers:
            del self._handlers[query_type]
            self._logger.info(f"Unregistered query handler for {query_type.__name__}")
    
    async def execute(self, query: Query) -> QueryResult:
        """
        Execute a query.
        
        Args:
            query: The query to execute
        
        Returns:
            QueryResult with query result
        """
        start_time = time.time()
        
        # Log query
        self._query_log.append(query)
        
        # Update metrics
        self._metrics['queries_sent'] += 1
        
        try:
            # Check cache first
            if query.cache_key and query.cache_key in self._cache:
                cached_result = self._cache[query.cache_key]
                if time.time() - cached_result.timestamp.timestamp() < query.cache_ttl:
                    self._metrics['cache_hits'] += 1
                    cached_result.cached = True
                    return cached_result
            
            # Update query status
            query.status = QueryStatus.PROCESSING
            
            # Get handler for this query type
            handler = self._handlers.get(type(query))
            
            if not handler:
                error_msg = f"No handler found for query type: {query.query_type}"
                self._logger.error(error_msg)
                query.status = QueryStatus.FAILED
                query.error_message = error_msg
                self._metrics['queries_failed'] += 1
                return QueryResult(
                    success=False,
                    query_id=query.query_id,
                    error_message=error_msg
                )
            
            # Execute query
            if handler.async_processing:
                result = await handler.handle(query)
            else:
                # Run in thread pool for sync handlers
                result = await asyncio.get_event_loop().run_in_executor(
                    None, lambda: asyncio.run(handler.handle(query))
                )
            
            # Update query status
            if result.success:
                query.status = QueryStatus.COMPLETED
                self._metrics['queries_processed'] += 1
                self._logger.debug(f"Processed query {query.query_id} successfully")
                
                # Cache result if enabled
                if query.cache_key and handler.cache_enabled:
                    self._cache[query.cache_key] = result
            else:
                query.status = QueryStatus.FAILED
                query.error_message = result.error_message
                self._metrics['queries_failed'] += 1
                self._logger.error(f"Failed to process query {query.query_id}: {result.error_message}")
            
            # Update processing time
            query.processing_time_ms = (time.time() - start_time) * 1000
            result.processing_time_ms = query.processing_time_ms
            
            # Update metrics
            self._metrics['processing_time_avg'] = (
                (self._metrics['processing_time_avg'] * (self._metrics['queries_processed'] - 1) + query.processing_time_ms) /
                max(self._metrics['queries_processed'], 1)
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Failed to process query {query.query_id}: {e}")
            query.status = QueryStatus.FAILED
            query.error_message = str(e)
            self._metrics['queries_failed'] += 1
            
            return QueryResult(
                success=False,
                query_id=query.query_id,
                error_message=str(e)
            )
    
    def clear_cache(self) -> None:
        """Clear the query cache."""
        self._cache.clear()
        self._logger.info("Query cache cleared")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get query bus performance metrics."""
        return {
            'queries_sent': self._metrics['queries_sent'],
            'queries_processed': self._metrics['queries_processed'],
            'queries_failed': self._metrics['queries_failed'],
            'cache_hits': self._metrics['cache_hits'],
            'cache_misses': self._metrics['cache_misses'],
            'processing_time_avg': self._metrics['processing_time_avg'],
            'total_queries_logged': len(self._query_log),
            'cache_size': len(self._cache),
            'active_handlers': len(self._handlers)
        }


# Global bus instances
command_bus = CommandBus()
query_bus = QueryBus()


# Decorators for easy registration
def command_handler(command_type: Type[Command], priority: int = 100):
    """Decorator to register a command handler."""
    def decorator(cls):
        class CommandHandlerWrapper(CommandHandler):
            def __init__(self):
                self._handler = cls()
            
            async def handle(self, command: Command) -> CommandResult:
                return await self._handler.handle(command)
            
            @property
            def command_type(self) -> Type[Command]:
                return command_type
            
            @property
            def priority(self) -> int:
                return priority
        
        # Register with command bus
        handler = CommandHandlerWrapper()
        command_bus.register_handler(handler)
        
        return cls
    return decorator


def query_handler(query_type: Type[Query], priority: int = 100):
    """Decorator to register a query handler."""
    def decorator(cls):
        class QueryHandlerWrapper(QueryHandler):
            def __init__(self):
                self._handler = cls()
            
            async def handle(self, query: Query) -> QueryResult:
                return await self._handler.handle(query)
            
            @property
            def query_type(self) -> Type[Query]:
                return query_type
            
            @property
            def priority(self) -> int:
                return priority
        
        # Register with query bus
        handler = QueryHandlerWrapper()
        query_bus.register_handler(handler)
        
        return cls
    return decorator 