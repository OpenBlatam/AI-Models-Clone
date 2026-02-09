#!/usr/bin/env python3
"""
Deployment Exceptions
Custom exceptions for deployment system
"""


class DeploymentError(Exception):
    """Base exception for deployment errors"""
    pass


class DeploymentValidationError(DeploymentError):
    """Raised when deployment validation fails"""
    pass


class DeploymentSecurityError(DeploymentError):
    """Raised when security checks fail"""
    pass


class DeploymentComplianceError(DeploymentError):
    """Raised when compliance checks fail"""
    pass


class DeploymentApprovalError(DeploymentError):
    """Raised when deployment is not approved"""
    pass


class DeploymentTimeoutError(DeploymentError):
    """Raised when deployment times out"""
    pass


class DeploymentRollbackError(DeploymentError):
    """Raised when rollback fails"""
    pass


class DeploymentStrategyError(DeploymentError):
    """Raised when deployment strategy fails"""
    pass


class DeploymentHealthCheckError(DeploymentError):
    """Raised when health checks fail"""
    pass


class DeploymentConfigurationError(DeploymentError):
    """Raised when configuration is invalid"""
    pass
