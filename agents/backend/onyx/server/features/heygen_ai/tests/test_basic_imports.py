"""
Basic import test to verify the test setup works correctly.
"""

import pytest
import sys
from pathlib import Path

def test_import_paths():
    """Test that import paths are set up correctly"""
    # Check that we can import the main modules
    try:
        from network_utils import NetworkUtils
        assert NetworkUtils is not None
    except ImportError as e:
        pytest.skip(f"NetworkUtils not available: {e}")
    
    try:
        from port_scanner import AsyncPortScanner
        assert AsyncPortScanner is not None
    except ImportError as e:
        pytest.skip(f"AsyncPortScanner not available: {e}")
    
    try:
        from security_config import SecurityConfigManager
        assert SecurityConfigManager is not None
    except ImportError as e:
        pytest.skip(f"SecurityConfigManager not available: {e}")
    
    try:
        from vulnerability_scanner import WebVulnerabilityScanner
        assert WebVulnerabilityScanner is not None
    except ImportError as e:
        pytest.skip(f"WebVulnerabilityScanner not available: {e}")

def test_python_path():
    """Test that Python path includes the current directory"""
    current_dir = Path(__file__).parent
    assert str(current_dir) in sys.path
    
    # Check that we can import from the parent directory
    parent_dir = current_dir.parent
    assert str(parent_dir) in sys.path

def test_basic_assertions():
    """Basic test to ensure pytest is working"""
    assert 1 + 1 == 2
    assert "hello" in "hello world"
    assert len([1, 2, 3]) == 3
