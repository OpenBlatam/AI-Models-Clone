"""
Dependency resolution and validation module.
Handles dependency checking, circular dependency detection, and resolution strategies.
"""

from typing import Dict, List, Set, Optional, Tuple
from .dependency_structures import ServiceStatus, ServiceInfo


class DependencyResolver:
    """Resolves and validates service dependencies"""
    
    def __init__(self):
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependencies: Dict[str, Set[str]] = {}
    
    def add_dependency(self, service_name: str, dependency_name: str) -> None:
        """Add a dependency relationship"""
        if service_name not in self.dependency_graph:
            self.dependency_graph[service_name] = set()
        
        if dependency_name not in self.reverse_dependencies:
            self.reverse_dependencies[dependency_name] = set()
        
        self.dependency_graph[service_name].add(dependency_name)
        self.reverse_dependencies[dependency_name].add(service_name)
    
    def remove_dependency(self, service_name: str, dependency_name: str) -> None:
        """Remove a dependency relationship"""
        if service_name in self.dependency_graph:
            self.dependency_graph[service_name].discard(dependency_name)
        
        if dependency_name in self.reverse_dependencies:
            self.reverse_dependencies[dependency_name].discard(service_name)
    
    def get_dependencies(self, service_name: str) -> Set[str]:
        """Get all dependencies for a service"""
        return self.dependency_graph.get(service_name, set()).copy()
    
    def get_dependents(self, service_name: str) -> Set[str]:
        """Get all services that depend on this service"""
        return self.reverse_dependencies.get(service_name, set()).copy()
    
    def check_circular_dependencies(self) -> List[List[str]]:
        """Detect circular dependencies using DFS"""
        visited = set()
        rec_stack = set()
        cycles = []
        
        def dfs(node: str, path: List[str]) -> None:
            if node in rec_stack:
                # Found a cycle
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for dependency in self.dependency_graph.get(node, set()):
                dfs(dependency, path)
            
            path.pop()
            rec_stack.discard(node)
        
        for service in self.dependency_graph:
            if service not in visited:
                dfs(service, [])
        
        return cycles
    
    def get_topological_order(self) -> List[str]:
        """Get topological ordering of services"""
        if self.check_circular_dependencies():
            raise ValueError("Circular dependencies detected")
        
        # Kahn's algorithm for topological sort
        in_degree = {service: 0 for service in self.dependency_graph}
        
        # Calculate in-degrees
        for dependencies in self.dependency_graph.values():
            for dep in dependencies:
                if dep in in_degree:
                    in_degree[dep] += 1
        
        # Find services with no dependencies
        queue = [service for service, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            service = queue.pop(0)
            result.append(service)
            
            # Reduce in-degree for dependents
            for dependent in self.reverse_dependencies.get(service, set()):
                if dependent in in_degree:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)
        
        # Check if all services were processed
        if len(result) != len(self.dependency_graph):
            raise ValueError("Circular dependencies detected")
        
        return result
    
    def validate_dependencies(self, services: Dict[str, ServiceInfo]) -> List[str]:
        """Validate that all dependencies exist"""
        missing_deps = []
        
        for service_name, service_info in services.items():
            for dep in service_info.dependencies:
                if dep not in services:
                    missing_deps.append(f"{service_name} -> {dep}")
        
        return missing_deps
    
    def get_dependency_chain(self, service_name: str) -> List[str]:
        """Get the complete dependency chain for a service"""
        chain = []
        visited = set()
        
        def build_chain(node: str) -> None:
            if node in visited:
                return
            
            visited.add(node)
            
            # Add dependencies first
            for dep in self.dependency_graph.get(node, set()):
                build_chain(dep)
            
            chain.append(node)
        
        build_chain(service_name)
        return chain
    
    def get_impact_analysis(self, service_name: str) -> Dict[str, List[str]]:
        """Analyze the impact of stopping a service"""
        impact = {
            "direct_dependents": list(self.reverse_dependencies.get(service_name, set())),
            "all_dependents": [],
            "affected_services": []
        }
        
        # Find all services that would be affected
        affected = set()
        queue = [service_name]
        
        while queue:
            current = queue.pop(0)
            affected.add(current)
            
            for dependent in self.reverse_dependencies.get(current, set()):
                if dependent not in affected:
                    queue.append(dependent)
        
        impact["all_dependents"] = list(affected)
        impact["affected_services"] = list(affected)
        
        return impact
    
    def optimize_dependencies(self, services: Dict[str, ServiceInfo]) -> Dict[str, List[str]]:
        """Optimize dependency relationships"""
        optimized = {}
        
        for service_name, service_info in services.items():
            # Remove redundant dependencies
            essential_deps = set()
            
            for dep in service_info.dependencies:
                # Check if this dependency is really needed
                if self._is_essential_dependency(service_name, dep, services):
                    essential_deps.add(dep)
            
            optimized[service_name] = list(essential_deps)
        
        return optimized
    
    def _is_essential_dependency(self, service: str, dependency: str, services: Dict[str, ServiceInfo]) -> bool:
        """Check if a dependency is essential"""
        # Simple heuristic: check if removing the dependency breaks the service
        # This could be enhanced with more sophisticated analysis
        
        # Check if the dependency is a direct requirement
        if dependency in services[service].dependencies:
            return True
        
        # Check if it's required by other dependencies
        for dep in services[service].dependencies:
            if dependency in services[dep].dependencies:
                return True
        
        return False
