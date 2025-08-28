from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from typing import Any, List, Dict, Optional
import logging
import asyncio
class ValidationError(Exception):
    """General exception for validation errors."""

    def __init__(self, message: str):
        
    """__init__ function."""
self.message = message
        super().__init__(self.message)


class ConnectorValidationError(ValidationError):
    """General exception for connector validation errors."""

    def __init__(self, message: str):
        
    """__init__ function."""
self.message = message
        super().__init__(self.message)


class UnexpectedValidationError(ValidationError):
    """Raised when an unexpected error occurs during connector validation.

    Unexpected errors don't necessarily mean the credential is invalid,
    but rather that there was an error during the validation process
    or we encountered a currently unhandled error case.

    Currently, unexpected validation errors are defined as transient and should not be
    used to disable the connector.
    """

    def __init__(self, message: str = "Unexpected error during connector validation"):
        
    """__init__ function."""
super().__init__(message)


class CredentialInvalidError(ConnectorValidationError):
    """Raised when a connector's credential is invalid."""

    def __init__(self, message: str = "Credential is invalid"):
        
    """__init__ function."""
super().__init__(message)


class CredentialExpiredError(ConnectorValidationError):
    """Raised when a connector's credential is expired."""

    def __init__(self, message: str = "Credential has expired"):
        
    """__init__ function."""
super().__init__(message)


class InsufficientPermissionsError(ConnectorValidationError):
    """Raised when the credential does not have sufficient API permissions."""

    def __init__(
        self, message: str = "Insufficient permissions for the requested operation"
    ):
        
    """__init__ function."""
super().__init__(message)
