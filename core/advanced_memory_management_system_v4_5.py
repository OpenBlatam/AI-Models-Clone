"""
Sistema de Gestión de Memoria Avanzada v4.5
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa gestión inteligente de memoria con:
- Asignación dinámica inteligente
- Detección automática de memory leaks
- Optimización de garbage collection
- Monitoreo de uso de memoria en tiempo real
- Compresión inteligente de datos
- Cache inteligente multi-nivel
"""

import asyncio
import time
import json
import logging
import psutil
import gc
import weakref
import tracemalloc
from typing import Dict, List, Any, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import statistics
import numpy as np
import pandas as pd
from pathlib import Path
import threading
import queue
import pickle
import hashlib
import random
import math
import os
import sys

# Memory Management Components
@dataclass
class MemoryBlock:
    """Represents a memory block with metadata"""
    id: str
    size: int
    type: str
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    priority: int = 1
    compression_ratio: float = 1.0
    is_compressed: bool = False

@dataclass
class MemoryMetrics:
    """Memory usage metrics"""
    total_physical: int
    available_physical: int
    used_physical: int
    total_virtual: int
    used_virtual: int
    swap_total: int
    swap_used: int
    swap_free: int
    memory_percent: float
    timestamp: datetime

@dataclass
class MemoryLeak:
    """Detected memory leak information"""
    id: str
    location: str
    size_increase: int
    detection_time: datetime
    severity: str
    stack_trace: List[str]
    estimated_impact: str

@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    key: str
    data: Any
    size: int
    created_at: datetime
    last_accessed: datetime
    access_count: int
    ttl: Optional[timedelta] = None
    priority: int = 1

class IntelligentMemoryAllocator:
    """Intelligent memory allocation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.memory_blocks: Dict[str, MemoryBlock] = {}
        self.allocation_history: deque = deque(maxlen=1000)
        self.fragmentation_threshold = config.get('fragmentation_threshold', 0.3)
        self.compression_threshold = config.get('compression_threshold', 0.7)
        
    async def allocate_memory(self, size: int, memory_type: str, priority: int = 1) -> str:
        """Intelligently allocate memory based on available space and priority"""
        block_id = f"block_{len(self.memory_blocks)}_{int(time.time())}"
        
        # Check if we need to compress existing blocks
        if self._should_compress_memory():
            await self._compress_low_priority_blocks()
        
        # Check for fragmentation
        if self._is_memory_fragmented():
            await self._defragment_memory()
        
        # Create memory block
        block = MemoryBlock(
            id=block_id,
            size=size,
            type=memory_type,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            priority=priority
        )
        
        self.memory_blocks[block_id] = block
        self.allocation_history.append({
            'action': 'allocate',
            'block_id': block_id,
            'size': size,
            'timestamp': datetime.now()
        })
        
        return block_id
    
    async def deallocate_memory(self, block_id: str) -> bool:
        """Deallocate memory block"""
        if block_id in self.memory_blocks:
            block = self.memory_blocks[block_id]
            self.allocation_history.append({
                'action': 'deallocate',
                'block_id': block_id,
                'size': block.size,
                'timestamp': datetime.now()
            })
            del self.memory_blocks[block_id]
            return True
        return False
    
    def _should_compress_memory(self) -> bool:
        """Determine if memory compression is needed"""
        used_memory = psutil.virtual_memory().percent / 100
        return used_memory > self.compression_threshold
    
    def _is_memory_fragmented(self) -> bool:
        """Check if memory is fragmented"""
        if len(self.memory_blocks) < 2:
            return False
        
        sizes = [block.size for block in self.memory_blocks.values()]
        mean_size = statistics.mean(sizes)
        std_size = statistics.stdev(sizes) if len(sizes) > 1 else 0
        
        fragmentation_score = std_size / mean_size if mean_size > 0 else 0
        return fragmentation_score > self.fragmentation_threshold
    
    async def _compress_low_priority_blocks(self):
        """Compress low priority memory blocks"""
        low_priority_blocks = [
            block for block in self.memory_blocks.values()
            if block.priority < 3
        ]
        
        for block in low_priority_blocks:
            if not block.is_compressed:
                # Simulate compression
                block.size = int(block.size * 0.7)
                block.is_compressed = True
                block.compression_ratio = 0.7
    
    async def _defragment_memory(self):
        """Defragment memory by reorganizing blocks"""
        # Sort blocks by size for better organization
        sorted_blocks = sorted(
            self.memory_blocks.values(),
            key=lambda x: x.size
        )
        
        # Reorganize block IDs for better memory layout
        new_blocks = {}
        for i, block in enumerate(sorted_blocks):
            new_id = f"defrag_{i}_{int(time.time())}"
            new_blocks[new_id] = block
            block.id = new_id
        
        self.memory_blocks = new_blocks

class MemoryLeakDetector:
    """Advanced memory leak detection system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detected_leaks: List[MemoryLeak] = []
        self.memory_snapshots: deque = deque(maxlen=100)
        self.leak_threshold = config.get('leak_threshold', 0.1)  # 10% increase
        self.detection_interval = config.get('detection_interval', 60)  # seconds
        
    async def start_monitoring(self):
        """Start memory leak monitoring"""
        tracemalloc.start()
        asyncio.create_task(self._monitoring_loop())
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while True:
            await self._take_memory_snapshot()
            await self._analyze_for_leaks()
            await asyncio.sleep(self.detection_interval)
    
    async def _take_memory_snapshot(self):
        """Take a memory snapshot for analysis"""
        snapshot = tracemalloc.take_snapshot()
        memory_info = psutil.virtual_memory()
        
        self.memory_snapshots.append({
            'snapshot': snapshot,
            'memory_info': memory_info,
            'timestamp': datetime.now()
        })
    
    async def _analyze_for_leaks(self):
        """Analyze snapshots for memory leaks"""
        if len(self.memory_snapshots) < 2:
            return
        
        current = self.memory_snapshots[-1]
        previous = self.memory_snapshots[-2]
        
        # Calculate memory growth
        memory_growth = (
            current['memory_info'].used - previous['memory_info'].used
        ) / previous['memory_info'].used
        
        if memory_growth > self.leak_threshold:
            leak = await self._identify_leak_source(current, previous)
            if leak:
                self.detected_leaks.append(leak)
    
    async def _identify_leak_source(self, current: Dict, previous: Dict) -> Optional[MemoryLeak]:
        """Identify the source of a memory leak"""
        try:
            # Compare snapshots to find top memory consumers
            top_stats = current['snapshot'].compare_to(previous['snapshot'], 'lineno')
            
            if top_stats:
                top_consumer = top_stats[0]
                
                leak = MemoryLeak(
                    id=f"leak_{len(self.detected_leaks)}_{int(time.time())}",
                    location=str(top_consumer.traceback.format()),
                    size_increase=top_consumer.size_diff,
                    detection_time=datetime.now(),
                    severity='high' if top_consumer.size_diff > 1024*1024 else 'medium',
                    stack_trace=[str(frame) for frame in top_consumer.traceback],
                    estimated_impact=f"Memory increase: {top_consumer.size_diff} bytes"
                )
                
                return leak
        except Exception as e:
            logging.error(f"Error identifying leak source: {e}")
        
        return None

class IntelligentCache:
    """Multi-level intelligent cache system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.l1_cache: Dict[str, CacheEntry] = {}  # Fast access
        self.l2_cache: Dict[str, CacheEntry] = {}  # Medium access
        self.l3_cache: Dict[str, CacheEntry] = {}  # Slow access
        self.max_l1_size = config.get('max_l1_size', 100 * 1024 * 1024)  # 100MB
        self.max_l2_size = config.get('max_l2_size', 500 * 1024 * 1024)  # 500MB
        self.max_l3_size = config.get('max_l3_size', 1024 * 1024 * 1024)  # 1GB
        self.current_l1_size = 0
        self.current_l2_size = 0
        self.current_l3_size = 0
        
    async def get(self, key: str) -> Optional[Any]:
        """Get data from cache with intelligent promotion"""
        # Check L1 cache first
        if key in self.l1_cache:
            entry = self.l1_cache[key]
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            return entry.data
        
        # Check L2 cache
        if key in self.l2_cache:
            entry = self.l2_cache[key]
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Promote to L1 if frequently accessed
            if entry.access_count > 5:
                await self._promote_to_l1(key, entry)
            
            return entry.data
        
        # Check L3 cache
        if key in self.l3_cache:
            entry = self.l3_cache[key]
            entry.last_accessed = datetime.now()
            entry.access_count += 1
            
            # Promote to L2 if moderately accessed
            if entry.access_count > 3:
                await self._promote_to_l2(key, entry)
            
            return entry.data
        
        return None
    
    async def set(self, key: str, data: Any, ttl: Optional[timedelta] = None, priority: int = 1):
        """Set data in cache with intelligent placement"""
        entry = CacheEntry(
            key=key,
            data=data,
            size=sys.getsizeof(data),
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            ttl=ttl,
            priority=priority
        )
        
        # Place in appropriate cache level based on priority and size
        if priority == 1 and entry.size <= self.max_l1_size:
            await self._add_to_l1(key, entry)
        elif priority <= 2 and entry.size <= self.max_l2_size:
            await self._add_to_l2(key, entry)
        else:
            await self._add_to_l3(key, entry)
    
    async def _add_to_l1(self, key: str, entry: CacheEntry):
        """Add entry to L1 cache with eviction if needed"""
        if self.current_l1_size + entry.size > self.max_l1_size:
            await self._evict_from_l1()
        
        self.l1_cache[key] = entry
        self.current_l1_size += entry.size
    
    async def _add_to_l2(self, key: str, entry: CacheEntry):
        """Add entry to L2 cache with eviction if needed"""
        if self.current_l2_size + entry.size > self.max_l2_size:
            await self._evict_from_l2()
        
        self.l2_cache[key] = entry
        self.current_l2_size += entry.size
    
    async def _add_to_l3(self, key: str, entry: CacheEntry):
        """Add entry to L3 cache with eviction if needed"""
        if self.current_l3_size + entry.size > self.max_l3_size:
            await self._evict_from_l3()
        
        self.l3_cache[key] = entry
        self.current_l3_size += entry.size
    
    async def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote entry from L2 to L1 cache"""
        if key in self.l2_cache:
            del self.l2_cache[key]
            self.current_l2_size -= entry.size
            await self._add_to_l1(key, entry)
    
    async def _promote_to_l2(self, key: str, entry: CacheEntry):
        """Promote entry from L3 to L2 cache"""
        if key in self.l3_cache:
            del self.l3_cache[key]
            self.current_l3_size -= entry.size
            await self._add_to_l2(key, entry)
    
    async def _evict_from_l1(self):
        """Evict least recently used entry from L1 cache"""
        if not self.l1_cache:
            return
        
        lru_key = min(
            self.l1_cache.keys(),
            key=lambda k: self.l1_cache[k].last_accessed
        )
        
        entry = self.l1_cache[lru_key]
        del self.l1_cache[lru_key]
        self.current_l1_size -= entry.size
        
        # Demote to L2
        await self._add_to_l2(lru_key, entry)
    
    async def _evict_from_l2(self):
        """Evict least recently used entry from L2 cache"""
        if not self.l2_cache:
            return
        
        lru_key = min(
            self.l2_cache.keys(),
            key=lambda k: self.l2_cache[k].last_accessed
        )
        
        entry = self.l2_cache[lru_key]
        del self.l2_cache[lru_key]
        self.current_l2_size -= entry.size
        
        # Demote to L3
        await self._add_to_l3(lru_key, entry)
    
    async def _evict_from_l3(self):
        """Evict least recently used entry from L3 cache"""
        if not self.l3_cache:
            return
        
        lru_key = min(
            self.l3_cache.keys(),
            key=lambda k: self.l3_cache[k].last_accessed
        )
        
        entry = self.l3_cache[lru_key]
        del self.l3_cache[lru_key]
        self.current_l3_size -= entry.size

class AdvancedMemoryManagementSystem:
    """Main memory management system v4.5"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.allocator = IntelligentMemoryAllocator(config)
        self.leak_detector = MemoryLeakDetector(config)
        self.intelligent_cache = IntelligentCache(config)
        self.memory_metrics_history: deque = deque(maxlen=1000)
        self.optimization_tasks: List[Dict] = []
        self.is_running = False
        
        # Performance tracking
        self.allocation_count = 0
        self.deallocation_count = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.memory_compression_savings = 0
        
    async def start(self):
        """Start the memory management system"""
        self.is_running = True
        logging.info("🚀 Sistema de Gestión de Memoria Avanzada v4.5 iniciado")
        
        # Start monitoring tasks
        asyncio.create_task(self._memory_monitoring_loop())
        asyncio.create_task(self._optimization_loop())
        asyncio.create_task(self._leak_detector.start_monitoring())
        
        logging.info("✅ Monitoreo de memoria y optimización iniciados")
    
    async def stop(self):
        """Stop the memory management system"""
        self.is_running = False
        logging.info("🛑 Sistema de Gestión de Memoria Avanzada v4.5 detenido")
    
    async def _memory_monitoring_loop(self):
        """Continuous memory monitoring loop"""
        while self.is_running:
            try:
                await self._collect_memory_metrics()
                await self._check_memory_health()
                await asyncio.sleep(30)  # Every 30 seconds
            except Exception as e:
                logging.error(f"Error en monitoreo de memoria: {e}")
    
    async def _collect_memory_metrics(self):
        """Collect current memory metrics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        metrics = MemoryMetrics(
            total_physical=memory.total,
            available_physical=memory.available,
            used_physical=memory.used,
            total_virtual=memory.total,
            used_virtual=memory.used,
            swap_total=swap.total,
            swap_used=swap.used,
            swap_free=swap.free,
            memory_percent=memory.percent,
            timestamp=datetime.now()
        )
        
        self.memory_metrics_history.append(metrics)
        
        # Log critical memory usage
        if memory.percent > 90:
            logging.warning(f"⚠️ Uso crítico de memoria: {memory.percent:.1f}%")
        elif memory.percent > 80:
            logging.info(f"📊 Uso alto de memoria: {memory.percent:.1f}%")
    
    async def _check_memory_health(self):
        """Check overall memory health and trigger optimizations"""
        if len(self.memory_metrics_history) < 2:
            return
        
        current = self.memory_metrics_history[-1]
        previous = self.memory_metrics_history[-2]
        
        # Check for memory pressure
        if current.memory_percent > 85:
            await self._trigger_memory_optimization('high_pressure')
        
        # Check for memory growth trend
        memory_growth = (
            current.used_physical - previous.used_physical
        ) / previous.used_physical
        
        if memory_growth > 0.1:  # 10% growth
            await self._trigger_memory_optimization('growth_trend')
    
    async def _trigger_memory_optimization(self, reason: str):
        """Trigger memory optimization based on reason"""
        optimization_task = {
            'id': f"opt_{len(self.optimization_tasks)}_{int(time.time())}",
            'reason': reason,
            'timestamp': datetime.now(),
            'status': 'pending'
        }
        
        self.optimization_tasks.append(optimization_task)
        logging.info(f"🔧 Optimización de memoria programada: {reason}")
    
    async def _optimization_loop(self):
        """Process optimization tasks"""
        while self.is_running:
            try:
                pending_tasks = [
                    task for task in self.optimization_tasks
                    if task['status'] == 'pending'
                ]
                
                for task in pending_tasks:
                    await self._execute_optimization(task)
                
                await asyncio.sleep(60)  # Check every minute
            except Exception as e:
                logging.error(f"Error en optimización: {e}")
    
    async def _execute_optimization(self, task: Dict):
        """Execute a memory optimization task"""
        try:
            task['status'] = 'running'
            
            if task['reason'] == 'high_pressure':
                await self._optimize_high_pressure()
            elif task['reason'] == 'growth_trend':
                await self._optimize_growth_trend()
            
            task['status'] = 'completed'
            logging.info(f"✅ Optimización completada: {task['reason']}")
            
        except Exception as e:
            task['status'] = 'failed'
            logging.error(f"❌ Error en optimización: {e}")
    
    async def _optimize_high_pressure(self):
        """Optimize memory under high pressure"""
        # Force garbage collection
        collected = gc.collect()
        logging.info(f"🗑️ Garbage collection: {collected} objetos recolectados")
        
        # Compress low priority memory
        await self.allocator._compress_low_priority_blocks()
        
        # Clear expired cache entries
        await self._clear_expired_cache()
    
    async def _optimize_growth_trend(self):
        """Optimize memory growth trend"""
        # Analyze memory usage patterns
        if len(self.memory_metrics_history) > 10:
            recent_metrics = list(self.memory_metrics_history)[-10:]
            growth_rate = self._calculate_growth_rate(recent_metrics)
            
            if growth_rate > 0.05:  # 5% per interval
                logging.info(f"📈 Tasa de crecimiento alta: {growth_rate:.2%}")
                await self._implement_growth_controls()
    
    async def _clear_expired_cache(self):
        """Clear expired cache entries"""
        current_time = datetime.now()
        
        # Clear L1 cache expired entries
        expired_l1 = [
            key for key, entry in self.l1_cache.items()
            if entry.ttl and current_time > entry.created_at + entry.ttl
        ]
        
        for key in expired_l1:
            entry = self.l1_cache[key]
            del self.l1_cache[key]
            self.current_l1_size -= entry.size
        
        if expired_l1:
            logging.info(f"🧹 Cache L1 limpiado: {len(expired_l1)} entradas expiradas")
    
    def _calculate_growth_rate(self, metrics: List[MemoryMetrics]) -> float:
        """Calculate memory growth rate from metrics"""
        if len(metrics) < 2:
            return 0.0
        
        first = metrics[0]
        last = metrics[-1]
        
        time_diff = (last.timestamp - first.timestamp).total_seconds()
        if time_diff == 0:
            return 0.0
        
        growth_rate = (last.used_physical - first.used_physical) / first.used_physical
        return growth_rate / (time_diff / 3600)  # Per hour
    
    async def _implement_growth_controls(self):
        """Implement memory growth controls"""
        # Increase garbage collection frequency
        gc.set_threshold(100, 5, 5)  # More aggressive GC
        
        # Compress more memory blocks
        await self.allocator._compress_low_priority_blocks()
        
        # Clear more cache entries
        await self._clear_expired_cache()
    
    async def get_memory_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics"""
        current_memory = psutil.virtual_memory()
        
        return {
            'system_memory': {
                'total': current_memory.total,
                'available': current_memory.available,
                'used': current_memory.used,
                'percent': current_memory.percent
            },
            'cache_stats': {
                'l1_size': self.current_l1_size,
                'l2_size': self.current_l2_size,
                'l3_size': self.current_l3_size,
                'l1_entries': len(self.l1_cache),
                'l2_entries': len(self.l2_cache),
                'l3_entries': len(self.l3_cache),
                'cache_hits': self.cache_hits,
                'cache_misses': self.cache_misses,
                'hit_ratio': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0
            },
            'memory_blocks': {
                'total_blocks': len(self.allocator.memory_blocks),
                'total_size': sum(block.size for block in self.allocator.memory_blocks.values()),
                'compressed_blocks': len([b for b in self.allocator.memory_blocks.values() if b.is_compressed])
            },
            'leak_detection': {
                'detected_leaks': len(self.leak_detector.detected_leaks),
                'active_monitoring': self.leak_detector.detection_interval
            },
            'optimization': {
                'pending_tasks': len([t for t in self.optimization_tasks if t['status'] == 'pending']),
                'completed_tasks': len([t for t in self.optimization_tasks if t['status'] == 'completed'])
            }
        }
    
    async def allocate_memory(self, size: int, memory_type: str, priority: int = 1) -> str:
        """Allocate memory with tracking"""
        block_id = await self.allocator.allocate_memory(size, memory_type, priority)
        self.allocation_count += 1
        return block_id
    
    async def deallocate_memory(self, block_id: str) -> bool:
        """Deallocate memory with tracking"""
        success = await self.allocator.deallocate_memory(block_id)
        if success:
            self.deallocation_count += 1
        return success
    
    async def cache_get(self, key: str) -> Optional[Any]:
        """Get from cache with hit/miss tracking"""
        result = await self.intelligent_cache.get(key)
        if result is not None:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        return result
    
    async def cache_set(self, key: str, data: Any, ttl: Optional[timedelta] = None, priority: int = 1):
        """Set in cache"""
        await self.intelligent_cache.set(key, data, ttl, priority)

# Configuration for the system
DEFAULT_CONFIG = {
    'fragmentation_threshold': 0.3,
    'compression_threshold': 0.7,
    'leak_threshold': 0.1,
    'detection_interval': 60,
    'max_l1_size': 100 * 1024 * 1024,  # 100MB
    'max_l2_size': 500 * 1024 * 1024,  # 500MB
    'max_l3_size': 1024 * 1024 * 1024,  # 1GB
    'optimization_interval': 60,
    'memory_pressure_threshold': 85,
    'growth_threshold': 0.1
}

if __name__ == "__main__":
    # Demo configuration
    config = DEFAULT_CONFIG.copy()
    
    async def demo():
        system = AdvancedMemoryManagementSystem(config)
        await system.start()
        
        # Simulate memory operations
        for i in range(10):
            block_id = await system.allocate_memory(1024 * 1024, f"test_{i}", 1)
            print(f"Memoria asignada: {block_id}")
            
            await asyncio.sleep(2)
        
        # Get stats
        stats = await system.get_memory_stats()
        print(f"Estadísticas: {json.dumps(stats, indent=2, default=str)}")
        
        await system.stop()
    
    asyncio.run(demo())
