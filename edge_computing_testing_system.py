#!/usr/bin/env python3
"""
Edge Computing Testing System
=============================

This system implements edge computing infrastructure for distributed test
execution, bringing testing capabilities closer to data sources and users
for improved performance and reduced latency.
"""

import sys
import time
import json
import os
import asyncio
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import uuid
import socket
import ssl
from collections import defaultdict, deque
import random
import hashlib

class EdgeNodeType(Enum):
    """Types of edge computing nodes"""
    MOBILE_EDGE = "mobile_edge"
    FOG_NODE = "fog_node"
    EDGE_SERVER = "edge_server"
    IOT_GATEWAY = "iot_gateway"
    CLOUDLET = "cloudlet"
    MICRO_DATACENTER = "micro_datacenter"

class EdgeResourceType(Enum):
    """Types of edge computing resources"""
    CPU = "cpu"
    MEMORY = "memory"
    STORAGE = "storage"
    NETWORK = "network"
    GPU = "gpu"
    TPU = "tpu"
    FPGA = "fpga"

class TestExecutionStrategy(Enum):
    """Edge computing test execution strategies"""
    CLOSEST_EDGE = "closest_edge"
    LOAD_BALANCED = "load_balanced"
    RESOURCE_OPTIMIZED = "resource_optimized"
    LATENCY_OPTIMIZED = "latency_optimized"
    COST_OPTIMIZED = "cost_optimized"
    HYBRID_STRATEGY = "hybrid_strategy"

@dataclass
class EdgeNode:
    """Edge computing node representation"""
    node_id: str
    node_type: EdgeNodeType
    location: Tuple[float, float]  # (latitude, longitude)
    resources: Dict[EdgeResourceType, float]
    capabilities: List[str]
    status: str = "active"
    last_heartbeat: datetime = field(default_factory=datetime.now)
    current_load: float = 0.0
    network_latency: float = 0.0
    security_level: int = 1
    cost_per_hour: float = 0.0

@dataclass
class EdgeTestTask:
    """Test task for edge execution"""
    task_id: str
    test_id: str
    test_data: Dict[str, Any]
    resource_requirements: Dict[EdgeResourceType, float]
    priority: int = 1
    deadline: Optional[datetime] = None
    assigned_node: Optional[str] = None
    execution_status: str = "pending"
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None

@dataclass
class EdgeNetworkTopology:
    """Edge network topology representation"""
    nodes: Dict[str, EdgeNode]
    connections: Dict[str, List[str]]
    bandwidth_matrix: Dict[Tuple[str, str], float]
    latency_matrix: Dict[Tuple[str, str], float]
    reliability_matrix: Dict[Tuple[str, str], float]

class EdgeResourceManager:
    """Manages edge computing resources"""
    
    def __init__(self):
        self.edge_nodes: Dict[str, EdgeNode] = {}
        self.resource_allocations: Dict[str, Dict[EdgeResourceType, float]] = {}
        self.task_queue: deque = deque()
        self.executing_tasks: Dict[str, EdgeTestTask] = {}
        self.completed_tasks: List[EdgeTestTask] = []
        
        self.logger = logging.getLogger(__name__)
    
    def register_edge_node(self, node: EdgeNode):
        """Register a new edge node"""
        self.edge_nodes[node.node_id] = node
        self.resource_allocations[node.node_id] = {
            resource_type: 0.0 for resource_type in EdgeResourceType
        }
        self.logger.info(f"Registered edge node {node.node_id} of type {node.node_type.value}")
    
    def discover_edge_nodes(self, discovery_radius: float = 100.0) -> List[EdgeNode]:
        """Discover edge nodes in the network"""
        self.logger.info(f"Discovering edge nodes within {discovery_radius}km radius")
        
        # Simulate edge node discovery
        discovered_nodes = []
        
        # Create sample edge nodes
        sample_nodes = [
            EdgeNode(
                node_id="mobile_edge_1",
                node_type=EdgeNodeType.MOBILE_EDGE,
                location=(40.7128, -74.0060),  # New York
                resources={
                    EdgeResourceType.CPU: 4.0,
                    EdgeResourceType.MEMORY: 8.0,
                    EdgeResourceType.STORAGE: 64.0,
                    EdgeResourceType.NETWORK: 100.0
                },
                capabilities=["unit_tests", "integration_tests"],
                cost_per_hour=0.1
            ),
            EdgeNode(
                node_id="fog_node_1",
                node_type=EdgeNodeType.FOG_NODE,
                location=(40.7589, -73.9851),  # Manhattan
                resources={
                    EdgeResourceType.CPU: 8.0,
                    EdgeResourceType.MEMORY: 16.0,
                    EdgeResourceType.STORAGE: 256.0,
                    EdgeResourceType.NETWORK: 1000.0,
                    EdgeResourceType.GPU: 1.0
                },
                capabilities=["performance_tests", "load_tests", "ui_tests"],
                cost_per_hour=0.5
            ),
            EdgeNode(
                node_id="edge_server_1",
                node_type=EdgeNodeType.EDGE_SERVER,
                location=(40.6892, -74.0445),  # Brooklyn
                resources={
                    EdgeResourceType.CPU: 16.0,
                    EdgeResourceType.MEMORY: 32.0,
                    EdgeResourceType.STORAGE: 512.0,
                    EdgeResourceType.NETWORK: 10000.0,
                    EdgeResourceType.GPU: 2.0
                },
                capabilities=["security_tests", "compliance_tests", "api_tests"],
                cost_per_hour=1.0
            ),
            EdgeNode(
                node_id="iot_gateway_1",
                node_type=EdgeNodeType.IOT_GATEWAY,
                location=(40.7505, -73.9934),  # Midtown
                resources={
                    EdgeResourceType.CPU: 2.0,
                    EdgeResourceType.MEMORY: 4.0,
                    EdgeResourceType.STORAGE: 32.0,
                    EdgeResourceType.NETWORK: 100.0
                },
                capabilities=["iot_tests", "sensor_tests"],
                cost_per_hour=0.05
            ),
            EdgeNode(
                node_id="cloudlet_1",
                node_type=EdgeNodeType.CLOUDLET,
                location=(40.7282, -73.7949),  # Queens
                resources={
                    EdgeResourceType.CPU: 32.0,
                    EdgeResourceType.MEMORY: 64.0,
                    EdgeResourceType.STORAGE: 1024.0,
                    EdgeResourceType.NETWORK: 100000.0,
                    EdgeResourceType.GPU: 4.0,
                    EdgeResourceType.TPU: 1.0
                },
                capabilities=["ai_tests", "ml_tests", "big_data_tests"],
                cost_per_hour=2.0
            )
        ]
        
        for node in sample_nodes:
            self.register_edge_node(node)
            discovered_nodes.append(node)
        
        return discovered_nodes
    
    def calculate_node_distance(self, node1: EdgeNode, node2: EdgeNode) -> float:
        """Calculate distance between two edge nodes"""
        # Simple Euclidean distance calculation
        lat1, lon1 = node1.location
        lat2, lon2 = node2.location
        
        # Convert to approximate km (rough calculation)
        distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0
        return distance
    
    def find_optimal_nodes(self, task: EdgeTestTask, strategy: TestExecutionStrategy) -> List[EdgeNode]:
        """Find optimal edge nodes for task execution"""
        self.logger.info(f"Finding optimal nodes for task {task.task_id} using strategy {strategy.value}")
        
        suitable_nodes = []
        
        # Filter nodes by resource requirements
        for node in self.edge_nodes.values():
            if node.status != "active":
                continue
            
            # Check if node has sufficient resources
            can_execute = True
            for resource_type, required_amount in task.resource_requirements.items():
                available = node.resources.get(resource_type, 0.0) - self.resource_allocations[node.node_id][resource_type]
                if available < required_amount:
                    can_execute = False
                    break
            
            if can_execute:
                suitable_nodes.append(node)
        
        if not suitable_nodes:
            return []
        
        # Apply strategy-specific optimization
        if strategy == TestExecutionStrategy.CLOSEST_EDGE:
            # Sort by distance (assuming central location)
            central_location = (40.7128, -74.0060)  # New York center
            suitable_nodes.sort(key=lambda n: np.sqrt((n.location[0] - central_location[0])**2 + (n.location[1] - central_location[1])**2))
        
        elif strategy == TestExecutionStrategy.LOAD_BALANCED:
            # Sort by current load
            suitable_nodes.sort(key=lambda n: n.current_load)
        
        elif strategy == TestExecutionStrategy.RESOURCE_OPTIMIZED:
            # Sort by resource availability
            suitable_nodes.sort(key=lambda n: sum(n.resources.values()) - sum(self.resource_allocations[n.node_id].values()), reverse=True)
        
        elif strategy == TestExecutionStrategy.LATENCY_OPTIMIZED:
            # Sort by network latency
            suitable_nodes.sort(key=lambda n: n.network_latency)
        
        elif strategy == TestExecutionStrategy.COST_OPTIMIZED:
            # Sort by cost
            suitable_nodes.sort(key=lambda n: n.cost_per_hour)
        
        elif strategy == TestExecutionStrategy.HYBRID_STRATEGY:
            # Combine multiple factors
            def hybrid_score(node):
                distance_score = 1.0 / (1.0 + self.calculate_node_distance(node, EdgeNode("", EdgeNodeType.EDGE_SERVER, (40.7128, -74.0060), {}, [])))
                load_score = 1.0 - node.current_load
                resource_score = sum(node.resources.values()) / 100.0  # Normalize
                cost_score = 1.0 / (1.0 + node.cost_per_hour)
                latency_score = 1.0 / (1.0 + node.network_latency)
                
                return (distance_score * 0.2 + load_score * 0.3 + resource_score * 0.2 + cost_score * 0.15 + latency_score * 0.15)
            
            suitable_nodes.sort(key=hybrid_score, reverse=True)
        
        return suitable_nodes
    
    def allocate_resources(self, node_id: str, task: EdgeTestTask) -> bool:
        """Allocate resources for a task on a specific node"""
        node = self.edge_nodes.get(node_id)
        if not node:
            return False
        
        # Check resource availability
        for resource_type, required_amount in task.resource_requirements.items():
            available = node.resources.get(resource_type, 0.0) - self.resource_allocations[node_id][resource_type]
            if available < required_amount:
                return False
        
        # Allocate resources
        for resource_type, required_amount in task.resource_requirements.items():
            self.resource_allocations[node_id][resource_type] += required_amount
        
        # Update node load
        total_resources = sum(node.resources.values())
        allocated_resources = sum(self.resource_allocations[node_id].values())
        node.current_load = allocated_resources / total_resources if total_resources > 0 else 0.0
        
        self.logger.info(f"Allocated resources for task {task.task_id} on node {node_id}")
        return True
    
    def deallocate_resources(self, node_id: str, task: EdgeTestTask):
        """Deallocate resources after task completion"""
        for resource_type, required_amount in task.resource_requirements.items():
            self.resource_allocations[node_id][resource_type] -= required_amount
        
        # Update node load
        node = self.edge_nodes.get(node_id)
        if node:
            total_resources = sum(node.resources.values())
            allocated_resources = sum(self.resource_allocations[node_id].values())
            node.current_load = allocated_resources / total_resources if total_resources > 0 else 0.0
        
        self.logger.info(f"Deallocated resources for task {task.task_id} from node {node_id}")

class EdgeTestOrchestrator:
    """Orchestrates test execution across edge nodes"""
    
    def __init__(self):
        self.resource_manager = EdgeResourceManager()
        self.execution_strategy = TestExecutionStrategy.HYBRID_STRATEGY
        self.max_concurrent_tasks = 10
        self.task_timeout = 300  # 5 minutes
        
        self.logger = logging.getLogger(__name__)
    
    async def initialize_edge_network(self):
        """Initialize the edge computing network"""
        self.logger.info("Initializing edge computing network")
        
        # Discover edge nodes
        discovered_nodes = self.resource_manager.discover_edge_nodes()
        
        # Create network topology
        topology = self._create_network_topology(discovered_nodes)
        
        self.logger.info(f"Edge network initialized with {len(discovered_nodes)} nodes")
        return topology
    
    def _create_network_topology(self, nodes: List[EdgeNode]) -> EdgeNetworkTopology:
        """Create network topology from discovered nodes"""
        node_dict = {node.node_id: node for node in nodes}
        connections = {}
        bandwidth_matrix = {}
        latency_matrix = {}
        reliability_matrix = {}
        
        # Create connections between nearby nodes
        for node1 in nodes:
            connections[node1.node_id] = []
            for node2 in nodes:
                if node1.node_id != node2.node_id:
                    distance = self.resource_manager.calculate_node_distance(node1, node2)
                    
                    # Connect nodes within 50km
                    if distance < 50.0:
                        connections[node1.node_id].append(node2.node_id)
                        
                        # Calculate network metrics
                        bandwidth = max(100.0, 1000.0 - distance * 10)  # Mbps
                        latency = max(1.0, distance * 2)  # ms
                        reliability = max(0.8, 1.0 - distance / 100.0)
                        
                        bandwidth_matrix[(node1.node_id, node2.node_id)] = bandwidth
                        latency_matrix[(node1.node_id, node2.node_id)] = latency
                        reliability_matrix[(node1.node_id, node2.node_id)] = reliability
        
        return EdgeNetworkTopology(
            nodes=node_dict,
            connections=connections,
            bandwidth_matrix=bandwidth_matrix,
            latency_matrix=latency_matrix,
            reliability_matrix=reliability_matrix
        )
    
    async def submit_test_task(self, test_id: str, test_data: Dict[str, Any], 
                              resource_requirements: Dict[EdgeResourceType, float],
                              priority: int = 1, deadline: Optional[datetime] = None) -> str:
        """Submit a test task for edge execution"""
        task_id = f"task_{uuid.uuid4().hex[:16]}"
        
        task = EdgeTestTask(
            task_id=task_id,
            test_id=test_id,
            test_data=test_data,
            resource_requirements=resource_requirements,
            priority=priority,
            deadline=deadline
        )
        
        self.resource_manager.task_queue.append(task)
        self.logger.info(f"Submitted test task {task_id} for test {test_id}")
        
        return task_id
    
    async def execute_edge_tests(self, max_tasks: int = 20) -> Dict[str, Any]:
        """Execute tests on edge nodes"""
        self.logger.info(f"Starting edge test execution for up to {max_tasks} tasks")
        
        start_time = time.time()
        executed_tasks = 0
        
        # Process tasks from queue
        while self.resource_manager.task_queue and executed_tasks < max_tasks:
            if len(self.resource_manager.executing_tasks) >= self.max_concurrent_tasks:
                await asyncio.sleep(0.1)  # Wait for some tasks to complete
                continue
            
            # Get next task
            task = self.resource_manager.task_queue.popleft()
            
            # Find optimal nodes
            optimal_nodes = self.resource_manager.find_optimal_nodes(task, self.execution_strategy)
            
            if not optimal_nodes:
                self.logger.warning(f"No suitable nodes found for task {task.task_id}")
                task.execution_status = "failed"
                task.result = {"error": "No suitable edge nodes available"}
                self.resource_manager.completed_tasks.append(task)
                continue
            
            # Assign task to best node
            best_node = optimal_nodes[0]
            task.assigned_node = best_node.node_id
            
            # Allocate resources
            if not self.resource_manager.allocate_resources(best_node.node_id, task):
                self.logger.warning(f"Failed to allocate resources for task {task.task_id}")
                task.execution_status = "failed"
                task.result = {"error": "Resource allocation failed"}
                self.resource_manager.completed_tasks.append(task)
                continue
            
            # Execute task
            self.resource_manager.executing_tasks[task.task_id] = task
            asyncio.create_task(self._execute_task_on_edge(task, best_node))
            
            executed_tasks += 1
        
        # Wait for all tasks to complete
        while self.resource_manager.executing_tasks:
            await asyncio.sleep(0.1)
        
        execution_time = time.time() - start_time
        
        return {
            'edge_execution_summary': {
                'total_tasks_submitted': executed_tasks,
                'tasks_completed': len(self.resource_manager.completed_tasks),
                'tasks_failed': len([t for t in self.resource_manager.completed_tasks if t.execution_status == "failed"]),
                'execution_time': execution_time,
                'edge_nodes_used': len(set(t.assigned_node for t in self.resource_manager.completed_tasks if t.assigned_node)),
                'average_execution_time': self._calculate_average_execution_time()
            },
            'edge_node_utilization': self._calculate_node_utilization(),
            'edge_performance_metrics': self._calculate_performance_metrics(),
            'edge_insights': self._generate_edge_insights()
        }
    
    async def _execute_task_on_edge(self, task: EdgeTestTask, node: EdgeNode):
        """Execute a task on an edge node"""
        self.logger.info(f"Executing task {task.task_id} on edge node {node.node_id}")
        
        task.execution_status = "running"
        task.started_at = datetime.now()
        
        try:
            # Simulate task execution
            execution_time = random.uniform(0.1, 2.0)
            await asyncio.sleep(execution_time)
            
            # Simulate success/failure based on node reliability
            success_probability = 0.9 - (node.current_load * 0.2)  # Lower success rate under high load
            success = random.random() < success_probability
            
            if success:
                task.execution_status = "completed"
                task.result = {
                    "success": True,
                    "execution_time": execution_time,
                    "node_id": node.node_id,
                    "node_type": node.node_type.value,
                    "test_results": {
                        "passed": random.choice([True, False]),
                        "coverage": random.uniform(0.7, 1.0),
                        "performance_score": random.uniform(0.6, 1.0)
                    }
                }
            else:
                task.execution_status = "failed"
                task.result = {
                    "success": False,
                    "error": "Test execution failed on edge node",
                    "node_id": node.node_id,
                    "execution_time": execution_time
                }
            
        except Exception as e:
            task.execution_status = "failed"
            task.result = {
                "success": False,
                "error": str(e),
                "node_id": node.node_id
            }
        
        finally:
            task.completed_at = datetime.now()
            
            # Deallocate resources
            if task.assigned_node:
                self.resource_manager.deallocate_resources(task.assigned_node, task)
            
            # Move to completed tasks
            self.resource_manager.completed_tasks.append(task)
            if task.task_id in self.resource_manager.executing_tasks:
                del self.resource_manager.executing_tasks[task.task_id]
    
    def _calculate_average_execution_time(self) -> float:
        """Calculate average execution time for completed tasks"""
        completed_tasks = [t for t in self.resource_manager.completed_tasks if t.completed_at and t.started_at]
        if not completed_tasks:
            return 0.0
        
        total_time = sum((t.completed_at - t.started_at).total_seconds() for t in completed_tasks)
        return total_time / len(completed_tasks)
    
    def _calculate_node_utilization(self) -> Dict[str, Any]:
        """Calculate edge node utilization metrics"""
        utilization = {}
        
        for node_id, node in self.resource_manager.edge_nodes.items():
            total_resources = sum(node.resources.values())
            allocated_resources = sum(self.resource_manager.resource_allocations[node_id].values())
            
            utilization[node_id] = {
                'node_type': node.node_type.value,
                'current_load': node.current_load,
                'resource_utilization': allocated_resources / total_resources if total_resources > 0 else 0.0,
                'tasks_executed': len([t for t in self.resource_manager.completed_tasks if t.assigned_node == node_id]),
                'location': node.location,
                'cost_per_hour': node.cost_per_hour
            }
        
        return utilization
    
    def _calculate_performance_metrics(self) -> Dict[str, Any]:
        """Calculate edge computing performance metrics"""
        completed_tasks = [t for t in self.resource_manager.completed_tasks if t.execution_status == "completed"]
        failed_tasks = [t for t in self.resource_manager.completed_tasks if t.execution_status == "failed"]
        
        total_tasks = len(self.resource_manager.completed_tasks)
        success_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0.0
        
        # Calculate average latency
        latencies = []
        for task in completed_tasks:
            if task.started_at and task.completed_at:
                latency = (task.completed_at - task.started_at).total_seconds()
                latencies.append(latency)
        
        average_latency = sum(latencies) / len(latencies) if latencies else 0.0
        
        # Calculate throughput
        total_execution_time = sum(latencies) if latencies else 1.0
        throughput = len(completed_tasks) / total_execution_time if total_execution_time > 0 else 0.0
        
        return {
            'success_rate': success_rate,
            'average_latency': average_latency,
            'throughput': throughput,
            'total_tasks': total_tasks,
            'completed_tasks': len(completed_tasks),
            'failed_tasks': len(failed_tasks),
            'edge_nodes_active': len([n for n in self.resource_manager.edge_nodes.values() if n.status == "active"])
        }
    
    def _generate_edge_insights(self) -> Dict[str, Any]:
        """Generate insights about edge computing performance"""
        insights = {
            'node_type_performance': {},
            'resource_utilization_analysis': {},
            'geographic_distribution': {},
            'cost_analysis': {},
            'recommendations': []
        }
        
        # Analyze performance by node type
        by_node_type = defaultdict(list)
        for task in self.resource_manager.completed_tasks:
            if task.assigned_node:
                node = self.resource_manager.edge_nodes.get(task.assigned_node)
                if node:
                    by_node_type[node.node_type.value].append(task)
        
        for node_type, tasks in by_node_type.items():
            success_rate = len([t for t in tasks if t.execution_status == "completed"]) / len(tasks)
            avg_execution_time = self._calculate_average_execution_time_for_tasks(tasks)
            
            insights['node_type_performance'][node_type] = {
                'success_rate': success_rate,
                'average_execution_time': avg_execution_time,
                'task_count': len(tasks)
            }
        
        # Resource utilization analysis
        total_resources = sum(sum(node.resources.values()) for node in self.resource_manager.edge_nodes.values())
        total_allocated = sum(sum(alloc.values()) for alloc in self.resource_manager.resource_allocations.values())
        
        insights['resource_utilization_analysis'] = {
            'overall_utilization': total_allocated / total_resources if total_resources > 0 else 0.0,
            'most_utilized_resource': self._find_most_utilized_resource(),
            'least_utilized_resource': self._find_least_utilized_resource()
        }
        
        # Geographic distribution
        locations = [node.location for node in self.resource_manager.edge_nodes.values()]
        insights['geographic_distribution'] = {
            'total_nodes': len(locations),
            'geographic_spread': self._calculate_geographic_spread(locations),
            'average_distance_between_nodes': self._calculate_average_node_distance()
        }
        
        # Cost analysis
        total_cost = sum(node.cost_per_hour for node in self.resource_manager.edge_nodes.values())
        insights['cost_analysis'] = {
            'total_hourly_cost': total_cost,
            'cost_per_completed_task': total_cost / len([t for t in self.resource_manager.completed_tasks if t.execution_status == "completed"]) if self.resource_manager.completed_tasks else 0.0,
            'most_cost_effective_node_type': self._find_most_cost_effective_node_type()
        }
        
        # Generate recommendations
        insights['recommendations'] = self._generate_edge_recommendations()
        
        return insights
    
    def _calculate_average_execution_time_for_tasks(self, tasks: List[EdgeTestTask]) -> float:
        """Calculate average execution time for specific tasks"""
        execution_times = []
        for task in tasks:
            if task.started_at and task.completed_at:
                execution_time = (task.completed_at - task.started_at).total_seconds()
                execution_times.append(execution_time)
        
        return sum(execution_times) / len(execution_times) if execution_times else 0.0
    
    def _find_most_utilized_resource(self) -> str:
        """Find the most utilized resource type"""
        resource_usage = defaultdict(float)
        
        for node_id, allocations in self.resource_manager.resource_allocations.items():
            for resource_type, amount in allocations.items():
                resource_usage[resource_type.value] += amount
        
        return max(resource_usage.items(), key=lambda x: x[1])[0] if resource_usage else "none"
    
    def _find_least_utilized_resource(self) -> str:
        """Find the least utilized resource type"""
        resource_usage = defaultdict(float)
        
        for node_id, allocations in self.resource_manager.resource_allocations.items():
            for resource_type, amount in allocations.items():
                resource_usage[resource_type.value] += amount
        
        return min(resource_usage.items(), key=lambda x: x[1])[0] if resource_usage else "none"
    
    def _calculate_geographic_spread(self, locations: List[Tuple[float, float]]) -> float:
        """Calculate geographic spread of nodes"""
        if len(locations) < 2:
            return 0.0
        
        distances = []
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                lat1, lon1 = locations[i]
                lat2, lon2 = locations[j]
                distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0
                distances.append(distance)
        
        return max(distances) if distances else 0.0
    
    def _calculate_average_node_distance(self) -> float:
        """Calculate average distance between nodes"""
        locations = [node.location for node in self.resource_manager.edge_nodes.values()]
        if len(locations) < 2:
            return 0.0
        
        total_distance = 0.0
        pair_count = 0
        
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                lat1, lon1 = locations[i]
                lat2, lon2 = locations[j]
                distance = np.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111.0
                total_distance += distance
                pair_count += 1
        
        return total_distance / pair_count if pair_count > 0 else 0.0
    
    def _find_most_cost_effective_node_type(self) -> str:
        """Find the most cost-effective node type"""
        node_type_costs = defaultdict(list)
        
        for node in self.resource_manager.edge_nodes.values():
            node_type_costs[node.node_type.value].append(node.cost_per_hour)
        
        avg_costs = {node_type: sum(costs) / len(costs) for node_type, costs in node_type_costs.items()}
        
        return min(avg_costs.items(), key=lambda x: x[1])[0] if avg_costs else "none"
    
    def _generate_edge_recommendations(self) -> List[str]:
        """Generate recommendations for edge computing optimization"""
        recommendations = []
        
        # Check resource utilization
        total_resources = sum(sum(node.resources.values()) for node in self.resource_manager.edge_nodes.values())
        total_allocated = sum(sum(alloc.values()) for alloc in self.resource_manager.resource_allocations.values())
        utilization = total_allocated / total_resources if total_resources > 0 else 0.0
        
        if utilization > 0.8:
            recommendations.append("High resource utilization detected - consider adding more edge nodes")
        elif utilization < 0.3:
            recommendations.append("Low resource utilization - consider consolidating edge nodes")
        
        # Check success rate
        completed_tasks = [t for t in self.resource_manager.completed_tasks if t.execution_status == "completed"]
        total_tasks = len(self.resource_manager.completed_tasks)
        success_rate = len(completed_tasks) / total_tasks if total_tasks > 0 else 0.0
        
        if success_rate < 0.8:
            recommendations.append("Low success rate - investigate edge node reliability and resource allocation")
        
        # Check geographic distribution
        locations = [node.location for node in self.resource_manager.edge_nodes.values()]
        spread = self._calculate_geographic_spread(locations)
        
        if spread < 10.0:
            recommendations.append("Nodes are clustered - consider distributing edge nodes geographically")
        
        # Check cost efficiency
        total_cost = sum(node.cost_per_hour for node in self.resource_manager.edge_nodes.values())
        cost_per_task = total_cost / len(completed_tasks) if completed_tasks else 0.0
        
        if cost_per_task > 1.0:
            recommendations.append("High cost per task - optimize resource allocation and node selection")
        
        return recommendations

class EdgeComputingTestingSystem:
    """Main Edge Computing Testing System"""
    
    def __init__(self):
        self.orchestrator = EdgeTestOrchestrator()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
    
    async def run_edge_testing(self, num_tests: int = 15) -> Dict[str, Any]:
        """Run edge computing-based testing"""
        self.logger.info("Starting edge computing-based testing system")
        
        # Initialize edge network
        topology = await self.orchestrator.initialize_edge_network()
        
        # Submit test tasks
        task_ids = []
        for i in range(num_tests):
            test_id = f"edge_test_{i}"
            test_data = {
                'name': f'Edge Test {i}',
                'type': random.choice(['unit', 'integration', 'performance', 'security']),
                'complexity': random.uniform(0.1, 1.0)
            }
            
            # Define resource requirements based on test type
            resource_requirements = {
                EdgeResourceType.CPU: random.uniform(0.5, 4.0),
                EdgeResourceType.MEMORY: random.uniform(1.0, 8.0),
                EdgeResourceType.STORAGE: random.uniform(1.0, 16.0),
                EdgeResourceType.NETWORK: random.uniform(10.0, 100.0)
            }
            
            # Add GPU requirement for performance tests
            if test_data['type'] == 'performance':
                resource_requirements[EdgeResourceType.GPU] = random.uniform(0.1, 1.0)
            
            task_id = await self.orchestrator.submit_test_task(
                test_id, test_data, resource_requirements
            )
            task_ids.append(task_id)
        
        # Execute tests
        execution_results = await self.orchestrator.execute_edge_tests(num_tests)
        
        return {
            'edge_testing_summary': execution_results['edge_execution_summary'],
            'edge_node_utilization': execution_results['edge_node_utilization'],
            'edge_performance_metrics': execution_results['edge_performance_metrics'],
            'edge_insights': execution_results['edge_insights'],
            'task_ids': task_ids,
            'network_topology': {
                'total_nodes': len(topology.nodes),
                'node_types': list(set(node.node_type.value for node in topology.nodes.values())),
                'total_connections': sum(len(connections) for connections in topology.connections.values()) // 2
            }
        }

async def main():
    """Main function to demonstrate Edge Computing Testing System"""
    print("🌐 Edge Computing Testing System")
    print("=" * 50)
    
    # Initialize edge testing system
    edge_system = EdgeComputingTestingSystem()
    
    # Run edge testing
    results = await edge_system.run_edge_testing(num_tests=20)
    
    # Display results
    print("\n🎯 Edge Computing Testing Results:")
    summary = results['edge_testing_summary']
    print(f"  📊 Total Tasks: {summary['total_tasks_submitted']}")
    print(f"  ✅ Completed Tasks: {summary['tasks_completed']}")
    print(f"  ❌ Failed Tasks: {summary['tasks_failed']}")
    print(f"  ⏱️  Execution Time: {summary['execution_time']:.2f}s")
    print(f"  🌐 Edge Nodes Used: {summary['edge_nodes_used']}")
    
    print("\n🌐 Edge Node Utilization:")
    for node_id, utilization in results['edge_node_utilization'].items():
        print(f"  📍 {node_id} ({utilization['node_type']}):")
        print(f"    Load: {utilization['current_load']:.2f}")
        print(f"    Tasks: {utilization['tasks_executed']}")
        print(f"    Cost: ${utilization['cost_per_hour']:.2f}/hour")
    
    print("\n📊 Edge Performance Metrics:")
    metrics = results['edge_performance_metrics']
    print(f"  📈 Success Rate: {metrics['success_rate']:.2%}")
    print(f"  ⚡ Average Latency: {metrics['average_latency']:.3f}s")
    print(f"  🚀 Throughput: {metrics['throughput']:.2f} tasks/s")
    print(f"  🖥️  Active Nodes: {metrics['edge_nodes_active']}")
    
    print("\n💡 Edge Insights:")
    insights = results['edge_insights']
    print(f"  🏆 Best Node Type: {max(insights['node_type_performance'].items(), key=lambda x: x[1]['success_rate'])[0]}")
    print(f"  📊 Resource Utilization: {insights['resource_utilization_analysis']['overall_utilization']:.2%}")
    print(f"  🌍 Geographic Spread: {insights['geographic_distribution']['geographic_spread']:.1f}km")
    print(f"  💰 Total Hourly Cost: ${insights['cost_analysis']['total_hourly_cost']:.2f}")
    
    print("\n🚀 Edge Recommendations:")
    for recommendation in insights['recommendations']:
        print(f"  • {recommendation}")
    
    print("\n🎉 Edge Computing Testing System demonstration completed!")
    
    return results

if __name__ == "__main__":
    asyncio.run(main())
