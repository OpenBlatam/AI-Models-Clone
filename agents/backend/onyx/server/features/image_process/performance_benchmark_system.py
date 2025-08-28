"""
🚀 Performance Benchmarking System
==================================

Comprehensive performance benchmarking and optimization system for the image processing
system with support for PyTorch, Transformers, Diffusers, and Gradio.
"""

import time
import logging
import psutil
import GPUtil
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Union
from dataclasses import dataclass, field
from contextlib import contextmanager
import warnings
import json
import yaml
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BenchmarkConfig:
    """Configuration for performance benchmarking."""
    
    # Benchmark settings
    num_runs: int = 5
    warmup_runs: int = 2
    timeout_seconds: int = 300
    
    # Memory profiling
    profile_memory: bool = True
    memory_snapshots: int = 10
    
    # GPU profiling
    profile_gpu: bool = True
    gpu_metrics_interval: float = 0.1
    
    # Performance thresholds
    memory_threshold_mb: float = 1024.0  # 1GB
    gpu_memory_threshold_mb: float = 2048.0  # 2GB
    inference_time_threshold_ms: float = 1000.0  # 1 second
    
    # Output settings
    save_results: bool = True
    results_dir: str = "benchmark_results"
    export_formats: List[str] = field(default_factory=lambda: ["json", "yaml", "csv"])
    
    # Detailed profiling
    profile_forward_pass: bool = True
    profile_backward_pass: bool = True
    profile_optimization: bool = True
    profile_data_loading: bool = True

class PerformanceProfiler:
    """Advanced performance profiler with memory and GPU monitoring."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results = {}
        self.memory_snapshots = []
        self.gpu_metrics = []
        self.start_time = None
        self.end_time = None
        
    def start_profiling(self):
        """Start performance profiling."""
        self.start_time = time.time()
        self.memory_snapshots = []
        self.gpu_metrics = []
        
        if self.config.profile_memory:
            self._start_memory_monitoring()
            
        if self.config.profile_gpu and torch.cuda.is_available():
            self._start_gpu_monitoring()
    
    def stop_profiling(self):
        """Stop performance profiling."""
        self.end_time = time.time()
        
        if self.config.profile_memory:
            self._stop_memory_monitoring()
            
        if self.config.profile_gpu:
            self._stop_gpu_monitoring()
    
    def _start_memory_monitoring(self):
        """Start memory monitoring in background."""
        import threading
        
        def monitor_memory():
            while self.start_time and not self.end_time:
                snapshot = {
                    'timestamp': time.time(),
                    'cpu_percent': psutil.cpu_percent(),
                    'memory_percent': psutil.virtual_memory().percent,
                    'memory_used_mb': psutil.virtual_memory().used / 1024 / 1024,
                    'memory_available_mb': psutil.virtual_memory().available / 1024 / 1024
                }
                self.memory_snapshots.append(snapshot)
                time.sleep(0.1)
        
        self.memory_thread = threading.Thread(target=monitor_memory, daemon=True)
        self.memory_thread.start()
    
    def _stop_memory_monitoring(self):
        """Stop memory monitoring."""
        self.end_time = time.time()
        if hasattr(self, 'memory_thread'):
            self.memory_thread.join(timeout=1.0)
    
    def _start_gpu_monitoring(self):
        """Start GPU monitoring in background."""
        if not torch.cuda.is_available():
            return
            
        import threading
        
        def monitor_gpu():
            while self.start_time and not self.end_time:
                try:
                    gpu = GPUtil.getGPUs()[0]
                    snapshot = {
                        'timestamp': time.time(),
                        'gpu_memory_used_mb': gpu.memoryUsed,
                        'gpu_memory_total_mb': gpu.memoryTotal,
                        'gpu_utilization_percent': gpu.load * 100,
                        'gpu_temperature_celsius': gpu.temperature
                    }
                    self.gpu_metrics.append(snapshot)
                except Exception as e:
                    logger.warning(f"GPU monitoring error: {e}")
                time.sleep(self.config.gpu_metrics_interval)
        
        self.gpu_thread = threading.Thread(target=monitor_gpu, daemon=True)
        self.gpu_thread.start()
    
    def _stop_gpu_monitoring(self):
        """Stop GPU monitoring."""
        if hasattr(self, 'gpu_thread'):
            self.gpu_thread.join(timeout=1.0)
    
    def get_profiling_results(self) -> Dict[str, Any]:
        """Get comprehensive profiling results."""
        if not self.start_time or not self.end_time:
            return {}
        
        total_time = self.end_time - self.start_time
        
        results = {
            'total_time_seconds': total_time,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': datetime.fromtimestamp(self.end_time).isoformat(),
            'memory_profiling': self._analyze_memory_results(),
            'gpu_profiling': self._analyze_gpu_results()
        }
        
        return results
    
    def _analyze_memory_results(self) -> Dict[str, Any]:
        """Analyze memory profiling results."""
        if not self.memory_snapshots:
            return {}
        
        memory_used = [s['memory_used_mb'] for s in self.memory_snapshots]
        cpu_usage = [s['cpu_percent'] for s in self.memory_snapshots]
        
        return {
            'peak_memory_mb': max(memory_used),
            'average_memory_mb': sum(memory_used) / len(memory_used),
            'peak_cpu_percent': max(cpu_usage),
            'average_cpu_percent': sum(cpu_usage) / len(cpu_usage),
            'memory_snapshots_count': len(self.memory_snapshots),
            'memory_trend': 'increasing' if memory_used[-1] > memory_used[0] else 'stable'
        }
    
    def _analyze_gpu_results(self) -> Dict[str, Any]:
        """Analyze GPU profiling results."""
        if not self.gpu_metrics:
            return {}
        
        gpu_memory = [s['gpu_memory_used_mb'] for s in self.gpu_metrics]
        gpu_util = [s['gpu_utilization_percent'] for s in self.gpu_metrics]
        
        return {
            'peak_gpu_memory_mb': max(gpu_memory),
            'average_gpu_memory_mb': sum(gpu_memory) / len(gpu_memory),
            'peak_gpu_utilization_percent': max(gpu_util),
            'average_gpu_utilization_percent': sum(gpu_util) / len(gpu_util),
            'gpu_metrics_count': len(self.gpu_metrics)
        }

class ModelBenchmarker:
    """Benchmark PyTorch models with comprehensive metrics."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.profiler = PerformanceProfiler(config)
        
    def benchmark_model(self, model: nn.Module, input_shape: Tuple[int, ...], 
                       device: str = "auto") -> Dict[str, Any]:
        """Benchmark a PyTorch model."""
        if device == "auto":
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        device = torch.device(device)
        model = model.to(device)
        
        # Warmup runs
        logger.info(f"Running {self.config.warmup_runs} warmup runs...")
        for _ in range(self.config.warmup_runs):
            dummy_input = torch.randn(input_shape).to(device)
            with torch.no_grad():
                _ = model(dummy_input)
        
        # Benchmark runs
        logger.info(f"Running {self.config.num_runs} benchmark runs...")
        inference_times = []
        memory_usage = []
        
        for run in range(self.config.num_runs):
            logger.info(f"Benchmark run {run + 1}/{self.config.num_runs}")
            
            # Clear cache
            if device.type == "cuda":
                torch.cuda.empty_cache()
            
            # Profile inference
            self.profiler.start_profiling()
            
            dummy_input = torch.randn(input_shape).to(device)
            start_time = time.time()
            
            with torch.no_grad():
                output = model(dummy_input)
            
            torch.cuda.synchronize() if device.type == "cuda" else None
            inference_time = (time.time() - start_time) * 1000  # Convert to ms
            
            self.profiler.stop_profiling()
            
            # Collect metrics
            inference_times.append(inference_time)
            
            if device.type == "cuda":
                memory_usage.append(torch.cuda.memory_allocated(device) / 1024 / 1024)
            
            # Get profiling results
            profiling_results = self.profiler.get_profiling_results()
            
            logger.info(f"  Run {run + 1}: {inference_time:.2f}ms")
        
        # Calculate statistics
        avg_inference_time = sum(inference_times) / len(inference_times)
        min_inference_time = min(inference_times)
        max_inference_time = max(inference_times)
        
        results = {
            'model_name': model.__class__.__name__,
            'input_shape': input_shape,
            'device': str(device),
            'num_runs': self.config.num_runs,
            'inference_times_ms': inference_times,
            'average_inference_time_ms': avg_inference_time,
            'min_inference_time_ms': min_inference_time,
            'max_inference_time_ms': max_inference_time,
            'std_inference_time_ms': self._calculate_std(inference_times),
            'throughput_fps': 1000.0 / avg_inference_time if avg_inference_time > 0 else 0,
            'memory_usage_mb': memory_usage,
            'profiling_results': profiling_results,
            'benchmark_timestamp': datetime.now().isoformat()
        }
        
        # Performance analysis
        results['performance_analysis'] = self._analyze_performance(results)
        
        return results
    
    def _calculate_std(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5
    
    def _analyze_performance(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze benchmark performance."""
        analysis = {
            'status': 'optimal',
            'recommendations': [],
            'warnings': []
        }
        
        # Check inference time
        avg_time = results['average_inference_time_ms']
        if avg_time > self.config.inference_time_threshold_ms:
            analysis['status'] = 'slow'
            analysis['recommendations'].append('Consider model optimization or GPU upgrade')
            analysis['warnings'].append(f'Inference time ({avg_time:.2f}ms) exceeds threshold')
        
        # Check memory usage
        if results['memory_usage_mb']:
            avg_memory = sum(results['memory_usage_mb']) / len(results['memory_usage_mb'])
            if avg_memory > self.config.memory_threshold_mb:
                analysis['status'] = 'memory_intensive'
                analysis['recommendations'].append('Enable gradient checkpointing or reduce batch size')
                analysis['warnings'].append(f'Memory usage ({avg_memory:.2f}MB) exceeds threshold')
        
        # Check GPU memory
        if 'gpu_profiling' in results['profiling_results']:
            gpu_memory = results['profiling_results']['gpu_profiling'].get('peak_gpu_memory_mb', 0)
            if gpu_memory > self.config.gpu_memory_threshold_mb:
                analysis['recommendations'].append('Enable attention slicing or model offloading')
                analysis['warnings'].append(f'GPU memory usage ({gpu_memory:.2f}MB) is high')
        
        return analysis

class TransformersBenchmarker:
    """Benchmark Transformers models with best practices."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.profiler = PerformanceProfiler(config)
        
    def benchmark_transformers_model(self, model_name: str, task: str = "text-classification",
                                   input_texts: List[str] = None) -> Dict[str, Any]:
        """Benchmark a Transformers model."""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            logger.info(f"Loading Transformers model: {model_name}")
            
            # Load model and tokenizer
            self.profiler.start_profiling()
            
            model = AutoModel.from_pretrained(model_name)
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            
            self.profiler.stop_profiling()
            loading_results = self.profiler.get_profiling_results()
            
            # Prepare input texts
            if input_texts is None:
                input_texts = [
                    "This is a test sentence for benchmarking.",
                    "Another example text for performance testing.",
                    "Third sample text to evaluate model speed."
                ]
            
            # Benchmark inference
            inference_times = []
            memory_usage = []
            
            device = next(model.parameters()).device
            
            for run in range(self.config.num_runs):
                logger.info(f"Transformers benchmark run {run + 1}/{self.config.num_runs}")
                
                # Clear cache
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                
                # Profile inference
                self.profiler.start_profiling()
                
                start_time = time.time()
                
                for text in input_texts:
                    inputs = tokenizer(
                        text,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512
                    ).to(device)
                    
                    with torch.no_grad():
                        outputs = model(**inputs)
                
                torch.cuda.synchronize() if device.type == "cuda" else None
                inference_time = (time.time() - start_time) * 1000
                
                self.profiler.stop_profiling()
                
                inference_times.append(inference_time)
                
                if device.type == "cuda":
                    memory_usage.append(torch.cuda.memory_allocated(device) / 1024 / 1024)
                
                logger.info(f"  Run {run + 1}: {inference_time:.2f}ms")
            
            # Calculate statistics
            avg_inference_time = sum(inference_times) / len(inference_times)
            
            results = {
                'model_name': model_name,
                'task': task,
                'device': str(device),
                'num_runs': self.config.num_runs,
                'input_texts': input_texts,
                'inference_times_ms': inference_times,
                'average_inference_time_ms': avg_inference_time,
                'throughput_texts_per_second': len(input_texts) / (avg_inference_time / 1000),
                'memory_usage_mb': memory_usage,
                'loading_results': loading_results,
                'profiling_results': self.profiler.get_profiling_results(),
                'benchmark_timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Transformers benchmarking failed: {e}")
            return {'error': str(e)}

class DiffusersBenchmarker:
    """Benchmark Diffusers pipelines with optimizations."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.profiler = PerformanceProfiler(config)
        
    def benchmark_diffusers_pipeline(self, model_name: str, pipeline_type: str = "text-to-image",
                                   prompts: List[str] = None) -> Dict[str, Any]:
        """Benchmark a Diffusers pipeline."""
        try:
            from diffusers import StableDiffusionPipeline
            
            logger.info(f"Loading Diffusers pipeline: {model_name}")
            
            # Load pipeline
            self.profiler.start_profiling()
            
            pipeline = StableDiffusionPipeline.from_pretrained(
                model_name,
                torch_dtype=torch.float16,
                use_safetensors=True
            )
            
            if torch.cuda.is_available():
                pipeline = pipeline.to("cuda")
                pipeline.enable_attention_slicing()
                pipeline.enable_model_cpu_offload()
            
            self.profiler.stop_profiling()
            loading_results = self.profiler.get_profiling_results()
            
            # Prepare prompts
            if prompts is None:
                prompts = [
                    "A beautiful sunset over mountains, high quality, detailed",
                    "A futuristic cityscape with flying cars, cinematic lighting",
                    "A serene forest with ancient trees and magical atmosphere"
                ]
            
            # Benchmark generation
            generation_times = []
            memory_usage = []
            
            device = next(pipeline.unet.parameters()).device
            
            for run in range(self.config.num_runs):
                logger.info(f"Diffusers benchmark run {run + 1}/{self.config.num_runs}")
                
                # Clear cache
                if device.type == "cuda":
                    torch.cuda.empty_cache()
                
                # Profile generation
                self.profiler.start_profiling()
                
                start_time = time.time()
                
                for prompt in prompts:
                    with torch.autocast(device_type="cuda", dtype=torch.float16):
                        image = pipeline(
                            prompt,
                            num_inference_steps=20,
                            guidance_scale=7.5
                        ).images[0]
                
                torch.cuda.synchronize() if device.type == "cuda" else None
                generation_time = (time.time() - start_time) * 1000
                
                self.profiler.stop_profiling()
                
                generation_times.append(generation_time)
                
                if device.type == "cuda":
                    memory_usage.append(torch.cuda.memory_allocated(device) / 1024 / 1024)
                
                logger.info(f"  Run {run + 1}: {generation_time:.2f}ms")
            
            # Calculate statistics
            avg_generation_time = sum(generation_times) / len(generation_times)
            
            results = {
                'model_name': model_name,
                'pipeline_type': pipeline_type,
                'device': str(device),
                'num_runs': self.config.num_runs,
                'prompts': prompts,
                'generation_times_ms': generation_times,
                'average_generation_time_ms': avg_generation_time,
                'throughput_images_per_second': len(prompts) / (avg_generation_time / 1000),
                'memory_usage_mb': memory_usage,
                'loading_results': loading_results,
                'profiling_results': self.profiler.get_profiling_results(),
                'benchmark_timestamp': datetime.now().isoformat()
            }
            
            return results
            
        except Exception as e:
            logger.error(f"Diffusers benchmarking failed: {e}")
            return {'error': str(e)}

class BenchmarkRunner:
    """Main benchmark runner orchestrating all benchmark types."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.model_benchmarker = ModelBenchmarker(config)
        self.transformers_benchmarker = TransformersBenchmarker(config)
        self.diffusers_benchmarker = DiffusersBenchmarker(config)
        self.results = {}
        
    def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmarking of all components."""
        logger.info("🚀 Starting comprehensive performance benchmark...")
        
        # Benchmark PyTorch models
        self._benchmark_pytorch_models()
        
        # Benchmark Transformers models
        self._benchmark_transformers_models()
        
        # Benchmark Diffusers pipelines
        self._benchmark_diffusers_pipelines()
        
        # Generate summary report
        summary = self._generate_summary_report()
        
        # Save results if configured
        if self.config.save_results:
            self._save_results()
        
        logger.info("✅ Comprehensive benchmark completed!")
        return summary
    
    def _benchmark_pytorch_models(self):
        """Benchmark PyTorch models."""
        logger.info("🔍 Benchmarking PyTorch models...")
        
        # Simple CNN model
        class SimpleCNN(nn.Module):
            def __init__(self):
                super().__init__()
                self.conv1 = nn.Conv2d(3, 64, 3, padding=1)
                self.conv2 = nn.Conv2d(64, 128, 3, padding=1)
                self.pool = nn.AdaptiveAvgPool2d((1, 1))
                self.fc = nn.Linear(128, 1000)
                self.relu = nn.ReLU()
            
            def forward(self, x):
                x = self.relu(self.conv1(x))
                x = self.relu(self.conv2(x))
                x = self.pool(x)
                x = x.view(x.size(0), -1)
                x = self.fc(x)
                return x
        
        # Benchmark different input sizes
        input_sizes = [(1, 3, 224, 224), (1, 3, 512, 512), (4, 3, 224, 224)]
        
        for input_size in input_sizes:
            model = SimpleCNN()
            results = self.model_benchmarker.benchmark_model(model, input_size)
            self.results[f'pytorch_cnn_{input_size[2]}x{input_size[3]}'] = results
    
    def _benchmark_transformers_models(self):
        """Benchmark Transformers models."""
        logger.info("🔍 Benchmarking Transformers models...")
        
        models_to_benchmark = [
            ("bert-base-uncased", "text-classification"),
            ("distilbert-base-uncased", "text-classification")
        ]
        
        for model_name, task in models_to_benchmark:
            try:
                results = self.transformers_benchmarker.benchmark_transformers_model(
                    model_name, task
                )
                self.results[f'transformers_{model_name.replace("/", "_")}'] = results
            except Exception as e:
                logger.warning(f"Failed to benchmark {model_name}: {e}")
    
    def _benchmark_diffusers_pipelines(self):
        """Benchmark Diffusers pipelines."""
        logger.info("🔍 Benchmarking Diffusers pipelines...")
        
        pipelines_to_benchmark = [
            ("runwayml/stable-diffusion-v1-5", "text-to-image")
        ]
        
        for model_name, pipeline_type in pipelines_to_benchmark:
            try:
                results = self.diffusers_benchmarker.benchmark_diffusers_pipeline(
                    model_name, pipeline_type
                )
                self.results[f'diffusers_{model_name.replace("/", "_")}'] = results
            except Exception as e:
                logger.warning(f"Failed to benchmark {model_name}: {e}")
    
    def _generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        logger.info("📊 Generating benchmark summary report...")
        
        summary = {
            'benchmark_config': self.config.__dict__,
            'total_models_benchmarked': len(self.results),
            'benchmark_timestamp': datetime.now().isoformat(),
            'performance_summary': {},
            'recommendations': [],
            'warnings': []
        }
        
        # Analyze performance across all models
        for model_name, results in self.results.items():
            if 'error' in results:
                continue
                
            # Extract key metrics
            if 'average_inference_time_ms' in results:
                inference_time = results['average_inference_time_ms']
                summary['performance_summary'][model_name] = {
                    'inference_time_ms': inference_time,
                    'throughput': results.get('throughput_fps', 0)
                }
            elif 'average_generation_time_ms' in results:
                generation_time = results['average_generation_time_ms']
                summary['performance_summary'][model_name] = {
                    'generation_time_ms': generation_time,
                    'throughput': results.get('throughput_images_per_second', 0)
                }
            
            # Collect recommendations and warnings
            if 'performance_analysis' in results:
                analysis = results['performance_analysis']
                summary['recommendations'].extend(analysis.get('recommendations', []))
                summary['warnings'].extend(analysis.get('warnings', []))
        
        # Overall performance analysis
        summary['overall_performance'] = self._analyze_overall_performance()
        
        return summary
    
    def _analyze_overall_performance(self) -> Dict[str, Any]:
        """Analyze overall benchmark performance."""
        analysis = {
            'status': 'optimal',
            'fastest_model': None,
            'slowest_model': None,
            'memory_intensive_models': [],
            'optimization_opportunities': []
        }
        
        fastest_time = float('inf')
        slowest_time = 0
        
        for model_name, results in self.results.items():
            if 'error' in results:
                continue
            
            # Find fastest and slowest
            if 'average_inference_time_ms' in results:
                time = results['average_inference_time_ms']
            elif 'average_generation_time_ms' in results:
                time = results['average_generation_time_ms']
            else:
                continue
            
            if time < fastest_time:
                fastest_time = time
                analysis['fastest_model'] = model_name
            
            if time > slowest_time:
                slowest_time = time
                analysis['slowest_model'] = model_name
            
            # Check for memory issues
            if 'memory_usage_mb' in results and results['memory_usage_mb']:
                avg_memory = sum(results['memory_usage_mb']) / len(results['memory_usage_mb'])
                if avg_memory > self.config.memory_threshold_mb:
                    analysis['memory_intensive_models'].append(model_name)
                    analysis['optimization_opportunities'].append(
                        f"Optimize memory usage for {model_name}"
                    )
        
        # Determine overall status
        if analysis['memory_intensive_models']:
            analysis['status'] = 'memory_optimization_needed'
        elif slowest_time > self.config.inference_time_threshold_ms:
            analysis['status'] = 'performance_optimization_needed'
        
        return analysis
    
    def _save_results(self):
        """Save benchmark results to files."""
        results_dir = Path(self.config.results_dir)
        results_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for format_type in self.config.export_formats:
            if format_type == "json":
                self._save_json_results(results_dir, timestamp)
            elif format_type == "yaml":
                self._save_yaml_results(results_dir, timestamp)
            elif format_type == "csv":
                self._save_csv_results(results_dir, timestamp)
    
    def _save_json_results(self, results_dir: Path, timestamp: str):
        """Save results as JSON."""
        file_path = results_dir / f"benchmark_results_{timestamp}.json"
        with open(file_path, 'w') as f:
            json.dump(self.results, f, indent=2, default=str)
        logger.info(f"Results saved to: {file_path}")
    
    def _save_yaml_results(self, results_dir: Path, timestamp: str):
        """Save results as YAML."""
        file_path = results_dir / f"benchmark_results_{timestamp}.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(self.results, f, default_flow_style=False, default_representer=str)
        logger.info(f"Results saved to: {file_path}")
    
    def _save_csv_results(self, results_dir: Path, timestamp: str):
        """Save results as CSV."""
        import pandas as pd
        
        # Flatten results for CSV
        csv_data = []
        for model_name, results in self.results.items():
            if 'error' in results:
                continue
            
            row = {'model_name': model_name}
            
            # Extract key metrics
            if 'average_inference_time_ms' in results:
                row['inference_time_ms'] = results['average_inference_time_ms']
                row['throughput'] = results.get('throughput_fps', 0)
            elif 'average_generation_time_ms' in results:
                row['generation_time_ms'] = results['average_generation_time_ms']
                row['throughput'] = results.get('throughput_images_per_second', 0)
            
            if 'memory_usage_mb' in results and results['memory_usage_mb']:
                row['avg_memory_mb'] = sum(results['memory_usage_mb']) / len(results['memory_usage_mb'])
            
            csv_data.append(row)
        
        if csv_data:
            df = pd.DataFrame(csv_data)
            file_path = results_dir / f"benchmark_results_{timestamp}.csv"
            df.to_csv(file_path, index=False)
            logger.info(f"Results saved to: {file_path}")

def main():
    """Main benchmark function."""
    logger.info("🚀 Performance Benchmarking System")
    logger.info("=" * 50)
    
    # Configuration
    config = BenchmarkConfig(
        num_runs=3,
        warmup_runs=1,
        profile_memory=True,
        profile_gpu=True,
        save_results=True
    )
    
    # Run comprehensive benchmark
    runner = BenchmarkRunner(config)
    summary = runner.run_comprehensive_benchmark()
    
    # Display summary
    logger.info("📊 Benchmark Summary:")
    logger.info(f"  Total models benchmarked: {summary['total_models_benchmarked']}")
    logger.info(f"  Overall status: {summary['overall_performance']['status']}")
    
    if summary['overall_performance']['fastest_model']:
        logger.info(f"  Fastest model: {summary['overall_performance']['fastest_model']}")
    
    if summary['recommendations']:
        logger.info("  Recommendations:")
        for rec in summary['recommendations']:
            logger.info(f"    - {rec}")
    
    if summary['warnings']:
        logger.info("  Warnings:")
        for warning in summary['warnings']:
            logger.info(f"    - {warning}")
    
    logger.info("✅ Benchmark completed successfully!")
    return summary

if __name__ == "__main__":
    main()



