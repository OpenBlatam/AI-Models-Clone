"""
Models Package
=============

Data models and schemas for the copywriting system.
"""

from .requests import CopywritingRequest, BatchRequest, OptimizationRequest
from .responses import CopywritingResponse, BatchResponse, SystemMetrics
from .entities import CopywritingVariant, PerformanceMetrics

__all__ = [
    "CopywritingRequest",
    "BatchRequest", 
    "OptimizationRequest",
    "CopywritingResponse",
    "BatchResponse",
    "SystemMetrics",
    "CopywritingVariant",
    "PerformanceMetrics"
] 