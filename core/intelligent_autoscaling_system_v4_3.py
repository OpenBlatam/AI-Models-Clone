"""
Sistema de Auto-Scaling Inteligente con Kubernetes v4.3
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Auto-scaling inteligente con Kubernetes
- Decisiones de escalado basadas en IA
- Optimización automática de recursos
- Predicción de demanda futura
- Gestión inteligente de pods y nodos
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

# Kubernetes imports
try:
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    KUBERNETES_AVAILABLE = True
except ImportError:
    KUBERNETES_AVAILABLE = False
    print("Warning: kubernetes not available, using simulated scaling")

# Intelligent Auto-Scaling Components
@dataclass
class ScalingDecision:
    """Intelligent scaling decision"""
    decision_id: str
    timestamp: datetime
    scaling_type: str  # scale_up, scale_down, maintain
    target_component: str  # deployment, hpa, node
    current_replicas: int
    target_replicas: int
    scaling_factor: float
    confidence: float
    reasoning: List[str]
    expected_impact: Dict[str, float]
    risk_assessment: str
    rollback_plan: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ResourceDemand:
    """Resource demand prediction"""
    demand_id: str
    timestamp: datetime
    component: str
    current_demand: float
    predicted_demand: float
    prediction_horizon: int  # minutes
    confidence: float
    demand_trend: str  # increasing, stable, decreasing
    seasonal_factors: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingPolicy:
    """Intelligent scaling policy"""
    policy_id: str
    timestamp: datetime
    component: str
    policy_type: str  # reactive, predictive, hybrid
    min_replicas: int
    max_replicas: int
    target_cpu_utilization: float
    target_memory_utilization: float
    scaling_cooldown: int  # seconds
    scaling_rules: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScalingAction:
    """Scaling action execution result"""
    action_id: str
    timestamp: datetime
    scaling_decision: ScalingDecision
    action_status: str  # pending, executing, completed, failed
    execution_time: float  # seconds
    actual_replicas: int
    actual_impact: Dict[str, float]
    success_metrics: Dict[str, float]
    error_details: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntelligentScalingEngine:
    """AI-powered intelligent scaling engine"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scaling_history = deque(maxlen=1000)
        self.demand_history = deque(maxlen=10000)
        self.policy_history = deque(maxlen=500)
        self.action_history = deque(maxlen=1000)
        
        # Scaling models
        self.scaling_models = {}
        self._initialize_scaling_models()
        
        # Kubernetes client
        self.k8s_client = self._initialize_kubernetes_client()
        
        # Scaling policies
        self.scaling_policies = {}
        self._load_scaling_policies()
        
    def _initialize_scaling_models(self):
        """Initialize AI scaling models"""
        # In a real system, these would be trained ML models
        # For demo purposes, use simplified models
        
        self.scaling_models = {
            'demand_predictor': self._create_demand_predictor(),
            'scaling_optimizer': self._create_scaling_optimizer(),
            'risk_assessor': self._create_risk_assessor(),
            'impact_predictor': self._create_impact_predictor()
        }
    
    def _create_demand_predictor(self):
        """Create demand prediction model"""
        class DemandPredictor:
            def __init__(self):
                self.demand_history = deque(maxlen=100)
                self.seasonal_patterns = {}
            
            def predict_demand(self, current_demand, horizon_minutes):
                if len(self.demand_history) < 5:
                    return current_demand, 0.5
                
                # Simple trend-based prediction
                recent_demands = list(self.demand_history)[-5:]
                trend = (recent_demands[-1] - recent_demands[0]) / len(recent_demands)
                
                # Add seasonal factor
                seasonal_factor = self._calculate_seasonal_factor(horizon_minutes)
                
                # Predict future demand
                predicted_demand = current_demand + (trend * horizon_minutes / 60) * seasonal_factor
                confidence = min(0.9, len(self.demand_history) / 100)
                
                return max(0, predicted_demand), confidence
            
            def _calculate_seasonal_factor(self, horizon_minutes):
                # Simple seasonal pattern (business hours vs off-hours)
                current_hour = datetime.now().hour
                if 9 <= current_hour <= 17:  # Business hours
                    return 1.2
                else:
                    return 0.8
            
            def update(self, demand):
                self.demand_history.append(demand)
        
        return DemandPredictor()
    
    def _create_scaling_optimizer(self):
        """Create scaling optimization model"""
        class ScalingOptimizer:
            def __init__(self):
                self.optimization_history = deque(maxlen=100)
            
            def optimize_scaling(self, current_metrics, target_metrics):
                # Calculate optimal scaling factor
                cpu_ratio = target_metrics.get('cpu', 70) / max(current_metrics.get('cpu', 1), 1)
                memory_ratio = target_metrics.get('memory', 80) / max(current_metrics.get('memory', 1), 1)
                
                # Use the higher ratio for scaling
                scaling_factor = max(cpu_ratio, memory_ratio)
                
                # Apply safety bounds
                scaling_factor = max(0.5, min(2.0, scaling_factor))
                
                return scaling_factor
            
            def update(self, optimization_result):
                self.optimization_history.append(optimization_result)
        
        return ScalingOptimizer()
    
    def _create_risk_assessor(self):
        """Create risk assessment model"""
        class RiskAssessor:
            def __init__(self):
                self.risk_patterns = {
                    'scale_up': ['high_resource_usage', 'increasing_demand', 'performance_degradation'],
                    'scale_down': ['low_resource_usage', 'decreasing_demand', 'cost_optimization']
                }
            
            def assess_risk(self, scaling_type, current_metrics, target_metrics):
                risk_score = 0.0
                
                if scaling_type == 'scale_up':
                    # Risk factors for scaling up
                    if current_metrics.get('cpu', 0) > 90:
                        risk_score += 0.3
                    if current_metrics.get('memory', 0) > 95:
                        risk_score += 0.3
                    if target_metrics.get('cpu', 0) > 80:
                        risk_score += 0.2
                
                elif scaling_type == 'scale_down':
                    # Risk factors for scaling down
                    if current_metrics.get('cpu', 0) > 70:
                        risk_score += 0.5
                    if current_metrics.get('memory', 0) > 80:
                        risk_score += 0.5
                
                # Normalize risk score
                risk_score = min(1.0, risk_score)
                
                # Determine risk level
                if risk_score > 0.7:
                    risk_level = 'high'
                elif risk_score > 0.4:
                    risk_level = 'medium'
                else:
                    risk_level = 'low'
                
                return risk_score, risk_level
        
        return RiskAssessor()
    
    def _create_impact_predictor(self):
        """Create impact prediction model"""
        class ImpactPredictor:
            def __init__(self):
                self.impact_history = deque(maxlen=100)
            
            def predict_impact(self, scaling_type, scaling_factor, current_metrics):
                impacts = {}
                
                if scaling_type == 'scale_up':
                    impacts['cpu_usage'] = current_metrics.get('cpu', 50) / scaling_factor
                    impacts['memory_usage'] = current_metrics.get('memory', 60) / scaling_factor
                    impacts['response_time'] = current_metrics.get('response_time', 1000) * 0.8
                    impacts['throughput'] = current_metrics.get('throughput', 100) * scaling_factor
                
                elif scaling_type == 'scale_down':
                    impacts['cpu_usage'] = current_metrics.get('cpu', 50) * scaling_factor
                    impacts['memory_usage'] = current_metrics.get('memory', 60) * scaling_factor
                    impacts['response_time'] = current_metrics.get('response_time', 1000) * 1.2
                    impacts['throughput'] = current_metrics.get('throughput', 100) / scaling_factor
                
                else:  # maintain
                    impacts['cpu_usage'] = current_metrics.get('cpu', 50)
                    impacts['memory_usage'] = current_metrics.get('memory', 60)
                    impacts['response_time'] = current_metrics.get('response_time', 1000)
                    impacts['throughput'] = current_metrics.get('throughput', 100)
                
                return impacts
        
        return ImpactPredictor()
    
    def _initialize_kubernetes_client(self):
        """Initialize Kubernetes client"""
        if not KUBERNETES_AVAILABLE:
            return None
        
        try:
            # Try to load in-cluster config first
            try:
                config.load_incluster_config()
            except config.ConfigException:
                # Fall back to kubeconfig file
                config.load_kube_config()
            
            # Create API client
            api_client = client.ApiClient()
            apps_v1 = client.AppsV1Api(api_client)
            core_v1 = client.CoreV1Api(api_client)
            
            return {
                'apps_v1': apps_v1,
                'core_v1': core_v1,
                'api_client': api_client
            }
            
        except Exception as e:
            print(f"Error initializing Kubernetes client: {e}")
            return None
    
    def _load_scaling_policies(self):
        """Load scaling policies from configuration"""
        default_policies = {
            'heygen_ai_core': {
                'min_replicas': 2,
                'max_replicas': 20,
                'target_cpu_utilization': 70,
                'target_memory_utilization': 80,
                'scaling_cooldown': 300
            },
            'heygen_ai_video': {
                'min_replicas': 1,
                'max_replicas': 15,
                'target_cpu_utilization': 75,
                'target_memory_utilization': 85,
                'scaling_cooldown': 240
            },
            'heygen_ai_audio': {
                'min_replicas': 1,
                'max_replicas': 10,
                'target_cpu_utilization': 70,
                'target_memory_utilization': 80,
                'scaling_cooldown': 180
            }
        }
        
        # Load from config or use defaults
        config_policies = self.config.get('scaling_policies', {})
        self.scaling_policies = {**default_policies, **config_policies}
    
    async def analyze_scaling_needs(
        self, 
        current_metrics: Dict[str, Any],
        component: str
    ) -> ScalingDecision:
        """Analyze if scaling is needed and make intelligent decision"""
        
        # Get scaling policy for component
        policy = self.scaling_policies.get(component, {})
        if not policy:
            raise ValueError(f"No scaling policy found for component: {component}")
        
        # Get current replicas
        current_replicas = await self._get_current_replicas(component)
        
        # Predict demand
        current_demand = current_metrics.get('cpu', 50)
        predicted_demand, confidence = self.scaling_models['demand_predictor'].predict_demand(
            current_demand, horizon_minutes=30
        )
        
        # Determine scaling type
        scaling_type, target_metrics = self._determine_scaling_type(
            current_metrics, policy, predicted_demand
        )
        
        # Optimize scaling factor
        scaling_factor = self.scaling_models['scaling_optimizer'].optimize_scaling(
            current_metrics, target_metrics
        )
        
        # Calculate target replicas
        target_replicas = self._calculate_target_replicas(
            current_replicas, scaling_factor, policy
        )
        
        # Assess risk
        risk_score, risk_level = self.scaling_models['risk_assessor'].assess_risk(
            scaling_type, current_metrics, target_metrics
        )
        
        # Predict impact
        expected_impact = self.scaling_models['impact_predictor'].predict_impact(
            scaling_type, scaling_factor, current_metrics
        )
        
        # Generate reasoning
        reasoning = self._generate_scaling_reasoning(
            scaling_type, current_metrics, target_metrics, predicted_demand
        )
        
        # Create scaling decision
        decision = ScalingDecision(
            decision_id=f"scale_{component}_{int(time.time())}",
            timestamp=datetime.now(),
            scaling_type=scaling_type,
            target_component=component,
            current_replicas=current_replicas,
            target_replicas=target_replicas,
            scaling_factor=scaling_factor,
            confidence=confidence,
            reasoning=reasoning,
            expected_impact=expected_impact,
            risk_assessment=risk_level,
            rollback_plan=self._generate_rollback_plan(scaling_type, current_replicas),
            metadata={
                'policy_used': policy,
                'demand_prediction': predicted_demand,
                'risk_score': risk_score
            }
        )
        
        # Store decision
        self.scaling_history.append(decision)
        
        return decision
    
    def _determine_scaling_type(
        self, 
        current_metrics: Dict[str, Any], 
        policy: Dict[str, Any],
        predicted_demand: float
    ) -> Tuple[str, Dict[str, float]]:
        """Determine if scaling up, down, or maintaining is needed"""
        
        current_cpu = current_metrics.get('cpu', 50)
        current_memory = current_metrics.get('memory', 60)
        
        target_cpu = policy.get('target_cpu_utilization', 70)
        target_memory = policy.get('target_memory_utilization', 80)
        
        # Check if scaling up is needed
        if current_cpu > target_cpu * 1.1 or current_memory > target_memory * 1.1:
            return 'scale_up', {'cpu': target_cpu, 'memory': target_memory}
        
        # Check if scaling down is needed
        elif (current_cpu < target_cpu * 0.6 and current_memory < target_memory * 0.6 and 
              predicted_demand < target_cpu * 0.8):
            return 'scale_down', {'cpu': target_cpu, 'memory': target_memory}
        
        else:
            return 'maintain', {'cpu': current_cpu, 'memory': current_memory}
    
    def _calculate_target_replicas(
        self, 
        current_replicas: int, 
        scaling_factor: float, 
        policy: Dict[str, Any]
    ) -> int:
        """Calculate target number of replicas"""
        
        target_replicas = int(current_replicas * scaling_factor)
        
        # Apply policy constraints
        min_replicas = policy.get('min_replicas', 1)
        max_replicas = policy.get('max_replicas', 10)
        
        target_replicas = max(min_replicas, min(max_replicas, target_replicas))
        
        return target_replicas
    
    def _generate_scaling_reasoning(
        self, 
        scaling_type: str, 
        current_metrics: Dict[str, Any],
        target_metrics: Dict[str, Any],
        predicted_demand: float
    ) -> List[str]:
        """Generate reasoning for scaling decision"""
        
        reasoning = []
        
        if scaling_type == 'scale_up':
            if current_metrics.get('cpu', 0) > 80:
                reasoning.append(f"CPU usage high: {current_metrics.get('cpu', 0):.1f}%")
            if current_metrics.get('memory', 0) > 85:
                reasoning.append(f"Memory usage high: {current_metrics.get('memory', 0):.1f}%")
            if predicted_demand > 80:
                reasoning.append(f"Predicted demand increase: {predicted_demand:.1f}%")
        
        elif scaling_type == 'scale_down':
            if current_metrics.get('cpu', 0) < 40:
                reasoning.append(f"CPU usage low: {current_metrics.get('cpu', 0):.1f}%")
            if current_metrics.get('memory', 0) < 50:
                reasoning.append(f"Memory usage low: {current_metrics.get('memory', 0):.1f}%")
            if predicted_demand < 60:
                reasoning.append(f"Predicted demand decrease: {predicted_demand:.1f}%")
        
        else:  # maintain
            reasoning.append("Current resource utilization within optimal range")
            reasoning.append("No immediate scaling action required")
        
        return reasoning
    
    def _generate_rollback_plan(self, scaling_type: str, current_replicas: int) -> str:
        """Generate rollback plan for scaling action"""
        
        if scaling_type == 'scale_up':
            return f"Scale down to {current_replicas} replicas if performance doesn't improve within 5 minutes"
        elif scaling_type == 'scale_down':
            return f"Scale up to {current_replicas} replicas immediately if performance degrades"
        else:
            return "No rollback needed for maintain action"
    
    async def _get_current_replicas(self, component: str) -> int:
        """Get current number of replicas for component"""
        
        if not self.k8s_client:
            # Simulate replicas for demo
            return random.randint(2, 8)
        
        try:
            # Get deployment
            deployment = self.k8s_client['apps_v1'].read_namespaced_deployment(
                name=component,
                namespace='default'
            )
            return deployment.spec.replicas or 1
            
        except ApiException as e:
            print(f"Error getting replicas for {component}: {e}")
            return 1
    
    async def execute_scaling_action(
        self, 
        scaling_decision: ScalingDecision
    ) -> ScalingAction:
        """Execute scaling action based on decision"""
        
        start_time = time.time()
        
        try:
            # Execute scaling action
            if scaling_decision.scaling_type == 'scale_up':
                success = await self._scale_up_deployment(
                    scaling_decision.target_component,
                    scaling_decision.target_replicas
                )
            elif scaling_decision.scaling_type == 'scale_down':
                success = await self._scale_down_deployment(
                    scaling_decision.target_component,
                    scaling_decision.target_replicas
                )
            else:  # maintain
                success = True
            
            # Get actual replicas after scaling
            actual_replicas = await self._get_current_replicas(scaling_decision.target_component)
            
            # Calculate execution time
            execution_time = time.time() - start_time
            
            # Create scaling action result
            action = ScalingAction(
                action_id=f"action_{scaling_decision.decision_id}",
                timestamp=datetime.now(),
                scaling_decision=scaling_decision,
                action_status='completed' if success else 'failed',
                execution_time=execution_time,
                actual_replicas=actual_replicas,
                actual_impact=self._calculate_actual_impact(scaling_decision),
                success_metrics=self._calculate_success_metrics(scaling_decision, success),
                error_details=None if success else "Scaling action failed",
                metadata={
                    'execution_method': 'kubernetes_api',
                    'target_achieved': success
                }
            )
            
            # Store action
            self.action_history.append(action)
            
            return action
            
        except Exception as e:
            # Handle execution errors
            execution_time = time.time() - start_time
            
            action = ScalingAction(
                action_id=f"action_{scaling_decision.decision_id}",
                timestamp=datetime.now(),
                scaling_decision=scaling_decision,
                action_status='failed',
                execution_time=execution_time,
                actual_replicas=scaling_decision.current_replicas,
                actual_impact={},
                success_metrics={},
                error_details=str(e),
                metadata={
                    'execution_method': 'kubernetes_api',
                    'target_achieved': False
                }
            )
            
            self.action_history.append(action)
            return action
    
    async def _scale_up_deployment(self, component: str, target_replicas: int) -> bool:
        """Scale up deployment to target replicas"""
        
        if not self.k8s_client:
            # Simulate scaling for demo
            print(f"🔄 Simulando scale up de {component} a {target_replicas} réplicas")
            await asyncio.sleep(2)  # Simulate scaling time
            return True
        
        try:
            # Patch deployment
            patch = {
                'spec': {
                    'replicas': target_replicas
                }
            }
            
            self.k8s_client['apps_v1'].patch_namespaced_deployment(
                name=component,
                namespace='default',
                body=patch
            )
            
            print(f"✅ Deployment {component} escalado a {target_replicas} réplicas")
            return True
            
        except Exception as e:
            print(f"❌ Error escalando deployment {component}: {e}")
            return False
    
    async def _scale_down_deployment(self, component: str, target_replicas: int) -> bool:
        """Scale down deployment to target replicas"""
        
        if not self.k8s_client:
            # Simulate scaling for demo
            print(f"🔄 Simulando scale down de {component} a {target_replicas} réplicas")
            await asyncio.sleep(1)  # Simulate scaling time
            return True
        
        try:
            # Patch deployment
            patch = {
                'spec': {
                    'replicas': target_replicas
                }
            }
            
            self.k8s_client['apps_v1'].patch_namespaced_deployment(
                name=component,
                namespace='default',
                body=patch
            )
            
            print(f"✅ Deployment {component} reducido a {target_replicas} réplicas")
            return True
            
        except Exception as e:
            print(f"❌ Error reduciendo deployment {component}: {e}")
            return False
    
    def _calculate_actual_impact(self, scaling_decision: ScalingDecision) -> Dict[str, float]:
        """Calculate actual impact of scaling action"""
        
        # In a real system, this would measure actual metrics after scaling
        # For demo purposes, return expected impact with some variation
        
        expected_impact = scaling_decision.expected_impact
        actual_impact = {}
        
        for metric, value in expected_impact.items():
            # Add some realistic variation (±10%)
            variation = random.uniform(0.9, 1.1)
            actual_impact[metric] = value * variation
        
        return actual_impact
    
    def _calculate_success_metrics(self, scaling_decision: ScalingDecision, success: bool) -> Dict[str, float]:
        """Calculate success metrics for scaling action"""
        
        if not success:
            return {'success_rate': 0.0, 'target_achievement': 0.0}
        
        # Calculate how well the target was achieved
        target_replicas = scaling_decision.target_replicas
        current_replicas = scaling_decision.current_replicas
        
        if target_replicas == current_replicas:
            target_achievement = 1.0
        else:
            target_achievement = min(1.0, current_replicas / target_replicas)
        
        return {
            'success_rate': 1.0,
            'target_achievement': target_achievement,
            'scaling_efficiency': 0.95  # 95% efficiency
        }
    
    async def get_scaling_summary(self) -> Dict[str, Any]:
        """Get summary of scaling activities"""
        
        total_decisions = len(self.scaling_history)
        total_actions = len(self.action_history)
        
        # Count by scaling type
        scaling_types = defaultdict(int)
        for decision in self.scaling_history:
            scaling_types[decision.scaling_type] += 1
        
        # Count by status
        action_statuses = defaultdict(int)
        for action in self.action_history:
            action_statuses[action.action_status] += 1
        
        # Calculate success rate
        success_rate = 0.0
        if total_actions > 0:
            successful_actions = action_statuses.get('completed', 0)
            success_rate = successful_actions / total_actions
        
        return {
            'total_decisions': total_decisions,
            'total_actions': total_actions,
            'scaling_type_distribution': dict(scaling_types),
            'action_status_distribution': dict(action_statuses),
            'success_rate': success_rate,
            'average_execution_time': '2.3 seconds',  # Would be calculated from actual data
            'active_policies': len(self.scaling_policies)
        }

class IntelligentAutoscalingSystem:
    """Main system combining all intelligent auto-scaling capabilities"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.scaling_engine = IntelligentScalingEngine(self.config)
        self.is_running = False
        self.scaling_interval = self.config.get('scaling_interval', 60)  # 1 minute
        
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
            'scaling_interval': 60,
            'scaling_policies': {
                'heygen_ai_core': {
                    'min_replicas': 2,
                    'max_replicas': 20,
                    'target_cpu_utilization': 70,
                    'target_memory_utilization': 80,
                    'scaling_cooldown': 300
                }
            }
        }
    
    async def start(self):
        """Start the intelligent auto-scaling system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Auto-Scaling Inteligente v4.3...")
        
        # Start scaling loop
        asyncio.create_task(self._intelligent_scaling_loop())
        
        print("✅ Sistema de Auto-Scaling Inteligente v4.3 iniciado")
    
    async def _intelligent_scaling_loop(self):
        """Main intelligent scaling loop"""
        while self.is_running:
            try:
                # Monitor all components
                await self._monitor_and_scale_components()
                
                # Display scaling summary
                await self._display_scaling_summary()
                
                # Wait for next cycle
                await asyncio.sleep(self.scaling_interval)
                
            except Exception as e:
                print(f"Error en loop de auto-scaling: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _monitor_and_scale_components(self):
        """Monitor components and execute scaling decisions"""
        
        # Components to monitor
        components = list(self.scaling_engine.scaling_policies.keys())
        
        for component in components:
            try:
                # Generate simulated metrics for demo
                current_metrics = self._generate_component_metrics(component)
                
                # Analyze scaling needs
                scaling_decision = await self.scaling_engine.analyze_scaling_needs(
                    current_metrics, component
                )
                
                # Execute scaling if needed
                if scaling_decision.scaling_type != 'maintain':
                    print(f"\n🔍 Analizando escalado para {component}...")
                    print(f"  Decisión: {scaling_decision.scaling_type}")
                    print(f"  Réplicas: {scaling_decision.current_replicas} → {scaling_decision.target_replicas}")
                    print(f"  Confianza: {scaling_decision.confidence:.1%}")
                    
                    # Execute scaling action
                    scaling_action = await self.scaling_engine.execute_scaling_action(scaling_decision)
                    
                    if scaling_action.action_status == 'completed':
                        print(f"  ✅ Escalado completado en {scaling_action.execution_time:.1f}s")
                    else:
                        print(f"  ❌ Error en escalado: {scaling_action.error_details}")
                
                # Update demand predictor
                self.scaling_engine.scaling_models['demand_predictor'].update(
                    current_metrics.get('cpu', 50)
                )
                
            except Exception as e:
                print(f"Error monitoreando {component}: {e}")
                continue
    
    def _generate_component_metrics(self, component: str) -> Dict[str, Any]:
        """Generate simulated component metrics for demo"""
        
        # Base metrics with some realistic variation
        base_cpu = random.uniform(40, 90)
        base_memory = random.uniform(50, 95)
        
        # Add component-specific patterns
        if 'core' in component:
            base_cpu += random.uniform(-10, 10)
            base_memory += random.uniform(-5, 15)
        elif 'video' in component:
            base_cpu += random.uniform(5, 20)
            base_memory += random.uniform(10, 25)
        elif 'audio' in component:
            base_cpu += random.uniform(-15, 5)
            base_memory += random.uniform(-10, 10)
        
        return {
            'cpu': max(0, min(100, base_cpu)),
            'memory': max(0, min(100, base_memory)),
            'response_time': random.uniform(100, 3000),
            'throughput': random.uniform(50, 200),
            'disk_usage': random.uniform(30, 80),
            'network_usage': random.uniform(20, 70)
        }
    
    async def _display_scaling_summary(self):
        """Display scaling summary"""
        
        try:
            summary = await self.scaling_engine.get_scaling_summary()
            
            print(f"\n📊 Resumen de Auto-Scaling - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 60)
            print(f"  Decisiones Totales: {summary['total_decisions']}")
            print(f"  Acciones Ejecutadas: {summary['total_actions']}")
            print(f"  Tasa de Éxito: {summary['success_rate']:.1%}")
            print(f"  Políticas Activas: {summary['active_policies']}")
            
            # Display scaling type distribution
            if summary['scaling_type_distribution']:
                print(f"\n  Distribución por Tipo:")
                for scaling_type, count in summary['scaling_type_distribution'].items():
                    print(f"    {scaling_type}: {count}")
            
            # Display action status distribution
            if summary['action_status_distribution']:
                print(f"\n  Estado de Acciones:")
                for status, count in summary['action_status_distribution'].items():
                    print(f"    {status}: {count}")
            
        except Exception as e:
            print(f"Error obteniendo resumen de escalado: {e}")
    
    async def stop(self):
        """Stop the intelligent auto-scaling system"""
        print("🛑 Deteniendo Sistema de Auto-Scaling Inteligente v4.3...")
        self.is_running = False
        print("✅ Sistema detenido")

# Factory function
async def create_intelligent_autoscaling_system(config_path: str) -> IntelligentAutoscalingSystem:
    """Create and initialize the intelligent auto-scaling system"""
    system = IntelligentAutoscalingSystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_intelligent_autoscaling_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
