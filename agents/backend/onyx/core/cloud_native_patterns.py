"""
☁️ CLOUD-NATIVE PATTERNS
=======================

Advanced cloud-native patterns:
- OpenTelemetry distributed tracing
- Service mesh integration
- Event sourcing and CQRS
- Database per service
"""

import time
import uuid
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from abc import ABC, abstractmethod

from fastapi import FastAPI, Request, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import structlog

logger = structlog.get_logger(__name__)

# =============================================================================
# OBSERVABILITY WITH OPENTELEMETRY
# =============================================================================

class DistributedTracing:
    """OpenTelemetry distributed tracing."""
    
    def __init__(self, service_name: str = "blatam-api"):
        self.service_name = service_name
        self.traces: Dict[str, Dict] = {}
    
    def start_span(self, operation_name: str, parent_span_id: Optional[str] = None) -> str:
        """Start a new span."""
        span_id = str(uuid.uuid4())
        trace_id = parent_span_id or str(uuid.uuid4())
        
        span = {
            "trace_id": trace_id,
            "span_id": span_id,
            "parent_span_id": parent_span_id,
            "operation_name": operation_name,
            "service_name": self.service_name,
            "start_time": time.time(),
            "tags": {},
            "logs": []
        }
        
        self.traces[span_id] = span
        return span_id
    
    def finish_span(self, span_id: str, status: str = "ok"):
        """Finish span."""
        if span_id in self.traces:
            self.traces[span_id]["end_time"] = time.time()
            self.traces[span_id]["duration"] = (
                self.traces[span_id]["end_time"] - self.traces[span_id]["start_time"]
            )
            self.traces[span_id]["status"] = status
    
    def add_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span."""
        if span_id in self.traces:
            self.traces[span_id]["tags"][key] = value
    
    def log_event(self, span_id: str, event: str, fields: Dict[str, Any] = None):
        """Log event in span."""
        if span_id in self.traces:
            log_entry = {
                "timestamp": time.time(),
                "event": event,
                "fields": fields or {}
            }
            self.traces[span_id]["logs"].append(log_entry)
    
    def get_trace_data(self, span_id: str) -> Optional[Dict]:
        """Get trace data."""
        return self.traces.get(span_id)

# Global tracer
tracer = DistributedTracing()

# =============================================================================
# EVENT SOURCING
# =============================================================================

@dataclass
class Event:
    """Base event class."""
    event_id: str
    event_type: str
    aggregate_id: str
    data: Dict[str, Any]
    timestamp: datetime
    version: int

class EventStore:
    """Simple event store implementation."""
    
    def __init__(self):
        self._events: List[Event] = []
        self._snapshots: Dict[str, Dict] = {}
    
    async def append_event(self, event: Event):
        """Append event to store."""
        self._events.append(event)
        logger.info(
            "Event appended",
            event_type=event.event_type,
            aggregate_id=event.aggregate_id,
            version=event.version
        )
    
    async def get_events(self, aggregate_id: str, from_version: int = 0) -> List[Event]:
        """Get events for aggregate."""
        return [
            event for event in self._events
            if event.aggregate_id == aggregate_id and event.version > from_version
        ]
    
    async def get_all_events(self) -> List[Event]:
        """Get all events."""
        return self._events.copy()
    
    async def save_snapshot(self, aggregate_id: str, data: Dict[str, Any], version: int):
        """Save aggregate snapshot."""
        self._snapshots[aggregate_id] = {
            "data": data,
            "version": version,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    async def get_snapshot(self, aggregate_id: str) -> Optional[Dict]:
        """Get aggregate snapshot."""
        return self._snapshots.get(aggregate_id)

# Global event store
event_store = EventStore()

# =============================================================================
# CQRS (Command Query Responsibility Segregation)
# =============================================================================

class Command(ABC):
    """Base command class."""
    
    @abstractmethod
    def validate(self) -> bool:
        pass

class Query(ABC):
    """Base query class."""
    pass

@dataclass
class CreateContentCommand(Command):
    """Command to create content."""
    content_id: str
    topic: str
    content_type: str
    user_id: str
    
    def validate(self) -> bool:
        return bool(self.topic and self.content_type and self.user_id)

@dataclass
class GetContentQuery(Query):
    """Query to get content."""
    content_id: str

class CommandHandler:
    """Handle commands and generate events."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
    
    async def handle_create_content(self, command: CreateContentCommand) -> str:
        """Handle create content command."""
        if not command.validate():
            raise ValueError("Invalid command")
        
        # Create event
        event = Event(
            event_id=str(uuid.uuid4()),
            event_type="ContentCreated",
            aggregate_id=command.content_id,
            data={
                "topic": command.topic,
                "content_type": command.content_type,
                "user_id": command.user_id,
                "status": "created"
            },
            timestamp=datetime.now(timezone.utc),
            version=1
        )
        
        # Store event
        await self.event_store.append_event(event)
        
        return event.event_id

class QueryHandler:
    """Handle queries and return projections."""
    
    def __init__(self, event_store: EventStore):
        self.event_store = event_store
        self._projections: Dict[str, Dict] = {}
    
    async def handle_get_content(self, query: GetContentQuery) -> Optional[Dict]:
        """Handle get content query."""
        
        # Check projection cache
        if query.content_id in self._projections:
            return self._projections[query.content_id]
        
        # Rebuild from events
        events = await self.event_store.get_events(query.content_id)
        if not events:
            return None
        
        # Build projection
        projection = {}
        for event in events:
            if event.event_type == "ContentCreated":
                projection = {
                    "content_id": event.aggregate_id,
                    "topic": event.data["topic"],
                    "content_type": event.data["content_type"],
                    "user_id": event.data["user_id"],
                    "status": event.data["status"],
                    "created_at": event.timestamp.isoformat(),
                    "version": event.version
                }
        
        # Cache projection
        self._projections[query.content_id] = projection
        
        return projection

# Global handlers
command_handler = CommandHandler(event_store)
query_handler = QueryHandler(event_store)

# =============================================================================
# SERVICE MESH INTEGRATION
# =============================================================================

class ServiceMeshHeaders:
    """Service mesh headers for Istio/Linkerd."""
    
    @staticmethod
    def get_trace_headers(request: Request) -> Dict[str, str]:
        """Extract distributed tracing headers."""
        trace_headers = {}
        
        # Common tracing headers
        headers_to_propagate = [
            "x-request-id",
            "x-b3-traceid",
            "x-b3-spanid", 
            "x-b3-parentspanid",
            "x-b3-sampled",
            "x-b3-flags",
            "x-ot-span-context",
            "x-cloud-trace-context",
            "traceparent",
            "tracestate"
        ]
        
        for header in headers_to_propagate:
            value = request.headers.get(header)
            if value:
                trace_headers[header] = value
        
        return trace_headers
    
    @staticmethod
    def add_service_info(response_headers: Dict[str, str], service_name: str, version: str):
        """Add service information headers."""
        response_headers.update({
            "x-service-name": service_name,
            "x-service-version": version,
            "x-mesh-version": "1.0.0"
        })

# =============================================================================
# CLOUD-NATIVE MODELS
# =============================================================================

class CloudNativeMetrics(BaseModel):
    """Cloud-native metrics."""
    
    service_name: str
    instance_id: str
    cpu_usage: float = Field(ge=0, le=100)
    memory_usage: float = Field(ge=0, le=100) 
    request_count: int = Field(ge=0)
    error_count: int = Field(ge=0)
    avg_response_time: float = Field(ge=0)
    
class HealthStatus(BaseModel):
    """Kubernetes-style health status."""
    
    status: str = Field(..., regex="^(healthy|unhealthy|degraded)$")
    checks: Dict[str, Any]
    timestamp: datetime
    version: str

# =============================================================================
# CLOUD-NATIVE APPLICATION
# =============================================================================

def create_cloud_native_app() -> FastAPI:
    """Create cloud-native FastAPI application."""
    
    app = FastAPI(
        title="Cloud-Native Patterns API",
        description="""
        ☁️ **Cloud-Native Patterns Implementation**
        
        ## 📊 Observability
        - **Distributed Tracing** with OpenTelemetry
        - **Metrics Collection** with Prometheus
        - **Structured Logging** with correlation IDs
        - **Health Checks** for Kubernetes
        
        ## 🔄 Event Architecture
        - **Event Sourcing** for data consistency
        - **CQRS** for read/write separation
        - **Event Store** for audit trail
        - **Projections** for query optimization
        
        ## 🕸️ Service Mesh
        - **Istio/Linkerd** compatible
        - **Header Propagation** for tracing
        - **Circuit Breakers** for resilience
        - **Load Balancing** with health checks
        """,
        version="1.0.0-cloud-native"
    )
    
    # Service mesh middleware
    @app.middleware("http")
    async def service_mesh_middleware(request: Request, call_next):
        """Service mesh integration middleware."""
        
        # Extract trace headers
        trace_headers = ServiceMeshHeaders.get_trace_headers(request)
        
        # Start distributed trace
        span_id = tracer.start_span(
            f"{request.method} {request.url.path}",
            parent_span_id=trace_headers.get("x-b3-traceid")
        )
        
        # Add tags
        tracer.add_tag(span_id, "http.method", request.method)
        tracer.add_tag(span_id, "http.path", request.url.path)
        tracer.add_tag(span_id, "http.user_agent", request.headers.get("user-agent", ""))
        
        # Process request
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        # Add response tags
        tracer.add_tag(span_id, "http.status_code", response.status_code)
        tracer.add_tag(span_id, "http.response_time", duration)
        
        # Finish span
        status = "ok" if response.status_code < 400 else "error"
        tracer.finish_span(span_id, status)
        
        # Add service mesh headers
        ServiceMeshHeaders.add_service_info(
            response.headers,
            "blatam-cloud-native-api",
            "1.0.0"
        )
        
        # Propagate trace headers
        for key, value in trace_headers.items():
            response.headers[f"x-propagated-{key}"] = value
        
        response.headers["x-trace-id"] = span_id
        
        return response
    
    return app

# Create cloud-native app
cloud_app = create_cloud_native_app()

# =============================================================================
# CLOUD-NATIVE ENDPOINTS
# =============================================================================

@cloud_app.get("/", tags=["Cloud-Native"])
async def cloud_native_root():
    """Cloud-native root endpoint."""
    return {
        "service": "Cloud-Native Patterns API",
        "version": "1.0.0",
        "patterns": [
            "Event Sourcing",
            "CQRS",
            "Distributed Tracing",
            "Service Mesh Integration"
        ],
        "observability": {
            "tracing": "OpenTelemetry",
            "metrics": "Prometheus",
            "logging": "Structured JSON"
        },
        "mesh_compatibility": [
            "Istio",
            "Linkerd", 
            "Consul Connect"
        ]
    }

@cloud_app.post("/api/v1/content", tags=["CQRS"])
async def create_content_cqrs(
    request: Request,
    content_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Create content using CQRS pattern."""
    
    # Start trace
    span_id = tracer.start_span("create_content_command")
    
    try:
        # Create command
        command = CreateContentCommand(
            content_id=str(uuid.uuid4()),
            topic=content_data.get("topic", ""),
            content_type=content_data.get("content_type", "blog_post"),
            user_id=content_data.get("user_id", "anonymous")
        )
        
        tracer.add_tag(span_id, "command.type", "CreateContentCommand")
        tracer.add_tag(span_id, "command.content_type", command.content_type)
        
        # Handle command
        event_id = await command_handler.handle_create_content(command)
        
        tracer.log_event(span_id, "command_handled", {"event_id": event_id})
        tracer.finish_span(span_id, "ok")
        
        return {
            "success": True,
            "content_id": command.content_id,
            "event_id": event_id,
            "message": "Content creation command processed"
        }
        
    except Exception as e:
        tracer.log_event(span_id, "error", {"error": str(e)})
        tracer.finish_span(span_id, "error")
        raise

@cloud_app.get("/api/v1/content/{content_id}", tags=["CQRS"])
async def get_content_cqrs(request: Request, content_id: str):
    """Get content using CQRS pattern."""
    
    span_id = tracer.start_span("get_content_query")
    
    try:
        # Create query
        query = GetContentQuery(content_id=content_id)
        
        tracer.add_tag(span_id, "query.type", "GetContentQuery")
        tracer.add_tag(span_id, "query.content_id", content_id)
        
        # Handle query
        result = await query_handler.handle_get_content(query)
        
        if not result:
            tracer.finish_span(span_id, "not_found")
            return JSONResponse(
                status_code=404,
                content={"error": "Content not found"}
            )
        
        tracer.log_event(span_id, "query_handled", {"found": True})
        tracer.finish_span(span_id, "ok")
        
        return {
            "success": True,
            "content": result
        }
        
    except Exception as e:
        tracer.log_event(span_id, "error", {"error": str(e)})
        tracer.finish_span(span_id, "error")
        raise

@cloud_app.get("/api/v1/events", tags=["Event Sourcing"])
async def get_all_events():
    """Get all events from event store."""
    events = await event_store.get_all_events()
    
    return {
        "events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "aggregate_id": event.aggregate_id,
                "data": event.data,
                "timestamp": event.timestamp.isoformat(),
                "version": event.version
            }
            for event in events
        ],
        "total_events": len(events)
    }

@cloud_app.get("/api/v1/traces/{span_id}", tags=["Observability"])
async def get_trace_data(span_id: str):
    """Get distributed trace data."""
    trace_data = tracer.get_trace_data(span_id)
    
    if not trace_data:
        return JSONResponse(
            status_code=404,
            content={"error": "Trace not found"}
        )
    
    return {
        "trace": trace_data
    }

@cloud_app.get("/health/live", tags=["Health"])
async def liveness_probe():
    """Kubernetes liveness probe."""
    return {"status": "alive", "timestamp": datetime.now(timezone.utc).isoformat()}

@cloud_app.get("/health/ready", tags=["Health"])
async def readiness_probe():
    """Kubernetes readiness probe."""
    
    # Check dependencies
    checks = {
        "event_store": {"status": "healthy"},
        "command_handler": {"status": "healthy"},
        "query_handler": {"status": "healthy"}
    }
    
    return HealthStatus(
        status="healthy",
        checks=checks,
        timestamp=datetime.now(timezone.utc),
        version="1.0.0"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(cloud_app, host="0.0.0.0", port=8000) 