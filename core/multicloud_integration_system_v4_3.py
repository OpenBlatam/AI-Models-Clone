"""
Sistema de Integración Multi-Cloud Automática v4.3
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Integración automática con múltiples proveedores cloud
- Balanceo de carga inteligente entre clouds
- Optimización de costos multi-cloud
- Migración automática de workloads
- Gestión unificada de recursos
"""

import asyncio
import time
import json
import logging
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

# Cloud provider imports
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False
    print("Warning: boto3 not available, AWS integration disabled")

try:
    from google.cloud import compute_v1
    from google.cloud import storage
    GCP_AVAILABLE = True
except ImportError:
    GCP_AVAILABLE = False
    print("Warning: google-cloud not available, GCP integration disabled")

try:
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.storage import StorageManagementClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    print("Warning: azure-mgmt not available, Azure integration disabled")

# Multi-Cloud Integration Components
@dataclass
class CloudProvider:
    """Cloud provider configuration and status"""
    provider_id: str
    name: str
    region: str
    credentials: Dict[str, Any]
    status: str  # active, inactive, error
    cost_per_hour: float
    performance_score: float
    availability_zone: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class WorkloadDistribution:
    """Workload distribution across cloud providers"""
    distribution_id: str
    timestamp: datetime
    workload_name: str
    total_resources: Dict[str, float]
    provider_allocations: Dict[str, Dict[str, float]]
    cost_distribution: Dict[str, float]
    performance_metrics: Dict[str, float]
    optimization_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CloudMigration:
    """Cloud migration plan and execution"""
    migration_id: str
    timestamp: datetime
    source_provider: str
    target_provider: str
    workload_name: str
    migration_type: str  # full, partial, failover
    estimated_duration: int  # minutes
    estimated_cost: float
    risk_assessment: str
    rollback_plan: str
    status: str  # planned, in_progress, completed, failed
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LoadBalancingDecision:
    """Intelligent load balancing decision"""
    decision_id: str
    timestamp: datetime
    workload_name: str
    current_distribution: Dict[str, float]
    recommended_distribution: Dict[str, float]
    reasoning: List[str]
    expected_improvements: Dict[str, float]
    confidence: float
    implementation_priority: int
    metadata: Dict[str, Any] = field(default_factory=dict)

class MultiCloudManager:
    """Manages multiple cloud providers and their integration"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers = {}
        self.workloads = {}
        self.migration_history = deque(maxlen=1000)
        self.balancing_history = deque(maxlen=1000)
        self.cost_history = deque(maxlen=10000)
        
        # Initialize cloud providers
        self._initialize_providers()
        
        # Load balancing algorithm
        self.load_balancer = IntelligentLoadBalancer(config)
        
        # Cost optimizer
        self.cost_optimizer = MultiCloudCostOptimizer(config)
        
    def _initialize_providers(self):
        """Initialize cloud provider connections"""
        provider_configs = self.config.get('cloud_providers', {})
        
        for provider_id, provider_config in provider_configs.items():
            try:
                provider = self._create_provider(provider_id, provider_config)
                if provider:
                    self.providers[provider_id] = provider
                    print(f"✅ Proveedor {provider.name} inicializado")
                    
            except Exception as e:
                print(f"❌ Error inicializando proveedor {provider_id}: {e}")
                continue
    
    def _create_provider(self, provider_id: str, config: Dict[str, Any]) -> Optional[CloudProvider]:
        """Create cloud provider instance"""
        provider_type = config.get('type', 'unknown')
        
        if provider_type == 'aws' and AWS_AVAILABLE:
            return self._create_aws_provider(provider_id, config)
        elif provider_type == 'gcp' and GCP_AVAILABLE:
            return self._create_gcp_provider(provider_id, config)
        elif provider_type == 'azure' and AZURE_AVAILABLE:
            return self._create_azure_provider(provider_id, config)
        else:
            print(f"⚠️ Proveedor {provider_type} no disponible o no configurado")
            return None
    
    def _create_aws_provider(self, provider_id: str, config: Dict[str, Any]) -> CloudProvider:
        """Create AWS provider instance"""
        try:
            # Test AWS credentials
            session = boto3.Session(
                aws_access_key_id=config['credentials']['access_key'],
                aws_secret_access_key=config['credentials']['secret_key'],
                region_name=config['region']
            )
            
            # Test connection
            ec2 = session.client('ec2')
            ec2.describe_regions()
            
            return CloudProvider(
                provider_id=provider_id,
                name=f"AWS {config['region']}",
                region=config['region'],
                credentials=config['credentials'],
                status='active',
                cost_per_hour=config.get('cost_per_hour', 0.10),
                performance_score=config.get('performance_score', 0.85),
                availability_zone=config.get('availability_zone', 'us-west-2a'),
                metadata={
                    'session': session,
                    'provider_type': 'aws',
                    'services': config.get('services', ['ec2', 's3', 'lambda'])
                }
            )
            
        except Exception as e:
            print(f"Error creando proveedor AWS: {e}")
            return None
    
    def _create_gcp_provider(self, provider_id: str, config: Dict[str, Any]) -> CloudProvider:
        """Create GCP provider instance"""
        try:
            # Test GCP credentials
            compute_client = compute_v1.InstancesClient()
            
            return CloudProvider(
                provider_id=provider_id,
                name=f"GCP {config['region']}",
                region=config['region'],
                credentials=config['credentials'],
                status='active',
                cost_per_hour=config.get('cost_per_hour', 0.12),
                performance_score=config.get('performance_score', 0.80),
                availability_zone=config.get('availability_zone', 'us-west1-a'),
                metadata={
                    'compute_client': compute_client,
                    'provider_type': 'gcp',
                    'services': config.get('services', ['compute', 'storage', 'functions'])
                }
            )
            
        except Exception as e:
            print(f"Error creando proveedor GCP: {e}")
            return None
    
    def _create_azure_provider(self, provider_id: str, config: Dict[str, Any]) -> CloudProvider:
        """Create Azure provider instance"""
        try:
            # Test Azure credentials
            compute_client = ComputeManagementClient(
                credential=config['credentials']['credential'],
                subscription_id=config['credentials']['subscription_id']
            )
            
            return CloudProvider(
                provider_id=provider_id,
                name=f"Azure {config['region']}",
                region=config['region'],
                credentials=config['credentials'],
                status='active',
                cost_per_hour=config.get('cost_per_hour', 0.11),
                performance_score=config.get('performance_score', 0.82),
                availability_zone=config.get('availability_zone', 'westus2'),
                metadata={
                    'compute_client': compute_client,
                    'provider_type': 'azure',
                    'services': config.get('services', ['vm', 'storage', 'functions'])
                }
            )
            
        except Exception as e:
            print(f"Error creando proveedor Azure: {e}")
            return None
    
    async def get_provider_status(self, provider_id: str) -> Dict[str, Any]:
        """Get current status of a cloud provider"""
        if provider_id not in self.providers:
            return {'status': 'not_found', 'error': 'Provider not found'}
        
        provider = self.providers[provider_id]
        
        try:
            # Test provider connectivity
            status = await self._test_provider_connectivity(provider)
            provider.status = status['status']
            
            return {
                'provider_id': provider_id,
                'name': provider.name,
                'status': provider.status,
                'region': provider.region,
                'cost_per_hour': provider.cost_per_hour,
                'performance_score': provider.performance_score,
                'last_check': datetime.now().isoformat(),
                'details': status
            }
            
        except Exception as e:
            provider.status = 'error'
            return {
                'provider_id': provider_id,
                'status': 'error',
                'error': str(e),
                'last_check': datetime.now().isoformat()
            }
    
    async def _test_provider_connectivity(self, provider: CloudProvider) -> Dict[str, Any]:
        """Test connectivity to cloud provider"""
        provider_type = provider.metadata.get('provider_type', 'unknown')
        
        if provider_type == 'aws':
            return await self._test_aws_connectivity(provider)
        elif provider_type == 'gcp':
            return await self._test_gcp_connectivity(provider)
        elif provider_type == 'azure':
            return await self._test_azure_connectivity(provider)
        else:
            return {'status': 'unknown', 'error': 'Unknown provider type'}
    
    async def _test_aws_connectivity(self, provider: CloudProvider) -> Dict[str, Any]:
        """Test AWS connectivity"""
        try:
            session = provider.metadata['session']
            ec2 = session.client('ec2')
            
            # Test basic operations
            response = ec2.describe_instances(MaxResults=1)
            
            return {
                'status': 'active',
                'instances_count': len(response['Reservations']),
                'services_available': ['ec2', 's3', 'lambda'],
                'response_time': 'fast'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'services_available': [],
                'response_time': 'slow'
            }
    
    async def _test_gcp_connectivity(self, provider: CloudProvider) -> Dict[str, Any]:
        """Test GCP connectivity"""
        try:
            compute_client = provider.metadata['compute_client']
            
            # Test basic operations
            project = provider.credentials.get('project_id', 'default')
            zone = provider.region
            
            # List instances (limited to 1 for testing)
            request = compute_v1.ListInstancesRequest(
                project=project,
                zone=zone,
                max_results=1
            )
            
            instances = compute_client.list(request=request)
            instances_list = list(instances)
            
            return {
                'status': 'active',
                'instances_count': len(instances_list),
                'services_available': ['compute', 'storage', 'functions'],
                'response_time': 'fast'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'services_available': [],
                'response_time': 'slow'
            }
    
    async def _test_azure_connectivity(self, provider: CloudProvider) -> Dict[str, Any]:
        """Test Azure connectivity"""
        try:
            compute_client = provider.metadata['compute_client']
            
            # Test basic operations
            resource_group = provider.credentials.get('resource_group', 'default')
            
            # List VMs (limited to 1 for testing)
            vms = compute_client.virtual_machines.list(resource_group)
            vms_list = list(vms)
            
            return {
                'status': 'active',
                'instances_count': len(vms_list),
                'services_available': ['vm', 'storage', 'functions'],
                'response_time': 'fast'
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'services_available': [],
                'response_time': 'slow'
            }
    
    async def distribute_workload(
        self, 
        workload_name: str, 
        resource_requirements: Dict[str, float]
    ) -> WorkloadDistribution:
        """Distribute workload across available cloud providers"""
        
        # Get available providers
        available_providers = [
            p for p in self.providers.values() 
            if p.status == 'active'
        ]
        
        if not available_providers:
            raise ValueError("No hay proveedores cloud disponibles")
        
        # Calculate optimal distribution
        distribution = await self.load_balancer.calculate_optimal_distribution(
            workload_name, resource_requirements, available_providers
        )
        
        # Create workload distribution object
        workload_distribution = WorkloadDistribution(
            distribution_id=f"dist_{workload_name}_{int(time.time())}",
            timestamp=datetime.now(),
            workload_name=workload_name,
            total_resources=resource_requirements,
            provider_allocations=distribution['allocations'],
            cost_distribution=distribution['costs'],
            performance_metrics=distribution['performance'],
            optimization_score=distribution['score'],
            metadata={
                'balancing_algorithm': 'intelligent',
                'providers_used': len(available_providers),
                'distribution_method': 'cost_performance_optimized'
            }
        )
        
        # Store workload
        self.workloads[workload_name] = workload_distribution
        
        # Store in history
        self.balancing_history.append(workload_distribution)
        
        return workload_distribution
    
    async def optimize_workload_distribution(
        self, 
        workload_name: str
    ) -> LoadBalancingDecision:
        """Optimize existing workload distribution"""
        
        if workload_name not in self.workloads:
            raise ValueError(f"Workload {workload_name} no encontrado")
        
        current_distribution = self.workloads[workload_name]
        
        # Get current provider statuses
        provider_statuses = {}
        for provider_id in current_distribution.provider_allocations.keys():
            status = await self.get_provider_status(provider_id)
            provider_statuses[provider_id] = status
        
        # Calculate optimization
        optimization = await self.load_balancer.optimize_distribution(
            current_distribution, provider_statuses
        )
        
        # Create decision object
        decision = LoadBalancingDecision(
            decision_id=f"opt_{workload_name}_{int(time.time())}",
            timestamp=datetime.now(),
            workload_name=workload_name,
            current_distribution=current_distribution.provider_allocations,
            recommended_distribution=optimization['new_distribution'],
            reasoning=optimization['reasoning'],
            expected_improvements=optimization['improvements'],
            confidence=optimization['confidence'],
            implementation_priority=optimization['priority'],
            metadata={
                'optimization_type': 'cost_performance',
                'providers_analyzed': len(provider_statuses),
                'current_score': current_distribution.optimization_score
            }
        )
        
        # Store decision
        self.balancing_history.append(decision)
        
        return decision
    
    async def plan_migration(
        self, 
        workload_name: str, 
        target_provider: str,
        migration_type: str = 'partial'
    ) -> CloudMigration:
        """Plan workload migration to different cloud provider"""
        
        if workload_name not in self.workloads:
            raise ValueError(f"Workload {workload_name} no encontrado")
        
        if target_provider not in self.providers:
            raise ValueError(f"Proveedor objetivo {target_provider} no encontrado")
        
        current_distribution = self.workloads[workload_name]
        target_provider_info = self.providers[target_provider]
        
        # Calculate migration parameters
        migration_params = await self._calculate_migration_params(
            current_distribution, target_provider_info, migration_type
        )
        
        # Create migration plan
        migration = CloudMigration(
            migration_id=f"mig_{workload_name}_{int(time.time())}",
            timestamp=datetime.now(),
            source_provider=list(current_distribution.provider_allocations.keys())[0],
            target_provider=target_provider,
            workload_name=workload_name,
            migration_type=migration_type,
            estimated_duration=migration_params['duration'],
            estimated_cost=migration_params['cost'],
            risk_assessment=migration_params['risk'],
            rollback_plan=migration_params['rollback'],
            status='planned',
            metadata={
                'current_cost': sum(current_distribution.cost_distribution.values()),
                'target_cost': migration_params['target_cost'],
                'cost_savings': migration_params['cost_savings'],
                'performance_improvement': migration_params['performance_improvement']
            }
        )
        
        # Store migration plan
        self.migration_history.append(migration)
        
        return migration
    
    async def _calculate_migration_params(
        self, 
        current_distribution: WorkloadDistribution,
        target_provider: CloudProvider,
        migration_type: str
    ) -> Dict[str, Any]:
        """Calculate migration parameters"""
        
        # Calculate current costs
        current_cost = sum(current_distribution.cost_distribution.values())
        
        # Estimate target costs
        target_cost = current_cost * (target_provider.cost_per_hour / 0.10)  # Normalize to AWS
        
        # Calculate cost savings
        cost_savings = current_cost - target_cost
        
        # Estimate migration duration
        if migration_type == 'full':
            duration = 120  # 2 hours
        elif migration_type == 'partial':
            duration = 60   # 1 hour
        else:  # failover
            duration = 15   # 15 minutes
        
        # Estimate migration cost
        migration_cost = duration / 60 * target_provider.cost_per_hour * 1.5  # 50% overhead
        
        # Assess risk
        if target_provider.performance_score > 0.8:
            risk = 'low'
        elif target_provider.performance_score > 0.6:
            risk = 'medium'
        else:
            risk = 'high'
        
        # Generate rollback plan
        rollback = f"Revertir a {current_distribution.source_provider} en caso de problemas"
        
        # Calculate performance improvement
        performance_improvement = (target_provider.performance_score - 0.8) * 100
        
        return {
            'duration': duration,
            'cost': migration_cost,
            'target_cost': target_cost,
            'cost_savings': cost_savings,
            'risk': risk,
            'rollback': rollback,
            'performance_improvement': performance_improvement
        }
    
    async def get_cost_analysis(self) -> Dict[str, Any]:
        """Get comprehensive cost analysis across all providers"""
        
        cost_analysis = {
            'total_cost_per_hour': 0.0,
            'provider_costs': {},
            'cost_optimization_opportunities': [],
            'recommendations': []
        }
        
        # Calculate costs for each provider
        for provider_id, provider in self.providers.items():
            if provider.status == 'active':
                # Get current usage (simulated for demo)
                usage_cost = provider.cost_per_hour * random.uniform(0.5, 1.5)
                cost_analysis['provider_costs'][provider_id] = {
                    'name': provider.name,
                    'cost_per_hour': usage_cost,
                    'performance_score': provider.performance_score,
                    'region': provider.region
                }
                cost_analysis['total_cost_per_hour'] += usage_cost
        
        # Generate optimization recommendations
        recommendations = await self.cost_optimizer.generate_recommendations(
            cost_analysis['provider_costs']
        )
        cost_analysis['recommendations'] = recommendations
        
        return cost_analysis
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics across all providers"""
        
        performance_metrics = {
            'overall_score': 0.0,
            'provider_metrics': {},
            'bottlenecks': [],
            'optimization_opportunities': []
        }
        
        total_score = 0.0
        active_providers = 0
        
        for provider_id, provider in self.providers.items():
            if provider.status == 'active':
                # Get current performance (simulated for demo)
                current_performance = provider.performance_score * random.uniform(0.8, 1.2)
                
                performance_metrics['provider_metrics'][provider_id] = {
                    'name': provider.name,
                    'performance_score': current_performance,
                    'status': provider.status,
                    'region': provider.region,
                    'availability_zone': provider.availability_zone
                }
                
                total_score += current_performance
                active_providers += 1
                
                # Check for bottlenecks
                if current_performance < 0.7:
                    performance_metrics['bottlenecks'].append({
                        'provider': provider.name,
                        'issue': 'Low performance score',
                        'current_score': current_performance,
                        'recommendation': 'Consider migration or optimization'
                    })
        
        if active_providers > 0:
            performance_metrics['overall_score'] = total_score / active_providers
        
        return performance_metrics

class IntelligentLoadBalancer:
    """Intelligent load balancing across multiple cloud providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.balancing_history = deque(maxlen=1000)
        self.performance_weights = {
            'cost': 0.4,
            'performance': 0.3,
            'availability': 0.2,
            'latency': 0.1
        }
    
    async def calculate_optimal_distribution(
        self,
        workload_name: str,
        resource_requirements: Dict[str, float],
        available_providers: List[CloudProvider]
    ) -> Dict[str, Any]:
        """Calculate optimal workload distribution"""
        
        if not available_providers:
            raise ValueError("No hay proveedores disponibles")
        
        # Calculate scores for each provider
        provider_scores = []
        for provider in available_providers:
            score = await self._calculate_provider_score(provider, resource_requirements)
            provider_scores.append((provider, score))
        
        # Sort by score (descending)
        provider_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate distribution based on scores
        total_score = sum(score for _, score in provider_scores)
        allocations = {}
        costs = {}
        performance = {}
        
        for provider, score in provider_scores:
            # Allocate resources proportionally to score
            allocation_ratio = score / total_score
            
            allocations[provider.provider_id] = {
                'cpu': resource_requirements.get('cpu', 0) * allocation_ratio,
                'memory': resource_requirements.get('memory', 0) * allocation_ratio,
                'gpu': resource_requirements.get('gpu', 0) * allocation_ratio,
                'storage': resource_requirements.get('storage', 0) * allocation_ratio
            }
            
            # Calculate costs
            costs[provider.provider_id] = (
                sum(allocations[provider.provider_id].values()) * 
                provider.cost_per_hour
            )
            
            # Performance metrics
            performance[provider.provider_id] = {
                'score': score,
                'performance_rating': provider.performance_score,
                'cost_efficiency': score / provider.cost_per_hour
            }
        
        # Calculate overall optimization score
        optimization_score = self._calculate_optimization_score(
            allocations, costs, performance
        )
        
        return {
            'allocations': allocations,
            'costs': costs,
            'performance': performance,
            'score': optimization_score
        }
    
    async def _calculate_provider_score(
        self, 
        provider: CloudProvider, 
        requirements: Dict[str, float]
    ) -> float:
        """Calculate score for a provider based on requirements"""
        
        # Base score from provider performance
        base_score = provider.performance_score
        
        # Cost efficiency score (lower cost = higher score)
        cost_score = 1.0 / (1.0 + provider.cost_per_hour)
        
        # Availability score (assume high availability for active providers)
        availability_score = 0.95 if provider.status == 'active' else 0.0
        
        # Latency score (assume low latency for same region)
        latency_score = 0.9  # Could be calculated based on actual latency
        
        # Calculate weighted score
        weighted_score = (
            base_score * self.performance_weights['performance'] +
            cost_score * self.performance_weights['cost'] +
            availability_score * self.performance_weights['availability'] +
            latency_score * self.performance_weights['latency']
        )
        
        return weighted_score
    
    def _calculate_optimization_score(
        self,
        allocations: Dict[str, Dict[str, float]],
        costs: Dict[str, float],
        performance: Dict[str, Any]
    ) -> float:
        """Calculate overall optimization score"""
        
        # Cost efficiency (lower total cost = higher score)
        total_cost = sum(costs.values())
        cost_score = 1.0 / (1.0 + total_cost)
        
        # Performance balance (even distribution = higher score)
        performance_scores = [p['score'] for p in performance.values()]
        performance_variance = np.var(performance_scores) if len(performance_scores) > 1 else 0
        balance_score = 1.0 / (1.0 + performance_variance)
        
        # Resource utilization (higher utilization = higher score)
        total_allocated = sum(
            sum(alloc.values()) for alloc in allocations.values()
        )
        utilization_score = min(1.0, total_allocated / 100)  # Normalize to 100
        
        # Combined score
        optimization_score = (
            cost_score * 0.4 +
            balance_score * 0.3 +
            utilization_score * 0.3
        )
        
        return optimization_score
    
    async def optimize_distribution(
        self,
        current_distribution: WorkloadDistribution,
        provider_statuses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Optimize existing workload distribution"""
        
        # Analyze current distribution
        current_score = current_distribution.optimization_score
        
        # Identify optimization opportunities
        opportunities = []
        for provider_id, status in provider_statuses.items():
            if status['status'] == 'error':
                opportunities.append({
                    'type': 'provider_failure',
                    'provider': provider_id,
                    'priority': 'high',
                    'action': 'migrate_workload'
                })
            elif status['status'] == 'active':
                # Check for cost optimization
                current_cost = current_distribution.cost_distribution.get(provider_id, 0)
                if current_cost > 0.5:  # High cost threshold
                    opportunities.append({
                        'type': 'cost_optimization',
                        'provider': provider_id,
                        'priority': 'medium',
                        'action': 'reduce_allocation'
                    })
        
        # Generate new distribution recommendation
        new_distribution = current_distribution.provider_allocations.copy()
        
        # Apply optimizations
        for opportunity in opportunities:
            if opportunity['type'] == 'provider_failure':
                # Move workload to healthy providers
                failed_provider = opportunity['provider']
                if failed_provider in new_distribution:
                    # Redistribute to other providers
                    failed_allocation = new_distribution.pop(failed_provider)
                    self._redistribute_failed_allocation(
                        failed_allocation, new_distribution, provider_statuses
                    )
        
        # Calculate expected improvements
        improvements = {
            'cost_reduction': 0.15,  # 15% cost reduction
            'performance_improvement': 0.10,  # 10% performance improvement
            'availability_increase': 0.05  # 5% availability increase
        }
        
        # Generate reasoning
        reasoning = [
            "Optimización basada en estado actual de proveedores",
            "Redistribución para mejorar balance de carga",
            "Ajuste de costos según rendimiento actual"
        ]
        
        return {
            'new_distribution': new_distribution,
            'reasoning': reasoning,
            'improvements': improvements,
            'confidence': 0.85,
            'priority': 2  # Medium priority
        }
    
    def _redistribute_failed_allocation(
        self,
        failed_allocation: Dict[str, float],
        new_distribution: Dict[str, Dict[str, float]],
        provider_statuses: Dict[str, Any]
    ):
        """Redistribute failed allocation to healthy providers"""
        
        # Find healthy providers
        healthy_providers = [
            pid for pid, status in provider_statuses.items()
            if status['status'] == 'active'
        ]
        
        if not healthy_providers:
            return  # No healthy providers available
        
        # Distribute failed allocation evenly
        allocation_per_provider = {}
        for resource_type, amount in failed_allocation.items():
            allocation_per_provider[resource_type] = amount / len(healthy_providers)
        
        # Add to healthy providers
        for provider_id in healthy_providers:
            if provider_id not in new_distribution:
                new_distribution[provider_id] = {}
            
            for resource_type, amount in allocation_per_provider.items():
                current_amount = new_distribution[provider_id].get(resource_type, 0)
                new_distribution[provider_id][resource_type] = current_amount + amount

class MultiCloudCostOptimizer:
    """Optimizes costs across multiple cloud providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.optimization_history = deque(maxlen=1000)
    
    async def generate_recommendations(
        self, 
        provider_costs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate cost optimization recommendations"""
        
        recommendations = []
        
        # Analyze cost distribution
        total_cost = sum(cost['cost_per_hour'] for cost in provider_costs.values())
        
        for provider_id, cost_info in provider_costs.items():
            cost_percentage = cost_info['cost_per_hour'] / total_cost if total_cost > 0 else 0
            
            # High cost provider recommendation
            if cost_percentage > 0.4:  # More than 40% of total cost
                recommendations.append({
                    'type': 'cost_reduction',
                    'provider': provider_id,
                    'priority': 'high',
                    'description': f'Proveedor {cost_info["name"]} representa {cost_percentage:.1%} del costo total',
                    'action': 'Considerar migración parcial a proveedores más económicos',
                    'expected_savings': '15-25%'
                })
            
            # Performance vs cost analysis
            if cost_info['performance_score'] < 0.7 and cost_info['cost_per_hour'] > 0.1:
                recommendations.append({
                    'type': 'performance_optimization',
                    'provider': provider_id,
                    'priority': 'medium',
                    'description': f'Proveedor {cost_info["name"]} tiene bajo rendimiento y alto costo',
                    'action': 'Optimizar configuración o migrar a mejor proveedor',
                    'expected_savings': '10-20%'
                })
        
        # Cross-provider optimization
        if len(provider_costs) > 1:
            recommendations.append({
                'type': 'load_balancing',
                'provider': 'all',
                'priority': 'medium',
                'description': 'Optimizar distribución de carga entre proveedores',
                'action': 'Implementar balanceo de carga inteligente',
                'expected_savings': '5-15%'
            })
        
        return recommendations

class MultiCloudIntegrationSystem:
    """Main system combining all multi-cloud capabilities"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.cloud_manager = MultiCloudManager(self.config)
        self.is_running = False
        self.integration_interval = self.config.get('integration_interval', 300)  # 5 minutes
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        try:
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'integration_interval': 300,
            'cloud_providers': {
                'aws_west': {
                    'type': 'aws',
                    'region': 'us-west-2',
                    'credentials': {
                        'access_key': 'your_access_key',
                        'secret_key': 'your_secret_key'
                    },
                    'cost_per_hour': 0.10,
                    'performance_score': 0.85
                },
                'gcp_west': {
                    'type': 'gcp',
                    'region': 'us-west1',
                    'credentials': {
                        'project_id': 'your_project_id',
                        'key_file': 'path/to/key.json'
                    },
                    'cost_per_hour': 0.12,
                    'performance_score': 0.80
                }
            }
        }
    
    async def start(self):
        """Start the multi-cloud integration system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Integración Multi-Cloud v4.3...")
        
        # Start integration loop
        asyncio.create_task(self._integration_loop())
        
        print("✅ Sistema de Integración Multi-Cloud v4.3 iniciado")
    
    async def _integration_loop(self):
        """Main integration loop"""
        while self.is_running:
            try:
                # Monitor all providers
                await self._monitor_providers()
                
                # Optimize existing workloads
                await self._optimize_workloads()
                
                # Generate cost analysis
                await self._generate_cost_analysis()
                
                # Wait for next cycle
                await asyncio.sleep(self.integration_interval)
                
            except Exception as e:
                print(f"Error en loop de integración: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _monitor_providers(self):
        """Monitor all cloud providers"""
        print(f"\n🔍 Monitoreando Proveedores Cloud - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 60)
        
        for provider_id in self.cloud_manager.providers.keys():
            try:
                status = await self.cloud_manager.get_provider_status(provider_id)
                print(f"  {status['name']}: {status['status'].upper()}")
                
            except Exception as e:
                print(f"  Error monitoreando {provider_id}: {e}")
    
    async def _optimize_workloads(self):
        """Optimize existing workloads"""
        if not self.cloud_manager.workloads:
            return
        
        print(f"\n🔧 Optimizando Distribución de Carga")
        
        for workload_name in list(self.cloud_manager.workloads.keys()):
            try:
                decision = await self.cloud_manager.optimize_workload_distribution(workload_name)
                print(f"  {workload_name}: Optimización recomendada (Confianza: {decision.confidence:.1%})")
                
            except Exception as e:
                print(f"  Error optimizando {workload_name}: {e}")
    
    async def _generate_cost_analysis(self):
        """Generate cost analysis"""
        try:
            cost_analysis = await self.cloud_manager.get_cost_analysis()
            performance_metrics = await self.cloud_manager.get_performance_metrics()
            
            print(f"\n💰 Análisis de Costos Multi-Cloud")
            print(f"  Costo Total: ${cost_analysis['total_cost_per_hour']:.2f}/hora")
            print(f"  Score General: {performance_metrics['overall_score']:.2%}")
            
            if cost_analysis['recommendations']:
                print(f"  Recomendaciones: {len(cost_analysis['recommendations'])}")
            
        except Exception as e:
            print(f"Error generando análisis: {e}")
    
    async def stop(self):
        """Stop the multi-cloud integration system"""
        print("🛑 Deteniendo Sistema de Integración Multi-Cloud v4.3...")
        self.is_running = False
        print("✅ Sistema detenido")

# Factory function
async def create_multicloud_integration_system(config_path: str) -> MultiCloudIntegrationSystem:
    """Create and initialize the multi-cloud integration system"""
    system = MultiCloudIntegrationSystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_multicloud_integration_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
