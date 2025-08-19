from typing_extensions import Literal, TypedDict
from typing import Any, Dict, List, Optional, Tuple, Union
# Constants
MAX_RETRIES = 100

# Constants
TIMEOUT_SECONDS = 60

import os
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import logging
from pathlib import Path
import asyncio
"""
Security Configuration Module
============================

Security configuration management following lowercase_underscores naming convention.
"""


class SecurityLevel(Enum):
    """Security level definitions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class EncryptionAlgorithm(Enum):
    """Supported encryption algorithms."""
    AES_256 = "aes-256-gcm"
    CHACHA20 = "chacha20-poly1305"
    RSA_2048 = "rsa-2048"
    RSA_4096 = "rsa-4096"

@dataclass
class SecurityPolicy:
    """Security policy configuration."""
    policy_name: str
    security_level: SecurityLevel
    is_policy_enabled: bool = True
    policy_description: str = ""
    created_timestamp: datetime = field(default_factory=datetime.utcnow)
    last_modified: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AccessControlRule:
    """Access control rule definition."""
    rule_name: str
    resource_path: str
    allowed_roles: List[str]
    denied_roles: List[str] = field(default_factory=list)
    is_rule_enabled: bool = True
    requires_authentication: bool = True
    requires_authorization: bool = True

class SecurityConfigManager:
    """Security configuration manager with descriptive naming."""

    def __init__(self, config_file_path: Optional[str] = None):
        """Initialize manager with optional config file path."""
        self.config_file_path = config_file_path or "security_config.json"
        self.logger = logging.getLogger(__name__)
        
        # Default security configurations
        self.default_security_config = {
            'authentication_settings': {
                'is_multi_factor_enabled': False,
                'is_password_complexity_required': True,
                'password_minimum_length': 8,
                'password_expiry_days': 90,
                'max_login_attempts': 5,
                'account_lockout_duration_minutes': 30,
                'session_timeout_minutes': 60
            },
            'encryption_settings': {
                'default_encryption_algorithm': EncryptionAlgorithm.AES_256.value,
                'is_encryption_at_rest_enabled': True,
                'is_encryption_in_transit_enabled': True,
                'key_rotation_days': 365,
                'is_secure_key_storage_enabled': True
            },
            'network_security_settings': {
                'is_firewall_enabled': True,
                'is_intrusion_detection_enabled': True,
                'allowed_ip_ranges': [],
                'blocked_ip_ranges': [],
                'is_rate_limiting_enabled': True,
                'max_requests_per_minute': 100
            },
            'data_protection_settings': {
                'is_data_anonymization_enabled': False,
                'is_data_encryption_enabled': True,
                'data_retention_days': 2555,  # 7 years
                'is_backup_encryption_enabled': True,
                'is_audit_logging_enabled': True
            },
            'compliance_settings': {
                'is_gdpr_compliant': False,
                'is_hipaa_compliant': False,
                'is_sox_compliant': False,
                'is_pci_dss_compliant': False,
                'compliance_reporting_enabled': True
            }
        }
        
        # Load configuration
        self.current_config = self._load_configuration()
    
    def _load_configuration(self) -> Dict[str, Any]:
        """Load security configuration from file or create default."""
        try:
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self.logger.info(f"Security configuration loaded from {self.config_file_path}")
                    return self._merge_with_defaults(loaded_config)
            else:
                self.logger.info("No configuration file found, using defaults")
                return self.default_security_config.copy()
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {str(e)}")
            return self.default_security_config.copy()
    
    def _merge_with_defaults(self, loaded_config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded configuration with defaults."""
        merged_config = self.default_security_config.copy()
        
        for section, settings in loaded_config.items():
            if section in merged_config:
                merged_config[section].update(settings)
            else:
                merged_config[section] = settings
        
        return merged_config
    
    def save_configuration(self) -> bool:
        """Save current configuration to file."""
        try:
            config_dir = os.path.dirname(self.config_file_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            with open(self.config_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.current_config, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Security configuration saved to {self.config_file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save configuration: {str(e)}")
            return False
    
    def get_authentication_settings(self) -> Dict[str, Any]:
        """Get authentication security settings."""
        return self.current_config.get('authentication_settings', {})
    
    def get_encryption_settings(self) -> Dict[str, Any]:
        """Get encryption security settings."""
        return self.current_config.get('encryption_settings', {})
    
    def get_network_security_settings(self) -> Dict[str, Any]:
        """Get network security settings."""
        return self.current_config.get('network_security_settings', {})
    
    def get_data_protection_settings(self) -> Dict[str, Any]:
        """Get data protection settings."""
        return self.current_config.get('data_protection_settings', {})
    
    def get_compliance_settings(self) -> Dict[str, Any]:
        """Get compliance settings."""
        return self.current_config.get('compliance_settings', {})
    
    def update_authentication_setting(self, setting_name: str, setting_value: Any) -> bool:
        """Update a specific authentication setting."""
        try:
            auth_settings = self.current_config.get('authentication_settings', {})
            auth_settings[setting_name] = setting_value
            self.current_config['authentication_settings'] = auth_settings
            self.logger.info(f"Updated authentication setting: {setting_name} = {setting_value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update authentication setting: {str(e)}")
            return False
    
    def update_encryption_setting(self, setting_name: str, setting_value: Any) -> bool:
        """Update a specific encryption setting."""
        try:
            encryption_settings = self.current_config.get('encryption_settings', {})
            encryption_settings[setting_name] = setting_value
            self.current_config['encryption_settings'] = encryption_settings
            self.logger.info(f"Updated encryption setting: {setting_name} = {setting_value}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update encryption setting: {str(e)}")
            return False
    
    def is_security_feature_enabled(self, feature_name: str) -> bool:
        """Check if a security feature is enabled."""
        feature_mapping = {
            'multi_factor_authentication': 'authentication_settings.is_multi_factor_enabled',
            'password_complexity': 'authentication_settings.is_password_complexity_required',
            'encryption_at_rest': 'encryption_settings.is_encryption_at_rest_enabled',
            'encryption_in_transit': 'encryption_settings.is_encryption_in_transit_enabled',
            'firewall': 'network_security_settings.is_firewall_enabled',
            'intrusion_detection': 'network_security_settings.is_intrusion_detection_enabled',
            'rate_limiting': 'network_security_settings.is_rate_limiting_enabled',
            'data_anonymization': 'data_protection_settings.is_data_anonymization_enabled',
            'audit_logging': 'data_protection_settings.is_audit_logging_enabled'
        }
        
        if feature_name in feature_mapping:
            config_path = feature_mapping[feature_name].split('.')
            current_value = self.current_config
            for path_part in config_path:
                current_value = current_value.get(path_part, {})
            return bool(current_value)
        
        return False
    
    def get_security_compliance_status(self) -> Dict[str, bool]:
        """Get compliance status for various standards."""
        compliance_settings = self.get_compliance_settings()
        
        return {
            'is_gdpr_compliant': compliance_settings.get('is_gdpr_compliant', False),
            'is_hipaa_compliant': compliance_settings.get('is_hipaa_compliant', False),
            'is_sox_compliant': compliance_settings.get('is_sox_compliant', False),
            'is_pci_dss_compliant': compliance_settings.get('is_pci_dss_compliant', False)
        }
    
    def validate_security_configuration(self) -> Dict[str, Any]:
        """Validate current security configuration."""
        validation_result = {
            'is_configuration_valid': True,
            'validation_errors': [],
            'security_score': 0,
            'recommendations': []
        }
        
        # Check authentication settings
        auth_settings = self.get_authentication_settings()
        if auth_settings.get('password_minimum_length', 0) < 8:
            validation_result['validation_errors'].append("Password minimum length should be at least 8 characters")
            validation_result['recommendations'].append("Increase password minimum length to 8 or more")
        
        if not auth_settings.get('is_multi_factor_enabled', False):
            validation_result['recommendations'].append("Enable multi-factor authentication for enhanced security")
        
        # Check encryption settings
        encryption_settings = self.get_encryption_settings()
        if not encryption_settings.get('is_encryption_at_rest_enabled', False):
            validation_result['validation_errors'].append("Encryption at rest should be enabled")
            validation_result['recommendations'].append("Enable encryption at rest for data protection")
        
        if not encryption_settings.get('is_encryption_in_transit_enabled', False):
            validation_result['validation_errors'].append("Encryption in transit should be enabled")
            validation_result['recommendations'].append("Enable encryption in transit for secure communication")
        
        # Check network security settings
        network_settings = self.get_network_security_settings()
        if not network_settings.get('is_firewall_enabled', False):
            validation_result['validation_errors'].append("Firewall should be enabled")
            validation_result['recommendations'].append("Enable firewall for network protection")
        
        if not network_settings.get('is_rate_limiting_enabled', False):
            validation_result['recommendations'].append("Enable rate limiting to prevent abuse")
        
        # Calculate security score
        total_checks = 6
        passed_checks = 0
        
        if auth_settings.get('password_minimum_length', 0) >= 8:
            passed_checks += 1
        if auth_settings.get('is_multi_factor_enabled', False):
            passed_checks += 1
        if encryption_settings.get('is_encryption_at_rest_enabled', False):
            passed_checks += 1
        if encryption_settings.get('is_encryption_in_transit_enabled', False):
            passed_checks += 1
        if network_settings.get('is_firewall_enabled', False):
            passed_checks += 1
        if network_settings.get('is_rate_limiting_enabled', False):
            passed_checks += 1
        
        validation_result['security_score'] = (passed_checks / total_checks) * 100
        validation_result['is_configuration_valid'] = len(validation_result['validation_errors']) == 0
        
        return validation_result
    
    def generate_security_report(self) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        validation_result = self.validate_security_configuration()
        
        report = {
            'report_generated_at': datetime.utcnow().isoformat(),
            'configuration_file_path': self.config_file_path,
            'security_score': validation_result['security_score'],
            'is_configuration_valid': validation_result['is_configuration_valid'],
            'validation_errors': validation_result['validation_errors'],
            'recommendations': validation_result['recommendations'],
            'feature_status': {
                'multi_factor_authentication': self.is_security_feature_enabled('multi_factor_authentication'),
                'password_complexity': self.is_security_feature_enabled('password_complexity'),
                'encryption_at_rest': self.is_security_feature_enabled('encryption_at_rest'),
                'encryption_in_transit': self.is_security_feature_enabled('encryption_in_transit'),
                'firewall': self.is_security_feature_enabled('firewall'),
                'intrusion_detection': self.is_security_feature_enabled('intrusion_detection'),
                'rate_limiting': self.is_security_feature_enabled('rate_limiting'),
                'audit_logging': self.is_security_feature_enabled('audit_logging')
            },
            'compliance_status': self.get_security_compliance_status(),
            'current_settings': {
                'authentication': self.get_authentication_settings(),
                'encryption': self.get_encryption_settings(),
                'network_security': self.get_network_security_settings(),
                'data_protection': self.get_data_protection_settings()
            }
        }
        
        return report

# Usage example
def main():
    """Example usage of the security configuration manager."""
    security_config = SecurityConfigManager("security_config.json")
    
    # Update some settings
    security_config.update_authentication_setting('is_multi_factor_enabled', True)
    security_config.update_encryption_setting('is_encryption_at_rest_enabled', True)
    
    # Save configuration
    security_config.save_configuration()
    
    # Generate security report
    security_report = security_config.generate_security_report()
    
    print(f"Security Score: {security_report['security_score']:.1f}%")
    print(f"Configuration Valid: {security_report['is_configuration_valid']}")
    
    if security_report['recommendations']:
        print("\nRecommendations:")
        for recommendation in security_report['recommendations']:
            print(f"  - {recommendation}")
    
    print(f"\nMulti-factor Authentication: {security_report['feature_status']['multi_factor_authentication']}")
    print(f"Encryption at Rest: {security_report['feature_status']['encryption_at_rest']}")

# Run: main() 