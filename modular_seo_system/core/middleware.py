"""
Middleware Pipeline System for Modular SEO System
Provides chainable middleware processing for data transformation and validation
"""

import asyncio
import functools
import inspect
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from typing_extensions import Protocol

# Configure logging
logger = logging.getLogger(__name__)

# Type variables for middleware
T = TypeVar("T")
R = TypeVar("R")


class MiddlewarePriority(Enum):
    """Middleware priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class MiddlewareType(Enum):
    """Types of middleware."""

    PRE_PROCESSING = "pre_processing"
    PROCESSING = "processing"
    POST_PROCESSING = "post_processing"
    VALIDATION = "validation"
    TRANSFORMATION = "transformation"
    LOGGING = "logging"
    MONITORING = "monitoring"
    ERROR_HANDLING = "error_handling"


@dataclass
class MiddlewareContext:
    """Context for middleware execution."""

    data: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    execution_path: List[str] = field(default_factory=list)
    errors: List[Exception] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

    def add_execution_step(self, step_name: str):
        """Add an execution step to the path."""
        self.execution_path.append(step_name)

    def add_error(self, error: Exception):
        """Add an error to the context."""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Add a warning to the context."""
        self.warnings.append(warning)

    def add_metric(self, name: str, value: float):
        """Add a performance metric."""
        self.performance_metrics[name] = value


class Middleware(Protocol[T, R]):
    """Protocol for middleware functions."""

    name: str
    priority: MiddlewarePriority
    middleware_type: MiddlewareType

    async def process(self, data: T, context: MiddlewareContext) -> R:
        """Process data through this middleware."""
        ...


class BaseMiddleware(ABC):
    """Base class for middleware implementations."""

    def __init__(
        self,
        name: str,
        priority: MiddlewarePriority = MiddlewarePriority.NORMAL,
        middleware_type: MiddlewareType = MiddlewareType.PROCESSING,
    ):
        self.name = name
        self.priority = priority
        self.middleware_type = middleware_type
        self.enabled = True
        self.execution_count = 0
        self.total_execution_time = 0.0
        self.error_count = 0
        self.last_execution = None

    @abstractmethod
    async def process(self, data: T, context: MiddlewareContext) -> R:
        """Process data through this middleware."""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Get middleware statistics."""
        return {
            "name": self.name,
            "priority": self.priority.value,
            "type": self.middleware_type.value,
            "enabled": self.enabled,
            "execution_count": self.execution_count,
            "total_execution_time": self.total_execution_time,
            "avg_execution_time": self.total_execution_time / self.execution_count if self.execution_count > 0 else 0,
            "error_count": self.error_count,
            "last_execution": self.last_execution,
        }

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, priority={self.priority}, type={self.middleware_type})"


class MiddlewarePipeline:
    """Pipeline for executing middleware in sequence."""

    def __init__(self, name: str = "default"):
        self.name = name
        self.middleware: List[BaseMiddleware] = []
        self._lock = asyncio.Lock()
        self.execution_stats: Dict[str, Dict[str, Any]] = {}

    def add_middleware(self, middleware: BaseMiddleware) -> "MiddlewarePipeline":
        """Add middleware to the pipeline."""
        self.middleware.append(middleware)
        # Sort by priority (highest first)
        self.middleware.sort(key=lambda m: m.priority.value, reverse=True)
        return self

    def add_middleware_chain(self, *middleware_list: BaseMiddleware) -> "MiddlewarePipeline":
        """Add multiple middleware to the pipeline."""
        for middleware in middleware_list:
            self.add_middleware(middleware)
        return self

    def remove_middleware(self, middleware_name: str) -> bool:
        """Remove middleware from the pipeline."""
        for i, middleware in enumerate(self.middleware):
            if middleware.name == middleware_name:
                del self.middleware[i]
                return True
        return False

    def get_middleware(self, middleware_name: str) -> Optional[BaseMiddleware]:
        """Get middleware by name."""
        for middleware in self.middleware:
            if middleware.name == middleware_name:
                return middleware
        return None

    async def execute(self, data: T, metadata: Optional[Dict[str, Any]] = None) -> R:
        """Execute the middleware pipeline."""
        async with self._lock:
            context = MiddlewareContext(data=data, metadata=metadata or {})

            try:
                result = data

                # Execute middleware in order
                for middleware in self.middleware:
                    if not middleware.enabled:
                        continue

                    start_time = time.time()
                    context.add_execution_step(middleware.name)

                    try:
                        # Execute middleware
                        result = await middleware.process(result, context)

                        # Update middleware stats
                        execution_time = time.time() - start_time
                        middleware.execution_count += 1
                        middleware.total_execution_time += execution_time
                        middleware.last_execution = time.time()

                        # Add to context metrics
                        context.add_metric(f"{middleware.name}_execution_time", execution_time)

                        logger.debug(f"Middleware {middleware.name} executed in {execution_time:.4f}s")

                    except Exception as e:
                        # Update error stats
                        middleware.error_count += 1
                        context.add_error(e)
                        logger.error(f"Middleware {middleware.name} failed: {e}")

                        # Decide whether to continue based on middleware type
                        if middleware.middleware_type == MiddlewareType.CRITICAL:
                            raise
                        elif middleware.middleware_type == MiddlewareType.ERROR_HANDLING:
                            # Error handling middleware should continue
                            continue
                        else:
                            # For other types, log and continue
                            logger.warning(f"Continuing pipeline execution after middleware {middleware.name} error")
                            continue

                return result

            except Exception as e:
                logger.error(f"Pipeline execution failed: {e}")
                context.add_error(e)
                raise
            finally:
                # Store execution stats
                self.execution_stats[context.start_time] = {
                    "execution_path": context.execution_path,
                    "errors": [str(e) for e in context.errors],
                    "warnings": context.warnings,
                    "performance_metrics": context.performance_metrics,
                    "total_time": time.time() - context.start_time,
                }

    def get_pipeline_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            "name": self.name,
            "middleware_count": len(self.middleware),
            "enabled_middleware": [m.name for m in self.middleware if m.enabled],
            "disabled_middleware": [m.name for m in self.middleware if not m.enabled],
            "execution_stats": self.execution_stats,
            "middleware_stats": {m.name: m.get_stats() for m in self.middleware},
        }

    def clear_stats(self):
        """Clear execution statistics."""
        self.execution_stats.clear()
        for middleware in self.middleware:
            middleware.execution_count = 0
            middleware.total_execution_time = 0.0
            middleware.error_count = 0
            middleware.last_execution = None


class MiddlewareRegistry:
    """Registry for managing middleware across the system."""

    def __init__(self):
        self._middleware: Dict[str, BaseMiddleware] = {}
        self._pipelines: Dict[str, MiddlewarePipeline] = {}
        self._lock = asyncio.Lock()

    def register_middleware(self, middleware: BaseMiddleware) -> bool:
        """Register middleware in the registry."""
        async with self._lock:
            if middleware.name in self._middleware:
                logger.warning(f"Middleware {middleware.name} already registered")
                return False

            self._middleware[middleware.name] = middleware
            logger.info(f"Registered middleware: {middleware.name}")
            return True

    def unregister_middleware(self, middleware_name: str) -> bool:
        """Unregister middleware from the registry."""
        async with self._lock:
            if middleware_name not in self._middleware:
                return False

            # Check if middleware is used in any pipelines
            for pipeline in self._pipelines.values():
                if pipeline.get_middleware(middleware_name):
                    logger.warning(f"Cannot unregister middleware {middleware_name}, used in pipeline {pipeline.name}")
                    return False

            del self._middleware[middleware_name]
            logger.info(f"Unregistered middleware: {middleware_name}")
            return True

    def get_middleware(self, middleware_name: str) -> Optional[BaseMiddleware]:
        """Get middleware by name."""
        return self._middleware.get(middleware_name)

    def list_middleware(self) -> List[str]:
        """List all registered middleware names."""
        return list(self._middleware.keys())

    def create_pipeline(self, name: str, *middleware_names: str) -> Optional[MiddlewarePipeline]:
        """Create a pipeline with specified middleware."""
        pipeline = MiddlewarePipeline(name)

        for middleware_name in middleware_names:
            middleware = self._middleware.get(middleware_name)
            if middleware:
                pipeline.add_middleware(middleware)
            else:
                logger.error(f"Middleware {middleware_name} not found for pipeline {name}")
                return None

        self._pipelines[name] = pipeline
        logger.info(f"Created pipeline: {name}")
        return pipeline

    def get_pipeline(self, pipeline_name: str) -> Optional[MiddlewarePipeline]:
        """Get pipeline by name."""
        return self._pipelines.get(pipeline_name)

    def list_pipelines(self) -> List[str]:
        """List all pipeline names."""
        return list(self._pipelines.keys())

    def remove_pipeline(self, pipeline_name: str) -> bool:
        """Remove a pipeline."""
        if pipeline_name in self._pipelines:
            del self._pipelines[pipeline_name]
            logger.info(f"Removed pipeline: {pipeline_name}")
            return True
        return False


# Common middleware implementations
class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging data processing."""

    def __init__(self, name: str = "logging", log_level: str = "INFO"):
        super().__init__(name, MiddlewarePriority.LOW, MiddlewareType.LOGGING)
        self.log_level = log_level.upper()

    async def process(self, data: T, context: MiddlewareContext) -> T:
        """Log data processing."""
        logger.log(getattr(logging, self.log_level), f"Processing data through {self.name}: {type(data).__name__}")
        return data


class ValidationMiddleware(BaseMiddleware):
    """Middleware for data validation."""

    def __init__(self, name: str = "validation", validator: Optional[Callable] = None):
        super().__init__(name, MiddlewarePriority.HIGH, MiddlewareType.VALIDATION)
        self.validator = validator

    async def process(self, data: T, context: MiddlewareContext) -> T:
        """Validate data."""
        if self.validator:
            if not self.validator(data):
                raise ValueError(f"Data validation failed in {self.name}")
        return data


class TransformationMiddleware(BaseMiddleware):
    """Middleware for data transformation."""

    def __init__(self, name: str = "transformation", transformer: Optional[Callable] = None):
        super().__init__(name, MiddlewarePriority.NORMAL, MiddlewareType.TRANSFORMATION)
        self.transformer = transformer

    async def process(self, data: T, context: MiddlewareContext) -> R:
        """Transform data."""
        if self.transformer:
            if asyncio.iscoroutinefunction(self.transformer):
                return await self.transformer(data)
            else:
                return self.transformer(data)
        return data


class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware for error handling."""

    def __init__(self, name: str = "error_handling", error_handler: Optional[Callable] = None):
        super().__init__(name, MiddlewarePriority.CRITICAL, MiddlewareType.ERROR_HANDLING)
        self.error_handler = error_handler

    async def process(self, data: T, context: MiddlewareContext) -> T:
        """Handle errors in the context."""
        if context.errors and self.error_handler:
            for error in context.errors:
                if asyncio.iscoroutinefunction(self.error_handler):
                    await self.error_handler(error, context)
                else:
                    self.error_handler(error, context)
        return data


class MonitoringMiddleware(BaseMiddleware):
    """Middleware for performance monitoring."""

    def __init__(self, name: str = "monitoring"):
        super().__init__(name, MiddlewarePriority.LOW, MiddlewareType.MONITORING)

    async def process(self, data: T, context: MiddlewareContext) -> T:
        """Monitor performance metrics."""
        # Add timing information
        if context.execution_path:
            step_name = context.execution_path[-1]
            if step_name in context.performance_metrics:
                logger.debug(f"Step {step_name} took {context.performance_metrics[step_name]:.4f}s")

        return data


# Global middleware registry
middleware_registry = MiddlewareRegistry()


# Convenience functions
def middleware(
    priority: MiddlewarePriority = MiddlewarePriority.NORMAL,
    middleware_type: MiddlewareType = MiddlewareType.PROCESSING,
):
    """Decorator for creating middleware from functions."""

    def decorator(func: Callable) -> BaseMiddleware:
        class FunctionMiddleware(BaseMiddleware):
            async def process(self, data: T, context: MiddlewareContext) -> R:
                if asyncio.iscoroutinefunction(func):
                    return await func(data, context)
                else:
                    return func(data, context)

        return FunctionMiddleware(func.__name__, priority, middleware_type)

    return decorator


def create_pipeline(name: str, *middleware_names: str) -> Optional[MiddlewarePipeline]:
    """Create a pipeline using the global registry."""
    return middleware_registry.create_pipeline(name, *middleware_names)


def register_middleware(middleware: BaseMiddleware) -> bool:
    """Register middleware in the global registry."""
    return middleware_registry.register_middleware(middleware)
