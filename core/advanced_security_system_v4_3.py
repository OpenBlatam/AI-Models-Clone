"""
Sistema de Seguridad Avanzada con IA v4.3
HeyGen AI - Sistema de Monitoreo Inteligente con IA Avanzada

Este sistema implementa:
- Detección de amenazas con IA
- Análisis de anomalías en tiempo real
- Monitoreo de seguridad proactivo
- Respuesta automática a incidentes
- Auditoría de seguridad inteligente
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

# Security and ML imports
try:
    import sklearn
    from sklearn.ensemble import IsolationForest, RandomForestClassifier
    from sklearn.preprocessing import StandardScaler
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: scikit-learn not available, using simplified security models")

# Advanced Security Components
@dataclass
class SecurityEvent:
    """Security event with threat analysis"""
    event_id: str
    timestamp: datetime
    event_type: str  # login, access, anomaly, threat
    severity: str  # low, medium, high, critical
    source_ip: str
    user_id: str
    resource_accessed: str
    threat_score: float
    anomaly_score: float
    ioc_indicators: List[str]  # Indicators of Compromise
    response_actions: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    threat_id: str
    timestamp: datetime
    threat_type: str
    description: str
    severity: str
    confidence: float
    source: str
    ioc_patterns: List[str]
    affected_resources: List[str]
    mitigation_strategies: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityAnomaly:
    """Security anomaly detection result"""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: str
    confidence: float
    affected_entities: List[str]
    risk_assessment: str
    recommended_actions: List[str]
    false_positive_probability: float
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityIncident:
    """Security incident with response plan"""
    incident_id: str
    timestamp: datetime
    incident_type: str
    severity: str
    status: str  # open, investigating, resolved, closed
    affected_systems: List[str]
    threat_actors: List[str]
    response_team: List[str]
    containment_actions: List[str]
    recovery_plan: str
    lessons_learned: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

class AIThreatDetector:
    """AI-powered threat detection system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.threat_models = {}
        self.anomaly_detectors = {}
        self.threat_intelligence_db = {}
        self.event_history = deque(maxlen=10000)
        self.threat_patterns = {}
        
        # Initialize ML models
        self._initialize_security_models()
        
        # Load threat intelligence
        self._load_threat_intelligence()
        
    def _initialize_security_models(self):
        """Initialize security ML models"""
        if ML_AVAILABLE:
            # Anomaly detection models
            self.anomaly_detectors = {
                'network': IsolationForest(contamination=0.1, random_state=42),
                'user_behavior': IsolationForest(contamination=0.05, random_state=42),
                'system_access': IsolationForest(contamination=0.15, random_state=42)
            }
            
            # Threat classification models
            self.threat_models = {
                'malware': RandomForestClassifier(n_estimators=100, random_state=42),
                'intrusion': RandomForestClassifier(n_estimators=100, random_state=42),
                'data_exfiltration': RandomForestClassifier(n_estimators=100, random_state=42)
            }
            
            # Feature scalers
            self.scalers = {
                'network': StandardScaler(),
                'user_behavior': StandardScaler(),
                'system_access': StandardScaler()
            }
        else:
            # Fallback to simplified models
            self.anomaly_detectors = {
                'network': self._create_simple_anomaly_detector(),
                'user_behavior': self._create_simple_anomaly_detector(),
                'system_access': self._create_simple_anomaly_detector()
            }
    
    def _create_simple_anomaly_detector(self):
        """Create simple anomaly detector as fallback"""
        class SimpleAnomalyDetector:
            def __init__(self):
                self.history = deque(maxlen=100)
                self.threshold = 2.0  # Standard deviations
                
            def detect_anomaly(self, features):
                if len(self.history) < 10:
                    return 0.0, 0.5  # No anomaly, low confidence
                
                # Calculate z-score
                values = list(self.history)
                mean_val = statistics.mean(values)
                std_val = statistics.stdev(values) if len(values) > 1 else 1.0
                
                if std_val == 0:
                    return 0.0, 0.5
                
                z_score = abs(features - mean_val) / std_val
                anomaly_score = min(1.0, z_score / self.threshold)
                confidence = min(0.9, len(self.history) / 100)
                
                return anomaly_score, confidence
            
            def update(self, value):
                self.history.append(value)
        
        return SimpleAnomalyDetector()
    
    def _load_threat_intelligence(self):
        """Load threat intelligence data"""
        # In a real system, this would load from external threat feeds
        # For demo purposes, create sample threat intelligence
        
        self.threat_intelligence_db = {
            'malware': {
                'patterns': ['suspicious_process', 'unusual_network_activity', 'file_modifications'],
                'severity': 'high',
                'mitigation': ['isolate_system', 'scan_for_malware', 'update_definitions']
            },
            'intrusion': {
                'patterns': ['failed_logins', 'privilege_escalation', 'unusual_access_patterns'],
                'severity': 'critical',
                'mitigation': ['block_ip', 'reset_credentials', 'audit_access_logs']
            },
            'data_exfiltration': {
                'patterns': ['large_data_transfers', 'unusual_export_activity', 'external_connections'],
                'severity': 'critical',
                'mitigation': ['block_transfers', 'investigate_user_activity', 'enhance_monitoring']
            }
        }
    
    async def analyze_security_event(
        self, 
        event_data: Dict[str, Any]
    ) -> SecurityEvent:
        """Analyze security event using AI models"""
        
        # Extract features for analysis
        features = self._extract_security_features(event_data)
        
        # Detect anomalies
        anomaly_scores = {}
        for detector_type, detector in self.anomaly_detectors.items():
            if hasattr(detector, 'detect_anomaly'):
                anomaly_score, confidence = detector.detect_anomaly(features.get(detector_type, 0))
                anomaly_scores[detector_type] = anomaly_score
                
                # Update detector with new data
                if hasattr(detector, 'update'):
                    detector.update(features.get(detector_type, 0))
        
        # Calculate overall anomaly score
        overall_anomaly_score = np.mean(list(anomaly_scores.values())) if anomaly_scores else 0.0
        
        # Detect threats
        threat_score, threat_type, ioc_indicators = await self._detect_threats(
            event_data, features, anomaly_scores
        )
        
        # Determine severity
        severity = self._determine_severity(threat_score, overall_anomaly_score)
        
        # Generate response actions
        response_actions = self._generate_response_actions(
            threat_type, severity, ioc_indicators
        )
        
        # Create security event
        security_event = SecurityEvent(
            event_id=f"sec_{int(time.time())}",
            timestamp=datetime.now(),
            event_type=event_data.get('event_type', 'unknown'),
            severity=severity,
            source_ip=event_data.get('source_ip', 'unknown'),
            user_id=event_data.get('user_id', 'unknown'),
            resource_accessed=event_data.get('resource', 'unknown'),
            threat_score=threat_score,
            anomaly_score=overall_anomaly_score,
            ioc_indicators=ioc_indicators,
            response_actions=response_actions,
            metadata={
                'anomaly_scores': anomaly_scores,
                'features_analyzed': list(features.keys()),
                'threat_type': threat_type,
                'analysis_confidence': min(0.95, (threat_score + overall_anomaly_score) / 2)
            }
        )
        
        # Store in history
        self.event_history.append(security_event)
        
        return security_event
    
    def _extract_security_features(self, event_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract security features from event data"""
        features = {}
        
        # Network features
        if 'source_ip' in event_data:
            features['network'] = self._calculate_ip_risk_score(event_data['source_ip'])
        
        # User behavior features
        if 'user_id' in event_data:
            features['user_behavior'] = self._calculate_user_risk_score(event_data['user_id'])
        
        # System access features
        if 'resource' in event_data:
            features['system_access'] = self._calculate_resource_risk_score(event_data['resource'])
        
        # Time-based features
        current_hour = datetime.now().hour
        features['time_factor'] = 1.0 if 9 <= current_hour <= 17 else 1.5  # Higher risk outside business hours
        
        # Frequency features
        features['event_frequency'] = self._calculate_event_frequency(event_data)
        
        return features
    
    def _calculate_ip_risk_score(self, ip_address: str) -> float:
        """Calculate risk score for IP address"""
        # In a real system, this would query threat intelligence databases
        # For demo purposes, generate synthetic risk scores
        
        # Simulate some IPs as higher risk
        if ip_address.startswith('192.168.'):
            return random.uniform(0.1, 0.3)  # Internal network
        elif ip_address.startswith('10.'):
            return random.uniform(0.2, 0.4)  # Private network
        else:
            return random.uniform(0.0, 0.8)  # External IPs
    
    def _calculate_user_risk_score(self, user_id: str) -> float:
        """Calculate risk score for user"""
        # In a real system, this would analyze user behavior patterns
        # For demo purposes, generate synthetic risk scores
        
        if user_id.startswith('admin'):
            return random.uniform(0.1, 0.3)  # Admin users
        elif user_id.startswith('guest'):
            return random.uniform(0.6, 0.9)  # Guest users
        else:
            return random.uniform(0.2, 0.6)  # Regular users
    
    def _calculate_resource_risk_score(self, resource: str) -> float:
        """Calculate risk score for resource access"""
        # In a real system, this would analyze resource sensitivity
        # For demo purposes, generate synthetic risk scores
        
        if 'admin' in resource.lower():
            return random.uniform(0.7, 0.9)  # Admin resources
        elif 'user' in resource.lower():
            return random.uniform(0.3, 0.6)  # User resources
        else:
            return random.uniform(0.1, 0.5)  # General resources
    
    def _calculate_event_frequency(self, event_data: Dict[str, Any]) -> float:
        """Calculate event frequency score"""
        # In a real system, this would analyze event patterns
        # For demo purposes, generate synthetic frequency scores
        
        return random.uniform(0.0, 1.0)
    
    async def _detect_threats(
        self, 
        event_data: Dict[str, Any], 
        features: Dict[str, float],
        anomaly_scores: Dict[str, float]
    ) -> Tuple[float, str, List[str]]:
        """Detect threats using AI models and threat intelligence"""
        
        threat_score = 0.0
        threat_type = 'unknown'
        ioc_indicators = []
        
        # Analyze against known threat patterns
        for threat_category, threat_info in self.threat_intelligence_db.items():
            pattern_matches = 0
            total_patterns = len(threat_info['patterns'])
            
            for pattern in threat_info['patterns']:
                if self._pattern_matches(event_data, pattern):
                    pattern_matches += 1
            
            # Calculate threat score based on pattern matches
            if pattern_matches > 0:
                category_score = pattern_matches / total_patterns
                if category_score > threat_score:
                    threat_score = category_score
                    threat_type = threat_category
        
        # Adjust threat score based on anomaly scores
        if anomaly_scores:
            anomaly_factor = np.mean(list(anomaly_scores.values()))
            threat_score = min(1.0, threat_score + anomaly_factor * 0.3)
        
        # Generate IOC indicators based on threat type
        if threat_type in self.threat_intelligence_db:
            ioc_indicators = self._generate_ioc_indicators(threat_type, event_data)
        
        return threat_score, threat_type, ioc_indicators
    
    def _pattern_matches(self, event_data: Dict[str, Any], pattern: str) -> bool:
        """Check if event data matches a threat pattern"""
        
        if pattern == 'suspicious_process':
            return 'process_name' in event_data and any(
                suspicious in event_data['process_name'].lower() 
                for suspicious in ['cmd', 'powershell', 'wscript']
            )
        
        elif pattern == 'unusual_network_activity':
            return 'bytes_transferred' in event_data and event_data['bytes_transferred'] > 1000000
        
        elif pattern == 'failed_logins':
            return 'login_success' in event_data and not event_data['login_success']
        
        elif pattern == 'privilege_escalation':
            return 'privilege_level' in event_data and event_data['privilege_level'] > 5
        
        elif pattern == 'large_data_transfers':
            return 'data_size' in event_data and event_data['data_size'] > 50000000
        
        return False
    
    def _generate_ioc_indicators(self, threat_type: str, event_data: Dict[str, Any]) -> List[str]:
        """Generate Indicators of Compromise based on threat type"""
        
        ioc_indicators = []
        
        if threat_type == 'malware':
            if 'process_name' in event_data:
                ioc_indicators.append(f"Suspicious process: {event_data['process_name']}")
            if 'source_ip' in event_data:
                ioc_indicators.append(f"Source IP: {event_data['source_ip']}")
        
        elif threat_type == 'intrusion':
            if 'user_id' in event_data:
                ioc_indicators.append(f"User account: {event_data['user_id']}")
            if 'resource' in event_data:
                ioc_indicators.append(f"Resource accessed: {event_data['resource']}")
        
        elif threat_type == 'data_exfiltration':
            if 'data_size' in event_data:
                ioc_indicators.append(f"Data size: {event_data['data_size']} bytes")
            if 'destination' in event_data:
                ioc_indicators.append(f"Destination: {event_data['destination']}")
        
        return ioc_indicators
    
    def _determine_severity(self, threat_score: float, anomaly_score: float) -> str:
        """Determine event severity based on threat and anomaly scores"""
        
        combined_score = (threat_score + anomaly_score) / 2
        
        if combined_score >= 0.8:
            return 'critical'
        elif combined_score >= 0.6:
            return 'high'
        elif combined_score >= 0.4:
            return 'medium'
        elif combined_score >= 0.2:
            return 'low'
        else:
            return 'info'
    
    def _generate_response_actions(
        self, 
        threat_type: str, 
        severity: str, 
        ioc_indicators: List[str]
    ) -> List[str]:
        """Generate recommended response actions"""
        
        actions = []
        
        if severity in ['high', 'critical']:
            actions.append("Immediate incident response required")
            actions.append("Isolate affected systems")
            actions.append("Notify security team")
        
        if threat_type in self.threat_intelligence_db:
            threat_info = self.threat_intelligence_db[threat_type]
            actions.extend(threat_info['mitigation'])
        
        if ioc_indicators:
            actions.append("Investigate IOC indicators")
            actions.append("Update threat intelligence")
        
        return actions

class SecurityIncidentManager:
    """Manages security incidents and response"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.active_incidents = {}
        self.incident_history = deque(maxlen=1000)
        self.response_teams = config.get('response_teams', [])
        self.escalation_policies = config.get('escalation_policies', {})
        
    async def create_incident(
        self, 
        security_event: SecurityEvent
    ) -> SecurityIncident:
        """Create security incident from security event"""
        
        # Determine incident type
        incident_type = self._determine_incident_type(security_event)
        
        # Assign response team
        response_team = self._assign_response_team(security_event)
        
        # Create containment plan
        containment_actions = self._generate_containment_plan(security_event)
        
        # Create recovery plan
        recovery_plan = self._generate_recovery_plan(security_event)
        
        # Create incident
        incident = SecurityIncident(
            incident_id=f"inc_{security_event.event_id}",
            timestamp=datetime.now(),
            incident_type=incident_type,
            severity=security_event.severity,
            status='open',
            affected_systems=[security_event.resource_accessed],
            threat_actors=['unknown'],  # Would be determined by investigation
            response_team=response_team,
            containment_actions=containment_actions,
            recovery_plan=recovery_plan,
            lessons_learned=[],
            metadata={
                'source_event': security_event.event_id,
                'threat_score': security_event.threat_score,
                'anomaly_score': security_event.anomaly_score
            }
        )
        
        # Store incident
        self.active_incidents[incident.incident_id] = incident
        self.incident_history.append(incident)
        
        return incident
    
    def _determine_incident_type(self, security_event: SecurityEvent) -> str:
        """Determine incident type from security event"""
        
        if security_event.threat_score > 0.8:
            return 'active_threat'
        elif security_event.anomaly_score > 0.7:
            return 'suspicious_activity'
        elif security_event.severity in ['high', 'critical']:
            return 'security_breach'
        else:
            return 'security_alert'
    
    def _assign_response_team(self, security_event: SecurityEvent) -> List[str]:
        """Assign response team based on severity and type"""
        
        if security_event.severity == 'critical':
            return ['incident_response_team', 'security_analysts', 'system_administrators']
        elif security_event.severity == 'high':
            return ['security_analysts', 'system_administrators']
        elif security_event.severity == 'medium':
            return ['security_analysts']
        else:
            return ['security_monitors']
    
    def _generate_containment_plan(self, security_event: SecurityEvent) -> List[str]:
        """Generate containment actions for security event"""
        
        containment_actions = []
        
        if security_event.severity in ['high', 'critical']:
            containment_actions.extend([
                "Isolate affected systems from network",
                "Disable compromised user accounts",
                "Block suspicious IP addresses",
                "Implement additional monitoring"
            ])
        
        if 'malware' in security_event.metadata.get('threat_type', ''):
            containment_actions.extend([
                "Run malware scans on affected systems",
                "Update antivirus definitions",
                "Quarantine suspicious files"
            ])
        
        return containment_actions
    
    def _generate_recovery_plan(self, security_event: SecurityEvent) -> List[str]:
        """Generate recovery plan for security event"""
        
        recovery_plan = [
            "Investigate root cause of incident",
            "Implement security patches and updates",
            "Restore systems from clean backups",
            "Conduct post-incident review",
            "Update security policies and procedures"
        ]
        
        return recovery_plan
    
    async def update_incident_status(
        self, 
        incident_id: str, 
        new_status: str,
        updates: Dict[str, Any] = None
    ):
        """Update incident status and details"""
        
        if incident_id not in self.active_incidents:
            raise ValueError(f"Incident {incident_id} not found")
        
        incident = self.active_incidents[incident_id]
        incident.status = new_status
        
        if updates:
            for key, value in updates.items():
                if hasattr(incident, key):
                    setattr(incident, key, value)
        
        # If incident is resolved, move to history
        if new_status in ['resolved', 'closed']:
            incident.lessons_learned = updates.get('lessons_learned', [])
            del self.active_incidents[incident_id]
    
    async def get_active_incidents(self) -> List[SecurityIncident]:
        """Get list of active security incidents"""
        return list(self.active_incidents.values())
    
    async def get_incident_summary(self) -> Dict[str, Any]:
        """Get summary of all incidents"""
        
        active_count = len(self.active_incidents)
        total_count = len(self.incident_history)
        
        severity_counts = defaultdict(int)
        for incident in self.incident_history:
            severity_counts[incident.severity] += 1
        
        return {
            'active_incidents': active_count,
            'total_incidents': total_count,
            'severity_distribution': dict(severity_counts),
            'average_resolution_time': '2.5 hours',  # Would be calculated from actual data
            'incident_types': list(set(inc.incident_type for inc in self.incident_history))
        }

class AdvancedSecuritySystem:
    """Main system combining all advanced security capabilities"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config = self._load_config()
        self.threat_detector = AIThreatDetector(self.config)
        self.incident_manager = SecurityIncidentManager(self.config)
        self.is_running = False
        self.security_interval = self.config.get('security_interval', 60)  # 1 minute
        
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
            'security_interval': 60,
            'response_teams': [
                'incident_response_team',
                'security_analysts',
                'system_administrators',
                'security_monitors'
            ],
            'escalation_policies': {
                'low': 'security_monitors',
                'medium': 'security_analysts',
                'high': 'incident_response_team',
                'critical': 'all_teams'
            }
        }
    
    async def start(self):
        """Start the advanced security system"""
        if self.is_running:
            print("⚠️ El sistema ya está ejecutándose")
            return
        
        self.is_running = True
        print("🚀 Iniciando Sistema de Seguridad Avanzada v4.3...")
        
        # Start security monitoring loop
        asyncio.create_task(self._security_monitoring_loop())
        
        print("✅ Sistema de Seguridad Avanzada v4.3 iniciado")
    
    async def _security_monitoring_loop(self):
        """Main security monitoring loop"""
        while self.is_running:
            try:
                # Generate simulated security events
                security_events = await self._generate_security_events()
                
                # Analyze each event
                for event_data in security_events:
                    try:
                        # Analyze security event
                        security_event = await self.threat_detector.analyze_security_event(event_data)
                        
                        # Create incident if high severity
                        if security_event.severity in ['high', 'critical']:
                            incident = await self.incident_manager.create_incident(security_event)
                            print(f"🚨 Incidente creado: {incident.incident_id} - {incident.incident_type}")
                        
                        # Display security event
                        await self._display_security_event(security_event)
                        
                    except Exception as e:
                        print(f"Error analizando evento de seguridad: {e}")
                        continue
                
                # Display incident summary
                await self._display_incident_summary()
                
                # Wait for next cycle
                await asyncio.sleep(self.security_interval)
                
            except Exception as e:
                print(f"Error en loop de monitoreo de seguridad: {e}")
                await asyncio.sleep(30)  # Wait 30 seconds on error
    
    async def _generate_security_events(self) -> List[Dict[str, Any]]:
        """Generate simulated security events for demo"""
        
        events = []
        
        # Generate random number of events (1-5)
        num_events = random.randint(1, 5)
        
        for i in range(num_events):
            event_type = random.choice(['login', 'access', 'anomaly', 'threat'])
            
            if event_type == 'login':
                event_data = {
                    'event_type': 'login',
                    'source_ip': f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                    'user_id': f"user_{random.randint(1, 100)}",
                    'resource': 'authentication_service',
                    'login_success': random.choice([True, False]),
                    'privilege_level': random.randint(1, 10)
                }
            
            elif event_type == 'access':
                event_data = {
                    'event_type': 'access',
                    'source_ip': f"10.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                    'user_id': f"admin_{random.randint(1, 20)}",
                    'resource': f"resource_{random.randint(1, 50)}",
                    'data_size': random.randint(1000, 1000000),
                    'destination': f"external_{random.randint(1, 10)}.com"
                }
            
            elif event_type == 'anomaly':
                event_data = {
                    'event_type': 'anomaly',
                    'source_ip': f"172.{random.randint(16, 31)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                    'user_id': f"guest_{random.randint(1, 50)}",
                    'resource': 'system_monitor',
                    'process_name': random.choice(['cmd.exe', 'powershell.exe', 'wscript.exe']),
                    'bytes_transferred': random.randint(1000000, 10000000)
                }
            
            else:  # threat
                event_data = {
                    'event_type': 'threat',
                    'source_ip': f"203.{random.randint(1, 254)}.{random.randint(1, 254)}.{random.randint(1, 254)}",
                    'user_id': f"unknown_{random.randint(1, 100)}",
                    'resource': 'critical_system',
                    'malware_signature': 'trojan.win32.generic',
                    'network_connections': random.randint(10, 100)
                }
            
            events.append(event_data)
        
        return events
    
    async def _display_security_event(self, security_event: SecurityEvent):
        """Display security event information"""
        
        print(f"\n🔒 Evento de Seguridad - {security_event.timestamp.strftime('%H:%M:%S')}")
        print(f"  Tipo: {security_event.event_type}")
        print(f"  Severidad: {security_event.severity.upper()}")
        print(f"  IP Origen: {security_event.source_ip}")
        print(f"  Usuario: {security_event.user_id}")
        print(f"  Recurso: {security_event.resource_accessed}")
        print(f"  Score de Amenaza: {security_event.threat_score:.2%}")
        print(f"  Score de Anomalía: {security_event.anomaly_score:.2%}")
        
        if security_event.ioc_indicators:
            print(f"  IOCs: {', '.join(security_event.ioc_indicators[:2])}")
        
        if security_event.response_actions:
            print(f"  Acciones: {security_event.response_actions[0]}")
    
    async def _display_incident_summary(self):
        """Display incident summary"""
        
        try:
            summary = await self.incident_manager.get_incident_summary()
            active_incidents = await self.incident_manager.get_active_incidents()
            
            print(f"\n🚨 Resumen de Incidentes - {datetime.now().strftime('%H:%M:%S')}")
            print(f"  Incidentes Activos: {summary['active_incidents']}")
            print(f"  Total Histórico: {summary['total_incidents']}")
            
            if active_incidents:
                print(f"  Incidentes Críticos: {len([i for i in active_incidents if i.severity == 'critical'])}")
                print(f"  Incidentes Altos: {len([i for i in active_incidents if i.severity == 'high'])}")
            
        except Exception as e:
            print(f"Error obteniendo resumen de incidentes: {e}")
    
    async def stop(self):
        """Stop the advanced security system"""
        print("🛑 Deteniendo Sistema de Seguridad Avanzada v4.3...")
        self.is_running = False
        print("✅ Sistema detenido")

# Factory function
async def create_advanced_security_system(config_path: str) -> AdvancedSecuritySystem:
    """Create and initialize the advanced security system"""
    system = AdvancedSecuritySystem(config_path)
    return system

if __name__ == "__main__":
    # Demo usage
    async def main():
        config_path = "advanced_integration_config_v4_1.yaml"
        system = await create_advanced_security_system(config_path)
        
        try:
            await system.start()
            
            # Keep running
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            await system.stop()
    
    asyncio.run(main())
