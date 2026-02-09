#!/usr/bin/env python3
"""
Deployment Distributed Tracing
Tracks deployment operations across components
"""

import time
import uuid
import logging
import json
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from contextlib import contextmanager


logger = logging.getLogger(__name__)


@dataclass
class TraceSpan:
    """Represents a trace span"""
    span_id: str
    trace_id: str
    operation_name: str
    start_time: float
    end_time: Optional[float] = None
    duration: Optional[float] = None
    tags: Dict[str, Any] = None
    logs: List[Dict[str, Any]] = None
    parent_span_id: Optional[str] = None
    status: str = "started"  # started, success, error
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}
        if self.logs is None:
            self.logs = []
    
    def finish(self, status: str = "success", error: Optional[str] = None):
        """Finish the span"""
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        self.status = status
        if error:
            self.logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'error',
                'message': error
            })
    
    def add_tag(self, key: str, value: Any):
        """Add a tag to the span"""
        self.tags[key] = value
    
    def add_log(self, message: str, level: str = "info"):
        """Add a log entry to the span"""
        self.logs.append({
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        })


class DeploymentTracer:
    """Distributed tracing for deployments"""
    
    def __init__(self, trace_file: str = '/var/lib/deployment-tracing/traces.json'):
        self.trace_file = Path(trace_file)
        self.trace_file.parent.mkdir(parents=True, exist_ok=True)
        self.active_traces: Dict[str, List[TraceSpan]] = {}
        self.active_spans: Dict[str, TraceSpan] = {}
    
    def start_trace(self, operation_name: str, trace_id: Optional[str] = None) -> str:
        """Start a new trace"""
        if trace_id is None:
            trace_id = str(uuid.uuid4())
        
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            operation_name=operation_name,
            start_time=time.time()
        )
        
        if trace_id not in self.active_traces:
            self.active_traces[trace_id] = []
        
        self.active_traces[trace_id].append(span)
        self.active_spans[span.span_id] = span
        
        logger.debug(f"Started trace {trace_id} with span {span.span_id}: {operation_name}")
        return trace_id
    
    def start_span(
        self,
        operation_name: str,
        trace_id: str,
        parent_span_id: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> str:
        """Start a new span within a trace"""
        span = TraceSpan(
            span_id=str(uuid.uuid4()),
            trace_id=trace_id,
            operation_name=operation_name,
            start_time=time.time(),
            parent_span_id=parent_span_id,
            tags=tags or {}
        )
        
        if trace_id not in self.active_traces:
            self.active_traces[trace_id] = []
        
        self.active_traces[trace_id].append(span)
        self.active_spans[span.span_id] = span
        
        logger.debug(f"Started span {span.span_id} in trace {trace_id}: {operation_name}")
        return span.span_id
    
    def finish_span(self, span_id: str, status: str = "success", error: Optional[str] = None):
        """Finish a span"""
        if span_id in self.active_spans:
            span = self.active_spans[span_id]
            span.finish(status, error)
            logger.debug(f"Finished span {span_id} with status {status}")
    
    def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add a tag to a span"""
        if span_id in self.active_spans:
            self.active_spans[span_id].add_tag(key, value)
    
    def add_span_log(self, span_id: str, message: str, level: str = "info"):
        """Add a log entry to a span"""
        if span_id in self.active_spans:
            self.active_spans[span_id].add_log(message, level)
    
    @contextmanager
    def span(self, operation_name: str, trace_id: str, parent_span_id: Optional[str] = None):
        """Context manager for automatic span management"""
        span_id = self.start_span(operation_name, trace_id, parent_span_id)
        try:
            yield span_id
            self.finish_span(span_id, "success")
        except Exception as e:
            self.finish_span(span_id, "error", str(e))
            raise
    
    def finish_trace(self, trace_id: str) -> Dict[str, Any]:
        """Finish a trace and return summary"""
        if trace_id not in self.active_traces:
            return {}
        
        spans = self.active_traces[trace_id]
        
        # Ensure all spans are finished
        for span in spans:
            if span.end_time is None:
                span.finish("unknown")
        
        # Calculate trace summary
        total_duration = max(s.end_time for s in spans) - min(s.start_time for s in spans)
        root_span = next((s for s in spans if s.parent_span_id is None), spans[0])
        
        trace_summary = {
            'trace_id': trace_id,
            'operation_name': root_span.operation_name,
            'start_time': datetime.fromtimestamp(root_span.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(max(s.end_time for s in spans)).isoformat(),
            'duration': total_duration,
            'span_count': len(spans),
            'status': 'success' if all(s.status == 'success' for s in spans) else 'error',
            'spans': [asdict(span) for span in spans]
        }
        
        # Save trace
        self._save_trace(trace_summary)
        
        # Cleanup
        for span in spans:
            if span.span_id in self.active_spans:
                del self.active_spans[span.span_id]
        del self.active_traces[trace_id]
        
        return trace_summary
    
    def _save_trace(self, trace_summary: Dict[str, Any]):
        """Save trace to file"""
        try:
            traces = []
            if self.trace_file.exists():
                with open(self.trace_file, 'r') as f:
                    traces = json.load(f)
            
            traces.append(trace_summary)
            
            # Keep only last 100 traces
            traces = traces[-100:]
            
            with open(self.trace_file, 'w') as f:
                json.dump(traces, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save trace: {e}")
    
    def get_trace(self, trace_id: str) -> Optional[Dict[str, Any]]:
        """Get trace by ID"""
        try:
            if self.trace_file.exists():
                with open(self.trace_file, 'r') as f:
                    traces = json.load(f)
                    for trace in traces:
                        if trace['trace_id'] == trace_id:
                            return trace
        except Exception as e:
            logger.error(f"Failed to get trace: {e}")
        return None
    
    def get_recent_traces(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent traces"""
        try:
            if self.trace_file.exists():
                with open(self.trace_file, 'r') as f:
                    traces = json.load(f)
                    return traces[-limit:]
        except Exception as e:
            logger.error(f"Failed to get recent traces: {e}")
        return []
