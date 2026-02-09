#!/usr/bin/env python3
"""
Comprehensive Test Script for Refactored Enhanced Blaze AI System

This script validates all components of the refactored system including:
- Core modules (config, logging, exceptions)
- Enhanced features (security, monitoring, rate limiting, error handling)
- API components (routes, middleware)
- Health monitoring
- Configuration loading
- System integration
"""

import asyncio
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def print_header(title: str):
    """Print a formatted header."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_section(title: str):
    """Print a formatted section."""
    print(f"\n{'-'*40}")
    print(f"  {title}")
    print(f"{'-'*40}")

def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"    {details}")

class SystemValidator:
    """Comprehensive system validator for the refactored Blaze AI."""
    
    def __init__(self):
        self.results = []
        self.start_time = time.time()
        
    def add_result(self, test_name: str, success: bool, details: str = ""):
        """Add a test result."""
        self.results.append({
            "test": test_name,
            "success": success,
            "details": details
        })
        print_result(test_name, success, details)
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test summary."""
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["success"])
        failed_tests = total_tests - passed_tests
        
        return {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "execution_time": time.time() - self.start_time,
            "results": self.results
        }
    
    def print_summary(self):
        """Print test summary."""
        summary = self.get_summary()
        
        print_header("TEST SUMMARY")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']} ✅")
        print(f"Failed: {summary['failed']} ❌")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Execution Time: {summary['execution_time']:.2f}s")
        
        if summary['failed'] > 0:
            print("\nFailed Tests:")
            for result in self.results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
    
    async def run_all_tests(self):
        """Run all system tests."""
        print_header("REFACTORED ENHANCED BLAZE AI SYSTEM VALIDATION")
        print("Starting comprehensive system validation...")
        
        # Test core modules
        await self.test_core_modules()
        
        # Test enhanced features
        await self.test_enhanced_features()
        
        # Test API components
        await self.test_api_components()
        
        # Test configuration
        await self.test_configuration()
        
        # Test system integration
        await self.test_system_integration()
        
        # Test health monitoring
        await self.test_health_monitoring()
        
        # Print final summary
        self.print_summary()
    
    async def test_core_modules(self):
        """Test core modules."""
        print_section("Testing Core Modules")
        
        # Test config module
        try:
            from core.config import AppConfig, load_config
            self.add_result("Core Config Import", True, "Successfully imported config module")
            
            # Test configuration loading
            config = load_config()
            self.add_result("Configuration Loading", True, f"Loaded config with {len(config.dict())} settings")
            
        except Exception as e:
            self.add_result("Core Config Module", False, f"Import failed: {e}")
        
        # Test logging module
        try:
            from core.logging import setup_logging, get_logger
            self.add_result("Core Logging Import", True, "Successfully imported logging module")
            
            # Test logger creation
            logger = get_logger("test")
            self.add_result("Logger Creation", True, "Successfully created logger instance")
            
        except Exception as e:
            self.add_result("Core Logging Module", False, f"Import failed: {e}")
        
        # Test exceptions module
        try:
            from core.exceptions import BlazeAIError, ServiceUnavailableError, ValidationError
            self.add_result("Core Exceptions Import", True, "Successfully imported exceptions module")
            
            # Test exception creation
            error = BlazeAIError("Test error", error_type="test_error")
            self.add_result("Exception Creation", True, "Successfully created exception instance")
            
        except Exception as e:
            self.add_result("Core Exceptions Module", False, f"Import failed: {e}")
    
    async def test_enhanced_features(self):
        """Test enhanced features modules."""
        print_section("Testing Enhanced Features")
        
        # Test security module
        try:
            from enhanced_features.security import SecurityMiddleware, SecurityConfig
            self.add_result("Security Module Import", True, "Successfully imported security module")
            
            # Test security config creation
            security_config = SecurityConfig(
                jwt_secret_key="test-key",
                jwt_algorithm="HS256",
                jwt_expiration_minutes=30
            )
            self.add_result("Security Config Creation", True, "Successfully created security config")
            
        except Exception as e:
            self.add_result("Security Module", False, f"Import failed: {e}")
        
        # Test monitoring module
        try:
            from enhanced_features.monitoring import PerformanceMonitor, MonitoringConfig
            self.add_result("Monitoring Module Import", True, "Successfully imported monitoring module")
            
            # Test monitoring config creation
            monitoring_config = MonitoringConfig(
                metrics_enabled=True,
                system_metrics_enabled=True,
                profiling_enabled=True
            )
            self.add_result("Monitoring Config Creation", True, "Successfully created monitoring config")
            
        except Exception as e:
            self.add_result("Monitoring Module", False, f"Import failed: {e}")
        
        # Test rate limiting module
        try:
            from enhanced_features.rate_limiting import RateLimiter, RateLimitConfig
            self.add_result("Rate Limiting Module Import", True, "Successfully imported rate limiting module")
            
            # Test rate limit config creation
            rate_limit_config = RateLimitConfig(
                default_limit=100,
                default_window=60,
                storage_type="memory"
            )
            self.add_result("Rate Limiting Config Creation", True, "Successfully created rate limit config")
            
        except Exception as e:
            self.add_result("Rate Limiting Module", False, f"Import failed: {e}")
        
        # Test error handling module
        try:
            from enhanced_features.error_handling import ErrorHandlingOrchestrator, ErrorHandlingConfig
            self.add_result("Error Handling Module Import", True, "Successfully imported error handling module")
            
            # Test error handling config creation
            error_config = ErrorHandlingConfig(
                circuit_breaker_enabled=True,
                retry_enabled=True,
                max_retries=3
            )
            self.add_result("Error Handling Config Creation", True, "Successfully created error handling config")
            
        except Exception as e:
            self.add_result("Error Handling Module", False, f"Import failed: {e}")
        
        # Test health module
        try:
            from enhanced_features.health import SystemHealth, HealthChecker
            self.add_result("Health Module Import", True, "Successfully imported health module")
            
            # Test health checker creation
            health_checker = HealthChecker()
            self.add_result("Health Checker Creation", True, "Successfully created health checker")
            
        except Exception as e:
            self.add_result("Health Module", False, f"Import failed: {e}")
    
    async def test_api_components(self):
        """Test API components."""
        print_section("Testing API Components")
        
        # Test API routes
        try:
            from api.routes import create_api_router
            router = create_api_router()
            self.add_result("API Router Creation", True, f"Created router with {len(router.routes)} routes")
            
        except Exception as e:
            self.add_result("API Router Module", False, f"Creation failed: {e}")
        
        # Test API middleware
        try:
            from api.middleware import create_middleware_stack
            middleware_stack = create_middleware_stack()
            self.add_result("API Middleware Creation", True, f"Created middleware stack with {len(middleware_stack)} components")
            
        except Exception as e:
            self.add_result("API Middleware Module", False, f"Creation failed: {e}")
    
    async def test_configuration(self):
        """Test configuration system."""
        print_section("Testing Configuration System")
        
        # Test YAML configuration file
        config_file = Path("config.yaml")
        if config_file.exists():
            self.add_result("Configuration File", True, "config.yaml exists")
            
            # Test configuration content
            try:
                import yaml
                with open(config_file, 'r') as f:
                    config_data = yaml.safe_load(f)
                
                required_sections = ['server', 'logging', 'security', 'rate_limiting', 'monitoring']
                missing_sections = [section for section in required_sections if section not in config_data]
                
                if not missing_sections:
                    self.add_result("Configuration Content", True, f"All required sections present: {', '.join(required_sections)}")
                else:
                    self.add_result("Configuration Content", False, f"Missing sections: {', '.join(missing_sections)}")
                    
            except Exception as e:
                self.add_result("Configuration Parsing", False, f"Failed to parse config: {e}")
        else:
            self.add_result("Configuration File", False, "config.yaml not found")
    
    async def test_system_integration(self):
        """Test system integration."""
        print_section("Testing System Integration")
        
        # Test main application creation
        try:
            from main import create_app
            self.add_result("Main App Import", True, "Successfully imported main module")
            
            # Test app creation (without starting server)
            try:
                app = create_app()
                self.add_result("Application Creation", True, "Successfully created FastAPI application")
                
                # Check if enhanced features are available
                if hasattr(app, 'state') and hasattr(app.state, 'enhanced_features'):
                    self.add_result("Enhanced Features Integration", True, "Enhanced features integrated into app")
                else:
                    self.add_result("Enhanced Features Integration", False, "Enhanced features not properly integrated")
                    
            except Exception as e:
                self.add_result("Application Creation", False, f"Failed to create app: {e}")
                
        except Exception as e:
            self.add_result("Main Module Import", False, f"Import failed: {e}")
    
    async def test_health_monitoring(self):
        """Test health monitoring system."""
        print_section("Testing Health Monitoring")
        
        try:
            from enhanced_features.health import SystemHealth
            
            # Create health monitor
            health_monitor = SystemHealth()
            
            # Test system health check
            health_data = await health_monitor.get_system_health()
            
            if health_data and 'overall_status' in health_data:
                self.add_result("System Health Check", True, f"Health status: {health_data['overall_status']}")
            else:
                self.add_result("System Health Check", False, "Health check returned invalid data")
                
            # Test service health check
            service_health = await health_monitor.get_service_health("api")
            if service_health and 'name' in service_health:
                self.add_result("Service Health Check", True, f"Service: {service_health['name']}")
            else:
                self.add_result("Service Health Check", False, "Service health check failed")
                
        except Exception as e:
            self.add_result("Health Monitoring System", False, f"Health monitoring failed: {e}")

async def main():
    """Main test execution function."""
    validator = SystemValidator()
    
    try:
        await validator.run_all_tests()
        
        # Save results to file
        summary = validator.get_summary()
        with open("test_results.json", "w") as f:
            json.dump(summary, f, indent=2, default=str)
        
        print(f"\nTest results saved to: test_results.json")
        
        # Exit with appropriate code
        if summary['failed'] > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
