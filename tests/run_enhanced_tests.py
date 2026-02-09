#!/usr/bin/env python3
"""
🧪 Enhanced Test Runner for ADS System

Advanced test runner with sophisticated reporting, parallel execution,
and comprehensive test suite management.
"""

import sys
import os
import subprocess
import time
import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any
import multiprocessing

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class EnhancedTestRunner:
    """Enhanced test runner with advanced features."""
    
    def __init__(self):
        self.start_time = None
        self.results = {}
        self.test_reports_dir = Path("tests/reports")
        self.test_reports_dir.mkdir(exist_ok=True)
        
        # Create logs directory
        logs_dir = Path("tests/logs")
        logs_dir.mkdir(exist_ok=True)
    
    def run_command(self, command: str, description: str, timeout: int = 300) -> Dict[str, Any]:
        """Run a command with enhanced logging and reporting."""
        print(f"\n{'='*80}")
        print(f"🚀 {description}")
        print(f"{'='*80}")
        print(f"Command: {command}")
        print(f"Timeout: {timeout}s")
        print(f"{'='*80}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=Path(__file__).parent
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            result_data = {
                "description": description,
                "command": command,
                "exit_code": result.returncode,
                "duration": duration,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
            print(f"Exit Code: {result.returncode}")
            print(f"Duration: {duration:.2f}s")
            
            if result.stdout:
                print(f"\n📤 STDOUT:")
                print(result.stdout[-2000:])  # Last 2000 chars to avoid spam
            
            if result.stderr:
                print(f"\n⚠️  STDERR:")
                print(result.stderr[-1000:])  # Last 1000 chars
            
            if result.returncode == 0:
                print(f"\n✅ {description} completed successfully!")
            else:
                print(f"\n❌ {description} failed!")
            
            return result_data
            
        except subprocess.TimeoutExpired:
            print(f"\n⏰ {description} timed out after {timeout}s")
            return {
                "description": description,
                "command": command,
                "exit_code": -1,
                "duration": timeout,
                "stdout": "",
                "stderr": f"Command timed out after {timeout}s",
                "success": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            print(f"\n💥 Error running {description}: {e}")
            return {
                "description": description,
                "command": command,
                "exit_code": -2,
                "duration": 0,
                "stdout": "",
                "stderr": str(e),
                "success": False,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    def run_unit_tests(self, parallel: bool = False, coverage: bool = True) -> Dict[str, Any]:
        """Run unit tests with options."""
        command_parts = ["py", "-m", "pytest", "unit/", "-v", "--tb=short"]
        
        if parallel:
            workers = min(multiprocessing.cpu_count(), 4)
            command_parts.extend(["-n", str(workers)])
        
        if coverage:
            command_parts.extend([
                "--cov=domain", "--cov=optimization", "--cov=training",
                "--cov-report=term-missing", "--cov-report=html:htmlcov"
            ])
        
        command_parts.extend(["-m", "unit"])
        
        return self.run_command(
            " ".join(command_parts),
            "Enhanced Unit Tests",
            timeout=600
        )
    
    def run_integration_tests(self, parallel: bool = False) -> Dict[str, Any]:
        """Run integration tests."""
        command_parts = ["py", "-m", "pytest", "integration/", "-v", "--tb=short"]
        
        if parallel:
            workers = min(multiprocessing.cpu_count(), 2)
            command_parts.extend(["-n", str(workers)])
        
        command_parts.extend(["-m", "integration"])
        
        return self.run_command(
            " ".join(command_parts),
            "Enhanced Integration Tests",
            timeout=900
        )
    
    def run_performance_tests(self) -> Dict[str, Any]:
        """Run performance tests."""
        return self.run_command(
            "py -m pytest performance/ -v --tb=short -m performance --durations=0",
            "Enhanced Performance Tests",
            timeout=1200
        )
    
    def run_security_tests(self) -> Dict[str, Any]:
        """Run security tests."""
        return self.run_command(
            "py -m pytest unit/test_security_validation.py -v --tb=short -m security",
            "Enhanced Security Tests",
            timeout=300
        )
    
    def run_api_tests(self) -> Dict[str, Any]:
        """Run API tests."""
        return self.run_command(
            "py -m pytest integration/test_api_endpoints.py -v --tb=short -m api",
            "Enhanced API Tests",
            timeout=600
        )
    
    def run_concurrency_tests(self) -> Dict[str, Any]:
        """Run concurrency tests."""
        return self.run_command(
            "py -m pytest performance/test_concurrency_threading.py -v --tb=short -m concurrency",
            "Enhanced Concurrency Tests",
            timeout=900
        )
    
    def run_regression_tests(self) -> Dict[str, Any]:
        """Run regression tests."""
        return self.run_command(
            "py -m pytest integration/test_regression_snapshots.py -v --tb=short -m regression",
            "Enhanced Regression Tests",
            timeout=600
        )
    
    def run_smoke_tests(self) -> Dict[str, Any]:
        """Run smoke tests for quick validation."""
        return self.run_command(
            "py -m pytest -v --tb=short -m smoke -x",
            "Enhanced Smoke Tests",
            timeout=180
        )
    
    def run_all_tests(self, parallel: bool = False, coverage: bool = True) -> Dict[str, Any]:
        """Run all tests."""
        command_parts = ["py", "-m", "pytest", "-v", "--tb=short"]
        
        if parallel:
            workers = min(multiprocessing.cpu_count(), 4)
            command_parts.extend(["-n", str(workers)])
        
        if coverage:
            command_parts.extend([
                "--cov=domain", "--cov=optimization", "--cov=training",
                "--cov-report=term-missing", "--cov-report=html:htmlcov",
                "--cov-report=xml:coverage.xml"
            ])
        
        return self.run_command(
            " ".join(command_parts),
            "Enhanced Full Test Suite",
            timeout=1800
        )
    
    def run_test_suite(self, suite_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run a custom test suite based on configuration."""
        suite_name = suite_config.get("name", "Custom Suite")
        test_types = suite_config.get("types", ["unit"])
        parallel = suite_config.get("parallel", False)
        coverage = suite_config.get("coverage", True)
        
        print(f"\n🎯 Running Test Suite: {suite_name}")
        print(f"Test Types: {test_types}")
        print(f"Parallel: {parallel}")
        print(f"Coverage: {coverage}")
        
        suite_results = {}
        
        for test_type in test_types:
            if test_type == "unit":
                result = self.run_unit_tests(parallel=parallel, coverage=coverage)
            elif test_type == "integration":
                result = self.run_integration_tests(parallel=parallel)
            elif test_type == "performance":
                result = self.run_performance_tests()
            elif test_type == "security":
                result = self.run_security_tests()
            elif test_type == "api":
                result = self.run_api_tests()
            elif test_type == "concurrency":
                result = self.run_concurrency_tests()
            elif test_type == "regression":
                result = self.run_regression_tests()
            elif test_type == "smoke":
                result = self.run_smoke_tests()
            else:
                result = {
                    "description": f"Unknown test type: {test_type}",
                    "success": False,
                    "error": f"Unknown test type: {test_type}"
                }
            
            suite_results[test_type] = result
        
        return suite_results
    
    def generate_report(self, results: Dict[str, Any]) -> str:
        """Generate a comprehensive test report."""
        report_time = datetime.now(timezone.utc)
        report_path = self.test_reports_dir / f"test_report_{report_time.strftime('%Y%m%d_%H%M%S')}.json"
        
        # Calculate summary statistics
        total_tests = len(results)
        successful_tests = sum(1 for r in results.values() if r.get("success", False))
        failed_tests = total_tests - successful_tests
        total_duration = sum(r.get("duration", 0) for r in results.values())
        
        report_data = {
            "report_metadata": {
                "generated_at": report_time.isoformat(),
                "report_version": "2.0",
                "test_runner": "EnhancedTestRunner"
            },
            "summary": {
                "total_test_suites": total_tests,
                "successful_suites": successful_tests,
                "failed_suites": failed_tests,
                "success_rate": (successful_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration_seconds": total_duration,
                "average_duration_seconds": total_duration / total_tests if total_tests > 0 else 0
            },
            "detailed_results": results,
            "environment": {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": multiprocessing.cpu_count(),
                "working_directory": str(Path.cwd())
            }
        }
        
        # Save report
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        # Generate summary
        summary = f"""
🧪 Enhanced Test Report Summary
{'='*50}
📊 Statistics:
   • Total Test Suites: {total_tests}
   • Successful: {successful_tests} ✅
   • Failed: {failed_tests} ❌
   • Success Rate: {report_data['summary']['success_rate']:.1f}%
   • Total Duration: {total_duration:.2f}s
   • Average Duration: {report_data['summary']['average_duration_seconds']:.2f}s

📁 Report saved to: {report_path}

🔍 Detailed Results:
"""
        
        for test_name, result in results.items():
            status = "✅" if result.get("success", False) else "❌"
            duration = result.get("duration", 0)
            summary += f"   • {test_name}: {status} ({duration:.2f}s)\n"
        
        return summary
    
    def check_environment(self) -> bool:
        """Check if the test environment is properly set up."""
        print("\n🔍 Checking Enhanced Test Environment...")
        
        checks = []
        
        # Check Python
        try:
            result = subprocess.run("py --version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Python: {result.stdout.strip()}")
                checks.append(True)
            else:
                print("❌ Python not found")
                checks.append(False)
        except Exception as e:
            print(f"❌ Error checking Python: {e}")
            checks.append(False)
        
        # Check pytest
        try:
            result = subprocess.run("py -m pytest --version", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Pytest: {result.stdout.strip()}")
                checks.append(True)
            else:
                print("❌ Pytest not found")
                checks.append(False)
        except Exception as e:
            print(f"❌ Error checking pytest: {e}")
            checks.append(False)
        
        # Check system imports
        try:
            from domain.entities import Ad, AdCampaign
            from optimization.factory import get_optimization_factory
            print("✅ System imports working")
            checks.append(True)
        except ImportError as e:
            print(f"❌ System imports failed: {e}")
            checks.append(False)
        
        # Check optional dependencies
        optional_deps = [
            ("pytest-xdist", "py -m pytest --help | findstr xdist"),
            ("pytest-cov", "py -m pytest --help | findstr cov"),
            ("pytest-asyncio", "py -m pytest --help | findstr asyncio")
        ]
        
        for dep_name, check_cmd in optional_deps:
            try:
                result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ {dep_name}: Available")
                    checks.append(True)
                else:
                    print(f"⚠️  {dep_name}: Not available (optional)")
                    # Don't fail for optional dependencies
            except Exception:
                print(f"⚠️  {dep_name}: Check failed (optional)")
        
        success = all(checks[:3])  # Only require the first 3 essential checks
        
        if success:
            print("✅ Enhanced test environment is ready!")
        else:
            print("❌ Enhanced test environment check failed!")
        
        return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Enhanced ADS System Test Runner")
    
    # Test type arguments
    parser.add_argument("--unit", action="store_true", help="Run unit tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--security", action="store_true", help="Run security tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--concurrency", action="store_true", help="Run concurrency tests")
    parser.add_argument("--regression", action="store_true", help="Run regression tests")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Configuration arguments
    parser.add_argument("--parallel", action="store_true", help="Run tests in parallel")
    parser.add_argument("--no-coverage", action="store_true", help="Disable coverage reporting")
    parser.add_argument("--check-env", action="store_true", help="Check environment only")
    parser.add_argument("--suite", help="Run custom test suite from JSON config file")
    
    args = parser.parse_args()
    
    runner = EnhancedTestRunner()
    runner.start_time = datetime.now(timezone.utc)
    
    print("🧪 Enhanced ADS System Test Runner")
    print("=" * 60)
    
    # Check environment
    if not runner.check_environment():
        print("❌ Environment check failed. Please fix issues above.")
        sys.exit(1)
    
    if args.check_env:
        print("✅ Environment check completed successfully!")
        return
    
    # Run tests
    results = {}
    
    if args.suite:
        # Load custom suite
        try:
            with open(args.suite, 'r') as f:
                suite_config = json.load(f)
            results = runner.run_test_suite(suite_config)
        except Exception as e:
            print(f"❌ Error loading test suite: {e}")
            sys.exit(1)
    else:
        # Run individual test types
        coverage = not args.no_coverage
        
        if args.unit:
            results["unit"] = runner.run_unit_tests(parallel=args.parallel, coverage=coverage)
        
        if args.integration:
            results["integration"] = runner.run_integration_tests(parallel=args.parallel)
        
        if args.performance:
            results["performance"] = runner.run_performance_tests()
        
        if args.security:
            results["security"] = runner.run_security_tests()
        
        if args.api:
            results["api"] = runner.run_api_tests()
        
        if args.concurrency:
            results["concurrency"] = runner.run_concurrency_tests()
        
        if args.regression:
            results["regression"] = runner.run_regression_tests()
        
        if args.smoke:
            results["smoke"] = runner.run_smoke_tests()
        
        if args.all or not any([args.unit, args.integration, args.performance, 
                               args.security, args.api, args.concurrency, 
                               args.regression, args.smoke]):
            results["all"] = runner.run_all_tests(parallel=args.parallel, coverage=coverage)
    
    # Generate and display report
    if results:
        summary = runner.generate_report(results)
        print(summary)
        
        # Determine exit code
        all_successful = all(r.get("success", False) for r in results.values())
        sys.exit(0 if all_successful else 1)
    else:
        print("⚠️  No tests were run. Use --help for usage information.")
        sys.exit(1)


if __name__ == "__main__":
    main()

