"""
Enterprise Features for HeyGen AI
=================================

Enterprise-grade security and management features:
- Single Sign-On (SSO) integration
- Role-Based Access Control (RBAC)
- Advanced audit logging
- Compliance and governance
- Enterprise user management
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union
import hashlib
import hmac
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

logger = logging.getLogger(__name__)


class Permission(str, Enum):
    """System permissions"""
    # User management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Content management
    CREATE_CONTENT = "create_content"
    READ_CONTENT = "read_content"
    UPDATE_CONTENT = "update_content"
    DELETE_CONTENT = "delete_content"
    
    # Video generation
    GENERATE_VIDEO = "generate_video"
    EXPORT_VIDEO = "export_video"
    SHARE_VIDEO = "share_video"
    
    # Analytics
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_ANALYTICS = "export_analytics"
    
    # System administration
    MANAGE_SYSTEM = "manage_system"
    VIEW_LOGS = "view_logs"
    MANAGE_BILLING = "manage_billing"


class Role(str, Enum):
    """User roles"""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    EDITOR = "editor"
    VIEWER = "viewer"
    GUEST = "guest"


class AuditEventType(str, Enum):
    """Audit event types"""
    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    PERMISSION_GRANTED = "permission_granted"
    PERMISSION_REVOKED = "permission_revoked"
    CONTENT_CREATED = "content_created"
    CONTENT_MODIFIED = "content_modified"
    CONTENT_DELETED = "content_deleted"
    VIDEO_GENERATED = "video_generated"
    VIDEO_EXPORTED = "video_exported"
    SYSTEM_CONFIG_CHANGED = "system_config_changed"
    SECURITY_EVENT = "security_event"


class SSOProvider(str, Enum):
    """SSO providers"""
    SAML = "saml"
    OIDC = "oidc"
    OAUTH2 = "oauth2"
    LDAP = "ldap"
    ACTIVE_DIRECTORY = "active_directory"


@dataclass
class User:
    """Enterprise user"""
    user_id: str
    username: str
    email: str
    first_name: str
    last_name: str
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    groups: Set[str] = field(default_factory=set)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_login: Optional[datetime] = None
    sso_provider: Optional[SSOProvider] = None
    sso_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Group:
    """User group"""
    group_id: str
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    members: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "system"


@dataclass
class AuditLog:
    """Audit log entry"""
    log_id: str
    timestamp: datetime
    event_type: AuditEventType
    user_id: str
    resource_type: str
    resource_id: str
    action: str
    details: Dict[str, Any]
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class SSOConfig:
    """SSO configuration"""
    provider: SSOProvider
    name: str
    enabled: bool = True
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    issuer_url: Optional[str] = None
    callback_url: Optional[str] = None
    metadata_url: Optional[str] = None
    certificate_path: Optional[str] = None
    settings: Dict[str, Any] = field(default_factory=dict)


class RoleBasedAccessControl:
    """Role-Based Access Control system"""
    
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.groups: Dict[str, Group] = {}
        self.role_permissions: Dict[Role, Set[Permission]] = {}
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default role permissions"""
        self.role_permissions = {
            Role.SUPER_ADMIN: set(Permission),  # All permissions
            Role.ADMIN: {
                Permission.CREATE_USER, Permission.READ_USER, Permission.UPDATE_USER,
                Permission.CREATE_CONTENT, Permission.READ_CONTENT, Permission.UPDATE_CONTENT, Permission.DELETE_CONTENT,
                Permission.GENERATE_VIDEO, Permission.EXPORT_VIDEO, Permission.SHARE_VIDEO,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_ANALYTICS,
                Permission.VIEW_LOGS, Permission.MANAGE_BILLING
            },
            Role.MANAGER: {
                Permission.READ_USER, Permission.UPDATE_USER,
                Permission.CREATE_CONTENT, Permission.READ_CONTENT, Permission.UPDATE_CONTENT,
                Permission.GENERATE_VIDEO, Permission.EXPORT_VIDEO, Permission.SHARE_VIDEO,
                Permission.VIEW_ANALYTICS
            },
            Role.EDITOR: {
                Permission.READ_USER,
                Permission.CREATE_CONTENT, Permission.READ_CONTENT, Permission.UPDATE_CONTENT,
                Permission.GENERATE_VIDEO, Permission.EXPORT_VIDEO
            },
            Role.VIEWER: {
                Permission.READ_CONTENT, Permission.READ_USER
            },
            Role.GUEST: {
                Permission.READ_CONTENT
            }
        }
    
    async def create_user(self, user_id: str, username: str, email: str, 
                         first_name: str, last_name: str, role: Role,
                         sso_provider: Optional[SSOProvider] = None,
                         sso_id: Optional[str] = None) -> User:
        """Create new user"""
        if user_id in self.users:
            raise ValueError(f"User {user_id} already exists")
        
        user = User(
            user_id=user_id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            permissions=self.role_permissions[role].copy(),
            sso_provider=sso_provider,
            sso_id=sso_id
        )
        
        self.users[user_id] = user
        logger.info(f"Created user: {username} ({user_id}) with role {role}")
        return user
    
    async def update_user(self, user_id: str, **kwargs) -> User:
        """Update user"""
        if user_id not in self.users:
            raise ValueError(f"User {user_id} not found")
        
        user = self.users[user_id]
        
        # Update allowed fields
        allowed_fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active']
        for field, value in kwargs.items():
            if field in allowed_fields:
                setattr(user, field, value)
                
                # Update permissions if role changed
                if field == 'role':
                    user.permissions = self.role_permissions[value].copy()
        
        logger.info(f"Updated user: {user_id}")
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if user_id not in self.users:
            return False
        
        del self.users[user_id]
        logger.info(f"Deleted user: {user_id}")
        return True
    
    async def create_group(self, group_id: str, name: str, description: str,
                          permissions: Set[Permission], created_by: str) -> Group:
        """Create user group"""
        if group_id in self.groups:
            raise ValueError(f"Group {group_id} already exists")
        
        group = Group(
            group_id=group_id,
            name=name,
            description=description,
            permissions=permissions,
            created_by=created_by
        )
        
        self.groups[group_id] = group
        logger.info(f"Created group: {name} ({group_id})")
        return group
    
    async def add_user_to_group(self, user_id: str, group_id: str) -> bool:
        """Add user to group"""
        if user_id not in self.users or group_id not in self.groups:
            return False
        
        user = self.users[user_id]
        group = self.groups[group_id]
        
        user.groups.add(group_id)
        group.members.add(user_id)
        
        # Add group permissions to user
        user.permissions.update(group.permissions)
        
        logger.info(f"Added user {user_id} to group {group_id}")
        return True
    
    async def remove_user_from_group(self, user_id: str, group_id: str) -> bool:
        """Remove user from group"""
        if user_id not in self.users or group_id not in self.groups:
            return False
        
        user = self.users[user_id]
        group = self.groups[group_id]
        
        user.groups.discard(group_id)
        group.members.discard(user_id)
        
        # Recalculate user permissions
        await self._recalculate_user_permissions(user_id)
        
        logger.info(f"Removed user {user_id} from group {group_id}")
        return True
    
    async def _recalculate_user_permissions(self, user_id: str):
        """Recalculate user permissions based on role and groups"""
        user = self.users[user_id]
        
        # Start with role permissions
        permissions = self.role_permissions[user.role].copy()
        
        # Add group permissions
        for group_id in user.groups:
            if group_id in self.groups:
                permissions.update(self.groups[group_id].permissions)
        
        user.permissions = permissions
    
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check if user has permission"""
        if user_id not in self.users:
            return False
        
        user = self.users[user_id]
        return permission in user.permissions
    
    async def get_user_permissions(self, user_id: str) -> Set[Permission]:
        """Get user permissions"""
        if user_id not in self.users:
            return set()
        
        return self.users[user_id].permissions.copy()
    
    async def grant_permission(self, user_id: str, permission: Permission) -> bool:
        """Grant permission to user"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].permissions.add(permission)
        logger.info(f"Granted permission {permission} to user {user_id}")
        return True
    
    async def revoke_permission(self, user_id: str, permission: Permission) -> bool:
        """Revoke permission from user"""
        if user_id not in self.users:
            return False
        
        self.users[user_id].permissions.discard(permission)
        logger.info(f"Revoked permission {permission} from user {user_id}")
        return True


class SSOManager:
    """Single Sign-On manager"""
    
    def __init__(self):
        self.providers: Dict[str, SSOConfig] = {}
        self.sso_users: Dict[str, str] = {}  # sso_id -> user_id
        self.sessions: Dict[str, Dict[str, Any]] = {}
    
    async def register_provider(self, config: SSOConfig) -> str:
        """Register SSO provider"""
        provider_id = f"{config.provider.value}_{config.name}"
        self.providers[provider_id] = config
        logger.info(f"Registered SSO provider: {config.name} ({provider_id})")
        return provider_id
    
    async def authenticate_sso_user(self, provider_id: str, sso_id: str, 
                                  user_info: Dict[str, Any]) -> Optional[str]:
        """Authenticate SSO user"""
        if provider_id not in self.providers:
            return None
        
        # Check if user exists
        if sso_id in self.sso_users:
            user_id = self.sso_users[sso_id]
            logger.info(f"SSO user authenticated: {sso_id} -> {user_id}")
            return user_id
        
        # Create new user if auto-provisioning is enabled
        config = self.providers[provider_id]
        if config.settings.get("auto_provision", False):
            user_id = await self._provision_sso_user(sso_id, user_info, config.provider)
            if user_id:
                self.sso_users[sso_id] = user_id
                return user_id
        
        return None
    
    async def _provision_sso_user(self, sso_id: str, user_info: Dict[str, Any], 
                                provider: SSOProvider) -> Optional[str]:
        """Provision new SSO user"""
        # Extract user information
        username = user_info.get("username", f"sso_{sso_id}")
        email = user_info.get("email", f"{sso_id}@sso.local")
        first_name = user_info.get("first_name", "SSO")
        last_name = user_info.get("last_name", "User")
        
        # Generate user ID
        user_id = f"sso_{sso_id}"
        
        # Create user (this would typically integrate with RBAC system)
        logger.info(f"Provisioned SSO user: {username} ({user_id})")
        return user_id
    
    async def create_sso_session(self, user_id: str, provider_id: str, 
                               session_data: Dict[str, Any]) -> str:
        """Create SSO session"""
        session_id = f"sso_{user_id}_{int(time.time())}"
        
        self.sessions[session_id] = {
            "user_id": user_id,
            "provider_id": provider_id,
            "created_at": datetime.now(),
            "expires_at": datetime.now() + timedelta(hours=8),
            "data": session_data
        }
        
        logger.info(f"Created SSO session: {session_id} for user {user_id}")
        return session_id
    
    async def validate_sso_session(self, session_id: str) -> Optional[str]:
        """Validate SSO session"""
        if session_id not in self.sessions:
            return None
        
        session = self.sessions[session_id]
        
        if datetime.now() > session["expires_at"]:
            del self.sessions[session_id]
            return None
        
        return session["user_id"]
    
    async def get_sso_providers(self) -> List[SSOConfig]:
        """Get all SSO providers"""
        return list(self.providers.values())


class AuditLogger:
    """Advanced audit logging system"""
    
    def __init__(self, log_file: str = "audit.log"):
        self.log_file = Path(log_file)
        self.log_buffer: List[AuditLog] = []
        self.buffer_size = 100
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    async def log_event(self, event_type: AuditEventType, user_id: str,
                       resource_type: str, resource_id: str, action: str,
                       details: Dict[str, Any], ip_address: Optional[str] = None,
                       user_agent: Optional[str] = None, session_id: Optional[str] = None):
        """Log audit event"""
        log_entry = AuditLog(
            log_id=f"audit_{int(time.time())}_{hash(user_id) % 10000}",
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            session_id=session_id
        )
        
        self.log_buffer.append(log_entry)
        
        # Flush buffer if full
        if len(self.log_buffer) >= self.buffer_size:
            await self._flush_buffer()
        
        logger.debug(f"Audit event logged: {event_type.value} by {user_id}")
    
    async def _flush_buffer(self):
        """Flush log buffer to file"""
        if not self.log_buffer:
            return
        
        # Encrypt and write logs
        encrypted_logs = []
        for log_entry in self.log_buffer:
            log_data = {
                "log_id": log_entry.log_id,
                "timestamp": log_entry.timestamp.isoformat(),
                "event_type": log_entry.event_type.value,
                "user_id": log_entry.user_id,
                "resource_type": log_entry.resource_type,
                "resource_id": log_entry.resource_id,
                "action": log_entry.action,
                "details": log_entry.details,
                "ip_address": log_entry.ip_address,
                "user_agent": log_entry.user_agent,
                "session_id": log_entry.session_id
            }
            
            # Encrypt sensitive data
            encrypted_data = self.cipher.encrypt(json.dumps(log_data).encode())
            encrypted_logs.append(encrypted_data.hex())
        
        # Write to file
        with open(self.log_file, "a") as f:
            for encrypted_log in encrypted_logs:
                f.write(f"{encrypted_log}\n")
        
        self.log_buffer.clear()
        logger.debug(f"Flushed {len(encrypted_logs)} audit logs to file")
    
    async def search_logs(self, filters: Dict[str, Any], 
                         start_date: Optional[datetime] = None,
                         end_date: Optional[datetime] = None,
                         limit: int = 100) -> List[AuditLog]:
        """Search audit logs"""
        # This is a simplified search - in production, you'd use a proper database
        results = []
        
        # Read and decrypt logs
        if self.log_file.exists():
            with open(self.log_file, "r") as f:
                for line in f:
                    try:
                        encrypted_data = bytes.fromhex(line.strip())
                        decrypted_data = self.cipher.decrypt(encrypted_data)
                        log_data = json.loads(decrypted_data.decode())
                        
                        # Apply filters
                        if await self._matches_filters(log_data, filters, start_date, end_date):
                            log_entry = AuditLog(
                                log_id=log_data["log_id"],
                                timestamp=datetime.fromisoformat(log_data["timestamp"]),
                                event_type=AuditEventType(log_data["event_type"]),
                                user_id=log_data["user_id"],
                                resource_type=log_data["resource_type"],
                                resource_id=log_data["resource_id"],
                                action=log_data["action"],
                                details=log_data["details"],
                                ip_address=log_data.get("ip_address"),
                                user_agent=log_data.get("user_agent"),
                                session_id=log_data.get("session_id")
                            )
                            results.append(log_entry)
                            
                            if len(results) >= limit:
                                break
                    except Exception as e:
                        logger.error(f"Error reading audit log: {e}")
        
        return results
    
    async def _matches_filters(self, log_data: Dict[str, Any], filters: Dict[str, Any],
                             start_date: Optional[datetime], end_date: Optional[datetime]) -> bool:
        """Check if log entry matches filters"""
        # Date range filter
        if start_date or end_date:
            log_timestamp = datetime.fromisoformat(log_data["timestamp"])
            if start_date and log_timestamp < start_date:
                return False
            if end_date and log_timestamp > end_date:
                return False
        
        # Other filters
        for key, value in filters.items():
            if key in log_data and log_data[key] != value:
                return False
        
        return True
    
    async def generate_audit_report(self, start_date: datetime, end_date: datetime,
                                  report_type: str = "summary") -> Dict[str, Any]:
        """Generate audit report"""
        logs = await self.search_logs({}, start_date, end_date, limit=10000)
        
        report = {
            "report_type": report_type,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_events": len(logs),
            "event_summary": {},
            "user_activity": {},
            "security_events": []
        }
        
        # Event summary
        for log in logs:
            event_type = log.event_type.value
            report["event_summary"][event_type] = report["event_summary"].get(event_type, 0) + 1
        
        # User activity
        for log in logs:
            user_id = log.user_id
            if user_id not in report["user_activity"]:
                report["user_activity"][user_id] = 0
            report["user_activity"][user_id] += 1
        
        # Security events
        security_event_types = [
            AuditEventType.USER_LOGIN, AuditEventType.USER_LOGOUT,
            AuditEventType.PERMISSION_GRANTED, AuditEventType.PERMISSION_REVOKED,
            AuditEventType.SECURITY_EVENT
        ]
        
        for log in logs:
            if log.event_type in security_event_types:
                report["security_events"].append({
                    "timestamp": log.timestamp.isoformat(),
                    "event_type": log.event_type.value,
                    "user_id": log.user_id,
                    "details": log.details
                })
        
        return report


class EnterpriseFeatures:
    """Main enterprise features manager"""
    
    def __init__(self):
        self.rbac = RoleBasedAccessControl()
        self.sso_manager = SSOManager()
        self.audit_logger = AuditLogger()
        self.jwt_secret = "your-jwt-secret-key"  # In production, use secure secret
    
    async def initialize(self):
        """Initialize enterprise features"""
        # Create default admin user
        await self.rbac.create_user(
            user_id="admin",
            username="admin",
            email="admin@heygen.ai",
            first_name="System",
            last_name="Administrator",
            role=Role.SUPER_ADMIN
        )
        
        logger.info("Enterprise features initialized")
    
    async def authenticate_user(self, username: str, password: str) -> Optional[str]:
        """Authenticate user with username/password"""
        # Find user by username
        user = None
        for u in self.rbac.users.values():
            if u.username == username:
                user = u
                break
        
        if not user or not user.is_active:
            return None
        
        # In production, verify password hash
        # For demo, accept any password
        user.last_login = datetime.now()
        
        # Log authentication event
        await self.audit_logger.log_event(
            AuditEventType.USER_LOGIN,
            user.user_id,
            "user",
            user.user_id,
            "login",
            {"method": "password", "username": username}
        )
        
        return user.user_id
    
    async def authenticate_sso(self, provider_id: str, sso_id: str, 
                             user_info: Dict[str, Any]) -> Optional[str]:
        """Authenticate user via SSO"""
        user_id = await self.sso_manager.authenticate_sso_user(provider_id, sso_id, user_info)
        
        if user_id:
            # Log SSO authentication
            await self.audit_logger.log_event(
                AuditEventType.USER_LOGIN,
                user_id,
                "user",
                user_id,
                "login",
                {"method": "sso", "provider": provider_id, "sso_id": sso_id}
            )
        
        return user_id
    
    async def check_permission(self, user_id: str, permission: Permission) -> bool:
        """Check user permission"""
        return await self.rbac.check_permission(user_id, permission)
    
    async def create_user(self, user_id: str, username: str, email: str,
                         first_name: str, last_name: str, role: Role,
                         created_by: str) -> User:
        """Create new user"""
        user = await self.rbac.create_user(
            user_id, username, email, first_name, last_name, role
        )
        
        # Log user creation
        await self.audit_logger.log_event(
            AuditEventType.USER_CREATED,
            created_by,
            "user",
            user_id,
            "create",
            {"username": username, "email": email, "role": role.value}
        )
        
        return user
    
    async def update_user(self, user_id: str, updated_by: str, **kwargs) -> User:
        """Update user"""
        user = await self.rbac.update_user(user_id, **kwargs)
        
        # Log user update
        await self.audit_logger.log_event(
            AuditEventType.USER_UPDATED,
            updated_by,
            "user",
            user_id,
            "update",
            kwargs
        )
        
        return user
    
    async def grant_permission(self, user_id: str, permission: Permission, granted_by: str) -> bool:
        """Grant permission to user"""
        success = await self.rbac.grant_permission(user_id, permission)
        
        if success:
            await self.audit_logger.log_event(
                AuditEventType.PERMISSION_GRANTED,
                granted_by,
                "user",
                user_id,
                "grant_permission",
                {"permission": permission.value}
            )
        
        return success
    
    async def revoke_permission(self, user_id: str, permission: Permission, revoked_by: str) -> bool:
        """Revoke permission from user"""
        success = await self.rbac.revoke_permission(user_id, permission)
        
        if success:
            await self.audit_logger.log_event(
                AuditEventType.PERMISSION_REVOKED,
                revoked_by,
                "user",
                user_id,
                "revoke_permission",
                {"permission": permission.value}
            )
        
        return success
    
    async def register_sso_provider(self, config: SSOConfig) -> str:
        """Register SSO provider"""
        return await self.sso_manager.register_provider(config)
    
    async def search_audit_logs(self, filters: Dict[str, Any],
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> List[AuditLog]:
        """Search audit logs"""
        return await self.audit_logger.search_logs(filters, start_date, end_date)
    
    async def generate_audit_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Generate audit report"""
        return await self.audit_logger.generate_audit_report(start_date, end_date)
    
    async def health_check(self) -> Dict[str, Any]:
        """Get enterprise features health status"""
        return {
            "status": "healthy",
            "total_users": len(self.rbac.users),
            "total_groups": len(self.rbac.groups),
            "sso_providers": len(self.sso_manager.providers),
            "audit_logs": len(self.audit_logger.log_buffer),
            "last_audit_flush": datetime.now().isoformat()
        }


# Example usage
async def create_enterprise_features() -> EnterpriseFeatures:
    """Create and configure enterprise features"""
    enterprise = EnterpriseFeatures()
    await enterprise.initialize()
    return enterprise


if __name__ == "__main__":
    async def main():
        # Create enterprise features
        enterprise = await create_enterprise_features()
        
        # Create users
        await enterprise.create_user(
            "user1", "john.doe", "john@company.com",
            "John", "Doe", Role.EDITOR, "admin"
        )
        
        await enterprise.create_user(
            "user2", "jane.smith", "jane@company.com",
            "Jane", "Smith", Role.MANAGER, "admin"
        )
        
        # Test authentication
        user_id = await enterprise.authenticate_user("john.doe", "password")
        if user_id:
            print(f"User authenticated: {user_id}")
        
        # Test permissions
        can_generate = await enterprise.check_permission("user1", Permission.GENERATE_VIDEO)
        print(f"Can generate video: {can_generate}")
        
        # Grant permission
        await enterprise.grant_permission("user1", Permission.EXPORT_ANALYTICS, "admin")
        
        # Search audit logs
        logs = await enterprise.search_audit_logs({"user_id": "user1"})
        print(f"Found {len(logs)} audit logs for user1")
        
        # Generate audit report
        report = await enterprise.generate_audit_report(
            datetime.now() - timedelta(days=1),
            datetime.now()
        )
        print(f"Audit report: {json.dumps(report, indent=2)}")
        
        # Health check
        health = await enterprise.health_check()
        print(f"Health: {json.dumps(health, indent=2)}")
    
    asyncio.run(main())
