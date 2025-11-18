"""
Advanced Security Service with Threat Detection and Prevention
"""

import asyncio
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import ipaddress
from collections import defaultdict, deque
import re

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import jwt
from passlib.context import CryptContext

from ..utils.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

class ThreatLevel(Enum):
    """Threat levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SecurityEventType(Enum):
    """Security event types"""
    LOGIN_ATTEMPT = "login_attempt"
    LOGIN_SUCCESS = "login_success"
    LOGIN_FAILURE = "login_failure"
    PASSWORD_CHANGE = "password_change"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_DENIED = "permission_denied"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SQL_INJECTION_ATTEMPT = "sql_injection_attempt"
    XSS_ATTEMPT = "xss_attempt"
    CSRF_ATTEMPT = "csrf_attempt"
    FILE_UPLOAD = "file_upload"
    API_ABUSE = "api_abuse"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"

class SecurityAction(Enum):
    """Security actions"""
    ALLOW = "allow"
    BLOCK = "block"
    CHALLENGE = "challenge"
    LOG = "log"
    ALERT = "alert"
    QUARANTINE = "quarantine"

@dataclass
class SecurityEvent:
    """Security event data structure"""
    id: str
    event_type: SecurityEventType
    threat_level: ThreatLevel
    timestamp: datetime
    source_ip: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    action_taken: SecurityAction = SecurityAction.LOG
    resolved: bool = False

@dataclass
class SecurityRule:
    """Security rule configuration"""
    name: str
    description: str
    event_type: SecurityEventType
    condition: str
    threshold: int
    time_window: int  # seconds
    action: SecurityAction
    enabled: bool = True
    tags: Dict[str, str] = field(default_factory=dict)

@dataclass
class ThreatIntelligence:
    """Threat intelligence data"""
    source: str
    threat_type: str
    indicator: str
    confidence: float
    severity: ThreatLevel
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SecurityConfig:
    """Security configuration"""
    enable_rate_limiting: bool = True
    enable_ip_blocking: bool = True
    enable_brute_force_protection: bool = True
    enable_sql_injection_protection: bool = True
    enable_xss_protection: bool = True
    enable_csrf_protection: bool = True
    enable_file_scanning: bool = True
    enable_api_security: bool = True
    max_login_attempts: int = 5
    lockout_duration: int = 900  # seconds
    session_timeout: int = 3600  # seconds
    password_min_length: int = 8
    password_require_special: bool = True
    password_require_numbers: bool = True
    password_require_uppercase: bool = True
    encryption_key: Optional[str] = None
    jwt_secret: Optional[str] = None
    jwt_expiry: int = 3600  # seconds

class AdvancedSecurityService:
    """Advanced Security Service with Threat Detection and Prevention"""
    
    def __init__(self):
        self.config = SecurityConfig()
        self.security_events = deque(maxlen=10000)
        self.security_rules = {}
        self.threat_intelligence = {}
        self.blocked_ips = set()
        self.failed_attempts = defaultdict(list)
        self.active_sessions = {}
        self.encryption_key = None
        self.jwt_secret = None
        self.password_context = None
        
        # Initialize security components
        self._initialize_encryption()
        self._initialize_password_hashing()
        self._initialize_default_rules()
        self._initialize_threat_intelligence()
        
        logger.info("Advanced Security Service initialized")
    
    def _initialize_encryption(self):
        """Initialize encryption components"""
        try:
            # Generate or load encryption key
            if self.config.encryption_key:
                self.encryption_key = self.config.encryption_key.encode()
            else:
                self.encryption_key = Fernet.generate_key()
            
            # Generate or load JWT secret
            if self.config.jwt_secret:
                self.jwt_secret = self.config.jwt_secret
            else:
                self.jwt_secret = secrets.token_urlsafe(32)
            
            logger.info("Encryption components initialized")
            
        except Exception as e:
            logger.error(f"Error initializing encryption: {e}")
            raise
    
    def _initialize_password_hashing(self):
        """Initialize password hashing"""
        try:
            self.password_context = CryptContext(
                schemes=["bcrypt"],
                deprecated="auto",
                bcrypt__rounds=12
            )
            
            logger.info("Password hashing initialized")
            
        except Exception as e:
            logger.error(f"Error initializing password hashing: {e}")
            raise
    
    def _initialize_default_rules(self):
        """Initialize default security rules"""
        try:
            default_rules = [
                SecurityRule(
                    name="Brute Force Protection",
                    description="Detect and block brute force attacks",
                    event_type=SecurityEventType.LOGIN_FAILURE,
                    condition="count",
                    threshold=5,
                    time_window=300,  # 5 minutes
                    action=SecurityAction.BLOCK
                ),
                SecurityRule(
                    name="SQL Injection Detection",
                    description="Detect SQL injection attempts",
                    event_type=SecurityEventType.SQL_INJECTION_ATTEMPT,
                    condition="detect",
                    threshold=1,
                    time_window=60,
                    action=SecurityAction.BLOCK
                ),
                SecurityRule(
                    name="XSS Detection",
                    description="Detect XSS attempts",
                    event_type=SecurityEventType.XSS_ATTEMPT,
                    condition="detect",
                    threshold=1,
                    time_window=60,
                    action=SecurityAction.BLOCK
                ),
                SecurityRule(
                    name="API Rate Limiting",
                    description="Limit API requests per IP",
                    event_type=SecurityEventType.API_ABUSE,
                    condition="count",
                    threshold=100,
                    time_window=60,
                    action=SecurityAction.BLOCK
                ),
                SecurityRule(
                    name="Suspicious Activity",
                    description="Detect suspicious patterns",
                    event_type=SecurityEventType.SUSPICIOUS_ACTIVITY,
                    condition="detect",
                    threshold=1,
                    time_window=300,
                    action=SecurityAction.ALERT
                )
            ]
            
            for rule in default_rules:
                self.security_rules[rule.name] = rule
            
            logger.info(f"Initialized {len(default_rules)} default security rules")
            
        except Exception as e:
            logger.error(f"Error initializing default rules: {e}")
    
    def _initialize_threat_intelligence(self):
        """Initialize threat intelligence"""
        try:
            # Common malicious IPs (example)
            malicious_ips = [
                "192.168.1.100",
                "10.0.0.50"
            ]
            
            for ip in malicious_ips:
                self.threat_intelligence[ip] = ThreatIntelligence(
                    source="internal",
                    threat_type="malicious_ip",
                    indicator=ip,
                    confidence=0.9,
                    severity=ThreatLevel.HIGH,
                    timestamp=datetime.utcnow()
                )
            
            # Common SQL injection patterns
            sql_patterns = [
                r"union\s+select",
                r"drop\s+table",
                r"delete\s+from",
                r"insert\s+into",
                r"update\s+set",
                r"'\s*or\s*'",
                r"'\s*and\s*'",
                r"'\s*;\s*--",
                r"'\s*;\s*#"
            ]
            
            for pattern in sql_patterns:
                self.threat_intelligence[f"sql_pattern_{pattern}"] = ThreatIntelligence(
                    source="internal",
                    threat_type="sql_injection",
                    indicator=pattern,
                    confidence=0.8,
                    severity=ThreatLevel.HIGH,
                    timestamp=datetime.utcnow()
                )
            
            # Common XSS patterns
            xss_patterns = [
                r"<script[^>]*>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>"
            ]
            
            for pattern in xss_patterns:
                self.threat_intelligence[f"xss_pattern_{pattern}"] = ThreatIntelligence(
                    source="internal",
                    threat_type="xss",
                    indicator=pattern,
                    confidence=0.8,
                    severity=ThreatLevel.MEDIUM,
                    timestamp=datetime.utcnow()
                )
            
            logger.info("Threat intelligence initialized")
            
        except Exception as e:
            logger.error(f"Error initializing threat intelligence: {e}")
    
    async def log_security_event(self, event_type: SecurityEventType, source_ip: str, 
                                user_id: Optional[str] = None, session_id: Optional[str] = None,
                                details: Dict[str, Any] = None, threat_level: ThreatLevel = ThreatLevel.LOW) -> SecurityEvent:
        """Log a security event"""
        try:
            event_id = secrets.token_urlsafe(16)
            
            event = SecurityEvent(
                id=event_id,
                event_type=event_type,
                threat_level=threat_level,
                timestamp=datetime.utcnow(),
                source_ip=source_ip,
                user_id=user_id,
                session_id=session_id,
                details=details or {}
            )
            
            # Add to events list
            self.security_events.append(event)
            
            # Check security rules
            action = await self._check_security_rules(event)
            event.action_taken = action
            
            # Execute action
            await self._execute_security_action(event, action)
            
            logger.info(f"Security event logged: {event_type.value} from {source_ip}")
            
            return event
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            raise
    
    async def _check_security_rules(self, event: SecurityEvent) -> SecurityAction:
        """Check security rules against event"""
        try:
            for rule_name, rule in self.security_rules.items():
                if not rule.enabled or rule.event_type != event.event_type:
                    continue
                
                if rule.condition == "count":
                    # Check if threshold is exceeded within time window
                    if await self._check_count_rule(event, rule):
                        return rule.action
                
                elif rule.condition == "detect":
                    # Check if threat is detected
                    if await self._check_detection_rule(event, rule):
                        return rule.action
            
            return SecurityAction.LOG
            
        except Exception as e:
            logger.error(f"Error checking security rules: {e}")
            return SecurityAction.LOG
    
    async def _check_count_rule(self, event: SecurityEvent, rule: SecurityRule) -> bool:
        """Check count-based security rule"""
        try:
            # Count events of the same type from the same source within time window
            cutoff_time = datetime.utcnow() - timedelta(seconds=rule.time_window)
            
            if rule.event_type == SecurityEventType.LOGIN_FAILURE:
                # Check failed login attempts
                key = f"{event.source_ip}_{event.user_id}"
                attempts = self.failed_attempts.get(key, [])
                
                # Remove old attempts
                recent_attempts = [attempt for attempt in attempts if attempt >= cutoff_time]
                self.failed_attempts[key] = recent_attempts
                
                # Add current attempt
                recent_attempts.append(event.timestamp)
                
                return len(recent_attempts) >= rule.threshold
            
            elif rule.event_type == SecurityEventType.API_ABUSE:
                # Count API requests from same IP
                count = 0
                for e in self.security_events:
                    if (e.source_ip == event.source_ip and 
                        e.event_type == SecurityEventType.API_ABUSE and 
                        e.timestamp >= cutoff_time):
                        count += 1
                
                return count >= rule.threshold
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking count rule: {e}")
            return False
    
    async def _check_detection_rule(self, event: SecurityEvent, rule: SecurityRule) -> bool:
        """Check detection-based security rule"""
        try:
            if rule.event_type == SecurityEventType.SQL_INJECTION_ATTEMPT:
                # Check for SQL injection patterns
                return await self._detect_sql_injection(event)
            
            elif rule.event_type == SecurityEventType.XSS_ATTEMPT:
                # Check for XSS patterns
                return await self._detect_xss(event)
            
            elif rule.event_type == SecurityEventType.SUSPICIOUS_ACTIVITY:
                # Check for suspicious patterns
                return await self._detect_suspicious_activity(event)
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking detection rule: {e}")
            return False
    
    async def _detect_sql_injection(self, event: SecurityEvent) -> bool:
        """Detect SQL injection attempts"""
        try:
            # Check request data for SQL injection patterns
            request_data = event.details.get('request_data', '')
            if isinstance(request_data, dict):
                request_data = json.dumps(request_data)
            
            request_data = str(request_data).lower()
            
            # Check against known SQL injection patterns
            for threat_id, threat in self.threat_intelligence.items():
                if threat.threat_type == "sql_injection":
                    pattern = threat.indicator
                    if re.search(pattern, request_data, re.IGNORECASE):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting SQL injection: {e}")
            return False
    
    async def _detect_xss(self, event: SecurityEvent) -> bool:
        """Detect XSS attempts"""
        try:
            # Check request data for XSS patterns
            request_data = event.details.get('request_data', '')
            if isinstance(request_data, dict):
                request_data = json.dumps(request_data)
            
            request_data = str(request_data)
            
            # Check against known XSS patterns
            for threat_id, threat in self.threat_intelligence.items():
                if threat.threat_type == "xss":
                    pattern = threat.indicator
                    if re.search(pattern, request_data, re.IGNORECASE):
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting XSS: {e}")
            return False
    
    async def _detect_suspicious_activity(self, event: SecurityEvent) -> bool:
        """Detect suspicious activity patterns"""
        try:
            # Check for multiple failed login attempts from different IPs
            if event.event_type == SecurityEventType.LOGIN_FAILURE:
                user_id = event.user_id
                if user_id:
                    # Count unique IPs with failed attempts for this user
                    unique_ips = set()
                    cutoff_time = datetime.utcnow() - timedelta(hours=1)
                    
                    for e in self.security_events:
                        if (e.user_id == user_id and 
                            e.event_type == SecurityEventType.LOGIN_FAILURE and 
                            e.timestamp >= cutoff_time):
                            unique_ips.add(e.source_ip)
                    
                    if len(unique_ips) >= 3:  # Suspicious if from 3+ different IPs
                        return True
            
            # Check for rapid API requests
            if event.event_type == SecurityEventType.API_ABUSE:
                # Count requests in last minute
                cutoff_time = datetime.utcnow() - timedelta(minutes=1)
                count = 0
                
                for e in self.security_events:
                    if (e.source_ip == event.source_ip and 
                        e.event_type == SecurityEventType.API_ABUSE and 
                        e.timestamp >= cutoff_time):
                        count += 1
                
                if count >= 50:  # Suspicious if 50+ requests per minute
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error detecting suspicious activity: {e}")
            return False
    
    async def _execute_security_action(self, event: SecurityEvent, action: SecurityAction):
        """Execute security action"""
        try:
            if action == SecurityAction.BLOCK:
                await self._block_ip(event.source_ip, "Security rule violation")
            
            elif action == SecurityAction.ALERT:
                await self._send_security_alert(event)
            
            elif action == SecurityAction.QUARANTINE:
                await self._quarantine_user(event.user_id, "Suspicious activity detected")
            
            elif action == SecurityAction.CHALLENGE:
                await self._challenge_request(event)
            
        except Exception as e:
            logger.error(f"Error executing security action: {e}")
    
    async def _block_ip(self, ip: str, reason: str):
        """Block an IP address"""
        try:
            self.blocked_ips.add(ip)
            logger.warning(f"IP blocked: {ip} - {reason}")
            
        except Exception as e:
            logger.error(f"Error blocking IP: {e}")
    
    async def _send_security_alert(self, event: SecurityEvent):
        """Send security alert"""
        try:
            alert_data = {
                'event_id': event.id,
                'event_type': event.event_type.value,
                'threat_level': event.threat_level.value,
                'source_ip': event.source_ip,
                'user_id': event.user_id,
                'timestamp': event.timestamp.isoformat(),
                'details': event.details
            }
            
            # This would typically send to notification service
            logger.warning(f"Security alert: {json.dumps(alert_data)}")
            
        except Exception as e:
            logger.error(f"Error sending security alert: {e}")
    
    async def _quarantine_user(self, user_id: str, reason: str):
        """Quarantine a user"""
        try:
            if user_id:
                # This would typically update user status in database
                logger.warning(f"User quarantined: {user_id} - {reason}")
            
        except Exception as e:
            logger.error(f"Error quarantining user: {e}")
    
    async def _challenge_request(self, event: SecurityEvent):
        """Challenge a request (e.g., CAPTCHA)"""
        try:
            # This would typically implement CAPTCHA or other challenge
            logger.info(f"Request challenged: {event.id}")
            
        except Exception as e:
            logger.error(f"Error challenging request: {e}")
    
    async def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked"""
        try:
            return ip in self.blocked_ips
            
        except Exception as e:
            logger.error(f"Error checking IP block status: {e}")
            return False
    
    async def unblock_ip(self, ip: str):
        """Unblock an IP address"""
        try:
            self.blocked_ips.discard(ip)
            logger.info(f"IP unblocked: {ip}")
            
        except Exception as e:
            logger.error(f"Error unblocking IP: {e}")
    
    async def hash_password(self, password: str) -> str:
        """Hash a password"""
        try:
            return self.password_context.hash(password)
            
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password"""
        try:
            return self.password_context.verify(password, hashed_password)
            
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    async def generate_jwt_token(self, user_id: str, additional_claims: Dict[str, Any] = None) -> str:
        """Generate JWT token"""
        try:
            payload = {
                'user_id': user_id,
                'iat': datetime.utcnow(),
                'exp': datetime.utcnow() + timedelta(seconds=self.config.jwt_expiry)
            }
            
            if additional_claims:
                payload.update(additional_claims)
            
            token = jwt.encode(payload, self.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    async def verify_jwt_token(self, token: str) -> Dict[str, Any]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return {}
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return {}
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return {}
    
    async def encrypt_data(self, data: str) -> str:
        """Encrypt data"""
        try:
            fernet = Fernet(self.encryption_key)
            encrypted_data = fernet.encrypt(data.encode())
            return encrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data"""
        try:
            fernet = Fernet(self.encryption_key)
            decrypted_data = fernet.decrypt(encrypted_data.encode())
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    async def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength"""
        try:
            issues = []
            score = 0
            
            # Length check
            if len(password) < self.config.password_min_length:
                issues.append(f"Password must be at least {self.config.password_min_length} characters long")
            else:
                score += 1
            
            # Special characters check
            if self.config.password_require_special:
                if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                    issues.append("Password must contain at least one special character")
                else:
                    score += 1
            
            # Numbers check
            if self.config.password_require_numbers:
                if not re.search(r'\d', password):
                    issues.append("Password must contain at least one number")
                else:
                    score += 1
            
            # Uppercase check
            if self.config.password_require_uppercase:
                if not re.search(r'[A-Z]', password):
                    issues.append("Password must contain at least one uppercase letter")
                else:
                    score += 1
            
            # Common password check
            common_passwords = ['password', '123456', 'qwerty', 'abc123', 'password123']
            if password.lower() in common_passwords:
                issues.append("Password is too common")
                score = 0
            
            # Determine strength
            if score >= 4:
                strength = "strong"
            elif score >= 3:
                strength = "medium"
            elif score >= 2:
                strength = "weak"
            else:
                strength = "very_weak"
            
            return {
                'valid': len(issues) == 0,
                'strength': strength,
                'score': score,
                'issues': issues
            }
            
        except Exception as e:
            logger.error(f"Error validating password strength: {e}")
            return {'valid': False, 'strength': 'unknown', 'score': 0, 'issues': ['Validation error']}
    
    async def scan_file(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Scan file for security threats"""
        try:
            threats = []
            risk_level = "low"
            
            # Check file size
            if len(file_content) > 10 * 1024 * 1024:  # 10MB
                threats.append("File size exceeds limit")
                risk_level = "medium"
            
            # Check file extension
            dangerous_extensions = ['.exe', '.bat', '.cmd', '.scr', '.pif', '.com']
            file_ext = filename.lower().split('.')[-1] if '.' in filename else ''
            if f'.{file_ext}' in dangerous_extensions:
                threats.append("Dangerous file extension")
                risk_level = "high"
            
            # Check for embedded scripts
            content_str = file_content.decode('utf-8', errors='ignore').lower()
            script_patterns = ['<script', 'javascript:', 'vbscript:', 'onload=', 'onerror=']
            for pattern in script_patterns:
                if pattern in content_str:
                    threats.append(f"Embedded script detected: {pattern}")
                    risk_level = "high"
            
            # Check for suspicious strings
            suspicious_strings = ['eval(', 'exec(', 'system(', 'shell_exec', 'passthru(']
            for pattern in suspicious_strings:
                if pattern in content_str:
                    threats.append(f"Suspicious function call: {pattern}")
                    risk_level = "high"
            
            return {
                'safe': len(threats) == 0,
                'risk_level': risk_level,
                'threats': threats,
                'file_size': len(file_content),
                'filename': filename
            }
            
        except Exception as e:
            logger.error(f"Error scanning file: {e}")
            return {'safe': False, 'risk_level': 'unknown', 'threats': ['Scan error'], 'file_size': 0, 'filename': filename}
    
    async def add_security_rule(self, rule: SecurityRule):
        """Add a security rule"""
        try:
            self.security_rules[rule.name] = rule
            logger.info(f"Added security rule: {rule.name}")
            
        except Exception as e:
            logger.error(f"Error adding security rule: {e}")
    
    async def remove_security_rule(self, rule_name: str):
        """Remove a security rule"""
        try:
            if rule_name in self.security_rules:
                del self.security_rules[rule_name]
                logger.info(f"Removed security rule: {rule_name}")
            else:
                logger.warning(f"Security rule not found: {rule_name}")
                
        except Exception as e:
            logger.error(f"Error removing security rule: {e}")
    
    async def get_security_events(self, limit: int = 100, event_type: Optional[SecurityEventType] = None) -> List[SecurityEvent]:
        """Get security events"""
        try:
            events = list(self.security_events)
            
            if event_type:
                events = [e for e in events if e.event_type == event_type]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    async def get_security_summary(self) -> Dict[str, Any]:
        """Get security summary"""
        try:
            # Count events by type
            event_counts = defaultdict(int)
            for event in self.security_events:
                event_counts[event.event_type.value] += 1
            
            # Count events by threat level
            threat_counts = defaultdict(int)
            for event in self.security_events:
                threat_counts[event.threat_level.value] += 1
            
            # Count blocked IPs
            blocked_ip_count = len(self.blocked_ips)
            
            # Count active rules
            active_rules = len([rule for rule in self.security_rules.values() if rule.enabled])
            
            summary = {
                'total_events': len(self.security_events),
                'events_by_type': dict(event_counts),
                'events_by_threat_level': dict(threat_counts),
                'blocked_ips': blocked_ip_count,
                'security_rules': len(self.security_rules),
                'active_rules': active_rules,
                'threat_intelligence': len(self.threat_intelligence)
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting security summary: {e}")
            return {}
    
    async def export_security_data(self, format: str = "json", period_hours: int = 24) -> str:
        """Export security data"""
        try:
            # Get events for the specified period
            cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
            events = [e for e in self.security_events if e.timestamp >= cutoff_time]
            
            export_data = {
                'events': [
                    {
                        'id': event.id,
                        'event_type': event.event_type.value,
                        'threat_level': event.threat_level.value,
                        'timestamp': event.timestamp.isoformat(),
                        'source_ip': event.source_ip,
                        'user_id': event.user_id,
                        'session_id': event.session_id,
                        'details': event.details,
                        'action_taken': event.action_taken.value,
                        'resolved': event.resolved
                    }
                    for event in events
                ],
                'blocked_ips': list(self.blocked_ips),
                'security_rules': [
                    {
                        'name': rule.name,
                        'description': rule.description,
                        'event_type': rule.event_type.value,
                        'condition': rule.condition,
                        'threshold': rule.threshold,
                        'time_window': rule.time_window,
                        'action': rule.action.value,
                        'enabled': rule.enabled,
                        'tags': rule.tags
                    }
                    for rule in self.security_rules.values()
                ]
            }
            
            if format.lower() == "json":
                return json.dumps(export_data, indent=2)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
        except Exception as e:
            logger.error(f"Error exporting security data: {e}")
            return ""
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get service status"""
        try:
            status = {
                'service': 'Advanced Security Service',
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'config': {
                    'enable_rate_limiting': self.config.enable_rate_limiting,
                    'enable_ip_blocking': self.config.enable_ip_blocking,
                    'enable_brute_force_protection': self.config.enable_brute_force_protection,
                    'enable_sql_injection_protection': self.config.enable_sql_injection_protection,
                    'enable_xss_protection': self.config.enable_xss_protection,
                    'enable_csrf_protection': self.config.enable_csrf_protection,
                    'enable_file_scanning': self.config.enable_file_scanning,
                    'enable_api_security': self.config.enable_api_security
                },
                'security': {
                    'total_events': len(self.security_events),
                    'blocked_ips': len(self.blocked_ips),
                    'security_rules': len(self.security_rules),
                    'active_rules': len([rule for rule in self.security_rules.values() if rule.enabled]),
                    'threat_intelligence': len(self.threat_intelligence)
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting service status: {e}")
            return {
                'service': 'Advanced Security Service',
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }


























