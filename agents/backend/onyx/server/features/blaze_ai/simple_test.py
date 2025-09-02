#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple test script for Blaze AI Plugin System.
"""

import sys
import os
import subprocess
from pathlib import Path

def test_file_compilation():
    """Test that all Python files can be compiled without syntax errors."""
    print("Testing file compilation...")
    
    # List of files to test
    files_to_test = [
        "engines/__init__.py",
        "engines/plugins.py",
        "engines/base.py",
        "engines/factory.py"
    ]
    
    passed = 0
    total = len(files_to_test)
    
    for file_path in files_to_test:
        if os.path.exists(file_path):
            try:
                # Use Python to compile the file
                result = subprocess.run([
                    sys.executable, "-m", "py_compile", file_path
                ], capture_output=True, text=True, check=True)
                print(f"✅ {file_path} compiled successfully")
                passed += 1
            except subprocess.CalledProcessError as e:
                print(f"❌ {file_path} failed to compile: {e.stderr}")
        else:
            print(f"⚠️  {file_path} not found")
    
    return passed, total

def test_basic_imports():
    """Test basic Python imports without complex dependencies."""
    print("\nTesting basic imports...")
    
    try:
        import tempfile
        import shutil
        import json
        import time
        from pathlib import Path
        from dataclasses import dataclass
        from typing import Any, Dict, List, Optional, Type, Callable, Union
        print("✅ Basic Python imports successful")
        return True
    except ImportError as e:
        print(f"❌ Basic imports failed: {e}")
        return False

def test_file_structure():
    """Test that the expected file structure exists."""
    print("\nTesting file structure...")
    
    expected_files = [
        "engines/",
        "engines/__init__.py",
        "engines/plugins.py",
        "engines/base.py",
        "engines/factory.py",
        "tests/",
        "tests/test_plugins.py",
        "tests/test_llm_engine_cache.py",
        "tests/conftest.py",
        "tests/requirements-test.txt",
        "tests/README.md",
        "run_tests.py"
    ]
    
    passed = 0
    total = len(expected_files)
    
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
            passed += 1
        else:
            print(f"❌ {file_path} missing")
    
    return passed, total

def run_all_tests():
    """Run all tests and report results."""
    print("Blaze AI Plugin System - Simple Test Suite")
    print("=" * 60)
    
    # Test file compilation
    comp_passed, comp_total = test_file_compilation()
    
    # Test basic imports
    import_passed = test_basic_imports()
    
    # Test file structure
    struct_passed, struct_total = test_file_structure()
    
    # Calculate total results
    total_passed = comp_passed + (1 if import_passed else 0) + struct_passed
    total_tests = comp_total + 1 + struct_total
    
    print("\n" + "=" * 60)
    print(f"Test Results: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All tests passed!")
        return True
    else:
        print("💥 Some tests failed!")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
