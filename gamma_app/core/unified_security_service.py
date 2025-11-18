"""
Unified Security Service - Consolidated security functionality
Combines all security-related services into a single, optimized service
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import hashlib
import hmac
import secrets
import jwt
import bcrypt
from datetime import datetime, timedelta
import ipaddress
import re
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import json
import time
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security Levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ThreatType(Enum):
    """Threat Types"""
    BRUTE_FORCE = "brute_force"
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    DDOS = "ddos"
    MALWARE = "malware"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"

@dataclass
class SecurityEvent:
    """Security Event"""
    id: str
    timestamp: datetime
    threat_type: ThreatType
    level: SecurityLevel
    source_ip: str
    user_id: Optional[str]
    description: str
    metadata: Dict[str, Any]

@dataclass
class SecurityConfig:
    """Security Configuration"""
    jwt_secret: str
    encryption_key: str
    rate_limit_requests: int = 100
    rate_limit_window: int = 3600
    max_login_attempts: int = 5
    lockout_duration: int = 900
    password_min_length: int = 8
    session_timeout: int = 3600
    enable_2fa: bool = True
    enable_ip_blocking: bool = True
    enable_threat_detection: bool = True

class UnifiedSecurityService:
    """
    Unified Security Service - Consolidated security functionality
    Handles authentication, authorization, encryption, threat detection, and more
    """
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.encryption_key = config.encryption_key.encode()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # Security tracking
        self.failed_attempts: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, datetime] = {}
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Rate limiting
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        
        # Threat detection patterns
        self.threat_patterns = {
            ThreatType.SQL_INJECTION: [
                r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
                r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
                r"(\b(OR|AND)\s+'.*'\s*=\s*'.*')",
                r"(\b(OR|AND)\s+\".*\"\s*=\s*\".*\")"
            ],
            ThreatType.XSS: [
                r"<script[^>]*>.*?</script>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>"
            ],
            ThreatType.CSRF: [
                r"<form[^>]*action\s*=\s*[\"'][^\"']*[\"']",
                r"<a[^>]*href\s*=\s*[\"']javascript:",
                r"<img[^>]*src\s*=\s*[\"'][^\"']*[\"']"
            ]
        }
        
        logger.info("UnifiedSecurityService initialized")
    
    async def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        try:
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        except Exception as e:
            logger.error(f"Error hashing password: {e}")
            raise
    
    async def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Error verifying password: {e}")
            return False
    
    async def generate_jwt_token(self, user_id: str, payload: Dict[str, Any] = None) -> str:
        """Generate JWT token"""
        try:
            now = datetime.utcnow()
            token_payload = {
                'user_id': user_id,
                'iat': now,
                'exp': now + timedelta(seconds=self.config.session_timeout),
                'jti': secrets.token_urlsafe(32)
            }
            
            if payload:
                token_payload.update(payload)
            
            token = jwt.encode(token_payload, self.config.jwt_secret, algorithm='HS256')
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {e}")
            raise
    
    async def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.config.jwt_secret, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
        except Exception as e:
            logger.error(f"Error verifying JWT token: {e}")
            return None
    
    async def encrypt_data(self, data: str) -> str:
        """Encrypt data using Fernet"""
        try:
            encrypted_data = self.cipher_suite.encrypt(data.encode())
            return base64.b64encode(encrypted_data).decode()
        except Exception as e:
            logger.error(f"Error encrypting data: {e}")
            raise
    
    async def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt data using Fernet"""
        try:
            decoded_data = base64.b64decode(encrypted_data.encode())
            decrypted_data = self.cipher_suite.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            logger.error(f"Error decrypting data: {e}")
            raise
    
    async def check_rate_limit(self, identifier: str) -> bool:
        """Check if request is within rate limit"""
        try:
            now = time.time()
            window_start = now - self.config.rate_limit_window
            
            # Clean old requests
            while (self.rate_limits[identifier] and 
                   self.rate_limits[identifier][0] < window_start):
                self.rate_limits[identifier].popleft()
            
            # Check if under limit
            if len(self.rate_limits[identifier]) >= self.config.rate_limit_requests:
                return False
            
            # Add current request
            self.rate_limits[identifier].append(now)
            return True
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return False
    
    async def check_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        try:
            if ip_address in self.blocked_ips:
                block_time = self.blocked_ips[ip_address]
                if datetime.now() < block_time:
                    return True
                else:
                    # Remove expired block
                    del self.blocked_ips[ip_address]
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking IP block: {e}")
            return False
    
    async def block_ip(self, ip_address: str, duration: int = None) -> bool:
        """Block IP address"""
        try:
            if duration is None:
                duration = self.config.lockout_duration
            
            block_until = datetime.now() + timedelta(seconds=duration)
            self.blocked_ips[ip_address] = block_until
            
            await self.log_security_event(
                threat_type=ThreatType.SUSPICIOUS_ACTIVITY,
                level=SecurityLevel.HIGH,
                source_ip=ip_address,
                description=f"IP {ip_address} blocked for {duration} seconds"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Error blocking IP {ip_address}: {e}")
            return False
    
    async def detect_threats(self, input_data: str, source_ip: str) -> List[ThreatType]:
        """Detect security threats in input data"""
        try:
            detected_threats = []
            
            for threat_type, patterns in self.threat_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, input_data, re.IGNORECASE):
                        detected_threats.append(threat_type)
                        break
            
            # Log detected threats
            for threat in detected_threats:
                await self.log_security_event(
                    threat_type=threat,
                    level=SecurityLevel.HIGH,
                    source_ip=source_ip,
                    description=f"Threat detected: {threat.value} in input data"
                )
            
            return detected_threats
            
        except Exception as e:
            logger.error(f"Error detecting threats: {e}")
            return []
    
    async def validate_input(self, input_data: str, input_type: str = "general") -> Dict[str, Any]:
        """Validate input data for security"""
        try:
            validation_result = {
                "valid": True,
                "threats": [],
                "sanitized": input_data,
                "warnings": []
            }
            
            # Basic validation
            if len(input_data) > 10000:  # Max length
                validation_result["valid"] = False
                validation_result["warnings"].append("Input too long")
            
            # SQL injection check
            sql_patterns = self.threat_patterns[ThreatType.SQL_INJECTION]
            for pattern in sql_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    validation_result["threats"].append(ThreatType.SQL_INJECTION)
                    validation_result["valid"] = False
            
            # XSS check
            xss_patterns = self.threat_patterns[ThreatType.XSS]
            for pattern in xss_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    validation_result["threats"].append(ThreatType.XSS)
                    validation_result["valid"] = False
            
            # Sanitize input
            if validation_result["threats"]:
                validation_result["sanitized"] = self._sanitize_input(input_data)
            
            return validation_result
            
        except Exception as e:
            logger.error(f"Error validating input: {e}")
            return {"valid": False, "error": str(e)}
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize input data"""
        try:
            # Remove script tags
            sanitized = re.sub(r'<script[^>]*>.*?</script>', '', input_data, flags=re.IGNORECASE | re.DOTALL)
            
            # Remove javascript: protocols
            sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
            
            # Remove event handlers
            sanitized = re.sub(r'on\w+\s*=\s*["\'][^"\']*["\']', '', sanitized, flags=re.IGNORECASE)
            
            # Remove SQL keywords (basic)
            sql_keywords = ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'DROP', 'CREATE', 'ALTER', 'EXEC', 'UNION']
            for keyword in sql_keywords:
                sanitized = re.sub(rf'\b{keyword}\b', '', sanitized, flags=re.IGNORECASE)
            
            return sanitized.strip()
            
        except Exception as e:
            logger.error(f"Error sanitizing input: {e}")
            return input_data
    
    async def log_security_event(self, 
                                threat_type: ThreatType,
                                level: SecurityLevel,
                                source_ip: str,
                                description: str,
                                user_id: str = None,
                                metadata: Dict[str, Any] = None) -> str:
        """Log security event"""
        try:
            event_id = secrets.token_urlsafe(16)
            event = SecurityEvent(
                id=event_id,
                timestamp=datetime.now(),
                threat_type=threat_type,
                level=level,
                source_ip=source_ip,
                user_id=user_id,
                description=description,
                metadata=metadata or {}
            )
            
            self.security_events.append(event)
            
            # Keep only last 1000 events
            if len(self.security_events) > 1000:
                self.security_events = self.security_events[-1000:]
            
            logger.warning(f"Security event: {threat_type.value} - {description}")
            return event_id
            
        except Exception as e:
            logger.error(f"Error logging security event: {e}")
            return ""
    
    async def get_security_events(self, 
                                 threat_type: ThreatType = None,
                                 level: SecurityLevel = None,
                                 limit: int = 100) -> List[SecurityEvent]:
        """Get security events with filters"""
        try:
            events = self.security_events.copy()
            
            # Apply filters
            if threat_type:
                events = [e for e in events if e.threat_type == threat_type]
            if level:
                events = [e for e in events if e.level == level]
            
            # Sort by timestamp (newest first)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Error getting security events: {e}")
            return []
    
    async def get_security_statistics(self) -> Dict[str, Any]:
        """Get security statistics"""
        try:
            total_events = len(self.security_events)
            events_by_type = defaultdict(int)
            events_by_level = defaultdict(int)
            blocked_ips_count = len(self.blocked_ips)
            
            for event in self.security_events:
                events_by_type[event.threat_type.value] += 1
                events_by_level[event.level.value] += 1
            
            return {
                "total_events": total_events,
                "events_by_type": dict(events_by_type),
                "events_by_level": dict(events_by_level),
                "blocked_ips": blocked_ips_count,
                "active_sessions": len(self.active_sessions),
                "rate_limits_active": len(self.rate_limits)
            }
            
        except Exception as e:
            logger.error(f"Error getting security statistics: {e}")
            return {}
    
    async def create_session(self, user_id: str, ip_address: str) -> str:
        """Create user session"""
        try:
            session_id = secrets.token_urlsafe(32)
            session_data = {
                "user_id": user_id,
                "ip_address": ip_address,
                "created_at": datetime.now(),
                "last_activity": datetime.now(),
                "active": True
            }
            
            self.active_sessions[session_id] = session_data
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            raise
    
    async def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Validate user session"""
        try:
            if session_id not in self.active_sessions:
                return None
            
            session = self.active_sessions[session_id]
            
            # Check if session is expired
            if datetime.now() - session["last_activity"] > timedelta(seconds=self.config.session_timeout):
                del self.active_sessions[session_id]
                return None
            
            # Update last activity
            session["last_activity"] = datetime.now()
            return session
            
        except Exception as e:
            logger.error(f"Error validating session: {e}")
            return None
    
    async def destroy_session(self, session_id: str) -> bool:
        """Destroy user session"""
        try:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error destroying session: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Health check for security service"""
        try:
            stats = await self.get_security_statistics()
            
            return {
                "status": "healthy",
                "total_events": stats.get("total_events", 0),
                "blocked_ips": stats.get("blocked_ips", 0),
                "active_sessions": stats.get("active_sessions", 0),
                "encryption_available": True,
                "threat_detection_active": True
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


























