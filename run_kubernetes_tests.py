#!/usr/bin/env python3
"""
Test runner for Kubernetes deployment manager tests.
"""
import unittest
import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import the test module
from kubernetes.test_deployment_manager import TestDeploymentManager

if __name__ == '__main__':
    # Run the tests
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDeploymentManager)
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
