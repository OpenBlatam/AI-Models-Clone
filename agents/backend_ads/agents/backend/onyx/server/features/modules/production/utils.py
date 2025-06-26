"""
Production Utilities Module.

Utility functions and system optimization for production environments.
"""

import os
import gc
import time
from typing import Dict, Any, Optional

import structlog

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from .config import ProductionSettings

logger = structlog.get_logger(__name__)


class ProductionUtils:
    """Utility functions for production operations."""
    
    @staticmethod
    def generate_correlation_id() -> str:
        """Generate a correlation ID for request tracking."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    @staticmethod
    def format_bytes(bytes_value: int) -> str:
        """Format bytes in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} PB"
    
    @staticmethod
    def get_system_info() -> Dict[str, Any]:
        """Get comprehensive system information."""
        info = {
            "platform": os.name,
            "cpu_count": os.cpu_count(),
            "python_version": f"{os.sys.version_info.major}.{os.sys.version_info.minor}.{os.sys.version_info.micro}"
        }
        
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            info.update({
                "total_memory": ProductionUtils.format_bytes(memory.total),
                "available_memory": ProductionUtils.format_bytes(memory.available),
                "memory_percent": memory.percent,
                "cpu_percent": psutil.cpu_percent(),
                "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent
            })
        
        return info
    
    @staticmethod
    def optimize_memory() -> Dict[str, Any]:
        """Perform memory optimization."""
        initial_memory = None
        if PSUTIL_AVAILABLE:
            initial_memory = psutil.virtual_memory().percent
        
        # Force garbage collection
        collected = gc.collect()
        
        final_memory = None
        if PSUTIL_AVAILABLE:
            final_memory = psutil.virtual_memory().percent
        
        result = {
            "objects_collected": collected,
            "gc_stats": gc.get_stats() if hasattr(gc, 'get_stats') else None
        }
        
        if initial_memory is not None and final_memory is not None:
            result.update({
                "initial_memory_percent": initial_memory,
                "final_memory_percent": final_memory,
                "memory_freed_percent": initial_memory - final_memory
            })
        
        return result


class SystemOptimizer:
    """System optimization for production environments."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
    
    def optimize_system(self) -> Dict[str, Any]:
        """Perform comprehensive system optimization."""
        optimizations = {}
        
        # Memory optimization
        if self.config.enable_memory_optimization:
            memory_result = ProductionUtils.optimize_memory()
            optimizations["memory"] = memory_result
        
        # Garbage collection tuning
        if self.config.gc_threshold > 0:
            gc.set_threshold(self.config.gc_threshold, 10, 10)
            optimizations["gc"] = {
                "threshold_set": self.config.gc_threshold,
                "current_thresholds": gc.get_threshold()
            }
        
        # Process optimization
        if PSUTIL_AVAILABLE:
            try:
                process = psutil.Process()
                if hasattr(process, 'nice'):
                    process.nice(-5)  # Higher priority for production
                optimizations["process"] = {
                    "priority_set": True,
                    "pid": process.pid
                }
            except Exception as e:
                optimizations["process"] = {
                    "error": str(e)
                }
        
        return {
            "timestamp": time.time(),
            "optimizations_applied": optimizations,
            "system_info": ProductionUtils.get_system_info()
        }
    
    def get_optimization_recommendations(self) -> Dict[str, Any]:
        """Get optimization recommendations based on current system state."""
        recommendations = []
        
        if PSUTIL_AVAILABLE:
            memory = psutil.virtual_memory()
            cpu = psutil.cpu_percent()
            
            if memory.percent > 80:
                recommendations.append({
                    "type": "memory",
                    "priority": "high",
                    "message": f"Memory usage is high ({memory.percent:.1f}%)",
                    "action": "Consider increasing memory or optimizing application"
                })
            
            if cpu > 80:
                recommendations.append({
                    "type": "cpu",
                    "priority": "high", 
                    "message": f"CPU usage is high ({cpu:.1f}%)",
                    "action": "Consider scaling horizontally or optimizing code"
                })
            
            if self.config.workers < os.cpu_count():
                recommendations.append({
                    "type": "workers",
                    "priority": "medium",
                    "message": f"Worker count ({self.config.workers}) is less than CPU count ({os.cpu_count()})",
                    "action": "Consider increasing worker count for better utilization"
                })
        
        if not self.config.enable_uvloop:
            recommendations.append({
                "type": "event_loop",
                "priority": "medium",
                "message": "UVLoop is not enabled",
                "action": "Enable UVLoop for better async performance"
            })
        
        return {
            "recommendations": recommendations,
            "total_recommendations": len(recommendations),
            "high_priority": len([r for r in recommendations if r["priority"] == "high"])
        }


class DeploymentManager:
    """Manage production deployments."""
    
    def __init__(self, config: ProductionSettings):
        self.config = config
    
    def quick_deploy(self, environment: str) -> Dict[str, Any]:
        """Perform quick deployment."""
        # This would integrate with actual deployment systems
        # For now, return deployment configuration
        return {
            "environment": environment,
            "image": f"{self.config.container_registry}/{self.config.image_name}:{self.config.image_tag}",
            "configuration": self.config.get_deployment_config(),
            "status": "configured"
        }
    
    async def cleanup(self):
        """Cleanup deployment resources."""
        pass


# Quick utility functions
def get_system_info() -> Dict[str, Any]:
    """Quick access to system information."""
    return ProductionUtils.get_system_info()


def optimize_memory() -> Dict[str, Any]:
    """Quick memory optimization."""
    return ProductionUtils.optimize_memory()


# Export main components
__all__ = [
    "ProductionUtils",
    "SystemOptimizer",
    "DeploymentManager",
    "get_system_info",
    "optimize_memory"
] 