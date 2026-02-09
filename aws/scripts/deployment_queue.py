#!/usr/bin/env python3
"""
Deployment Queue Manager
Manages deployment queue to prevent concurrent deployments
"""

import os
import json
import time
import logging
import threading
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
from queue import Queue, Empty
from dataclasses import dataclass, asdict


logger = logging.getLogger(__name__)


@dataclass
class DeploymentRequest:
    """Deployment request"""
    id: str
    commit_hash: str
    branch: str
    requested_at: str
    status: str  # 'pending', 'processing', 'completed', 'failed'
    priority: int = 0  # Higher = more priority
    strategy: str = 'standard'
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DeploymentQueue:
    """Manages deployment queue"""
    
    def __init__(self, queue_file: str = '/var/lib/deployment-queue/queue.json'):
        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self.queue: Queue = Queue()
        self.processing: Optional[DeploymentRequest] = None
        self.lock = threading.Lock()
        self.history: List[DeploymentRequest] = []
        self._load_queue()
    
    def _load_queue(self) -> None:
        """Load queue from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get('pending', []):
                        req = DeploymentRequest(**item)
                        self.queue.put(req)
                    if data.get('processing'):
                        self.processing = DeploymentRequest(**data['processing'])
                    self.history = [DeploymentRequest(**item) for item in data.get('history', [])]
            except Exception as e:
                logger.error(f"Failed to load queue: {e}")
    
    def _save_queue(self) -> None:
        """Save queue to file"""
        try:
            with self.lock:
                pending = []
                while not self.queue.empty():
                    try:
                        pending.append(asdict(self.queue.get_nowait()))
                    except Empty:
                        break
                    # Put back in queue
                    for item in pending:
                        self.queue.put(DeploymentRequest(**item))
                
                data = {
                    'pending': pending,
                    'processing': asdict(self.processing) if self.processing else None,
                    'history': [asdict(item) for item in self.history[-100:]]  # Keep last 100
                }
                
                with open(self.queue_file, 'w') as f:
                    json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save queue: {e}")
    
    def enqueue(
        self,
        commit_hash: str,
        branch: str = 'main',
        priority: int = 0,
        strategy: str = 'standard',
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add deployment request to queue"""
        request_id = f"{int(time.time())}_{commit_hash[:7]}"
        
        request = DeploymentRequest(
            id=request_id,
            commit_hash=commit_hash,
            branch=branch,
            requested_at=datetime.now().isoformat(),
            status='pending',
            priority=priority,
            strategy=strategy,
            metadata=metadata or {}
        )
        
        with self.lock:
            self.queue.put(request)
            self._save_queue()
        
        logger.info(f"Deployment request queued: {request_id} (priority: {priority})")
        return request_id
    
    def dequeue(self) -> Optional[DeploymentRequest]:
        """Get next deployment request from queue"""
        with self.lock:
            if self.processing:
                logger.warning("Deployment already in progress, skipping queue")
                return None
            
            try:
                request = self.queue.get_nowait()
                request.status = 'processing'
                self.processing = request
                self._save_queue()
                logger.info(f"Deployment request dequeued: {request.id}")
                return request
            except Empty:
                return None
    
    def complete(self, request_id: str, success: bool, message: str = '') -> None:
        """Mark deployment as completed"""
        with self.lock:
            if self.processing and self.processing.id == request_id:
                self.processing.status = 'completed' if success else 'failed'
                self.processing.metadata['completed_at'] = datetime.now().isoformat()
                self.processing.metadata['message'] = message
                self.history.append(self.processing)
                self.processing = None
                self._save_queue()
                logger.info(f"Deployment {request_id} marked as {'completed' if success else 'failed'}")
            else:
                logger.warning(f"Deployment {request_id} not found in processing")
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get queue status"""
        with self.lock:
            pending_count = self.queue.qsize()
            return {
                'pending': pending_count,
                'processing': asdict(self.processing) if self.processing else None,
                'recent_history': [asdict(item) for item in self.history[-10:]]
            }
    
    def clear_queue(self) -> int:
        """Clear all pending deployments"""
        with self.lock:
            count = 0
            while not self.queue.empty():
                try:
                    self.queue.get_nowait()
                    count += 1
                except Empty:
                    break
            self._save_queue()
            logger.info(f"Cleared {count} pending deployments")
            return count
