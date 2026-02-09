"""
Security System - Sistema de Seguridad Avanzado
Sistema completo de autenticación, autorización y seguridad
"""

import asyncio
import logging
import json
import hashlib
import secrets
import jwt
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import bcrypt
import re
from passlib.context import CryptContext
from passlib.hash import bcrypt
import ipaddress
import time
from collections import defaultdict, deque
import uuid

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """Roles de usuario"""
    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"
    GUEST = "guest"

class Permission(Enum):
    """Permisos del sistema"""
    READ_DOCUMENTS = "read_documents"
    WRITE_DOCUMENTS = "write_documents"
    DELETE_DOCUMENTS = "delete_documents"
    MANAGE_USERS = "manage_users"
    VIEW_ANALYTICS = "view_analytics"
    MANAGE_SYSTEM = "manage_system"
    USE_CHATBOT = "use_chatbot"
    USE_VOICE_SEARCH = "use_voice_search"
    EXPORT_DATA = "export_data"
    IMPORT_DATA = "import_data"

@dataclass
class User:
    """Usuario del sistema"""
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    permissions: List[Permission]
    is_active: bool
    is_verified: bool
    created_at: str
    last_login: Optional[str] = None
    failed_login_attempts: int = 0
    locked_until: Optional[str] = None
    two_factor_enabled: bool = False
    two_factor_secret: Optional[str] = None
    api_key: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class SecurityEvent:
    """Evento de seguridad"""
    id: str
    event_type: str
    user_id: Optional[str]
    ip_address: str
    user_agent: str
    details: Dict[str, Any]
    severity: str  # low, medium, high, critical
    timestamp: str
    resolved: bool = False

@dataclass
class AccessToken:
    """Token de acceso"""
    token: str
    user_id: str
    expires_at: str
    permissions: List[str]
    created_at: str
    is_revoked: bool = False

class SecuritySystem:
    """
    Sistema de seguridad avanzado
    """
    
    def __init__(self, secret_key: str = None, jwt_secret: str = None):
        self.secret_key = secret_key or secrets.token_urlsafe(32)
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        
        # Contexto de encriptación de contraseñas
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        # Almacenamiento en memoria (en producción usar base de datos)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, AccessToken] = {}
        self.security_events: List[SecurityEvent] = []
        
        # Rate limiting
        self.rate_limits: Dict[str, deque] = defaultdict(lambda: deque())
        self.blocked_ips: Dict[str, str] = {}  # IP -> timestamp when blocked
        
        # Configuraciones de seguridad
        self.security_config = {
            "max_login_attempts": 5,
            "lockout_duration": 300,  # 5 minutos
            "session_timeout": 3600,  # 1 hora
            "password_min_length": 8,
            "password_require_uppercase": True,
            "password_require_lowercase": True,
            "password_require_numbers": True,
            "password_require_special": True,
            "rate_limit_requests": 100,  # requests per minute
            "rate_limit_window": 60,  # seconds
            "max_failed_attempts_per_ip": 10,
            "ip_block_duration": 1800,  # 30 minutos
        }
        
        # Roles y permisos por defecto
        self.role_permissions = {
            UserRole.ADMIN: [
                Permission.READ_DOCUMENTS,
                Permission.WRITE_DOCUMENTS,
                Permission.DELETE_DOCUMENTS,
                Permission.MANAGE_USERS,
                Permission.VIEW_ANALYTICS,
                Permission.MANAGE_SYSTEM,
                Permission.USE_CHATBOT,
                Permission.USE_VOICE_SEARCH,
                Permission.EXPORT_DATA,
                Permission.IMPORT_DATA
            ],
            UserRole.MODERATOR: [
                Permission.READ_DOCUMENTS,
                Permission.WRITE_DOCUMENTS,
                Permission.DELETE_DOCUMENTS,
                Permission.VIEW_ANALYTICS,
                Permission.USE_CHATBOT,
                Permission.USE_VOICE_SEARCH,
                Permission.EXPORT_DATA
            ],
            UserRole.USER: [
                Permission.READ_DOCUMENTS,
                Permission.WRITE_DOCUMENTS,
                Permission.USE_CHATBOT,
                Permission.USE_VOICE_SEARCH
            ],
            UserRole.GUEST: [
                Permission.READ_DOCUMENTS
            ]
        }
    
    async def initialize(self):
        """Inicializar sistema de seguridad"""
        try:
            logger.info("Inicializando sistema de seguridad...")
            
            # Crear usuario administrador por defecto
            await self._create_default_admin()
            
            # Limpiar sesiones expiradas
            await self._cleanup_expired_sessions()
            
            logger.info("Sistema de seguridad inicializado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando sistema de seguridad: {e}")
            raise
    
    async def _create_default_admin(self):
        """Crear usuario administrador por defecto"""
        try:
            admin_user = await self.create_user(
                username="admin",
                email="admin@ai-search.com",
                password="admin123!",
                role=UserRole.ADMIN
            )
            
            logger.info("Usuario administrador creado por defecto")
            
        except Exception as e:
            logger.warning(f"No se pudo crear usuario administrador: {e}")
    
    async def create_user(self, username: str, email: str, password: str, 
                         role: UserRole = UserRole.USER, 
                         permissions: List[Permission] = None) -> User:
        """Crear nuevo usuario"""
        try:
            # Validar datos de entrada
            await self._validate_user_data(username, email, password)
            
            # Verificar que el usuario no existe
            if await self.get_user_by_username(username):
                raise ValueError("El nombre de usuario ya existe")
            
            if await self.get_user_by_email(email):
                raise ValueError("El email ya está registrado")
            
            # Generar ID único
            user_id = str(uuid.uuid4())
            
            # Encriptar contraseña
            password_hash = self.pwd_context.hash(password)
            
            # Generar API key
            api_key = secrets.token_urlsafe(32)
            
            # Asignar permisos por defecto del rol
            if permissions is None:
                permissions = self.role_permissions.get(role, [])
            
            # Crear usuario
            user = User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                role=role,
                permissions=permissions,
                is_active=True,
                is_verified=False,
                created_at=datetime.now(timezone.utc).isoformat(),
                api_key=api_key
            )
            
            # Guardar usuario
            self.users[user_id] = user
            
            # Registrar evento de seguridad
            await self._log_security_event(
                "user_created",
                user_id,
                "127.0.0.1",
                "System",
                {"username": username, "role": role.value},
                "low"
            )
            
            logger.info(f"Usuario creado: {username}")
            return user
            
        except Exception as e:
            logger.error(f"Error creando usuario: {e}")
            raise
    
    async def _validate_user_data(self, username: str, email: str, password: str):
        """Validar datos del usuario"""
        # Validar nombre de usuario
        if not username or len(username) < 3:
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValueError("El nombre de usuario solo puede contener letras, números y guiones bajos")
        
        # Validar email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Email inválido")
        
        # Validar contraseña
        await self._validate_password(password)
    
    async def _validate_password(self, password: str):
        """Validar contraseña"""
        config = self.security_config
        
        if len(password) < config["password_min_length"]:
            raise ValueError(f"La contraseña debe tener al menos {config['password_min_length']} caracteres")
        
        if config["password_require_uppercase"] and not re.search(r'[A-Z]', password):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula")
        
        if config["password_require_lowercase"] and not re.search(r'[a-z]', password):
            raise ValueError("La contraseña debe contener al menos una letra minúscula")
        
        if config["password_require_numbers"] and not re.search(r'\d', password):
            raise ValueError("La contraseña debe contener al menos un número")
        
        if config["password_require_special"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValueError("La contraseña debe contener al menos un carácter especial")
    
    async def authenticate_user(self, username: str, password: str, 
                              ip_address: str, user_agent: str) -> Optional[AccessToken]:
        """Autenticar usuario"""
        try:
            # Verificar rate limiting
            if await self._is_rate_limited(ip_address):
                await self._log_security_event(
                    "rate_limit_exceeded",
                    None,
                    ip_address,
                    user_agent,
                    {"username": username},
                    "medium"
                )
                raise ValueError("Demasiados intentos de login. Intenta más tarde.")
            
            # Verificar si la IP está bloqueada
            if await self._is_ip_blocked(ip_address):
                await self._log_security_event(
                    "blocked_ip_access",
                    None,
                    ip_address,
                    user_agent,
                    {"username": username},
                    "high"
                )
                raise ValueError("IP bloqueada por intentos de acceso maliciosos")
            
            # Buscar usuario
            user = await self.get_user_by_username(username)
            if not user:
                await self._log_failed_login(username, ip_address, user_agent)
                raise ValueError("Credenciales inválidas")
            
            # Verificar si el usuario está activo
            if not user.is_active:
                await self._log_security_event(
                    "inactive_user_login",
                    user.id,
                    ip_address,
                    user_agent,
                    {"username": username},
                    "medium"
                )
                raise ValueError("Usuario inactivo")
            
            # Verificar si el usuario está bloqueado
            if user.locked_until:
                lock_time = datetime.fromisoformat(user.locked_until)
                if datetime.now(timezone.utc) < lock_time:
                    await self._log_security_event(
                        "locked_user_login",
                        user.id,
                        ip_address,
                        user_agent,
                        {"username": username, "locked_until": user.locked_until},
                        "medium"
                    )
                    raise ValueError("Usuario bloqueado temporalmente")
                else:
                    # Desbloquear usuario
                    user.locked_until = None
                    user.failed_login_attempts = 0
            
            # Verificar contraseña
            if not self.pwd_context.verify(password, user.password_hash):
                await self._log_failed_login(username, ip_address, user_agent, user.id)
                raise ValueError("Credenciales inválidas")
            
            # Login exitoso
            user.last_login = datetime.now(timezone.utc).isoformat()
            user.failed_login_attempts = 0
            user.locked_until = None
            
            # Crear token de acceso
            access_token = await self._create_access_token(user)
            
            # Registrar evento de login exitoso
            await self._log_security_event(
                "successful_login",
                user.id,
                ip_address,
                user_agent,
                {"username": username},
                "low"
            )
            
            logger.info(f"Login exitoso: {username}")
            return access_token
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error en autenticación: {e}")
            raise ValueError("Error interno de autenticación")
    
    async def _log_failed_login(self, username: str, ip_address: str, 
                              user_agent: str, user_id: str = None):
        """Registrar intento de login fallido"""
        try:
            # Incrementar contador de intentos fallidos
            if user_id and user_id in self.users:
                user = self.users[user_id]
                user.failed_login_attempts += 1
                
                # Bloquear usuario si excede el límite
                if user.failed_login_attempts >= self.security_config["max_login_attempts"]:
                    lock_until = datetime.now(timezone.utc) + timedelta(
                        seconds=self.security_config["lockout_duration"]
                    )
                    user.locked_until = lock_until.isoformat()
                    
                    await self._log_security_event(
                        "user_locked",
                        user_id,
                        ip_address,
                        user_agent,
                        {"username": username, "failed_attempts": user.failed_login_attempts},
                        "high"
                    )
            
            # Verificar si bloquear IP
            await self._check_ip_blocking(ip_address)
            
            # Registrar evento
            await self._log_security_event(
                "failed_login",
                user_id,
                ip_address,
                user_agent,
                {"username": username},
                "medium"
            )
            
        except Exception as e:
            logger.error(f"Error registrando login fallido: {e}")
    
    async def _check_ip_blocking(self, ip_address: str):
        """Verificar si bloquear IP por intentos fallidos"""
        try:
            # Contar intentos fallidos recientes desde esta IP
            recent_attempts = 0
            cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=10)
            
            for event in self.security_events:
                if (event.ip_address == ip_address and 
                    event.event_type == "failed_login" and
                    datetime.fromisoformat(event.timestamp) > cutoff_time):
                    recent_attempts += 1
            
            # Bloquear IP si excede el límite
            if recent_attempts >= self.security_config["max_failed_attempts_per_ip"]:
                block_until = datetime.now(timezone.utc) + timedelta(
                    seconds=self.security_config["ip_block_duration"]
                )
                self.blocked_ips[ip_address] = block_until.isoformat()
                
                await self._log_security_event(
                    "ip_blocked",
                    None,
                    ip_address,
                    "System",
                    {"reason": "too_many_failed_attempts", "attempts": recent_attempts},
                    "high"
                )
                
        except Exception as e:
            logger.error(f"Error verificando bloqueo de IP: {e}")
    
    async def _is_ip_blocked(self, ip_address: str) -> bool:
        """Verificar si una IP está bloqueada"""
        try:
            if ip_address not in self.blocked_ips:
                return False
            
            block_until = datetime.fromisoformat(self.blocked_ips[ip_address])
            if datetime.now(timezone.utc) > block_until:
                # Desbloquear IP
                del self.blocked_ips[ip_address]
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error verificando bloqueo de IP: {e}")
            return False
    
    async def _is_rate_limited(self, ip_address: str) -> bool:
        """Verificar rate limiting"""
        try:
            now = time.time()
            window_start = now - self.security_config["rate_limit_window"]
            
            # Limpiar requests antiguos
            while (self.rate_limits[ip_address] and 
                   self.rate_limits[ip_address][0] < window_start):
                self.rate_limits[ip_address].popleft()
            
            # Verificar límite
            if len(self.rate_limits[ip_address]) >= self.security_config["rate_limit_requests"]:
                return True
            
            # Agregar request actual
            self.rate_limits[ip_address].append(now)
            return False
            
        except Exception as e:
            logger.error(f"Error verificando rate limiting: {e}")
            return False
    
    async def _create_access_token(self, user: User) -> AccessToken:
        """Crear token de acceso"""
        try:
            # Generar token JWT
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=self.security_config["session_timeout"])
            
            payload = {
                "user_id": user.id,
                "username": user.username,
                "role": user.role.value,
                "permissions": [p.value for p in user.permissions],
                "iat": now,
                "exp": expires_at
            }
            
            token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
            
            # Crear objeto de token
            access_token = AccessToken(
                token=token,
                user_id=user.id,
                expires_at=expires_at.isoformat(),
                permissions=[p.value for p in user.permissions],
                created_at=now.isoformat()
            )
            
            # Guardar sesión
            self.sessions[token] = access_token
            
            return access_token
            
        except Exception as e:
            logger.error(f"Error creando token de acceso: {e}")
            raise
    
    async def verify_token(self, token: str) -> Optional[User]:
        """Verificar token de acceso"""
        try:
            # Verificar si el token existe en las sesiones
            if token not in self.sessions:
                return None
            
            access_token = self.sessions[token]
            
            # Verificar si está revocado
            if access_token.is_revoked:
                return None
            
            # Verificar expiración
            expires_at = datetime.fromisoformat(access_token.expires_at)
            if datetime.now(timezone.utc) > expires_at:
                # Token expirado, remover de sesiones
                del self.sessions[token]
                return None
            
            # Verificar JWT
            try:
                payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
                user_id = payload["user_id"]
            except jwt.ExpiredSignatureError:
                del self.sessions[token]
                return None
            except jwt.InvalidTokenError:
                return None
            
            # Obtener usuario
            user = self.users.get(user_id)
            if not user or not user.is_active:
                return None
            
            return user
            
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            return None
    
    async def revoke_token(self, token: str) -> bool:
        """Revocar token de acceso"""
        try:
            if token in self.sessions:
                self.sessions[token].is_revoked = True
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error revocando token: {e}")
            return False
    
    async def check_permission(self, user: User, permission: Permission) -> bool:
        """Verificar si el usuario tiene un permiso"""
        try:
            return permission in user.permissions
            
        except Exception as e:
            logger.error(f"Error verificando permiso: {e}")
            return False
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        try:
            for user in self.users.values():
                if user.username == username:
                    return user
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por username: {e}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Obtener usuario por email"""
        try:
            for user in self.users.values():
                if user.email == email:
                    return user
            return None
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por email: {e}")
            return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Obtener usuario por ID"""
        try:
            return self.users.get(user_id)
            
        except Exception as e:
            logger.error(f"Error obteniendo usuario por ID: {e}")
            return None
    
    async def _log_security_event(self, event_type: str, user_id: Optional[str], 
                                ip_address: str, user_agent: str, 
                                details: Dict[str, Any], severity: str):
        """Registrar evento de seguridad"""
        try:
            event = SecurityEvent(
                id=str(uuid.uuid4()),
                event_type=event_type,
                user_id=user_id,
                ip_address=ip_address,
                user_agent=user_agent,
                details=details,
                severity=severity,
                timestamp=datetime.now(timezone.utc).isoformat()
            )
            
            self.security_events.append(event)
            
            # Mantener solo los últimos 10000 eventos
            if len(self.security_events) > 10000:
                self.security_events = self.security_events[-10000:]
            
            # Log según severidad
            if severity == "critical":
                logger.critical(f"Security Event: {event_type} - {details}")
            elif severity == "high":
                logger.warning(f"Security Event: {event_type} - {details}")
            else:
                logger.info(f"Security Event: {event_type} - {details}")
            
        except Exception as e:
            logger.error(f"Error registrando evento de seguridad: {e}")
    
    async def _cleanup_expired_sessions(self):
        """Limpiar sesiones expiradas"""
        try:
            now = datetime.now(timezone.utc)
            expired_tokens = []
            
            for token, access_token in self.sessions.items():
                expires_at = datetime.fromisoformat(access_token.expires_at)
                if now > expires_at:
                    expired_tokens.append(token)
            
            for token in expired_tokens:
                del self.sessions[token]
            
            if expired_tokens:
                logger.info(f"Limpiadas {len(expired_tokens)} sesiones expiradas")
            
        except Exception as e:
            logger.error(f"Error limpiando sesiones expiradas: {e}")
    
    async def get_security_events(self, limit: int = 100, 
                                severity: str = None) -> List[SecurityEvent]:
        """Obtener eventos de seguridad"""
        try:
            events = self.security_events
            
            if severity:
                events = [e for e in events if e.severity == severity]
            
            # Ordenar por timestamp (más recientes primero)
            events.sort(key=lambda x: x.timestamp, reverse=True)
            
            return events[:limit]
            
        except Exception as e:
            logger.error(f"Error obteniendo eventos de seguridad: {e}")
            return []
    
    async def get_security_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de seguridad"""
        try:
            now = datetime.now(timezone.utc)
            last_24h = now - timedelta(hours=24)
            
            # Contar eventos por severidad
            severity_counts = defaultdict(int)
            recent_events = 0
            
            for event in self.security_events:
                severity_counts[event.severity] += 1
                if datetime.fromisoformat(event.timestamp) > last_24h:
                    recent_events += 1
            
            return {
                "total_users": len(self.users),
                "active_sessions": len([s for s in self.sessions.values() if not s.is_revoked]),
                "blocked_ips": len(self.blocked_ips),
                "total_security_events": len(self.security_events),
                "recent_events_24h": recent_events,
                "events_by_severity": dict(severity_counts),
                "last_updated": now.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de seguridad: {e}")
            return {}


























