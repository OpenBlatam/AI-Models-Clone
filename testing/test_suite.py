"""
Test Suite for Instagram Captions API v10.0
Test organization, grouping, and management.
"""
import inspect
import time
from typing import Dict, Any, Optional, List, Callable, Type, Union
from dataclasses import dataclass, field
from datetime import datetime
import logging

from .test_result import TestResult, TestStatus

logger = logging.getLogger(__name__)

@dataclass
class TestCase:
    """Represents a test case."""
    
    name: str
    test_function: Callable
    test_class: Optional[Type] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    priority: str = "normal"  # low, normal, high, critical
    timeout: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)
    skip_condition: Optional[Callable] = None
    setup_function: Optional[Callable] = None
    teardown_function: Optional[Callable] = None
    
    def __post_init__(self):
        """Extract description from docstring if not provided."""
        if not self.description and self.test_function.__doc__:
            self.description = self.test_function.__doc__.strip().split('\n')[0]
    
    def should_skip(self, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if the test should be skipped."""
        if self.skip_condition:
            try:
                return bool(self.skip_condition(context or {}))
            except Exception as e:
                logger.warning(f"Error in skip condition for {self.name}: {e}")
                return False
        return False
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get test case metadata."""
        return {
            'name': self.name,
            'description': self.description,
            'tags': self.tags,
            'priority': self.priority,
            'timeout': self.timeout,
            'dependencies': self.dependencies,
            'module': self.test_function.__module__,
            'function': self.test_function.__name__,
            'class': self.test_class.__name__ if self.test_class else None
        }

class TestSuite:
    """Organizes and manages test cases."""
    
    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self.test_cases: Dict[str, TestCase] = {}
        self.test_groups: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        
        # Metadata
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.tags: List[str] = []
        self.priority: str = "normal"
        
        # Statistics
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.error_tests = 0
    
    def add_test(self, test_function: Callable, name: Optional[str] = None,
                 description: Optional[str] = None, tags: Optional[List[str]] = None,
                 priority: str = "normal", timeout: Optional[float] = None,
                 dependencies: Optional[List[str]] = None, 
                 skip_condition: Optional[Callable] = None,
                 setup_function: Optional[Callable] = None,
                 teardown_function: Optional[Callable] = None,
                 test_class: Optional[Type] = None) -> str:
        """Add a test case to the suite."""
        if name is None:
            name = test_function.__name__
        
        if name in self.test_cases:
            logger.warning(f"Test case '{name}' already exists, overwriting")
        
        test_case = TestCase(
            name=name,
            test_function=test_function,
            test_class=test_class,
            description=description,
            tags=tags or [],
            priority=priority,
            timeout=timeout,
            dependencies=dependencies or [],
            skip_condition=skip_condition,
            setup_function=setup_function,
            teardown_function=teardown_function
        )
        
        self.test_cases[name] = test_case
        self.total_tests += 1
        self.modified_at = datetime.now()
        
        logger.debug(f"Added test case: {name}")
        return name
    
    def remove_test(self, name: str) -> bool:
        """Remove a test case from the suite."""
        if name in self.test_cases:
            del self.test_cases[name]
            self.total_tests -= 1
            self.modified_at = datetime.now()
            
            # Remove from groups
            for group_tests in self.test_groups.values():
                if name in group_tests:
                    group_tests.remove(name)
            
            # Remove from execution order
            if name in self.execution_order:
                self.execution_order.remove(name)
            
            logger.debug(f"Removed test case: {name}")
            return True
        
        return False
    
    def create_group(self, group_name: str, test_names: Optional[List[str]] = None,
                     description: Optional[str] = None) -> bool:
        """Create a test group."""
        if group_name in self.test_groups:
            logger.warning(f"Test group '{group_name}' already exists, updating")
        
        self.test_groups[group_name] = test_names or []
        
        if description:
            # Store description in metadata
            if not hasattr(self, 'group_descriptions'):
                self.group_descriptions = {}
            self.group_descriptions[group_name] = description
        
        logger.debug(f"Created test group: {group_name} with {len(test_names or [])} tests")
        return True
    
    def add_to_group(self, group_name: str, test_name: str) -> bool:
        """Add a test to a group."""
        if group_name not in self.test_groups:
            self.create_group(group_name)
        
        if test_name not in self.test_cases:
            logger.error(f"Test case '{test_name}' not found")
            return False
        
        if test_name not in self.test_groups[group_name]:
            self.test_groups[group_name].append(test_name)
            logger.debug(f"Added test '{test_name}' to group '{group_name}'")
            return True
        
        return False
    
    def remove_from_group(self, group_name: str, test_name: str) -> bool:
        """Remove a test from a group."""
        if group_name in self.test_groups and test_name in self.test_groups[group_name]:
            self.test_groups[group_name].remove(test_name)
            logger.debug(f"Removed test '{test_name}' from group '{group_name}'")
            return True
        
        return False
    
    def get_tests_by_group(self, group_name: str) -> List[TestCase]:
        """Get all tests in a group."""
        if group_name not in self.test_groups:
            return []
        
        tests = []
        for test_name in self.test_groups[group_name]:
            if test_name in self.test_cases:
                tests.append(self.test_cases[test_name])
        
        return tests
    
    def get_tests_by_tag(self, tag: str) -> List[TestCase]:
        """Get all tests with a specific tag."""
        return [test for test in self.test_cases.values() if tag in test.tags]
    
    def get_tests_by_priority(self, priority: str) -> List[TestCase]:
        """Get all tests with a specific priority."""
        return [test for test in self.test_cases.values() if test.priority == priority]
    
    def get_tests_by_dependency(self, dependency: str) -> List[TestCase]:
        """Get all tests that depend on a specific test."""
        return [test for test in self.test_cases.values() if dependency in test.dependencies]
    
    def set_execution_order(self, test_names: List[str]) -> bool:
        """Set the execution order for tests."""
        # Validate that all test names exist
        for name in test_names:
            if name not in self.test_cases:
                logger.error(f"Test case '{name}' not found in execution order")
                return False
        
        self.execution_order = test_names.copy()
        logger.debug(f"Set execution order for {len(test_names)} tests")
        return True
    
    def get_execution_order(self) -> List[TestCase]:
        """Get tests in execution order."""
        if not self.execution_order:
            # Return all tests if no order specified
            return list(self.test_cases.values())
        
        ordered_tests = []
        for name in self.execution_order:
            if name in self.test_cases:
                ordered_tests.append(self.test_cases[name])
        
        return ordered_tests
    
    def get_dependency_order(self) -> List[TestCase]:
        """Get tests in dependency order (topological sort)."""
        # Create dependency graph
        graph = {}
        in_degree = {}
        
        for test_name in self.test_cases:
            graph[test_name] = []
            in_degree[test_name] = 0
        
        for test_name, test_case in self.test_cases.items():
            for dep in test_case.dependencies:
                if dep in self.test_cases:
                    graph[dep].append(test_name)
                    in_degree[test_name] += 1
        
        # Topological sort using Kahn's algorithm
        result = []
        queue = [name for name, degree in in_degree.items() if degree == 0]
        
        while queue:
            current = queue.pop(0)
            result.append(self.test_cases[current])
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        if len(result) != len(self.test_cases):
            logger.warning("Circular dependency detected in tests")
            # Return all tests if circular dependency
            return list(self.test_cases.values())
        
        return result
    
    def filter_tests(self, tags: Optional[List[str]] = None,
                     priority: Optional[str] = None,
                     groups: Optional[List[str]] = None,
                     exclude_tags: Optional[List[str]] = None) -> List[TestCase]:
        """Filter tests based on criteria."""
        filtered_tests = list(self.test_cases.values())
        
        # Filter by tags
        if tags:
            filtered_tests = [test for test in filtered_tests 
                            if any(tag in test.tags for tag in tags)]
        
        # Filter by priority
        if priority:
            filtered_tests = [test for test in filtered_tests 
                            if test.priority == priority]
        
        # Filter by groups
        if groups:
            group_tests = set()
            for group in groups:
                if group in self.test_groups:
                    group_tests.update(self.test_groups[group])
            filtered_tests = [test for test in filtered_tests 
                            if test.name in group_tests]
        
        # Exclude by tags
        if exclude_tags:
            filtered_tests = [test for test in filtered_tests 
                            if not any(tag in test.tags for tag in exclude_tags)]
        
        return filtered_tests
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get test suite statistics."""
        return {
            'name': self.name,
            'description': self.description,
            'total_tests': self.total_tests,
            'passed_tests': self.passed_tests,
            'failed_tests': self.failed_tests,
            'skipped_tests': self.skipped_tests,
            'error_tests': self.error_tests,
            'success_rate': (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0,
            'groups': list(self.test_groups.keys()),
            'tags': list(set(tag for test in self.test_cases.values() for tag in test.tags)),
            'priorities': list(set(test.priority for test in self.test_cases.values())),
            'created_at': self.created_at.isoformat(),
            'modified_at': self.modified_at.isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a comprehensive summary of the test suite."""
        summary = self.get_statistics()
        
        # Add test details
        summary['tests'] = {}
        for test_name, test_case in self.test_cases.items():
            summary['tests'][test_name] = test_case.get_metadata()
        
        # Add group details
        summary['groups'] = {}
        for group_name, test_names in self.test_groups.items():
            summary['groups'][group_name] = {
                'test_count': len(test_names),
                'tests': test_names,
                'description': getattr(self, 'group_descriptions', {}).get(group_name)
            }
        
        return summary
    
    def export_to_file(self, file_path: str, format: str = "json") -> bool:
        """Export test suite to file."""
        try:
            summary = self.get_summary()
            
            if format.lower() == "json":
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(summary, f, ensure_ascii=False, indent=2, default=str)
            
            elif format.lower() == "yaml":
                import yaml
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(summary, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Test suite exported to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export test suite: {e}")
            return False
    
    def clear_results(self):
        """Clear test execution results."""
        self.passed_tests = 0
        self.failed_tests = 0
        self.skipped_tests = 0
        self.error_tests = 0
        logger.debug("Cleared test suite results")
    
    def __str__(self) -> str:
        """String representation."""
        return f"TestSuite({self.name}, {self.total_tests} tests)"
    
    def __repr__(self) -> str:
        """Detailed representation."""
        return f"TestSuite(name='{self.name}', total_tests={self.total_tests}, groups={list(self.test_groups.keys())})"






