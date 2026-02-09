# TruthGPT Security Hardening Guide

This document provides comprehensive security hardening guidelines and best practices for the TruthGPT optimization core system, ensuring enterprise-grade security posture.

## 🎯 Design Goals

- **Defense in Depth**: Multiple layers of security controls
- **Zero Trust Architecture**: Verify everything, trust nothing
- **Compliance Ready**: Meet all regulatory requirements
- **Continuous Monitoring**: Real-time security monitoring
- **Incident Response**: Rapid detection and response capabilities

## 🏗️ Security Framework

### 1. Network Security Hardening

#### Network Segmentation
```yaml
# Network security zones
security_zones:
  dmz:
    description: "Demilitarized zone for external-facing services"
    allowed_services:
      - load_balancer
      - api_gateway
      - web_application_firewall
    access_rules:
      - source: "internet"
        destination: "dmz"
        ports: [80, 443]
        protocol: "tcp"
    
  application_tier:
    description: "Application services tier"
    allowed_services:
      - truthgpt_api
      - authentication_service
      - monitoring_services
    access_rules:
      - source: "dmz"
        destination: "application_tier"
        ports: [8000, 8080]
        protocol: "tcp"
    
  data_tier:
    description: "Database and storage tier"
    allowed_services:
      - postgresql
      - redis
      - model_storage
    access_rules:
      - source: "application_tier"
        destination: "data_tier"
        ports: [5432, 6379]
        protocol: "tcp"
    
  management_tier:
    description: "Management and monitoring tier"
    allowed_services:
      - kubernetes_api
      - monitoring_systems
      - logging_systems
    access_rules:
      - source: "vpn"
        destination: "management_tier"
        ports: [6443, 9090]
        protocol: "tcp"
```

#### Firewall Configuration
```bash
#!/bin/bash
# Advanced firewall configuration for TruthGPT

# Clear existing rules
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback traffic
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (restrict to specific IPs)
iptables -A INPUT -p tcp --dport 22 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -s 172.16.0.0/12 -j ACCEPT
iptables -A INPUT -p tcp --dport 22 -s 192.168.0.0/16 -j ACCEPT

# Allow HTTP/HTTPS
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Allow TruthGPT API
iptables -A INPUT -p tcp --dport 8000 -s 10.0.0.0/8 -j ACCEPT

# Allow Kubernetes API
iptables -A INPUT -p tcp --dport 6443 -s 10.0.0.0/8 -j ACCEPT

# Allow monitoring ports
iptables -A INPUT -p tcp --dport 9090 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p tcp --dport 3000 -s 10.0.0.0/8 -j ACCEPT

# Rate limiting for API endpoints
iptables -A INPUT -p tcp --dport 8000 -m limit --limit 100/minute --limit-burst 200 -j ACCEPT
iptables -A INPUT -p tcp --dport 8000 -j DROP

# DDoS protection
iptables -A INPUT -p tcp --dport 80 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -m limit --limit 25/minute --limit-burst 100 -j ACCEPT

# Block common attack patterns
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL FIN,URG,PSH -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL SYN,RST,ACK,FIN,URG -j DROP

# Log dropped packets
iptables -A INPUT -j LOG --log-prefix "DROPPED: " --log-level 4
iptables -A INPUT -j DROP

# Save rules
iptables-save > /etc/iptables/rules.v4
```

### 2. Application Security Hardening

#### Input Validation and Sanitization
```python
# Advanced input validation and sanitization
import re
import html
import bleach
from typing import Any, Dict, List, Optional
import logging

class SecurityValidator:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define allowed patterns
        self.allowed_patterns = {
            'text_input': re.compile(r'^[a-zA-Z0-9\s\.,!?\-_()]+$'),
            'api_key': re.compile(r'^[a-zA-Z0-9]{32,64}$'),
            'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            'url': re.compile(r'^https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(/.*)?$')
        }
        
        # Define dangerous patterns
        self.dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload\s*=',
            r'onerror\s*=',
            r'eval\s*\(',
            r'exec\s*\(',
            r'system\s*\(',
            r'cmd\s*\/',
            r'rm\s+-rf',
            r'drop\s+table',
            r'union\s+select',
            r'<iframe.*?>',
            r'<object.*?>',
            r'<embed.*?>'
        ]
    
    def validate_input(self, input_data: Any, input_type: str) -> Dict[str, Any]:
        """Validate and sanitize input data"""
        validation_result = {
            'valid': True,
            'sanitized_data': None,
            'errors': [],
            'warnings': []
        }
        
        try:
            # Convert to string if not already
            if not isinstance(input_data, str):
                input_data = str(input_data)
            
            # Check for dangerous patterns
            for pattern in self.dangerous_patterns:
                if re.search(pattern, input_data, re.IGNORECASE):
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Dangerous pattern detected: {pattern}")
                    self.logger.warning(f"Dangerous pattern detected in input: {pattern}")
            
            # Validate against allowed patterns
            if input_type in self.allowed_patterns:
                if not self.allowed_patterns[input_type].match(input_data):
                    validation_result['valid'] = False
                    validation_result['errors'].append(f"Input does not match allowed pattern for {input_type}")
            
            # Sanitize input
            if validation_result['valid']:
                validation_result['sanitized_data'] = self._sanitize_input(input_data)
            
            # Check input length
            if len(input_data) > self._get_max_length(input_type):
                validation_result['warnings'].append(f"Input length exceeds recommended maximum for {input_type}")
            
        except Exception as e:
            validation_result['valid'] = False
            validation_result['errors'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Input validation error: {str(e)}")
        
        return validation_result
    
    def _sanitize_input(self, input_data: str) -> str:
        """Sanitize input data"""
        # HTML escape
        sanitized = html.escape(input_data)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        return sanitized
    
    def _get_max_length(self, input_type: str) -> int:
        """Get maximum allowed length for input type"""
        max_lengths = {
            'text_input': 10000,
            'api_key': 64,
            'email': 254,
            'url': 2048,
            'query': 1000
        }
        return max_lengths.get(input_type, 1000)
    
    def validate_api_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API request data"""
        validation_result = {
            'valid': True,
            'sanitized_data': {},
            'errors': [],
            'warnings': []
        }
        
        # Validate required fields
        required_fields = ['input_text']
        for field in required_fields:
            if field not in request_data:
                validation_result['valid'] = False
                validation_result['errors'].append(f"Required field missing: {field}")
        
        # Validate each field
        for field, value in request_data.items():
            field_validation = self.validate_input(value, field)
            
            if not field_validation['valid']:
                validation_result['valid'] = False
                validation_result['errors'].extend(field_validation['errors'])
            
            validation_result['sanitized_data'][field] = field_validation['sanitized_data']
            validation_result['warnings'].extend(field_validation['warnings'])
        
        return validation_result
```

#### Authentication and Authorization Hardening
```python
# Advanced authentication and authorization system
import jwt
import bcrypt
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import redis
import logging

class SecurityManager:
    def __init__(self, config):
        self.config = config
        self.redis_client = redis.Redis(
            host=config['redis_host'],
            port=config['redis_port'],
            password=config['redis_password'],
            decode_responses=True
        )
        self.logger = logging.getLogger(__name__)
        
        # JWT configuration
        self.jwt_secret = config['jwt_secret']
        self.jwt_algorithm = 'HS256'
        self.jwt_expiry = timedelta(hours=1)
        
        # Rate limiting configuration
        self.rate_limits = {
            'login': {'requests': 5, 'window': 300},  # 5 requests per 5 minutes
            'api': {'requests': 100, 'window': 60},  # 100 requests per minute
            'inference': {'requests': 50, 'window': 60}  # 50 requests per minute
        }
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def generate_jwt_token(self, user_id: str, roles: List[str]) -> str:
        """Generate JWT token"""
        payload = {
            'user_id': user_id,
            'roles': roles,
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + self.jwt_expiry,
            'jti': secrets.token_urlsafe(32)  # JWT ID for revocation
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        
        # Store token in Redis for revocation capability
        self.redis_client.setex(
            f"jwt:{payload['jti']}",
            int(self.jwt_expiry.total_seconds()),
            user_id
        )
        
        return token
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            
            # Check if token is revoked
            jti = payload.get('jti')
            if jti and not self.redis_client.exists(f"jwt:{jti}"):
                self.logger.warning(f"Revoked token used: {jti}")
                return None
            
            return payload
            
        except jwt.ExpiredSignatureError:
            self.logger.warning("Expired JWT token")
            return None
        except jwt.InvalidTokenError:
            self.logger.warning("Invalid JWT token")
            return None
    
    def revoke_token(self, token: str) -> bool:
        """Revoke JWT token"""
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            jti = payload.get('jti')
            
            if jti:
                self.redis_client.delete(f"jwt:{jti}")
                return True
            
            return False
            
        except jwt.InvalidTokenError:
            return False
    
    def check_rate_limit(self, identifier: str, endpoint: str) -> bool:
        """Check rate limit for identifier and endpoint"""
        if endpoint not in self.rate_limits:
            return True
        
        limit_config = self.rate_limits[endpoint]
        key = f"rate_limit:{endpoint}:{identifier}"
        
        # Get current count
        current_count = self.redis_client.get(key)
        
        if current_count is None:
            # First request
            self.redis_client.setex(key, limit_config['window'], 1)
            return True
        
        current_count = int(current_count)
        
        if current_count >= limit_config['requests']:
            self.logger.warning(f"Rate limit exceeded for {identifier} on {endpoint}")
            return False
        
        # Increment counter
        self.redis_client.incr(key)
        return True
    
    def check_permissions(self, user_roles: List[str], required_permission: str) -> bool:
        """Check if user has required permission"""
        # Define role-based permissions
        role_permissions = {
            'admin': ['*'],  # All permissions
            'user': ['inference', 'read_models'],
            'api_user': ['inference'],
            'monitor': ['read_metrics', 'read_logs']
        }
        
        for role in user_roles:
            permissions = role_permissions.get(role, [])
            
            # Check for wildcard permission
            if '*' in permissions:
                return True
            
            # Check for specific permission
            if required_permission in permissions:
                return True
        
        return False
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': self._get_event_severity(event_type)
        }
        
        self.logger.info(f"Security event: {event}")
        
        # Store in security event log
        self.redis_client.lpush('security_events', str(event))
        self.redis_client.ltrim('security_events', 0, 9999)  # Keep last 10000 events
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for event type"""
        severity_map = {
            'login_success': 'info',
            'login_failure': 'warning',
            'rate_limit_exceeded': 'warning',
            'invalid_token': 'warning',
            'permission_denied': 'warning',
            'suspicious_activity': 'error',
            'security_violation': 'critical'
        }
        return severity_map.get(event_type, 'info')
```

### 3. Container Security Hardening

#### Docker Security Configuration
```dockerfile
# Security-hardened Dockerfile for TruthGPT
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Security: Use specific version tags
ARG DEBIAN_FRONTEND=noninteractive

# Security: Create non-root user first
RUN groupadd -r truthgpt && useradd -r -g truthgpt truthgpt

# Security: Update packages and install security updates
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
        python3.10 \
        python3.10-dev \
        python3-pip \
        curl \
        wget \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/*

# Security: Set proper file permissions
RUN chmod 755 /usr/bin/python3.10

# Security: Create application directory with proper permissions
RUN mkdir -p /app && chown truthgpt:truthgpt /app
WORKDIR /app

# Security: Copy requirements first for better caching
COPY --chown=truthgpt:truthgpt requirements.txt /app/

# Security: Install Python packages as non-root user
USER truthgpt
RUN pip3 install --user --no-cache-dir -r requirements.txt

# Security: Copy application code with proper ownership
COPY --chown=truthgpt:truthgpt . /app/

# Security: Set proper file permissions
RUN chmod -R 755 /app

# Security: Remove unnecessary files
RUN find /app -name "*.pyc" -delete && \
    find /app -name "__pycache__" -type d -exec rm -rf {} + || true

# Security: Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Security: Expose only necessary port
EXPOSE 8000

# Security: Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Security: Use non-root user
USER truthgpt

# Security: Set proper entrypoint
ENTRYPOINT ["python3", "-m", "truthgpt.server"]
CMD ["--host", "0.0.0.0", "--port", "8000"]
```

#### Kubernetes Security Policies
```yaml
# Pod Security Policy
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: truthgpt-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
---
# Network Policy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: truthgpt-netpol
spec:
  podSelector:
    matchLabels:
      app: truthgpt
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: kube-system
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53
  - to:
    - namespaceSelector:
        matchLabels:
          name: truthgpt
    ports:
    - protocol: TCP
      port: 5432
    - protocol: TCP
      port: 6379
---
# Security Context
apiVersion: v1
kind: Pod
metadata:
  name: truthgpt-secure
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 1000
    fsGroup: 1000
  containers:
  - name: truthgpt
    image: truthgpt:latest
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop:
        - ALL
    resources:
      requests:
        memory: "1Gi"
        cpu: "500m"
      limits:
        memory: "2Gi"
        cpu: "1000m"
    volumeMounts:
    - name: tmp
      mountPath: /tmp
    - name: var-tmp
      mountPath: /var/tmp
  volumes:
  - name: tmp
    emptyDir: {}
  - name: var-tmp
    emptyDir: {}
```

### 4. Data Security Hardening

#### Encryption at Rest and in Transit
```python
# Advanced encryption system
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import os
import logging

class EncryptionManager:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Generate or load encryption keys
        self.fernet_key = self._get_or_generate_key('fernet_key')
        self.fernet = Fernet(self.fernet_key)
        
        # Database encryption key
        self.db_key = self._get_or_generate_key('db_key')
        
        # Model encryption key
        self.model_key = self._get_or_generate_key('model_key')
    
    def _get_or_generate_key(self, key_name: str) -> bytes:
        """Get or generate encryption key"""
        key_file = f"/etc/truthgpt/keys/{key_name}.key"
        
        if os.path.exists(key_file):
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(key_file), exist_ok=True)
            
            # Save key with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(key)
            
            os.chmod(key_file, 0o600)
            
            return key
    
    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data using Fernet"""
        try:
            encrypted_data = self.fernet.encrypt(data)
            return encrypted_data
        except Exception as e:
            self.logger.error(f"Encryption failed: {str(e)}")
            raise
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data using Fernet"""
        try:
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            self.logger.error(f"Decryption failed: {str(e)}")
            raise
    
    def encrypt_file(self, file_path: str, output_path: str = None) -> str:
        """Encrypt file"""
        if output_path is None:
            output_path = f"{file_path}.encrypted"
        
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.encrypt_data(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            # Set proper permissions
            os.chmod(output_path, 0o600)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"File encryption failed: {str(e)}")
            raise
    
    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> str:
        """Decrypt file"""
        if output_path is None:
            output_path = encrypted_file_path.replace('.encrypted', '')
        
        try:
            with open(encrypted_file_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_data(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return output_path
            
        except Exception as e:
            self.logger.error(f"File decryption failed: {str(e)}")
            raise
    
    def encrypt_database_field(self, value: str) -> str:
        """Encrypt database field value"""
        if value is None:
            return None
        
        encrypted_bytes = self.encrypt_data(value.encode('utf-8'))
        return base64.b64encode(encrypted_bytes).decode('utf-8')
    
    def decrypt_database_field(self, encrypted_value: str) -> str:
        """Decrypt database field value"""
        if encrypted_value is None:
            return None
        
        encrypted_bytes = base64.b64decode(encrypted_value.encode('utf-8'))
        decrypted_bytes = self.decrypt_data(encrypted_bytes)
        return decrypted_bytes.decode('utf-8')
```

### 5. Monitoring and Incident Response

#### Security Monitoring System
```python
# Comprehensive security monitoring system
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging

class SecurityMonitor:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Security event patterns
        self.threat_patterns = {
            'sql_injection': [
                r'union\s+select',
                r'drop\s+table',
                r'insert\s+into',
                r'delete\s+from',
                r'update\s+set'
            ],
            'xss_attack': [
                r'<script.*?>',
                r'javascript:',
                r'onload\s*=',
                r'onerror\s*=',
                r'<iframe.*?>'
            ],
            'path_traversal': [
                r'\.\./',
                r'\.\.\\',
                r'/etc/passwd',
                r'/etc/shadow',
                r'C:\\Windows\\System32'
            ],
            'command_injection': [
                r';\s*rm\s+-rf',
                r';\s*cat\s+/etc/passwd',
                r';\s*whoami',
                r';\s*id',
                r';\s*ps\s+aux'
            ]
        }
        
        # Alert thresholds
        self.alert_thresholds = {
            'failed_logins': 5,  # Alert after 5 failed logins
            'rate_limit_violations': 10,  # Alert after 10 rate limit violations
            'suspicious_requests': 3,  # Alert after 3 suspicious requests
            'privilege_escalation': 1  # Alert on any privilege escalation attempt
        }
    
    def monitor_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Monitor incoming request for security threats"""
        monitoring_result = {
            'threats_detected': [],
            'risk_score': 0,
            'action_required': False,
            'recommendations': []
        }
        
        # Check for threat patterns
        for threat_type, patterns in self.threat_patterns.items():
            for pattern in patterns:
                if self._check_pattern(request_data, pattern):
                    monitoring_result['threats_detected'].append(threat_type)
                    monitoring_result['risk_score'] += 10
        
        # Check for suspicious behavior
        suspicious_behavior = self._detect_suspicious_behavior(request_data)
        if suspicious_behavior:
            monitoring_result['threats_detected'].extend(suspicious_behavior)
            monitoring_result['risk_score'] += 5
        
        # Determine if action is required
        if monitoring_result['risk_score'] > 20:
            monitoring_result['action_required'] = True
            monitoring_result['recommendations'].append("Block request and investigate")
        
        # Log security event
        if monitoring_result['threats_detected']:
            self._log_security_event('threat_detected', {
                'threats': monitoring_result['threats_detected'],
                'risk_score': monitoring_result['risk_score'],
                'request_data': request_data
            })
        
        return monitoring_result
    
    def _check_pattern(self, request_data: Dict[str, Any], pattern: str) -> bool:
        """Check if pattern exists in request data"""
        import re
        
        for key, value in request_data.items():
            if isinstance(value, str):
                if re.search(pattern, value, re.IGNORECASE):
                    return True
        return False
    
    def _detect_suspicious_behavior(self, request_data: Dict[str, Any]) -> List[str]:
        """Detect suspicious behavior patterns"""
        suspicious_behaviors = []
        
        # Check for unusual request patterns
        if 'user_agent' in request_data:
            user_agent = request_data['user_agent'].lower()
            if any(bot in user_agent for bot in ['bot', 'crawler', 'spider', 'scraper']):
                suspicious_behaviors.append('bot_behavior')
        
        # Check for unusual timing patterns
        if 'timestamp' in request_data:
            # This would be implemented with historical data analysis
            pass
        
        # Check for unusual geographic patterns
        if 'ip_address' in request_data:
            # This would be implemented with IP geolocation
            pass
        
        return suspicious_behaviors
    
    def _log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Log security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'details': details,
            'severity': self._get_event_severity(event_type)
        }
        
        self.logger.warning(f"Security event: {json.dumps(event)}")
        
        # Store in security event database
        # This would be implemented with actual database storage
    
    def _get_event_severity(self, event_type: str) -> str:
        """Get severity level for event type"""
        severity_map = {
            'threat_detected': 'high',
            'failed_login': 'medium',
            'rate_limit_exceeded': 'low',
            'privilege_escalation': 'critical'
        }
        return severity_map.get(event_type, 'medium')
    
    def generate_security_report(self, time_period: timedelta = timedelta(hours=24)) -> Dict[str, Any]:
        """Generate security report for time period"""
        # This would query the security event database
        # and generate a comprehensive report
        
        report = {
            'time_period': {
                'start': (datetime.utcnow() - time_period).isoformat(),
                'end': datetime.utcnow().isoformat()
            },
            'threat_summary': {
                'total_threats': 0,
                'threat_types': {},
                'risk_distribution': {}
            },
            'incident_summary': {
                'total_incidents': 0,
                'resolved_incidents': 0,
                'open_incidents': 0
            },
            'recommendations': []
        }
        
        return report
```

### 6. Compliance and Audit

#### Compliance Monitoring
```yaml
# Compliance monitoring configuration
compliance:
  gdpr:
    data_protection:
      - encryption_at_rest: true
      - encryption_in_transit: true
      - data_anonymization: true
      - right_to_erasure: true
      - data_portability: true
    
  hipaa:
    security_requirements:
      - access_controls: true
      - audit_logging: true
      - data_encryption: true
      - backup_procedures: true
      - incident_response: true
    
  soc2:
    trust_services:
      security:
        - access_controls: true
        - system_monitoring: true
        - vulnerability_management: true
      availability:
        - system_monitoring: true
        - incident_response: true
        - disaster_recovery: true
      processing_integrity:
        - data_validation: true
        - error_handling: true
        - system_monitoring: true
      confidentiality:
        - data_encryption: true
        - access_controls: true
        - data_classification: true
      privacy:
        - data_protection: true
        - consent_management: true
        - data_retention: true
```

---

*This comprehensive security hardening guide ensures TruthGPT maintains enterprise-grade security posture and meets all regulatory compliance requirements.*

