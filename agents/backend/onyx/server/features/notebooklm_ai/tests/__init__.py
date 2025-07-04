"""
Comprehensive Test Suite
🧪 Testing all components and integrations
"""

from .test_integration import TestFullSystemIntegration, TestPerformanceBenchmarks

__version__ = "1.0.0"
__author__ = "NotebookLM AI Team"
__description__ = "Comprehensive test suite for NotebookLM AI system"

__all__ = [
    "TestFullSystemIntegration",
    "TestPerformanceBenchmarks"
]

# Test suite metadata
TEST_SUITE_INFO = {
    "name": "notebooklm-ai-tests",
    "version": __version__,
    "description": __description__,
    "test_categories": [
        "Integration Tests",
        "Performance Benchmarks",
        "Component Tests",
        "End-to-End Tests"
    ],
    "test_components": [
        "Ultra Performance Boost",
        "ML Model Integration", 
        "NLP Engine",
        "Ultra Optimized Engine"
    ]
} 