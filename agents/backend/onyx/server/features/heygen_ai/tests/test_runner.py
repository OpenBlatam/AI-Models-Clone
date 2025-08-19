from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
# Constants
MAX_RETRIES = 100

import argparse
import asyncio
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import tempfile
import shutil
import platform
import sys
from typing import Any, List, Dict, Optional
import logging
#!/usr/bin/env python3
"""
HeyGen AI Testing Framework - Comprehensive Test Runner
======================================================

A sophisticated test runner that provides comprehensive testing capabilities
for the HeyGen AI FastAPI service following clean architecture principles.

Features:
- Multiple test categories (unit, integration, performance, e2e)
- Parallel test execution
- Coverage reporting
- Performance benchmarking
- Test result analysis
- CI/CD integration support
- Custom test filtering
- Detailed reporting

Usage:
    python tests/test_runner.py                    # Run all tests
    python tests/test_runner.py --unit             # Unit tests only
    python tests/test_runner.py --integration      # Integration tests only
    python tests/test_runner.py --performance      # Performance tests only
    python tests/test_runner.py --coverage         # With coverage
    python tests/test_runner.py --parallel         # Parallel execution
    python tests/test_runner.py --verbose          # Verbose output
    python tests/test_runner.py --benchmark        # Include benchmarks
"""


# Add project root to Python path
current_dir = Path(__file__).parent
project_root = current_dir.parent
sys.path.insert(0, str(project_root))


class TestRunner:
    """Comprehensive test runner for HeyGen AI service."""
    
    def __init__(self) -> Any:
        self.start_time = None
        self.results = {}
        self.coverage_data = {}
        self.performance_metrics = {}
        self.project_root = project_root
        self.tests_dir = current_dir
        
    def run_tests(
        self,
        categories: List[str] = None,
        parallel: bool = False,
        coverage: bool = False,
        verbose: bool = False,
        benchmark: bool = False,
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run tests with specified configuration.
        
        Args:
            categories: List of test categories to run
            parallel: Enable parallel test execution
            coverage: Enable coverage reporting
            verbose: Enable verbose output
            benchmark: Enable performance benchmarking
            output_dir: Output directory for reports
            
        Returns:
            Dictionary containing test results and metrics
        """
        self.start_time = time.time()
        
        if categories is None:
            categories = ['unit', 'integration', 'performance']
        
        if output_dir:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
        else:
            output_path = self.tests_dir / "reports"
            output_path.mkdir(exist_ok=True)
        
        print("🚀 HeyGen AI Testing Framework")
        print("=" * 50)
        print(f"Categories: {', '.join(categories)}")
        print(f"Parallel: {parallel}")
        print(f"Coverage: {coverage}")
        print(f"Benchmark: {benchmark}")
        print(f"Output: {output_path}")
        print("=" * 50)
        
        # Run each test category
        for category in categories:
            print(f"\n🧪 Running {category} tests...")
            category_results = self._run_category(
                category=category,
                parallel=parallel,
                coverage=coverage,
                verbose=verbose,
                benchmark=benchmark,
                output_dir=output_path
            )
            self.results[category] = category_results
        
        # Generate comprehensive report
        report = self._generate_report(output_path)
        
        # Print summary
        self._print_summary()
        
        return {
            'results': self.results,
            'coverage': self.coverage_data,
            'performance': self.performance_metrics,
            'report_path': str(output_path / "test_report.json"),
            'duration': time.time() - self.start_time
        }
    
    def _run_category(
        self,
        category: str,
        parallel: bool,
        coverage: bool,
        verbose: bool,
        benchmark: bool,
        output_dir: Path
    ) -> Dict[str, Any]:
        """Run tests for a specific category."""
        category_start = time.time()
        
        # Build pytest command
        cmd = ["python", "-m", "pytest"]
        
        # Add test directory for category
        test_path = self._get_test_path(category)
        if test_path.exists():
            cmd.append(str(test_path))
        else:
            print(f"⚠️  Warning: Test path {test_path} does not exist")
            return {'status': 'skipped', 'reason': 'path_not_found'}
        
        # Add markers
        cmd.extend(["-m", category])
        
        # Add coverage if requested
        if coverage:
            cmd.extend([
                "--cov=heygen_ai",
                "--cov-report=html:" + str(output_dir / f"coverage_{category}"),
                "--cov-report=xml:" + str(output_dir / f"coverage_{category}.xml"),
                "--cov-report=term-missing"
            ])
        
        # Add parallel execution
        if parallel:
            cmd.extend(["-n", "auto"])
        
        # Add verbose output
        if verbose:
            cmd.append("-v")
        else:
            cmd.append("-q")
        
        # Add benchmark if requested
        if benchmark and category in ['unit', 'performance']:
            cmd.append("--benchmark-only")
            cmd.append("--benchmark-json=" + str(output_dir / f"benchmark_{category}.json"))
        
        # Add output files
        cmd.extend([
            "--junitxml=" + str(output_dir / f"junit_{category}.xml"),
            "--html=" + str(output_dir / f"report_{category}.html"),
            "--self-contained-html"
        ])
        
        # Add timeout
        cmd.extend(["--timeout=300"])
        
        # Run tests
        try:
            print(f"   Command: {' '.join(cmd)}")
            result = subprocess.run(
                cmd,
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=1800  # 30 minutes max
            )
            
            duration = time.time() - category_start
            
            # Parse results
            return {
                'status': 'passed' if result.returncode == 0 else 'failed',
                'returncode': result.returncode,
                'duration': duration,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'command': ' '.join(cmd)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': 'timeout',
                'duration': time.time() - category_start,
                'error': 'Test execution timed out'
            }
        except Exception as e:
            return {
                'status': 'error',
                'duration': time.time() - category_start,
                'error': str(e)
            }
    
    def _get_test_path(self, category: str) -> Path:
        """Get the test path for a category."""
        if category == 'unit':
            return self.tests_dir / "unit"
        elif category == 'integration':
            return self.tests_dir / "integration"
        elif category == 'performance':
            return self.tests_dir / "performance"
        elif category == 'e2e':
            return self.tests_dir / "e2e"
        else:
            return self.tests_dir
    
    def _generate_report(self, output_dir: Path) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'duration': time.time() - self.start_time,
            'results': self.results,
            'summary': self._calculate_summary(),
            'environment': self._get_environment_info(),
            'coverage': self._collect_coverage_data(output_dir),
            'performance': self._collect_performance_data(output_dir)
        }
        
        # Save report
        report_file = output_dir / "test_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report, output_dir)
        
        return report
    
    def _calculate_summary(self) -> Dict[str, Any]:
        """Calculate test summary statistics."""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        skipped_tests = 0
        total_duration = 0
        
        for category, result in self.results.items():
            if result.get('status') == 'passed':
                passed_tests += 1
            elif result.get('status') == 'failed':
                failed_tests += 1
            elif result.get('status') == 'skipped':
                skipped_tests += 1
            
            total_duration += result.get('duration', 0)
            total_tests += 1
        
        return {
            'total_categories': total_tests,
            'passed_categories': passed_tests,
            'failed_categories': failed_tests,
            'skipped_categories': skipped_tests,
            'total_duration': total_duration,
            'success_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _get_environment_info(self) -> Dict[str, Any]:
        """Collect environment information."""
        
        return {
            'python_version': sys.version,
            'platform': platform.platform(),
            'architecture': platform.architecture(),
            'processor': platform.processor(),
            'working_directory': str(Path.cwd()),
            'project_root': str(self.project_root)
        }
    
    def _collect_coverage_data(self, output_dir: Path) -> Dict[str, Any]:
        """Collect coverage data from reports."""
        coverage_data = {}
        
        for category in self.results.keys():
            coverage_file = output_dir / f"coverage_{category}.xml"
            if coverage_file.exists():
                # Parse coverage XML (simplified)
                coverage_data[category] = {
                    'file': str(coverage_file),
                    'exists': True
                }
        
        return coverage_data
    
    def _collect_performance_data(self, output_dir: Path) -> Dict[str, Any]:
        """Collect performance benchmark data."""
        performance_data = {}
        
        for category in self.results.keys():
            benchmark_file = output_dir / f"benchmark_{category}.json"
            if benchmark_file.exists():
                try:
                    with open(benchmark_file, 'r') as f:
                        data = json.load(f)
                        performance_data[category] = data
                except Exception as e:
                    performance_data[category] = {'error': str(e)}
        
        return performance_data
    
    def _generate_html_report(self, report: Dict[str, Any], output_dir: Path):
        """Generate HTML report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>HeyGen AI Test Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
        .summary {{ margin: 20px 0; }}
        .category {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }}
        .passed {{ background-color: #d4edda; }}
        .failed {{ background-color: #f8d7da; }}
        .skipped {{ background-color: #fff3cd; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
        .metric {{ padding: 10px; background-color: #e9ecef; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 HeyGen AI Test Report</h1>
        <p>Generated: {report['timestamp']}</p>
        <p>Duration: {report['duration']:.2f} seconds</p>
    </div>
    
    <div class="summary">
        <h2>📊 Summary</h2>
        <div class="metrics">
            <div class="metric">
                <strong>Total Categories:</strong> {report['summary']['total_categories']}
            </div>
            <div class="metric">
                <strong>Success Rate:</strong> {report['summary']['success_rate']:.1f}%
            </div>
            <div class="metric">
                <strong>Passed:</strong> {report['summary']['passed_categories']}
            </div>
            <div class="metric">
                <strong>Failed:</strong> {report['summary']['failed_categories']}
            </div>
        </div>
    </div>
    
    <div class="results">
        <h2>🧪 Test Results</h2>
"""
        
        for category, result in report['results'].items():
            status_class = result.get('status', 'unknown')
            html_content += f"""
        <div class="category {status_class}">
            <h3>{category.title()} Tests</h3>
            <p><strong>Status:</strong> {result.get('status', 'unknown')}</p>
            <p><strong>Duration:</strong> {result.get('duration', 0):.2f}s</p>
            {f'<p><strong>Error:</strong> {result.get("error", "")}</p>' if result.get('error') else ''}
        </div>
"""
        
        html_content += """
    </div>
</body>
</html>
"""
        
        html_file = output_dir / "test_report.html"
        with open(html_file, 'w') as f:
            f.write(html_content)
    
    def _print_summary(self) -> Any:
        """Print test execution summary."""
        summary = self._calculate_summary()
        total_duration = time.time() - self.start_time
        
        print("\n" + "=" * 50)
        print("📊 TEST EXECUTION SUMMARY")
        print("=" * 50)
        print(f"Total Duration: {total_duration:.2f}s")
        print(f"Categories Run: {summary['total_categories']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"✅ Passed: {summary['passed_categories']}")
        print(f"❌ Failed: {summary['failed_categories']}")
        print(f"⏭️  Skipped: {summary['skipped_categories']}")
        print("=" * 50)
        
        # Print detailed results
        for category, result in self.results.items():
            status_icon = {
                'passed': '✅',
                'failed': '❌',
                'skipped': '⏭️',
                'timeout': '⏰',
                'error': '💥'
            }.get(result.get('status'), '❓')
            
            print(f"{status_icon} {category}: {result.get('status', 'unknown')} "
                  f"({result.get('duration', 0):.2f}s)")


def main():
    """Main entry point for test runner."""
    parser = argparse.ArgumentParser(
        description="HeyGen AI Testing Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    # Test categories
    parser.add_argument('--unit', action='store_true', help='Run unit tests')
    parser.add_argument('--integration', action='store_true', help='Run integration tests')
    parser.add_argument('--performance', action='store_true', help='Run performance tests')
    parser.add_argument('--e2e', action='store_true', help='Run end-to-end tests')
    parser.add_argument('--all', action='store_true', help='Run all test categories')
    
    # Execution options
    parser.add_argument('--parallel', action='store_true', help='Enable parallel execution')
    parser.add_argument('--coverage', action='store_true', help='Enable coverage reporting')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--benchmark', action='store_true', help='Enable performance benchmarking')
    
    # Output options
    parser.add_argument('--output-dir', type=str, help='Output directory for reports')
    parser.add_argument('--no-report', action='store_true', help='Skip report generation')
    
    # CI/CD options
    parser.add_argument('--ci', action='store_true', help='CI/CD mode (optimized for automation)')
    parser.add_argument('--fail-fast', action='store_true', help='Stop on first failure')
    
    args = parser.parse_args()
    
    # Determine categories to run
    categories = []
    if args.unit or args.all:
        categories.append('unit')
    if args.integration or args.all:
        categories.append('integration')
    if args.performance or args.all:
        categories.append('performance')
    if args.e2e or args.all:
        categories.append('e2e')
    
    # Default to unit tests if nothing specified
    if not categories:
        categories = ['unit']
    
    # CI mode adjustments
    if args.ci:
        args.parallel = True
        args.coverage = True
        if not args.output_dir:
            args.output_dir = "ci_reports"
    
    # Create and run test runner
    runner = TestRunner()
    
    try:
        results = runner.run_tests(
            categories=categories,
            parallel=args.parallel,
            coverage=args.coverage,
            verbose=args.verbose,
            benchmark=args.benchmark,
            output_dir=args.output_dir
        )
        
        # Exit with appropriate code
        summary = results.get('results', {})
        failed_categories = [cat for cat, result in summary.items() 
                           if result.get('status') in ['failed', 'error', 'timeout']]
        
        if failed_categories:
            print(f"\n❌ Tests failed in categories: {', '.join(failed_categories)}")
            sys.exit(1)
        else:
            print("\n✅ All tests passed!")
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n⚠️  Test execution interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Test runner error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()