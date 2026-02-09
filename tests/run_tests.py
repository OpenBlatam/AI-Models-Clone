#!/usr/bin/env python3
"""
🧪 Comprehensive Test Runner for ADS System

This script runs all types of tests with different configurations
"""

import sys
import os
import subprocess
import time
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import the system
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_command(command, description):
    """Run a command and return the result."""
    print(f"\n{'='*60}")
    print(f"🚀 {description}")
    print(f"{'='*60}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"Exit Code: {result.returncode}")
        print(f"Duration: {duration:.2f} seconds")
        
        if result.stdout:
            print("\n📤 STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("\n⚠️  STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"\n✅ {description} completed successfully!")
        else:
            print(f"\n❌ {description} failed with exit code {result.returncode}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"\n💥 Error running {description}: {e}")
        return False

def run_unit_tests():
    """Run unit tests."""
    return run_command(
        "py -m pytest tests/unit/ -v --tb=short",
        "Unit Tests"
    )

def run_integration_tests():
    """Run integration tests."""
    return run_command(
        "py -m pytest tests/integration/ -v --tb=short",
        "Integration Tests"
    )

def run_performance_tests():
    """Run performance tests."""
    return run_command(
        "py -m pytest tests/performance/ -v --tb=short -m performance",
        "Performance Tests"
    )

def run_stress_tests():
    """Run stress tests."""
    return run_command(
        "py -m pytest tests/performance/ -v --tb=short -m stress",
        "Stress Tests"
    )

def run_all_tests():
    """Run all tests."""
    return run_command(
        "py -m pytest tests/ -v --tb=short",
        "All Tests"
    )

def run_tests_with_coverage():
    """Run tests with coverage report."""
    return run_command(
        "py -m pytest tests/ -v --tb=short --cov=domain --cov=optimization --cov=training --cov-report=html --cov-report=term",
        "Tests with Coverage"
    )

def run_specific_test_file(test_file):
    """Run a specific test file."""
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return False
    
    return run_command(
        f"py -m pytest {test_file} -v --tb=short",
        f"Specific Test: {test_file}"
    )

def run_tests_by_marker(marker):
    """Run tests by marker."""
    return run_command(
        f"py -m pytest tests/ -v --tb=short -m {marker}",
        f"Tests with marker: {marker}"
    )

def run_fast_tests():
    """Run only fast tests (exclude slow ones)."""
    return run_command(
        "py -m pytest tests/ -v --tb=short -m 'not slow'",
        "Fast Tests Only"
    )

def run_slow_tests():
    """Run only slow tests."""
    return run_command(
        "py -m pytest tests/ -v --tb=short -m slow",
        "Slow Tests Only"
    )

def check_test_environment():
    """Check if the test environment is properly set up."""
    print("\n🔍 Checking Test Environment...")
    
    # Check Python version
    try:
        result = subprocess.run("py --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Python: {result.stdout.strip()}")
        else:
            print("❌ Python not found or not working")
            return False
    except Exception as e:
        print(f"❌ Error checking Python: {e}")
        return False
    
    # Check pytest
    try:
        result = subprocess.run("py -m pytest --version", shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Pytest: {result.stdout.strip()}")
        else:
            print("❌ Pytest not found")
            return False
    except Exception as e:
        print(f"❌ Error checking pytest: {e}")
        return False
    
    # Check if we can import the system
    try:
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from domain.entities import Ad, AdCampaign
        from optimization.factory import get_optimization_factory
        print("✅ System imports working")
    except ImportError as e:
        print(f"❌ System imports failed: {e}")
        return False
    
    print("✅ Test environment is ready!")
    return True

def main():
    """Main function to run tests based on command line arguments."""
    parser = argparse.ArgumentParser(description="ADS System Test Runner")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "performance", "stress", "all", "coverage"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--file",
        help="Run a specific test file"
    )
    parser.add_argument(
        "--marker",
        help="Run tests with a specific marker"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests"
    )
    parser.add_argument(
        "--slow",
        action="store_true",
        help="Run only slow tests"
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check test environment only"
    )
    
    args = parser.parse_args()
    
    print("🧪 ADS System Test Runner")
    print("=" * 50)
    
    # Check environment first
    if not check_test_environment():
        print("❌ Test environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    if args.check_env:
        print("✅ Environment check completed successfully!")
        return
    
    # Run tests based on arguments
    success = True
    
    if args.file:
        success = run_specific_test_file(args.file)
    elif args.marker:
        success = run_tests_by_marker(args.marker)
    elif args.fast:
        success = run_fast_tests()
    elif args.slow:
        success = run_slow_tests()
    elif args.type == "unit":
        success = run_unit_tests()
    elif args.type == "integration":
        success = run_integration_tests()
    elif args.type == "performance":
        success = run_performance_tests()
    elif args.type == "stress":
        success = run_stress_tests()
    elif args.type == "coverage":
        success = run_tests_with_coverage()
    else:  # all
        success = run_all_tests()
    
    # Final summary
    print("\n" + "="*60)
    if success:
        print("🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        print("💥 Some tests failed. Please check the output above.")
        sys.exit(1)

if __name__ == "__main__":
    main()

