#!/usr/bin/env python3
"""
Enhanced Performance Monitor Demo v3.7
Demonstrates the capabilities of the new performance monitoring system
"""

import asyncio
import time
import random
import json
import logging
from pathlib import Path
from typing import Dict, Any

# Import the enhanced performance monitor
from performance_monitor_v3_7 import (
    EnhancedPerformanceMonitor, 
    PerformanceThreshold, 
    create_performance_monitor
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerformanceMonitorDemo:
    """Demo class for the Enhanced Performance Monitor"""
    
    def __init__(self):
        self.monitor = None
        self.demo_services = {}
        self.running = False
        
    async def setup_monitor(self):
        """Set up the performance monitor with demo configuration"""
        logger.info("Setting up Enhanced Performance Monitor...")
        
        # Create configuration
        config = {
            'monitoring_interval': 2.0,  # Faster for demo
            'auto_scaling_enabled': True,
            'scaling_thresholds': {
                'cpu_usage': {'scale_up_threshold': 70, 'scale_down_threshold': 30},
                'memory_usage': {'scale_up_threshold': 75, 'scale_down_threshold': 25},
                'demo_metric': {'scale_up_threshold': 80, 'scale_down_threshold': 20}
            }
        }
        
        # Create monitor instance
        self.monitor = create_performance_monitor(config)
        
        # Add custom thresholds for demo
        self._add_demo_thresholds()
        
        # Set up demo services
        self._setup_demo_services()
        
        logger.info("Performance Monitor setup complete!")
        
    def _add_demo_thresholds(self):
        """Add demo-specific performance thresholds"""
        demo_thresholds = [
            PerformanceThreshold("demo_metric", 60.0, 80.0, ">", True, "auto_scale"),
            PerformanceThreshold("response_time", 500.0, 2000.0, ">", True, "alert"),
            PerformanceThreshold("error_rate", 2.0, 8.0, ">", True, "alert"),
        ]
        
        for threshold in demo_thresholds:
            self.monitor.add_threshold(threshold)
            logger.info(f"Added demo threshold: {threshold.metric_name}")
    
    def _setup_demo_services(self):
        """Set up demo services for monitoring"""
        # Web API service
        web_api_metrics = {
            'response_time': {
                'description': 'API response time',
                'unit': 'milliseconds',
                'labels': {'service': 'web_api', 'endpoint': 'demo'}
            },
            'request_count': {
                'description': 'Number of requests',
                'unit': 'count',
                'labels': {'service': 'web_api'}
            },
            'error_count': {
                'description': 'Number of errors',
                'unit': 'count',
                'labels': {'service': 'web_api'}
            }
        }
        
        self.monitor.add_service_monitoring('web_api', web_api_metrics)
        
        # Database service
        db_metrics = {
            'query_time': {
                'description': 'Database query time',
                'unit': 'milliseconds',
                'labels': {'service': 'database'}
            },
            'connection_count': {
                'description': 'Database connections',
                'unit': 'count',
                'labels': {'service': 'database'}
            }
        }
        
        self.monitor.add_service_monitoring('database', db_metrics)
        
        # Background worker service
        worker_metrics = {
            'job_queue_size': {
                'description': 'Jobs in queue',
                'unit': 'count',
                'labels': {'service': 'background_worker'}
            },
            'job_processing_time': {
                'description': 'Job processing time',
                'unit': 'seconds',
                'labels': {'service': 'background_worker'}
            }
        }
        
        self.monitor.add_service_monitoring('background_worker', worker_metrics)
        
        logger.info("Demo services configured for monitoring")
    
    async def start_demo(self):
        """Start the performance monitoring demo"""
        if not self.monitor:
            logger.error("Monitor not set up. Call setup_monitor() first.")
            return
        
        logger.info("Starting Performance Monitor Demo...")
        
        # Start monitoring
        self.monitor.start_monitoring()
        self.running = True
        
        # Start demo data generation
        demo_tasks = [
            asyncio.create_task(self._generate_web_api_metrics()),
            asyncio.create_task(self._generate_database_metrics()),
            asyncio.create_task(self._generate_worker_metrics()),
            asyncio.create_task(self._generate_demo_metrics()),
            asyncio.create_task(self._display_status())
        ]
        
        try:
            # Run demo for specified duration
            await asyncio.gather(*demo_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in demo: {e}")
        finally:
            await self.stop_demo()
    
    async def stop_demo(self):
        """Stop the performance monitoring demo"""
        if not self.running:
            return
        
        logger.info("Stopping Performance Monitor Demo...")
        self.running = False
        
        if self.monitor:
            self.monitor.stop_monitoring()
        
        logger.info("Demo stopped")
    
    async def _generate_web_api_metrics(self):
        """Generate simulated web API metrics"""
        request_count = 0
        error_count = 0
        
        while self.running:
            try:
                # Simulate varying load
                base_load = 50 + random.randint(-20, 30)
                response_time = base_load + random.randint(0, 200)
                
                # Simulate occasional errors
                if random.random() < 0.05:  # 5% error rate
                    error_count += 1
                    response_time += random.randint(100, 500)
                
                request_count += 1
                
                # Record metrics
                self.monitor.record_service_metric('web_api', 'response_time', response_time)
                self.monitor.record_service_metric('web_api', 'request_count', request_count)
                self.monitor.record_service_metric('web_api', 'error_count', error_count)
                
                # Simulate varying request patterns
                await asyncio.sleep(random.uniform(0.5, 2.0))
                
            except Exception as e:
                logger.error(f"Error generating web API metrics: {e}")
                await asyncio.sleep(1)
    
    async def _generate_database_metrics(self):
        """Generate simulated database metrics"""
        while self.running:
            try:
                # Simulate database query times
                query_time = random.randint(10, 150)
                connection_count = random.randint(5, 25)
                
                # Record metrics
                self.monitor.record_service_metric('database', 'query_time', query_time)
                self.monitor.record_service_metric('database', 'connection_count', connection_count)
                
                await asyncio.sleep(random.uniform(1.0, 3.0))
                
            except Exception as e:
                logger.error(f"Error generating database metrics: {e}")
                await asyncio.sleep(1)
    
    async def _generate_worker_metrics(self):
        """Generate simulated background worker metrics"""
        while self.running:
            try:
                # Simulate job queue and processing
                queue_size = random.randint(0, 50)
                processing_time = random.uniform(0.1, 5.0)
                
                # Record metrics
                self.monitor.record_service_metric('background_worker', 'job_queue_size', queue_size)
                self.monitor.record_service_metric('background_worker', 'job_processing_time', processing_time)
                
                await asyncio.sleep(random.uniform(2.0, 5.0))
                
            except Exception as e:
                logger.error(f"Error generating worker metrics: {e}")
                await asyncio.sleep(1)
    
    async def _generate_demo_metrics(self):
        """Generate demo metrics for threshold testing"""
        while self.running:
            try:
                # Generate varying demo metric values
                demo_value = random.uniform(20, 90)
                
                # Record in performance history for threshold checking
                self.monitor.performance_history['demo_metric'].append({
                    'timestamp': time.time(),
                    'value': demo_value
                })
                
                await asyncio.sleep(random.uniform(1.0, 4.0))
                
            except Exception as e:
                logger.error(f"Error generating demo metrics: {e}")
                await asyncio.sleep(1)
    
    async def _display_status(self):
        """Display periodic status updates"""
        while self.running:
            try:
                await asyncio.sleep(10)  # Update every 10 seconds
                
                if self.monitor:
                    # Get current status
                    summary = self.monitor.get_performance_summary(window_seconds=60)
                    
                    # Display key metrics
                    print("\n" + "="*60)
                    print("PERFORMANCE MONITOR STATUS UPDATE")
                    print("="*60)
                    
                    # System metrics
                    if summary['system_metrics']:
                        print("\nSYSTEM METRICS:")
                        for name, data in summary['system_metrics'].items():
                            if data['statistics']:
                                latest = data['statistics'].get('latest', 'N/A')
                                print(f"  {name}: {latest} {data['unit']}")
                    
                    # Service metrics
                    if summary['service_metrics']:
                        print("\nSERVICE METRICS:")
                        for service_name, service_data in summary['service_metrics'].items():
                            if service_data['metrics']:
                                print(f"  {service_name}:")
                                for metric_name, metric_data in service_data['metrics'].items():
                                    if metric_data['statistics']:
                                        latest = metric_data['statistics'].get('latest', 'N/A')
                                        print(f"    {metric_name}: {latest} {metric_data['unit']}")
                    
                    # Threshold status
                    threshold_status = self.monitor.get_threshold_status()
                    if threshold_status:
                        print("\nTHRESHOLD STATUS:")
                        for name, status in threshold_status.items():
                            current = status.get('current_value', 'N/A')
                            threshold_status_val = status.get('status', 'unknown')
                            print(f"  {name}: {current} ({threshold_status_val})")
                    
                    # Recent alerts
                    recent_alerts = self.monitor.get_alert_history(window_seconds=60)
                    if recent_alerts:
                        print(f"\nRECENT ALERTS ({len(recent_alerts)}):")
                        for alert in recent_alerts[-3:]:  # Show last 3 alerts
                            print(f"  [{alert['severity'].upper()}] {alert['message']}")
                    
                    print("="*60)
                
            except Exception as e:
                logger.error(f"Error displaying status: {e}")
                await asyncio.sleep(5)
    
    async def run_demo_scenarios(self):
        """Run various demo scenarios"""
        logger.info("Running demo scenarios...")
        
        # Scenario 1: Normal operation
        logger.info("Scenario 1: Normal operation (30 seconds)")
        await asyncio.sleep(30)
        
        # Scenario 2: High load simulation
        logger.info("Scenario 2: High load simulation (20 seconds)")
        await self._simulate_high_load()
        await asyncio.sleep(20)
        
        # Scenario 3: Error condition simulation
        logger.info("Scenario 3: Error condition simulation (20 seconds)")
        await self._simulate_error_conditions()
        await asyncio.sleep(20)
        
        # Scenario 4: Recovery simulation
        logger.info("Scenario 4: Recovery simulation (20 seconds)")
        await self._simulate_recovery()
        await asyncio.sleep(20)
        
        logger.info("Demo scenarios completed!")
    
    async def _simulate_high_load(self):
        """Simulate high system load"""
        logger.info("Simulating high system load...")
        
        # Generate high CPU and memory usage metrics
        for _ in range(10):
            high_cpu = random.uniform(75, 95)
            high_memory = random.uniform(80, 98)
            
            # Record high values
            self.monitor.performance_history['cpu_usage'].append({
                'timestamp': time.time(),
                'value': high_cpu
            })
            
            self.monitor.performance_history['memory_usage'].append({
                'timestamp': time.time(),
                'value': high_memory
            })
            
            await asyncio.sleep(0.5)
    
    async def _simulate_error_conditions(self):
        """Simulate error conditions"""
        logger.info("Simulating error conditions...")
        
        # Generate high error rates and response times
        for _ in range(8):
            high_error_rate = random.uniform(8, 20)
            high_response_time = random.uniform(2000, 8000)
            
            # Record error conditions
            self.monitor.performance_history['error_rate'].append({
                'timestamp': time.time(),
                'value': high_error_rate
            })
            
            self.monitor.performance_history['response_time'].append({
                'timestamp': time.time(),
                'value': high_response_time
            })
            
            await asyncio.sleep(0.5)
    
    async def _simulate_recovery(self):
        """Simulate system recovery"""
        logger.info("Simulating system recovery...")
        
        # Generate normal values
        for _ in range(10):
            normal_cpu = random.uniform(20, 50)
            normal_memory = random.uniform(30, 60)
            normal_error_rate = random.uniform(0, 3)
            
            # Record recovery values
            self.monitor.performance_history['cpu_usage'].append({
                'timestamp': time.time(),
                'value': normal_cpu
            })
            
            self.monitor.performance_history['memory_usage'].append({
                'timestamp': time.time(),
                'value': normal_memory
            })
            
            self.monitor.performance_history['error_rate'].append({
                'timestamp': time.time(),
                'value': normal_error_rate
            })
            
            await asyncio.sleep(0.5)
    
    def export_demo_results(self):
        """Export demo results for analysis"""
        if not self.monitor:
            logger.error("Monitor not available for export")
            return
        
        try:
            # Create exports directory
            exports_dir = Path("./demo_exports")
            exports_dir.mkdir(exist_ok=True)
            
            # Export comprehensive summary
            summary = self.monitor.get_performance_summary()
            
            # Export as JSON
            json_file = exports_dir / "demo_performance_summary.json"
            with open(json_file, 'w') as f:
                json.dump(summary, f, indent=2, default=str)
            
            # Export as CSV
            csv_file = exports_dir / "demo_performance_summary.csv"
            csv_data = self.monitor.export_metrics("csv", str(csv_file))
            
            # Export threshold status
            threshold_status = self.monitor.get_threshold_status()
            threshold_file = exports_dir / "threshold_status.json"
            with open(threshold_file, 'w') as f:
                json.dump(threshold_status, f, indent=2, default=str)
            
            # Export alert history
            alert_history = self.monitor.get_alert_history()
            alert_file = exports_dir / "alert_history.json"
            with open(alert_file, 'w') as f:
                json.dump(alert_history, f, indent=2, default=str)
            
            logger.info(f"Demo results exported to {exports_dir}")
            logger.info(f"Files created:")
            logger.info(f"  - {json_file}")
            logger.info(f"  - {csv_file}")
            logger.info(f"  - {threshold_file}")
            logger.info(f"  - {alert_file}")
            
        except Exception as e:
            logger.error(f"Error exporting demo results: {e}")


async def main():
    """Main demo function"""
    print("Enhanced Performance Monitor Demo v3.7")
    print("=" * 50)
    
    # Create demo instance
    demo = PerformanceMonitorDemo()
    
    try:
        # Set up monitor
        await demo.setup_monitor()
        
        # Run demo scenarios
        await demo.run_demo_scenarios()
        
        # Export results
        demo.export_demo_results()
        
        # Display final summary
        if demo.monitor:
            print("\n" + "="*60)
            print("FINAL PERFORMANCE SUMMARY")
            print("="*60)
            
            final_summary = demo.monitor.get_performance_summary()
            
            # Show key statistics
            if final_summary['system_metrics']:
                print("\nSYSTEM PERFORMANCE:")
                for name, data in final_summary['system_metrics'].items():
                    if data['statistics']:
                        stats = data['statistics']
                        print(f"  {name}:")
                        print(f"    Min: {stats.get('min', 'N/A')}")
                        print(f"    Max: {stats.get('max', 'N/A')}")
                        print(f"    Mean: {stats.get('mean', 'N/A'):.2f}")
                        print(f"    Latest: {stats.get('latest', 'N/A')}")
            
            # Show alert summary
            alert_history = demo.monitor.get_alert_history()
            if alert_history:
                print(f"\nTOTAL ALERTS: {len(alert_history)}")
                
                # Count by severity
                severity_counts = {}
                for alert in alert_history:
                    severity = alert.get('severity', 'unknown')
                    severity_counts[severity] = severity_counts.get(severity, 0) + 1
                
                for severity, count in severity_counts.items():
                    print(f"  {severity.upper()}: {count}")
            
            print("="*60)
        
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Demo error: {e}")
    finally:
        # Clean up
        await demo.stop_demo()
        print("\nDemo completed!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
