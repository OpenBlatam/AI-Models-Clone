#!/usr/bin/env python3
"""
HeyGen AI Intelligent Monitor Demo v4.0
Demonstrates advanced AI-powered monitoring and optimization for HeyGen AI systems
"""

import asyncio
import time
import json
import logging
import random
import yaml
from pathlib import Path
from typing import Dict, Any, List

# Import the AI Intelligent Monitor
try:
    from .ai_intelligent_monitor_v4_0 import (
        AIIntelligentMonitor,
        create_ai_intelligent_monitor,
        AIModelMetrics
    )
    AI_MONITOR_AVAILABLE = True
except ImportError:
    AI_MONITOR_AVAILABLE = False
    print("Warning: AI Intelligent Monitor v4.0 not available")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class HeyGenAIMonitorDemo:
    """Demo class for HeyGen AI Intelligent Monitor"""
    
    def __init__(self, config_path: str = "heygen_ai_monitor_config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.monitor = None
        self.running = False
        
        # Demo state
        self.demo_models = {}
        self.demo_scenarios = []
        self.current_scenario = 0
        
        # Load configuration
        self._load_configuration()
        
    def _load_configuration(self):
        """Load HeyGen AI monitor configuration"""
        try:
            if Path(self.config_path).exists():
                with open(self.config_path, 'r') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"Configuration loaded from {self.config_path}")
            else:
                logger.warning(f"Configuration file {self.config_path} not found, using defaults")
                self.config = self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for demo"""
        return {
            'monitoring_interval': 10.0,
            'auto_scaling_enabled': True,
            'enable_ai_anomaly_detection': True,
            'enable_predictive_scaling': True,
            'enable_smart_alerting': True,
            'ai_model_monitoring': True,
            'resource_prediction': True,
            'auto_optimization': True
        }
    
    async def setup_monitor(self):
        """Set up the AI Intelligent Monitor"""
        if not AI_MONITOR_AVAILABLE:
            logger.error("AI Intelligent Monitor not available")
            return False
        
        try:
            logger.info("Setting up HeyGen AI Intelligent Monitor...")
            
            # Create monitor instance
            self.monitor = create_ai_intelligent_monitor(self.config)
            
            # Set up demo models
            self._setup_demo_models()
            
            # Set up demo scenarios
            self._setup_demo_scenarios()
            
            logger.info("HeyGen AI Intelligent Monitor setup complete!")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up monitor: {e}")
            return False
    
    def _setup_demo_models(self):
        """Set up demo AI models"""
        self.demo_models = {
            'heygen_ai_model': {
                'name': 'HeyGen AI Core Model',
                'type': 'diffusion_model',
                'base_inference_time': 150.0,
                'base_memory_usage': 2048.0,
                'base_gpu_utilization': 75.0,
                'base_accuracy': 0.95,
                'base_throughput': 100.0
            },
            'heygen_video_model': {
                'name': 'HeyGen Video Generation Model',
                'type': 'video_diffusion',
                'base_inference_time': 5000.0,
                'base_memory_usage': 8192.0,
                'base_gpu_utilization': 90.0,
                'base_accuracy': 0.92,
                'base_throughput': 10.0
            },
            'heygen_audio_model': {
                'name': 'HeyGen Audio Synthesis Model',
                'type': 'audio_diffusion',
                'base_inference_time': 200.0,
                'base_memory_usage': 1024.0,
                'base_gpu_utilization': 60.0,
                'base_accuracy': 0.98,
                'base_throughput': 200.0
            }
        }
        
        logger.info(f"Demo models configured: {list(self.demo_models.keys())}")
    
    def _setup_demo_scenarios(self):
        """Set up demo scenarios"""
        self.demo_scenarios = [
            {
                'name': 'Normal Operation',
                'duration': 60,  # seconds
                'description': 'Simulate normal AI model operation with stable performance',
                'load_factor': 1.0,
                'error_rate': 0.02
            },
            {
                'name': 'High Load',
                'duration': 90,
                'description': 'Simulate high load scenario with increased resource usage',
                'load_factor': 2.5,
                'error_rate': 0.05
            },
            {
                'name': 'Performance Degradation',
                'duration': 60,
                'description': 'Simulate performance degradation and trigger optimizations',
                'load_factor': 1.8,
                'error_rate': 0.12
            },
            {
                'name': 'Resource Exhaustion',
                'duration': 45,
                'description': 'Simulate resource exhaustion and emergency scaling',
                'load_factor': 3.0,
                'error_rate': 0.18
            },
            {
                'name': 'Recovery and Optimization',
                'duration': 75,
                'description': 'Simulate system recovery and optimization actions',
                'load_factor': 1.2,
                'error_rate': 0.03
            }
        ]
        
        logger.info(f"Demo scenarios configured: {len(self.demo_scenarios)} scenarios")
    
    async def start_demo(self):
        """Start the HeyGen AI monitoring demo"""
        if not self.monitor:
            logger.error("Monitor not set up. Call setup_monitor() first.")
            return
        
        logger.info("Starting HeyGen AI Intelligent Monitor Demo...")
        
        # Start monitoring
        await self.monitor.start_monitoring()
        self.running = True
        
        # Start demo tasks
        demo_tasks = [
            asyncio.create_task(self._run_demo_scenarios()),
            asyncio.create_task(self._generate_ai_metrics()),
            asyncio.create_task(self._display_status()),
            asyncio.create_task(self._simulate_optimization_triggers())
        ]
        
        try:
            # Run demo for specified duration
            await asyncio.gather(*demo_tasks, return_exceptions=True)
            
        except Exception as e:
            logger.error(f"Error in demo: {e}")
        finally:
            await self.stop_demo()
    
    async def stop_demo(self):
        """Stop the demo"""
        if not self.running:
            return
        
        logger.info("Stopping HeyGen AI Intelligent Monitor Demo...")
        self.running = False
        
        if self.monitor:
            await self.monitor.stop_monitoring()
        
        logger.info("Demo stopped")
    
    async def _run_demo_scenarios(self):
        """Run through all demo scenarios"""
        logger.info("Starting demo scenarios...")
        
        for i, scenario in enumerate(self.demo_scenarios):
            if not self.running:
                break
            
            self.current_scenario = i
            logger.info(f"Scenario {i+1}/{len(self.demo_scenarios)}: {scenario['name']}")
            logger.info(f"Description: {scenario['description']}")
            logger.info(f"Duration: {scenario['duration']} seconds")
            
            # Run scenario
            await self._execute_scenario(scenario)
            
            # Brief pause between scenarios
            if i < len(self.demo_scenarios) - 1:
                logger.info("Preparing next scenario...")
                await asyncio.sleep(5)
        
        logger.info("All demo scenarios completed!")
    
    async def _execute_scenario(self, scenario: Dict[str, Any]):
        """Execute a specific demo scenario"""
        start_time = time.time()
        end_time = start_time + scenario['duration']
        
        # Update demo state for this scenario
        self.current_scenario_config = scenario
        
        while time.time() < end_time and self.running:
            # Simulate scenario-specific behavior
            await self._simulate_scenario_behavior(scenario)
            
            # Wait before next iteration
            await asyncio.sleep(2)
    
    async def _simulate_scenario_behavior(self, scenario: Dict[str, Any]):
        """Simulate behavior specific to a scenario"""
        load_factor = scenario['load_factor']
        error_rate = scenario['error_rate']
        
        # Simulate varying load patterns
        if scenario['name'] == 'High Load':
            # Simulate traffic spikes
            if random.random() < 0.3:  # 30% chance of spike
                load_factor *= 1.5
        elif scenario['name'] == 'Performance Degradation':
            # Simulate gradual degradation
            load_factor *= (1.0 + (time.time() % 30) / 100)  # Gradual increase
        elif scenario['name'] == 'Resource Exhaustion':
            # Simulate resource exhaustion
            load_factor *= (1.0 + random.uniform(0.5, 1.0))
        
        # Update scenario state
        scenario['current_load_factor'] = load_factor
        scenario['current_error_rate'] = error_rate
    
    async def _generate_ai_metrics(self):
        """Generate AI model metrics for demo"""
        while self.running:
            try:
                # Generate metrics for each demo model
                for model_name, model_config in self.demo_models.items():
                    if not self.running:
                        break
                    
                    # Get current scenario configuration
                    current_scenario = self.demo_scenarios[self.current_scenario] if self.demo_scenarios else None
                    load_factor = current_scenario.get('current_load_factor', 1.0) if current_scenario else 1.0
                    error_rate = current_scenario.get('current_error_rate', 0.02) if current_scenario else 0.02
                    
                    # Generate realistic metrics with scenario variations
                    metrics = self._generate_model_metrics(model_name, model_config, load_factor, error_rate)
                    
                    # Add metrics to monitor
                    if self.monitor:
                        self.monitor.add_ai_model_metrics(metrics)
                    
                    # Simulate processing time
                    await asyncio.sleep(random.uniform(1.0, 3.0))
                    
            except Exception as e:
                logger.error(f"Error generating AI metrics: {e}")
                await asyncio.sleep(5)
    
    def _generate_model_metrics(self, model_name: str, model_config: Dict[str, Any], 
                               load_factor: float, error_rate: float) -> AIModelMetrics:
        """Generate realistic model metrics"""
        base_config = model_config
        
        # Apply load factor variations
        inference_time = base_config['base_inference_time'] * load_factor * random.uniform(0.8, 1.2)
        memory_usage = base_config['base_memory_usage'] * load_factor * random.uniform(0.9, 1.1)
        gpu_utilization = min(100.0, base_config['base_gpu_utilization'] * load_factor * random.uniform(0.85, 1.15))
        
        # Simulate batch size variations
        batch_size = max(1, int(32 / load_factor))
        
        # Apply error rate variations
        accuracy = max(0.5, base_config['base_accuracy'] - (error_rate * 2))
        
        # Calculate throughput based on load and performance
        throughput = base_config['base_throughput'] / load_factor * random.uniform(0.7, 1.3)
        
        # Calculate latency percentiles
        latency_p95 = inference_time * random.uniform(1.2, 1.8)
        latency_p99 = inference_time * random.uniform(1.5, 2.5)
        
        return AIModelMetrics(
            model_name=model_name,
            inference_time=inference_time,
            memory_usage=memory_usage,
            gpu_utilization=gpu_utilization,
            batch_size=batch_size,
            accuracy=accuracy,
            throughput=throughput,
            error_rate=error_rate,
            latency_p95=latency_p95,
            latency_p99=latency_p99
        )
    
    async def _simulate_optimization_triggers(self):
        """Simulate optimization triggers"""
        while self.running:
            try:
                # Simulate various optimization triggers
                if random.random() < 0.1:  # 10% chance every cycle
                    await self._trigger_optimization_event()
                
                await asyncio.sleep(random.uniform(10.0, 20.0))
                
            except Exception as e:
                logger.error(f"Error in optimization triggers: {e}")
                await asyncio.sleep(5)
    
    async def _trigger_optimization_event(self):
        """Trigger a specific optimization event"""
        events = [
            'memory_pressure',
            'cpu_spike',
            'gpu_overload',
            'response_time_degradation',
            'error_rate_increase'
        ]
        
        event = random.choice(events)
        logger.info(f"Triggering optimization event: {event}")
        
        # This would typically trigger actual optimization logic
        # For demo purposes, we just log the event
    
    async def _display_status(self):
        """Display periodic status updates"""
        while self.running:
            try:
                await asyncio.sleep(15)  # Update every 15 seconds
                
                if self.monitor:
                    # Get current status
                    status = self.monitor.get_monitoring_status()
                    
                    # Display demo status
                    self._display_demo_status(status)
                    
            except Exception as e:
                logger.error(f"Error displaying status: {e}")
                await asyncio.sleep(5)
    
    def _display_demo_status(self, monitor_status: Dict[str, Any]):
        """Display demo status information"""
        current_scenario = self.demo_scenarios[self.current_scenario] if self.demo_scenarios else None
        
        print("\n" + "="*80)
        print("HEYGEN AI INTELLIGENT MONITOR DEMO STATUS")
        print("="*80)
        
        # Demo information
        if current_scenario:
            print(f"Current Scenario: {current_scenario['name']}")
            print(f"Description: {current_scenario['description']}")
            print(f"Load Factor: {current_scenario.get('current_load_factor', 1.0):.2f}")
            print(f"Error Rate: {current_scenario.get('current_error_rate', 0.02):.3f}")
        
        # Monitor status
        print(f"\nMonitor Version: {monitor_status.get('monitor_version', 'Unknown')}")
        print(f"Monitoring Active: {monitor_status.get('is_monitoring', False)}")
        
        # Component status
        components = monitor_status.get('components', {})
        print(f"\nComponent Status:")
        for component, status in components.items():
            status_str = "✓ Active" if status else "✗ Inactive"
            print(f"  {component}: {status_str}")
        
        # Optimization status
        if 'optimization_queue_size' in monitor_status:
            print(f"\nOptimization Queue: {monitor_status['optimization_queue_size']} actions")
        if 'optimization_history_size' in monitor_status:
            print(f"Optimization History: {monitor_status['optimization_history_size']} actions")
        
        # AI model analysis
        if self.monitor and self.demo_models:
            print(f"\nAI Model Performance:")
            for model_name in self.demo_models.keys():
                analysis = self.monitor.get_ai_model_analysis(model_name)
                if analysis:
                    current_metrics = analysis.get('current_metrics', {})
                    if current_metrics:
                        print(f"  {model_name}:")
                        print(f"    Inference Time: {current_metrics.get('inference_time', 0):.1f}ms")
                        print(f"    Memory Usage: {current_metrics.get('memory_usage', 0):.1f}MB")
                        print(f"    GPU Utilization: {current_metrics.get('gpu_utilization', 0):.1f}%")
                        print(f"    Accuracy: {current_metrics.get('accuracy', 0):.3f}")
        
        # Resource predictions
        if self.monitor:
            print(f"\nResource Predictions (10 min horizon):")
            key_metrics = ['cpu_usage', 'memory_usage', 'gpu_utilization']
            for metric in key_metrics:
                prediction = self.monitor.get_resource_prediction(metric, time_horizon=600.0)
                if prediction:
                    print(f"  {metric}: {prediction.trend_direction} "
                          f"({prediction.confidence:.2f} confidence)")
                    print(f"    Current: {prediction.current_value:.1f}, "
                          f"Predicted: {prediction.predicted_value:.1f}")
        
        print("="*80)
    
    def export_demo_results(self):
        """Export demo results for analysis"""
        if not self.monitor:
            logger.error("Monitor not available for export")
            return
        
        try:
            # Create exports directory
            exports_dir = Path("./heygen_ai_demo_exports")
            exports_dir.mkdir(exist_ok=True)
            
            # Export monitor status
            status = self.monitor.get_monitoring_status()
            status_file = exports_dir / "monitor_status.json"
            with open(status_file, 'w') as f:
                json.dump(status, f, indent=2, default=str)
            
            # Export AI model analysis
            model_analysis = {}
            for model_name in self.demo_models.keys():
                analysis = self.monitor.get_ai_model_analysis(model_name)
                if analysis:
                    model_analysis[model_name] = analysis
            
            analysis_file = exports_dir / "ai_model_analysis.json"
            with open(analysis_file, 'w') as f:
                json.dump(model_analysis, f, indent=2, default=str)
            
            # Export demo configuration
            demo_config = {
                'demo_models': self.demo_models,
                'demo_scenarios': self.demo_scenarios,
                'monitor_config': self.config
            }
            
            config_file = exports_dir / "demo_configuration.json"
            with open(config_file, 'w') as f:
                json.dump(demo_config, f, indent=2, default=str)
            
            logger.info(f"Demo results exported to {exports_dir}")
            logger.info(f"Files created:")
            logger.info(f"  - {status_file}")
            logger.info(f"  - {analysis_file}")
            logger.info(f"  - {config_file}")
            
        except Exception as e:
            logger.error(f"Error exporting demo results: {e}")


async def main():
    """Main demo function"""
    print("HeyGen AI Intelligent Monitor Demo v4.0")
    print("=" * 60)
    print("Advanced AI-powered monitoring and optimization for HeyGen AI systems")
    print("=" * 60)
    
    # Create demo instance
    demo = HeyGenAIMonitorDemo()
    
    try:
        # Set up monitor
        setup_success = await demo.setup_monitor()
        if not setup_success:
            print("Failed to set up monitor. Exiting.")
            return
        
        # Run demo
        await demo.start_demo()
        
        # Export results
        demo.export_demo_results()
        
        # Display final summary
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY")
        print("="*60)
        
        if demo.monitor:
            final_status = demo.monitor.get_monitoring_status()
            print(f"Final Monitor Status:")
            print(f"  Version: {final_status.get('monitor_version', 'Unknown')}")
            print(f"  Components Active: {sum(final_status.get('components', {}).values())}")
            print(f"  Optimization Actions: {final_status.get('optimization_history_size', 0)}")
        
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
