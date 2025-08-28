from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
from .crypto_helpers import (
from .network_helpers import (
from typing import Any, List, Dict, Optional
import logging
import asyncio
"""
Security Utils Module

Provides utility functions for cryptographic operations and network operations.
"""

    CryptoRequest,
    CryptoResult,
    CryptoOperation,
    HashAlgorithm,
    EncryptionAlgorithm,
    perform_hash_async,
    perform_encryption_async,
    perform_decryption_async,
    generate_key_async,
    verify_signature_async,
    create_digital_signature_async,
    generate_random_bytes_async,
    derive_key_from_password_async,
    encrypt_file_async,
    decrypt_file_async,
    hash_file_async,
    verify_file_integrity_async
)

    NetworkRequest,
    NetworkResult,
    NetworkOperation,
    perform_dns_lookup_async,
    perform_http_request_async,
    perform_https_request_async,
    check_port_availability_async,
    resolve_hostname_async,
    get_network_info_async,
    perform_traceroute_async,
    check_connectivity_async,
    get_ssl_certificate_async,
    perform_whois_lookup_async,
    get_geolocation_async,
    validate_ip_address,
    validate_domain_name,
    get_mac_address_async,
    perform_arp_scan_async
)

__all__ = [
    # Crypto Helpers
    "CryptoRequest",
    "CryptoResult", 
    "CryptoOperation",
    "HashAlgorithm",
    "EncryptionAlgorithm",
    "perform_hash_async",
    "perform_encryption_async",
    "perform_decryption_async",
    "generate_key_async",
    "verify_signature_async",
    "create_digital_signature_async",
    "generate_random_bytes_async",
    "derive_key_from_password_async",
    "encrypt_file_async",
    "decrypt_file_async",
    "hash_file_async",
    "verify_file_integrity_async",
    
    # Network Helpers
    "NetworkRequest",
    "NetworkResult",
    "NetworkOperation",
    "perform_dns_lookup_async",
    "perform_http_request_async",
    "perform_https_request_async",
    "check_port_availability_async",
    "resolve_hostname_async",
    "get_network_info_async",
    "perform_traceroute_async",
    "check_connectivity_async",
    "get_ssl_certificate_async",
    "perform_whois_lookup_async",
    "get_geolocation_async",
    "validate_ip_address",
    "validate_domain_name",
    "get_mac_address_async",
    "perform_arp_scan_async"
] 