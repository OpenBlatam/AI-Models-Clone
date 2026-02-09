#!/usr/bin/env python3
"""
Test Runner for Enhanced Quantum Neural Optimization System v10.0.0
Part of the "mejora" comprehensive improvement plan

This script provides an easy way to run different types of tests:
- Unit tests only
- Performance tests only
- All tests
- Specific test categories
"""

import sys
import os
import argparse
import subprocess
import json
from datetime import datetime

def run_unit_tests():
    """Run unit tests only"""
    print("🧪 Running Unit Tests Only")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "pytest", "test_enhanced_quantum_neural_demo.py", 
           "-k", "TestEnhancedQuantumNeuralDemo", "-v"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_performance_tests():
    """Run performance tests only"""
    print("🚀 Running Performance Tests Only")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "pytest", "test_enhanced_quantum_neural_demo.py", 
           "-k", "TestPerformanceBenchmarks", "-v"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests only"""
    print("🔗 Running Integration Tests Only")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "pytest", "test_enhanced_quantum_neural_demo.py", 
           "-k", "TestIntegrationTests", "-v"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_edge_case_tests():
    """Run edge case tests only"""
    print("🔍 Running Edge Case Tests Only")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "pytest", "test_enhanced_quantum_neural_demo.py", 
           "-k", "TestEdgeCases", "-v"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_all_tests():
    """Run all tests"""
    print("🎯 Running All Tests")
    print("=" * 50)
    
    cmd = [sys.executable, "test_enhanced_quantum_neural_demo.py"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def run_quick_tests():
    """Run quick tests (unit tests only)"""
    print("⚡ Running Quick Tests (Unit Tests Only)")
    print("=" * 50)
    
    cmd = [sys.executable, "-m", "pytest", "test_enhanced_quantum_neural_demo.py", 
           "-k", "TestEnhancedQuantumNeuralDemo", "-v", "--tb=short"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("Errors:", result.stderr)
    
    return result.returncode == 0

def generate_test_report():
    """Generate a comprehensive test report"""
    print("📊 Generating Test Report")
    print("=" * 50)
    
    # Check if test results file exists
    if os.path.exists('enhanced_quantum_neural_test_results.json'):
        with open('enhanced_quantum_neural_test_results.json', 'r') as f:
            results = json.load(f)
        
        print("📋 Test Report Summary:")
        print(f"   Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Unit Tests Success Rate: {results['unit_tests']['success_rate']:.1f}%")
        print(f"   Unit Tests Run: {results['unit_tests']['tests_run']}")
        print(f"   Unit Tests Failures: {results['unit_tests']['failures']}")
        print(f"   Unit Tests Errors: {results['unit_tests']['errors']}")
        
        if 'performance_tests' in results:
            perf = results['performance_tests']
            print(f"   Total Performance Time: {perf['total_time']:.4f}s")
            print(f"   Average Feature Time: {perf['total_time']/6:.4f}s")
        
        # Save detailed report
        report = {
            'timestamp': datetime.now().isoformat(),
            'test_results': results,
            'summary': {
                'overall_success': results['unit_tests']['success_rate'] > 90,
                'recommendations': []
            }
        }
        
        if results['unit_tests']['success_rate'] < 90:
            report['summary']['recommendations'].append("Consider fixing failing tests")
        
        if 'performance_tests' in results and results['performance_tests']['total_time'] > 10:
            report['summary']['recommendations'].append("Performance optimization needed")
        
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Detailed report saved to 'test_report.json'")
    else:
        print("❌ No test results found. Run tests first.")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description='Enhanced Quantum Neural Demo Test Runner')
    parser.add_argument('--type', choices=['unit', 'performance', 'integration', 'edge', 'all', 'quick'], 
                       default='all', help='Type of tests to run')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    print("🚀 Enhanced Quantum Neural Demo Test Runner")
    print("=" * 60)
    print(f"Test Type: {args.type}")
    print(f"Verbose: {args.verbose}")
    print("=" * 60)
    
    success = False
    
    try:
        if args.type == 'unit':
            success = run_unit_tests()
        elif args.type == 'performance':
            success = run_performance_tests()
        elif args.type == 'integration':
            success = run_integration_tests()
        elif args.type == 'edge':
            success = run_edge_case_tests()
        elif args.type == 'quick':
            success = run_quick_tests()
        else:  # all
            success = run_all_tests()
        
        if args.report:
            generate_test_report()
        
        if success:
            print("\n✅ All tests passed successfully!")
            return 0
        else:
            print("\n❌ Some tests failed!")
            return 1
            
    except Exception as e:
        print(f"\n💥 Error running tests: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
