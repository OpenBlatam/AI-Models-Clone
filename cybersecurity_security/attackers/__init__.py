"""
Security Attackers Module

Provides offensive security testing capabilities including brute force attacks and exploit development.
WARNING: This module is for authorized security testing only.
"""

from .brute_forcers import (
    BruteForceRequest,
    BruteForceResult,
    BruteForceType,
    SSHBruteForceRequest,
    SSHBruteForceResult,
    HTTPBruteForceRequest,
    HTTPBruteForceResult,
    FTPBruteForceRequest,
    FTPBruteForceResult,
    perform_ssh_brute_force_async,
    perform_http_brute_force_async,
    perform_ftp_brute_force_async,
    perform_generic_brute_force_async
)

from .exploiters import (
    ExploitRequest,
    ExploitResult,
    ExploitType,
    BufferOverflowRequest,
    BufferOverflowResult,
    SQLInjectionExploitRequest,
    SQLInjectionExploitResult,
    XSSExploitRequest,
    XSSExploitResult,
    CommandInjectionRequest,
    CommandInjectionResult,
    perform_buffer_overflow_test_async,
    perform_sql_injection_exploit_async,
    perform_xss_exploit_async,
    perform_command_injection_exploit_async,
    perform_generic_exploit_async
)

__all__ = [
    # Brute Forcers
    "BruteForceRequest",
    "BruteForceResult", 
    "BruteForceType",
    "SSHBruteForceRequest",
    "SSHBruteForceResult",
    "HTTPBruteForceRequest",
    "HTTPBruteForceResult",
    "FTPBruteForceRequest",
    "FTPBruteForceResult",
    "perform_ssh_brute_force_async",
    "perform_http_brute_force_async",
    "perform_ftp_brute_force_async",
    "perform_generic_brute_force_async",
    
    # Exploiters
    "ExploitRequest",
    "ExploitResult",
    "ExploitType",
    "BufferOverflowRequest",
    "BufferOverflowResult",
    "SQLInjectionExploitRequest",
    "SQLInjectionExploitResult",
    "XSSExploitRequest",
    "XSSExploitResult",
    "CommandInjectionRequest",
    "CommandInjectionResult",
    "perform_buffer_overflow_test_async",
    "perform_sql_injection_exploit_async",
    "perform_xss_exploit_async",
    "perform_command_injection_exploit_async",
    "perform_generic_exploit_async"
] 