#!/usr/bin/env python3
"""
🛡️ ADVANCED SECURITY MODULE - Blaze AI System
Anomaly detection, behavioral analysis, and adaptive threat prevention
"""

import asyncio
import time
import json
import hashlib
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, deque
import numpy as np
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class ThreatLevel(Enum):
    """Threat level enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AnomalyType(Enum):
    """Anomaly type enumeration."""
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    SUSPICIOUS_PATTERN = "suspicious_pattern"
    BEHAVIORAL_ANOMALY = "behavioral_anomaly"
    GEOGRAPHICAL_ANOMALY = "geographical_anomaly"
    TIMING_ANOMALY = "timing_anomaly"
    PAYLOAD_ANOMALY = "payload_anomaly"

class SecurityAction(Enum):
    """Security action enumeration."""
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    RATE_LIMIT = "rate_limit"
    LOG = "log"
    ALERT = "alert"

@dataclass
class SecurityEvent:
    """Security event information."""
    event_id: str
    timestamp: datetime
    source_ip: str
    user_agent: str
    endpoint: str
    method: str
    payload_size: int
    threat_level: ThreatLevel
    anomaly_type: Optional[AnomalyType]
    risk_score: float
    action_taken: SecurityAction
    details: Dict[str, Any]

@dataclass
class BehavioralProfile:
    """User behavioral profile."""
    user_id: str
    ip_address: str
    request_patterns: Dict[str, int]
    timing_patterns: List[float]
    payload_patterns: Dict[str, int]
    risk_score: float
    last_updated: datetime
    anomaly_count: int

@dataclass
class SecurityConfig:
    """Advanced security configuration."""
    enable_anomaly_detection: bool = True
    enable_behavioral_analysis: bool = True
    enable_ml_threat_detection: bool = True
    risk_threshold_high: float = 0.7
    risk_threshold_critical: float = 0.9
    learning_rate: float = 0.1
    max_behavioral_history: int = 1000
    anomaly_detection_window: int = 300  # 5 minutes
    suspicious_patterns: List[str] = None
    blocked_ips: List[str] = None
    whitelist_ips: List[str] = None

class AdvancedSecurity:
    """Advanced security system with anomaly detection and behavioral analysis."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.security_events: deque = deque(maxlen=10000)
        self.behavioral_profiles: Dict[str, BehavioralProfile] = {}
        self.ip_risk_scores: Dict[str, float] = defaultdict(float)
        self.endpoint_risk_scores: Dict[str, float] = defaultdict(float)
        self.global_risk_score: float = 0.0
        self.threat_patterns: Dict[str, float] = {}
        self.anomaly_detectors: Dict[str, Any] = {}
        self._init_time = time.time()
        
        # Initialize suspicious patterns
        if not self.config.suspicious_patterns:
            self.config.suspicious_patterns = [
                r"<script.*?>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"union\s+select",
                r"drop\s+table",
                r"exec\s*\(",
                r"eval\s*\(",
                r"system\s*\(",
                r"\.\./",
                r"\.\.\\",
                r"\.\.%2f",
                r"\.\.%5c"
            ]
        
        # Initialize blocked IPs
        if not self.config.blocked_ips:
            self.config.blocked_ips = []
        
        # Initialize whitelist IPs
        if not self.config.whitelist_ips:
            self.config.whitelist_ips = []
        
        self._initialize_anomaly_detectors()
    
    def _initialize_anomaly_detectors(self):
        """Initialize various anomaly detection algorithms."""
        # Rate limiting anomaly detector
        self.anomaly_detectors['rate_limit'] = {
            'window_size': 60,  # 1 minute
            'threshold': 100,    # requests per minute
            'history': defaultdict(list)
        }
        
        # Timing anomaly detector
        self.anomaly_detectors['timing'] = {
            'window_size': 300,  # 5 minutes
            'threshold': 2.0,    # standard deviations
            'history': defaultdict(list)
        }
        
        # Payload anomaly detector
        self.anomaly_detectors['payload'] = {
            'window_size': 300,  # 5 minutes
            'threshold': 2.0,    # standard deviations
            'history': defaultdict(list)
        }
    
    async def analyze_request(self, request_data: Dict[str, Any]) -> Tuple[SecurityAction, float, Optional[AnomalyType]]:
        """Analyze incoming request for security threats."""
        start_time = time.time()
        
        try:
            # Extract request information
            source_ip = request_data.get('source_ip', 'unknown')
            user_agent = request_data.get('user_agent', '')
            endpoint = request_data.get('endpoint', '')
            method = request_data.get('method', 'GET')
            payload_size = request_data.get('payload_size', 0)
            user_id = request_data.get('user_id', 'anonymous')
            
            # Check whitelist first
            if source_ip in self.config.whitelist_ips:
                return SecurityAction.ALLOW, 0.0, None
            
            # Check blacklist
            if source_ip in self.config.blocked_ips:
                return SecurityAction.BLOCK, 1.0, None
            
            # Calculate base risk score
            risk_score = self._calculate_base_risk_score(
                source_ip, endpoint, method, payload_size, user_agent
            )
            
            # Check for suspicious patterns
            pattern_anomaly = self._detect_suspicious_patterns(
                request_data.get('payload', ''),
                user_agent,
                endpoint
            )
            
            if pattern_anomaly:
                risk_score += 0.3
                anomaly_type = AnomalyType.SUSPICIOUS_PATTERN
            else:
                anomaly_type = None
            
            # Behavioral analysis
            if self.config.enable_behavioral_analysis:
                behavioral_risk = await self._analyze_behavior(
                    user_id, source_ip, endpoint, method, payload_size
                )
                risk_score += behavioral_risk
            
            # Anomaly detection
            if self.config.enable_anomaly_detection:
                anomaly_risk, detected_anomaly = await self._detect_anomalies(
                    source_ip, endpoint, payload_size, request_data
                )
                risk_score += anomaly_risk
                
                if detected_anomaly and not anomaly_type:
                    anomaly_type = detected_anomaly
            
            # Determine action based on risk score
            action = self._determine_security_action(risk_score)
            
            # Update behavioral profile
            await self._update_behavioral_profile(
                user_id, source_ip, endpoint, method, payload_size, risk_score
            )
            
            # Log security event
            event = SecurityEvent(
                event_id=self._generate_event_id(),
                timestamp=datetime.now(),
                source_ip=source_ip,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                payload_size=payload_size,
                threat_level=self._get_threat_level(risk_score),
                anomaly_type=anomaly_type,
                risk_score=risk_score,
                action_taken=action,
                details=request_data
            )
            
            self.security_events.append(event)
            
            # Update global risk metrics
            self._update_global_risk_metrics(risk_score, source_ip, endpoint)
            
            logger.info(f"Security analysis completed: {action.value} (risk: {risk_score:.3f})")
            
            return action, risk_score, anomaly_type
            
        except Exception as e:
            logger.error(f"Error in security analysis: {e}")
            # Default to logging on error
            return SecurityAction.LOG, 0.5, None
    
    def _calculate_base_risk_score(self, source_ip: str, endpoint: str, method: str, 
                                  payload_size: int, user_agent: str) -> float:
        """Calculate base risk score for request."""
        risk_score = 0.0
        
        # IP-based risk
        ip_risk = self.ip_risk_scores.get(source_ip, 0.0)
        risk_score += ip_risk * 0.3
        
        # Endpoint-based risk
        endpoint_risk = self.endpoint_risk_scores.get(endpoint, 0.0)
        risk_score += endpoint_risk * 0.2
        
        # Method-based risk
        if method in ['POST', 'PUT', 'DELETE']:
            risk_score += 0.1
        
        # Payload size risk
        if payload_size > 1000000:  # 1MB
            risk_score += 0.1
        elif payload_size > 100000:  # 100KB
            risk_score += 0.05
        
        # User agent risk
        if not user_agent or user_agent.lower() in ['', 'null', 'undefined']:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    def _detect_suspicious_patterns(self, payload: str, user_agent: str, endpoint: str) -> bool:
        """Detect suspicious patterns in request data."""
        try:
            # Check payload for suspicious patterns
            for pattern in self.config.suspicious_patterns:
                if re.search(pattern, payload, re.IGNORECASE):
                    logger.warning(f"Suspicious pattern detected: {pattern}")
                    return True
            
            # Check user agent for suspicious patterns
            suspicious_ua_patterns = [
                r"sqlmap",
                r"nmap",
                r"nikto",
                r"dirbuster",
                r"burpsuite"
            ]
            
            for pattern in suspicious_ua_patterns:
                if re.search(pattern, user_agent, re.IGNORECASE):
                    logger.warning(f"Suspicious user agent: {user_agent}")
                    return True
            
            # Check endpoint for suspicious patterns
            suspicious_endpoints = [
                r"\.\./",
                r"\.\.\\",
                r"admin",
                r"config",
                r"\.env"
            ]
            
            for pattern in suspicious_endpoints:
                if re.search(pattern, endpoint, re.IGNORECASE):
                    logger.warning(f"Suspicious endpoint: {endpoint}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in pattern detection: {e}")
            return False
    
    async def _analyze_behavior(self, user_id: str, source_ip: str, endpoint: str, 
                               method: str, payload_size: int) -> float:
        """Analyze user behavior for anomalies."""
        try:
            profile_key = f"{user_id}:{source_ip}"
            
            if profile_key not in self.behavioral_profiles:
                # Create new profile
                self.behavioral_profiles[profile_key] = BehavioralProfile(
                    user_id=user_id,
                    ip_address=source_ip,
                    request_patterns=defaultdict(int),
                    timing_patterns=[],
                    payload_patterns=defaultdict(int),
                    risk_score=0.0,
                    last_updated=datetime.now(),
                    anomaly_count=0
                )
            
            profile = self.behavioral_profiles[profile_key]
            
            # Update request patterns
            endpoint_key = f"{method}:{endpoint}"
            profile.request_patterns[endpoint_key] += 1
            
            # Update payload patterns
            payload_category = self._categorize_payload_size(payload_size)
            profile.payload_patterns[payload_category] += 1
            
            # Calculate behavioral risk
            behavioral_risk = self._calculate_behavioral_risk(profile)
            
            # Update profile
            profile.risk_score = behavioral_risk
            profile.last_updated = datetime.now()
            
            return behavioral_risk
            
        except Exception as e:
            logger.error(f"Error in behavioral analysis: {e}")
            return 0.0
    
    def _categorize_payload_size(self, payload_size: int) -> str:
        """Categorize payload size for analysis."""
        if payload_size == 0:
            return "empty"
        elif payload_size < 100:
            return "small"
        elif payload_size < 1000:
            return "medium"
        elif payload_size < 10000:
            return "large"
        else:
            return "very_large"
    
    def _calculate_behavioral_risk(self, profile: BehavioralProfile) -> float:
        """Calculate risk score based on behavioral patterns."""
        risk_score = 0.0
        
        # Check for unusual request patterns
        total_requests = sum(profile.request_patterns.values())
        if total_requests > 0:
            for endpoint, count in profile.request_patterns.items():
                frequency = count / total_requests
                if frequency > 0.8:  # Single endpoint dominates
                    risk_score += 0.2
                elif frequency < 0.01:  # Very rare endpoint
                    risk_score += 0.1
        
        # Check payload size distribution
        total_payloads = sum(profile.payload_patterns.values())
        if total_payloads > 0:
            for category, count in profile.payload_patterns.items():
                frequency = count / total_payloads
                if category == "very_large" and frequency > 0.5:
                    risk_score += 0.3
                elif category == "empty" and frequency > 0.8:
                    risk_score += 0.1
        
        # Check anomaly count
        if profile.anomaly_count > 5:
            risk_score += 0.2
        elif profile.anomaly_count > 2:
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    async def _detect_anomalies(self, source_ip: str, endpoint: str, 
                               payload_size: int, request_data: Dict[str, Any]) -> Tuple[float, Optional[AnomalyType]]:
        """Detect various types of anomalies."""
        try:
            total_risk = 0.0
            detected_anomaly = None
            
            # Rate limiting anomaly
            rate_anomaly, rate_risk = self._detect_rate_anomaly(source_ip, endpoint)
            if rate_anomaly:
                total_risk += rate_risk
                detected_anomaly = AnomalyType.RATE_LIMIT_EXCEEDED
            
            # Timing anomaly
            timing_anomaly, timing_risk = self._detect_timing_anomaly(source_ip)
            if timing_anomaly:
                total_risk += timing_risk
                if not detected_anomaly:
                    detected_anomaly = AnomalyType.TIMING_ANOMALY
            
            # Payload anomaly
            payload_anomaly, payload_risk = self._detect_payload_anomaly(endpoint, payload_size)
            if payload_anomaly:
                total_risk += payload_risk
                if not detected_anomaly:
                    detected_anomaly = AnomalyType.PAYLOAD_ANOMALY
            
            return total_risk, detected_anomaly
            
        except Exception as e:
            logger.error(f"Error in anomaly detection: {e}")
            return 0.0, None
    
    def _detect_rate_anomaly(self, source_ip: str, endpoint: str) -> Tuple[bool, float]:
        """Detect rate limiting anomalies."""
        try:
            detector = self.anomaly_detectors['rate_limit']
            key = f"{source_ip}:{endpoint}"
            current_time = time.time()
            
            # Clean old entries
            detector['history'][key] = [
                t for t in detector['history'][key] 
                if current_time - t < detector['window_size']
            ]
            
            # Add current request
            detector['history'][key].append(current_time)
            
            # Check if threshold exceeded
            if len(detector['history'][key]) > detector['threshold']:
                return True, 0.4
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Error in rate anomaly detection: {e}")
            return False, 0.0
    
    def _detect_timing_anomaly(self, source_ip: str) -> Tuple[bool, float]:
        """Detect timing anomalies."""
        try:
            detector = self.anomaly_detectors['timing']
            current_time = time.time()
            
            # Clean old entries
            detector['history'][source_ip] = [
                t for t in detector['history'][source_ip] 
                if current_time - t < detector['window_size']
            ]
            
            # Add current request
            detector['history'][source_ip].append(current_time)
            
            # Calculate timing intervals
            if len(detector['history'][source_ip]) > 2:
                intervals = np.diff(sorted(detector['history'][source_ip]))
                mean_interval = np.mean(intervals)
                std_interval = np.std(intervals)
                
                if std_interval > 0:
                    current_interval = intervals[-1]
                    z_score = abs(current_interval - mean_interval) / std_interval
                    
                    if z_score > detector['threshold']:
                        return True, 0.3
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Error in timing anomaly detection: {e}")
            return False, 0.0
    
    def _detect_payload_anomaly(self, endpoint: str, payload_size: int) -> Tuple[bool, float]:
        """Detect payload size anomalies."""
        try:
            detector = self.anomaly_detectors['payload']
            current_time = time.time()
            
            # Clean old entries
            detector['history'][endpoint] = [
                size for size in detector['history'][endpoint] 
                if current_time - size < detector['window_size']
            ]
            
            # Add current payload size
            detector['history'][endpoint].append(payload_size)
            
            # Calculate payload size statistics
            if len(detector['history'][endpoint]) > 5:
                sizes = np.array(detector['history'][endpoint])
                mean_size = np.mean(sizes)
                std_size = np.std(sizes)
                
                if std_size > 0:
                    z_score = abs(payload_size - mean_size) / std_size
                    
                    if z_score > detector['threshold']:
                        return True, 0.2
            
            return False, 0.0
            
        except Exception as e:
            logger.error(f"Error in payload anomaly detection: {e}")
            return False, 0.0
    
    def _determine_security_action(self, risk_score: float) -> SecurityAction:
        """Determine security action based on risk score."""
        if risk_score >= self.config.risk_threshold_critical:
            return SecurityAction.BLOCK
        elif risk_score >= self.config.risk_threshold_high:
            return SecurityAction.CHALLENGE
        elif risk_score >= 0.5:
            return SecurityAction.RATE_LIMIT
        elif risk_score >= 0.3:
            return SecurityAction.LOG
        else:
            return SecurityAction.ALLOW
    
    def _get_threat_level(self, risk_score: float) -> ThreatLevel:
        """Get threat level based on risk score."""
        if risk_score >= self.config.risk_threshold_critical:
            return ThreatLevel.CRITICAL
        elif risk_score >= self.config.risk_threshold_high:
            return ThreatLevel.HIGH
        elif risk_score >= 0.5:
            return ThreatLevel.MEDIUM
        else:
            return ThreatLevel.LOW
    
    async def _update_behavioral_profile(self, user_id: str, source_ip: str, 
                                       endpoint: str, method: str, payload_size: int, risk_score: float):
        """Update behavioral profile with new information."""
        try:
            profile_key = f"{user_id}:{source_ip}"
            
            if profile_key in self.behavioral_profiles:
                profile = self.behavioral_profiles[profile_key]
                
                # Update timing patterns
                current_time = time.time()
                if profile.timing_patterns:
                    last_time = profile.timing_patterns[-1]
                    interval = current_time - last_time
                    profile.timing_patterns.append(interval)
                    
                    # Keep only recent patterns
                    if len(profile.timing_patterns) > 100:
                        profile.timing_patterns = profile.timing_patterns[-100:]
                
                profile.timing_patterns.append(current_time)
                
                # Update risk score with learning
                profile.risk_score = (
                    profile.risk_score * (1 - self.config.learning_rate) +
                    risk_score * self.config.learning_rate
                )
                
        except Exception as e:
            logger.error(f"Error updating behavioral profile: {e}")
    
    def _update_global_risk_metrics(self, risk_score: float, source_ip: str, endpoint: str):
        """Update global risk metrics."""
        try:
            # Update IP risk score
            self.ip_risk_scores[source_ip] = (
                self.ip_risk_scores[source_ip] * 0.9 + risk_score * 0.1
            )
            
            # Update endpoint risk score
            self.endpoint_risk_scores[endpoint] = (
                self.endpoint_risk_scores[endpoint] * 0.9 + risk_score * 0.1
            )
            
            # Update global risk score
            self.global_risk_score = (
                self.global_risk_score * 0.99 + risk_score * 0.01
            )
            
        except Exception as e:
            logger.error(f"Error updating global risk metrics: {e}")
    
    def _generate_event_id(self) -> str:
        """Generate unique event ID."""
        timestamp = int(time.time() * 1000000)
        random_part = hashlib.md5(f"{timestamp}".encode()).hexdigest()[:8]
        return f"sec_{timestamp}_{random_part}"
    
    async def get_security_stats(self) -> Dict[str, Any]:
        """Get comprehensive security statistics."""
        try:
            current_time = datetime.now()
            
            # Calculate recent events
            recent_events = [
                event for event in self.security_events
                if (current_time - event.timestamp).total_seconds() < 3600  # Last hour
            ]
            
            # Calculate threat level distribution
            threat_levels = defaultdict(int)
            anomaly_types = defaultdict(int)
            actions_taken = defaultdict(int)
            
            for event in recent_events:
                threat_levels[event.threat_level.value] += 1
                if event.anomaly_type:
                    anomaly_types[event.anomaly_type.value] += 1
                actions_taken[event.action_taken.value] += 1
            
            # Calculate average risk scores
            if recent_events:
                avg_risk_score = sum(event.risk_score for event in recent_events) / len(recent_events)
            else:
                avg_risk_score = 0.0
            
            return {
                'global_risk_score': self.global_risk_score,
                'total_events': len(self.security_events),
                'recent_events': len(recent_events),
                'average_risk_score': avg_risk_score,
                'threat_level_distribution': dict(threat_levels),
                'anomaly_type_distribution': dict(anomaly_types),
                'actions_taken_distribution': dict(actions_taken),
                'behavioral_profiles_count': len(self.behavioral_profiles),
                'ip_risk_scores': dict(self.ip_risk_scores),
                'endpoint_risk_scores': dict(self.endpoint_risk_scores),
                'uptime': time.time() - self._init_time
            }
            
        except Exception as e:
            logger.error(f"Error getting security stats: {e}")
            return {}
    
    async def block_ip(self, ip_address: str, reason: str = "Manual block"):
        """Manually block an IP address."""
        try:
            if ip_address not in self.config.blocked_ips:
                self.config.blocked_ips.append(ip_address)
                logger.warning(f"IP {ip_address} manually blocked: {reason}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False
    
    async def unblock_ip(self, ip_address: str):
        """Unblock an IP address."""
        try:
            if ip_address in self.config.blocked_ips:
                self.config.blocked_ips.remove(ip_address)
                logger.info(f"IP {ip_address} unblocked")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error unblocking IP {ip_address}: {e}")
            return False
    
    async def whitelist_ip(self, ip_address: str, reason: str = "Manual whitelist"):
        """Add IP to whitelist."""
        try:
            if ip_address not in self.config.whitelist_ips:
                self.config.whitelist_ips.append(ip_address)
                logger.info(f"IP {ip_address} whitelisted: {reason}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error whitelisting IP {ip_address}: {e}")
            return False

# Utility functions
def create_advanced_security(config: SecurityConfig) -> AdvancedSecurity:
    """Create and configure an advanced security instance."""
    return AdvancedSecurity(config)

# Example usage
async def main():
    """Example usage of the advanced security system."""
    config = SecurityConfig(
        enable_anomaly_detection=True,
        enable_behavioral_analysis=True,
        risk_threshold_high=0.7,
        risk_threshold_critical=0.9
    )
    
    security = create_advanced_security(config)
    
    # Test security analysis
    request_data = {
        'source_ip': '192.168.1.100',
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'endpoint': '/api/users',
        'method': 'POST',
        'payload_size': 1500,
        'user_id': 'user123',
        'payload': '{"name": "John Doe", "email": "john@example.com"}'
    }
    
    action, risk_score, anomaly_type = await security.analyze_request(request_data)
    
    print(f"Security Analysis Result:")
    print(f"  Action: {action.value}")
    print(f"  Risk Score: {risk_score:.3f}")
    print(f"  Anomaly Type: {anomaly_type.value if anomaly_type else 'None'}")
    
    # Get security stats
    stats = await security.get_security_stats()
    print(f"\nSecurity Stats: {json.dumps(stats, indent=2)}")

if __name__ == "__main__":
    asyncio.run(main())
