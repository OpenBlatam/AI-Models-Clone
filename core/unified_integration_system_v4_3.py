"""
Sistema de Integración Unificada v4.3
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema unifica todos los sistemas v4.3:
- Sistema de Predicción Avanzada v4.2
- Sistema de Análisis de Costos v4.2
- Sistema de Integración Multi-Cloud v4.3
- Sistema de Seguridad Avanzada v4.3
- Sistema de Análisis de Rendimiento v4.3
- Sistema de Auto-Scaling Inteligente v4.3
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

# Import v4.3 systems
try:
    from .advanced_prediction_system_v4_2 import AdvancedPredictionSystem
    from .cost_analysis_system_v4_2 import CostAnalysisSystem
    from .multicloud_integration_system_v4_3 import MultiCloudIntegrationSystem
    from .advanced_security_system_v4_3 import AdvancedSecuritySystem
    from .performance_analysis_system_v4_3 import PerformanceAnalysisSystem
    from .intelligent_autoscaling_system_v4_3 import IntelligentAutoscalingSystem
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("Warning: Some v4.3 systems not available, using simulated versions")

# Unified Integration Components
@dataclass
class SystemStatus:
    """Status of individual systems"""
    system_name: str
    status: str  # running, stopped, error
    last_update: datetime
    health_score: float
    active_alerts: int
    performance_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class UnifiedMetrics:
    """Unified metrics from all systems"""
    timestamp: datetime
    system_metrics: Dict[str, Dict[str, float]]
    performance_metrics: Dict[str, float]
    security_metrics: Dict[str, float]
    cost_metrics: Dict[str, float]
    scaling_metrics: Dict[str, float]
    prediction_metrics: Dict[str, float]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CrossSystemAlert:
    """Alert that affects multiple systems"""
    alert_id: str
    timestamp: datetime
    alert_type: str
    severity: str
    affected_systems: List[str]
    root_cause: str
    impact_assessment: Dict[str, float]
    recommended_actions: List[str]
    status: str  # active, resolved, investigating
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SystemOptimization:
    """Cross-system optimization recommendation"""
    optimization_id: str
    timestamp: datetime
    optimization_type: str
    affected_systems: List[str]
    expected_improvements: Dict[str, float]
    implementation_effort: str
    priority: int
    cost_benefit_analysis: Dict[str, float]
    recommended_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class UnifiedIntegrationOrchestrator:
    """Orchestrates all v4.3 systems"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        
        # Initialize all systems
        self.systems = {}
        self.system_statuses = {}
        self.unified_metrics_history = deque(maxlen=10000)
        self.cross_system_alerts = deque(maxlen=1000)
        self.optimization_history = deque(maxlen=500)
        
        # Initialize systems
        self._initialize_systems()
        
        # Cross-system analysis engine
        self.cross_system_analyzer = CrossSystemAnalyzer(self.config)
        
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
            'orchestration_interval': 30,
            'system_health_thresholds': {
                'warning': 0.7,
                'critical': 0.5
            },
            'cross_system_analysis': {
                'enabled': True,
                'analysis_interval': 60
            }
        }
    
    def _initialize_systems(self):
        """Initialize all v4.3 systems"""
        
        if SYSTEMS_AVAILABLE:
            try:
                # Initialize Advanced Prediction System v4.2
                self.systems['prediction'] = AdvancedPredictionSystem(self.config_path)
                print("✅ Sistema de Predicción Avanzada v4.2 inicializado")
                
                # Initialize Cost Analysis System v4.2
                self.systems['cost_analysis'] = CostAnalysisSystem(self.config_path)
                print("✅ Sistema de Análisis de Costos v4.2 inicializado")
                
                # Initialize Multi-Cloud Integration System v4.3
                self.systems['multicloud'] = MultiCloudIntegrationSystem(self.config_path)
                print("✅ Sistema de Integración Multi-Cloud v4.3 inicializado")
                
                # Initialize Advanced Security System v4.3
                self.systems['security'] = AdvancedSecuritySystem(self.config_path)
                print("✅ Sistema de Seguridad Avanzada v4.3 inicializado")
                
                # Initialize Performance Analysis System v4.3
                self.systems['performance'] = PerformanceAnalysisSystem(self.config_path)
                print("✅ Sistema de Análisis de Rendimiento v4.3 inicializado")
                
                # Initialize Intelligent Auto-Scaling System v4.3
                self.systems['autoscaling'] = IntelligentAutoscalingSystem(self.config_path)
                print("✅ Sistema de Auto-Scaling Inteligente v4.3 inicializado")
                
            except Exception as e:
                print(f"Error inicializando sistemas: {e}")
                SYSTEMS_AVAILABLE = False
        
        if not SYSTEMS_AVAILABLE:
            # Create simulated systems for demo
            self._create_simulated_systems()
    
    def _create_simulated_systems(self):
        """Create simulated versions of systems for demo"""
        
        class SimulatedSystem:
            def __init__(self, name):
                self.name = name
                self.is_running = False
            
            async def start(self):
                self.is_running = True
                print(f"🚀 Sistema Simulado {self.name} iniciado")
            
            async def stop(self):
                self.is_running = False
                print(f"🛑 Sistema Simulado {self.name} detenido")
            
            async def get_status(self):
                return {
                    'status': 'running' if self.is_running else 'stopped',
                    'health_score': random.uniform(0.8, 1.0),
                    'active_alerts': random.randint(0, 3),
                    'performance_metrics': {
                        'cpu_usage': random.uniform(30, 80),
                        'memory_usage': random.uniform(40, 85),
                        'response_time': random.uniform(100, 2000)
                    }
                }
        
        # Create simulated systems
        system_names = [
            'prediction', 'cost_analysis', 'multicloud', 
            'security', 'performance', 'autoscaling'
        ]
        
        for name in system_names:
            self.systems[name] = SimulatedSystem(name)
            print(f"✅ Sistema Simulado {name} creado")
    
    async def start_all_systems(self):
        """Start all systems"""
        print("🚀 Iniciando todos los sistemas v4.3...")
        
        for system_name, system in self.systems.items():
            try:
                await system.start()
                self.system_statuses[system_name] = {
                    'status': 'running',
                    'start_time': datetime.now(),
                    'health_score': 1.0
                }
            except Exception as e:
                print(f"❌ Error iniciando {system_name}: {e}")
                self.system_statuses[system_name] = {
                    'status': 'error',
                    'start_time': datetime.now(),
                    'health_score': 0.0,
                    'error': str(e)
                }
        
        print("✅ Todos los sistemas iniciados")
    
    async def stop_all_systems(self):
        """Stop all systems"""
        print("🛑 Deteniendo todos los sistemas v4.3...")
        
        for system_name, system in self.systems.items():
            try:
                await system.stop()
                self.system_statuses[system_name]['status'] = 'stopped'
            except Exception as e:
                print(f"❌ Error deteniendo {system_name}: {e}")
        
        print("✅ Todos los sistemas detenidos")
    
    async def collect_unified_metrics(self) -> UnifiedMetrics:
        """Collect metrics from all systems"""
        
        system_metrics = {}
        performance_metrics = {}
        security_metrics = {}
        cost_metrics = {}
        scaling_metrics = {}
        prediction_metrics = {}
        
        for system_name, system in self.systems.items():
            try:
                # Get system status and metrics
                status = await system.get_status()
                
                # Store system-specific metrics
                system_metrics[system_name] = status.get('performance_metrics', {})
                
                # Categorize metrics by type
                if 'prediction' in system_name:
                    prediction_metrics.update(status.get('performance_metrics', {}))
                elif 'cost' in system_name:
                    cost_metrics.update(status.get('performance_metrics', {}))
                elif 'security' in system_name:
                    security_metrics.update(status.get('performance_metrics', {}))
                elif 'performance' in system_name:
                    performance_metrics.update(status.get('performance_metrics', {}))
                elif 'autoscaling' in system_name:
                    scaling_metrics.update(status.get('performance_metrics', {}))
                elif 'multicloud' in system_name:
                    # Multi-cloud affects all metrics
                    performance_metrics.update(status.get('performance_metrics', {}))
                
                # Update system status
                self.system_statuses[system_name] = {
                    'status': status.get('status', 'unknown'),
                    'last_update': datetime.now(),
                    'health_score': status.get('health_score', 0.0),
                    'active_alerts': status.get('active_alerts', 0),
                    'performance_metrics': status.get('performance_metrics', {}),
                    'metadata': status.get('metadata', {})
                }
                
            except Exception as e:
                print(f"Error obteniendo métricas de {system_name}: {e}")
                continue
        
        # Create unified metrics
        unified_metrics = UnifiedMetrics(
            timestamp=datetime.now(),
            system_metrics=system_metrics,
            performance_metrics=performance_metrics,
            security_metrics=security_metrics,
            cost_metrics=cost_metrics,
            scaling_metrics=scaling_metrics,
            prediction_metrics=prediction_metrics,
            metadata={
                'systems_analyzed': len(system_metrics),
                'collection_method': 'unified_orchestrator'
            }
        )
        
        # Store in history
        self.unified_metrics_history.append(unified_metrics)
        
        return unified_metrics
    
    async def analyze_cross_system_issues(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Analyze issues that affect multiple systems"""
        
        # Use cross-system analyzer
        alerts = await self.cross_system_analyzer.analyze_systems(unified_metrics)
        
        # Store alerts
        self.cross_system_alerts.extend(alerts)
        
        return alerts
    
    async def generate_optimization_recommendations(
        self, 
        unified_metrics: UnifiedMetrics,
        cross_system_alerts: List[CrossSystemAlert]
    ) -> List[SystemOptimization]:
        """Generate optimization recommendations across systems"""
        
        # Use cross-system analyzer
        optimizations = await self.cross_system_analyzer.generate_optimizations(
            unified_metrics, cross_system_alerts
        )
        
        # Store optimizations
        self.optimization_history.extend(optimizations)
        
        return optimizations
    
    async def get_system_health_summary(self) -> Dict[str, Any]:
        """Get overall system health summary"""
        
        total_systems = len(self.system_statuses)
        running_systems = sum(1 for status in self.system_statuses.values() 
                            if status['status'] == 'running')
        error_systems = sum(1 for status in self.system_statuses.values() 
                           if status['status'] == 'error')
        
        # Calculate overall health score
        health_scores = [status['health_score'] for status in self.system_statuses.values()]
        overall_health = np.mean(health_scores) if health_scores else 0.0
        
        # Count total alerts
        total_alerts = sum(status.get('active_alerts', 0) 
                          for status in self.system_statuses.values())
        
        # Add cross-system alerts
        total_alerts += len(self.cross_system_alerts)
        
        return {
            'total_systems': total_systems,
            'running_systems': running_systems,
            'error_systems': error_systems,
            'overall_health_score': overall_health,
            'total_alerts': total_alerts,
            'cross_system_alerts': len(self.cross_system_alerts),
            'optimization_recommendations': len(self.optimization_history),
            'last_update': datetime.now().isoformat()
        }
    
    async def display_unified_status(self):
        """Display unified status of all systems"""
        
        try:
            # Get health summary
            health_summary = await self.get_system_health_summary()
            
            print(f"\n🌐 Estado Unificado de Sistemas v4.3 - {datetime.now().strftime('%H:%M:%S')}")
            print("=" * 80)
            
            # Overall health
            health_icon = "🟢" if health_summary['overall_health_score'] > 0.8 else \
                         "🟡" if health_summary['overall_health_score'] > 0.6 else "🔴"
            
            print(f"{health_icon} Salud General: {health_summary['overall_health_score']:.1%}")
            print(f"📊 Sistemas Activos: {health_summary['running_systems']}/{health_summary['total_systems']}")
            print(f"⚠️ Alertas Totales: {health_summary['total_alerts']}")
            print(f"🔧 Optimizaciones: {health_summary['optimization_recommendations']}")
            
            # Individual system status
            print(f"\n🔍 Estado de Sistemas Individuales:")
            for system_name, status in self.system_statuses.items():
                status_icon = "🟢" if status['status'] == 'running' else \
                             "🟡" if status['status'] == 'stopped' else "🔴"
                
                print(f"  {status_icon} {system_name}: {status['status'].upper()} "
                      f"(Salud: {status['health_score']:.1%}, Alertas: {status['active_alerts']})")
            
            # Cross-system alerts
            if self.cross_system_alerts:
                active_alerts = [a for a in self.cross_system_alerts if a.status == 'active']
                if active_alerts:
                    print(f"\n🚨 Alertas Multi-Sistema ({len(active_alerts)}):")
                    for alert in active_alerts[:3]:  # Show top 3
                        severity_icon = "🔴" if alert.severity == 'critical' else \
                                       "🟡" if alert.severity == 'high' else "🟢"
                        print(f"  {severity_icon} {alert.alert_type}: {alert.root_cause}")
            
        except Exception as e:
            print(f"Error mostrando estado unificado: {e}")

class CrossSystemAnalyzer:
    """Analyzes interactions and issues across multiple systems"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.analysis_history = deque(maxlen=1000)
        
    async def analyze_systems(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Analyze systems for cross-system issues"""
        
        alerts = []
        
        # Check for performance degradation across systems
        performance_alerts = self._check_performance_degradation(unified_metrics)
        alerts.extend(performance_alerts)
        
        # Check for security issues affecting multiple systems
        security_alerts = self._check_security_issues(unified_metrics)
        alerts.extend(security_alerts)
        
        # Check for cost optimization opportunities
        cost_alerts = self._check_cost_optimization(unified_metrics)
        alerts.extend(cost_alerts)
        
        # Check for scaling coordination issues
        scaling_alerts = self._check_scaling_coordination(unified_metrics)
        alerts.extend(scaling_alerts)
        
        return alerts
    
    def _check_performance_degradation(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Check for performance degradation across systems"""
        
        alerts = []
        
        # Check if multiple systems show high resource usage
        high_usage_systems = []
        for system_name, metrics in unified_metrics.system_metrics.items():
            cpu_usage = metrics.get('cpu_usage', 0)
            memory_usage = metrics.get('memory_usage', 0)
            
            if cpu_usage > 80 or memory_usage > 85:
                high_usage_systems.append(system_name)
        
        if len(high_usage_systems) >= 2:
            alert = CrossSystemAlert(
                alert_id=f"perf_degradation_{int(time.time())}",
                timestamp=datetime.now(),
                alert_type='performance_degradation',
                severity='high',
                affected_systems=high_usage_systems,
                root_cause='Multiple systems showing high resource usage',
                impact_assessment={
                    'response_time': 25,
                    'throughput': -20,
                    'user_experience': -30
                },
                recommended_actions=[
                    'Review resource allocation across systems',
                    'Implement coordinated scaling',
                    'Optimize system interactions'
                ],
                status='active',
                metadata={
                    'systems_affected': len(high_usage_systems),
                    'detection_method': 'cross_system_analysis'
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_security_issues(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Check for security issues affecting multiple systems"""
        
        alerts = []
        
        # Check for unusual access patterns across systems
        suspicious_systems = []
        for system_name, metrics in unified_metrics.system_metrics.items():
            response_time = metrics.get('response_time', 1000)
            if response_time > 5000:  # Unusually high response time
                suspicious_systems.append(system_name)
        
        if len(suspicious_systems) >= 2:
            alert = CrossSystemAlert(
                alert_id=f"security_issue_{int(time.time())}",
                timestamp=datetime.now(),
                alert_type='security_anomaly',
                severity='critical',
                affected_systems=suspicious_systems,
                root_cause='Multiple systems showing unusual response patterns',
                impact_assessment={
                    'security_risk': 80,
                    'system_integrity': -40,
                    'data_protection': -60
                },
                recommended_actions=[
                    'Investigate potential security breach',
                    'Review access logs across all systems',
                    'Implement additional security monitoring'
                ],
                status='active',
                metadata={
                    'systems_affected': len(suspicious_systems),
                    'detection_method': 'cross_system_analysis'
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_cost_optimization(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Check for cost optimization opportunities across systems"""
        
        alerts = []
        
        # Check for underutilized systems
        underutilized_systems = []
        for system_name, metrics in unified_metrics.system_metrics.items():
            cpu_usage = metrics.get('cpu_usage', 50)
            memory_usage = metrics.get('memory_usage', 60)
            
            if cpu_usage < 30 and memory_usage < 40:
                underutilized_systems.append(system_name)
        
        if len(underutilized_systems) >= 2:
            alert = CrossSystemAlert(
                alert_id=f"cost_optimization_{int(time.time())}",
                timestamp=datetime.now(),
                alert_type='cost_optimization',
                severity='medium',
                affected_systems=underutilized_systems,
                root_cause='Multiple systems showing low resource utilization',
                impact_assessment={
                    'cost_savings': 25,
                    'resource_efficiency': 40,
                    'performance': 0
                },
                recommended_actions=[
                    'Consolidate underutilized systems',
                    'Implement resource sharing',
                    'Review system architecture'
                ],
                status='active',
                metadata={
                    'systems_affected': len(underutilized_systems),
                    'detection_method': 'cross_system_analysis'
                }
            )
            alerts.append(alert)
        
        return alerts
    
    def _check_scaling_coordination(self, unified_metrics: UnifiedMetrics) -> List[CrossSystemAlert]:
        """Check for scaling coordination issues"""
        
        alerts = []
        
        # Check for inconsistent scaling patterns
        scaling_systems = []
        for system_name, metrics in unified_metrics.system_metrics.items():
            if 'autoscaling' in system_name or 'performance' in system_name:
                scaling_systems.append(system_name)
        
        if len(scaling_systems) >= 2:
            # Check for scaling conflicts
            alert = CrossSystemAlert(
                alert_id=f"scaling_coordination_{int(time.time())}",
                timestamp=datetime.now(),
                alert_type='scaling_coordination',
                severity='medium',
                affected_systems=scaling_systems,
                root_cause='Multiple scaling systems may conflict',
                impact_assessment={
                    'scaling_efficiency': -15,
                    'resource_optimization': -20,
                    'cost_management': -10
                },
                recommended_actions=[
                    'Implement coordinated scaling policies',
                    'Review scaling priorities',
                    'Establish scaling hierarchy'
                ],
                status='active',
                metadata={
                    'systems_affected': len(scaling_systems),
                    'detection_method': 'cross_system_analysis'
                }
            )
            alerts.append(alert)
        
        return alerts
    
    async def generate_optimizations(
        self, 
        unified_metrics: UnifiedMetrics,
        cross_system_alerts: List[CrossSystemAlert]
    ) -> List[SystemOptimization]:
        """Generate optimization recommendations across systems"""
        
        optimizations = []
        
        # Generate performance optimizations
        if any(alert.alert_type == 'performance_degradation' for alert in cross_system_alerts):
            optimization = SystemOptimization(
                optimization_id=f"perf_opt_{int(time.time())}",
                timestamp=datetime.now(),
                optimization_type='performance_coordination',
                affected_systems=['performance', 'autoscaling', 'multicloud'],
                expected_improvements={
                    'response_time': -30,
                    'throughput': 25,
                    'resource_efficiency': 20
                },
                implementation_effort='medium',
                priority=1,
                cost_benefit_analysis={
                    'implementation_cost': 15,
                    'expected_savings': 40,
                    'roi': 167
                },
                recommended_actions=[
                    'Implement coordinated resource management',
                    'Optimize system interactions',
                    'Establish performance SLAs'
                ],
                metadata={
                    'triggered_by': 'performance_degradation_alert',
                    'optimization_method': 'cross_system_coordination'
                }
            )
            optimizations.append(optimization)
        
        # Generate security optimizations
        if any(alert.alert_type == 'security_anomaly' for alert in cross_system_alerts):
            optimization = SystemOptimization(
                optimization_id=f"security_opt_{int(time.time())}",
                timestamp=datetime.now(),
                optimization_type='security_coordination',
                affected_systems=['security', 'performance', 'autoscaling'],
                expected_improvements={
                    'security_posture': 50,
                    'incident_response': 40,
                    'threat_detection': 35
                },
                implementation_effort='high',
                priority=1,
                cost_benefit_analysis={
                    'implementation_cost': 25,
                    'expected_savings': 60,
                    'roi': 140
                },
                recommended_actions=[
                    'Implement unified security monitoring',
                    'Establish security response protocols',
                    'Enhance threat intelligence sharing'
                ],
                metadata={
                    'triggered_by': 'security_anomaly_alert',
                    'optimization_method': 'cross_system_security'
                }
            )
            optimizations.append(optimization)
        
        return optimizations

class UnifiedIntegrationSystem:
    """Main unified integration system"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.orchestrator = UnifiedIntegrationOrchestrator(self.config_path)
        self.is_running = False
        self.orchestration_interval = self.config.get('orchestration_interval', 30)  # 30 seconds
        
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
            'orchestration_interval': 30,
            'system_health_thresholds': {
                'warning': 0.7,
                'critical': 0.5
            },
            'cross_system_analysis': {
                'enabled': True,
                'analysis_interval': 60
            }
        }
    
    async def start(self):
        """Start the unified integration system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Integración Unificada v4.3...")
        
        # Start all systems
        await self.orchestrator.start_all_systems()
        
        # Start orchestration loop
        asyncio.create_task(self._orchestration_loop())
        
        print("✅ Sistema de Integración Unificada v4.3 iniciado")
    
    async def _orchestration_loop(self):
        """Main orchestration loop"""
        while self.is_running:
            try:
                # Collect unified metrics
                unified_metrics = await self.orchestrator.collect_unified_metrics()
                
                # Analyze cross-system issues
                cross_system_alerts = await self.orchestrator.analyze_cross_system_issues(unified_metrics)
                
                # Generate optimization recommendations
                optimizations = await self.orchestrator.generate_optimization_recommendations(
                    unified_metrics, cross_system_alerts
                )
                
                # Display unified status
                await self.orchestrator.display_unified_status()
                
                # Wait for next cycle
                await asyncio.sleep(self.orchestration_interval)
                
            except Exception as e:
                print(f"Error en loop de orquestación: {e}")
                await asyncio.sleep(15)  # Wait 15 seconds on error
    
    async def stop(self):
        """Stop the unified integration system"""
        print("🛑 Deteniendo Sistema de Integración Unificada v4.3...")
        self.is_running = False
        
        # Stop all systems
        await self.orchestrator.stop_all_systems()
        
        print("✅ Sistema detenido")

# Factory function
async def create_unified_integration_system(config_path: str) -> UnifiedIntegrationSystem:
    """Create and initialize the unified integration system"""
    system = UnifiedIntegrationSystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_unified_integration_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
