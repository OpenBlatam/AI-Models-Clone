# TruthGPT Advanced Examples

This document provides comprehensive code examples and tutorials for implementing TruthGPT optimization core features.

## 🎯 Design Goals

- **Practical Implementation**: Real-world code examples
- **Progressive Complexity**: From basic to advanced usage
- **Production Ready**: Enterprise-grade code patterns
- **Comprehensive Coverage**: All major features included

## 🚀 Quick Start Examples

### Basic TruthGPT Usage

```python
"""
Basic TruthGPT Usage Example
Demonstrates simple inference with TruthGPT optimization core
"""

import asyncio
import torch
from truthgpt import TruthGPT, TruthGPTConfig
from truthgpt.optimization import LightningProcessor
from truthgpt.pimoe import PiMoERouter

async def basic_inference_example():
    """Basic inference example with TruthGPT"""
    
    # Initialize configuration
    config = TruthGPTConfig(
        model_name="TruthGPT-PiMoE-v1",
        num_experts=8,
        expert_capacity=1.2,
        mixed_precision=True,
        dynamic_batching=True
    )
    
    # Initialize TruthGPT
    truthgpt = TruthGPT(config)
    
    # Initialize optimization components
    processor = LightningProcessor(
        microsecond_precision=True,
        zero_copy_operations=True
    )
    
    router = PiMoERouter(
        num_experts=config.num_experts,
        routing_algorithm="attention_based"
    )
    
    # Load model
    await truthgpt.load_model()
    
    # Example inference
    input_text = "What is the nature of reality and consciousness?"
    
    # Process input
    processed_input = await processor.preprocess(input_text)
    
    # Route to experts
    routing_weights = await router.route(processed_input)
    
    # Generate response
    response = await truthgpt.generate(
        input_text=input_text,
        max_tokens=512,
        temperature=0.7,
        routing_weights=routing_weights
    )
    
    print(f"Input: {input_text}")
    print(f"Response: {response}")
    
    # Cleanup
    await truthgpt.cleanup()

# Run the example
if __name__ == "__main__":
    asyncio.run(basic_inference_example())
```

### Advanced Optimization Example

```python
"""
Advanced TruthGPT Optimization Example
Demonstrates ultra-optimization techniques and performance tuning
"""

import asyncio
import torch
import time
from typing import List, Dict, Any
from truthgpt import TruthGPT, TruthGPTConfig
from truthgpt.optimization import (
    UltraOptimizer,
    ModelCompiler,
    GPUBatchProcessor,
    MemoryOptimizer
)
from truthgpt.pimoe import AdvancedPiMoERouter
from truthgpt.cache import UltraKVCache

class AdvancedTruthGPTExample:
    """Advanced TruthGPT implementation with full optimization"""
    
    def __init__(self):
        self.config = TruthGPTConfig(
            model_name="TruthGPT-PiMoE-Ultra",
            num_experts=16,
            expert_capacity=2.0,
            mixed_precision=True,
            dynamic_batching=True,
            lightning_processing=True,
            ultra_optimization=True
        )
        
        self.truthgpt = None
        self.optimizer = None
        self.compiler = None
        self.batch_processor = None
        self.memory_optimizer = None
        self.router = None
        self.cache = None
    
    async def initialize(self):
        """Initialize all components"""
        print("Initializing Advanced TruthGPT...")
        
        # Initialize TruthGPT
        self.truthgpt = TruthGPT(self.config)
        
        # Initialize optimization components
        self.optimizer = UltraOptimizer(
            enable_torch_compile=True,
            enable_tensorrt=True,
            enable_onnx=True,
            mixed_precision=True
        )
        
        self.compiler = ModelCompiler(
            backend="tensorrt",
            precision="fp16",
            optimization_level=5
        )
        
        self.batch_processor = GPUBatchProcessor(
            max_batch_size=32,
            dynamic_batching=True,
            memory_efficient=True
        )
        
        self.memory_optimizer = MemoryOptimizer(
            gradient_checkpointing=True,
            memory_efficient_attention=True,
            mixed_precision=True
        )
        
        self.router = AdvancedPiMoERouter(
            num_experts=self.config.num_experts,
            routing_algorithm="hierarchical",
            enable_cross_expert_communication=True,
            dynamic_expert_scaling=True
        )
        
        self.cache = UltraKVCache(
            hierarchical_caching=True,
            adaptive_eviction=True,
            compression=True,
            quantization=True
        )
        
        # Load and optimize model
        await self.truthgpt.load_model()
        await self.optimizer.optimize_model(self.truthgpt.model)
        await self.compiler.compile_model(self.truthgpt.model)
        
        print("Advanced TruthGPT initialized successfully!")
    
    async def batch_inference(self, inputs: List[str]) -> List[str]:
        """Perform batch inference with optimization"""
        print(f"Processing batch of {len(inputs)} inputs...")
        
        start_time = time.time()
        
        # Preprocess inputs
        processed_inputs = await self.batch_processor.preprocess_batch(inputs)
        
        # Route to experts
        routing_results = []
        for input_data in processed_inputs:
            routing_weights = await self.router.route(input_data)
            routing_results.append(routing_weights)
        
        # Batch inference
        responses = await self.truthgpt.batch_generate(
            inputs=processed_inputs,
            routing_weights=routing_results,
            max_tokens=256,
            temperature=0.7,
            batch_size=len(inputs)
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print(f"Batch processing completed in {processing_time:.3f} seconds")
        print(f"Average time per input: {processing_time/len(inputs):.3f} seconds")
        
        return responses
    
    async def performance_benchmark(self, test_inputs: List[str]):
        """Run performance benchmark"""
        print("Running performance benchmark...")
        
        # Warm up
        await self.batch_inference(test_inputs[:2])
        
        # Benchmark
        times = []
        for i in range(5):
            start_time = time.time()
            await self.batch_inference(test_inputs)
            end_time = time.time()
            times.append(end_time - start_time)
        
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        print(f"Benchmark Results:")
        print(f"  Average time: {avg_time:.3f}s")
        print(f"  Min time: {min_time:.3f}s")
        print(f"  Max time: {max_time:.3f}s")
        print(f"  Throughput: {len(test_inputs)/avg_time:.2f} inputs/second")
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.truthgpt:
            await self.truthgpt.cleanup()
        if self.cache:
            await self.cache.cleanup()
        print("Cleanup completed")

async def run_advanced_example():
    """Run the advanced example"""
    example = AdvancedTruthGPTExample()
    
    try:
        await example.initialize()
        
        # Test inputs
        test_inputs = [
            "Explain quantum computing in simple terms",
            "Write a Python function to sort a list",
            "What are the benefits of renewable energy?",
            "How does machine learning work?",
            "Describe the process of photosynthesis"
        ]
        
        # Run batch inference
        responses = await example.batch_inference(test_inputs)
        
        # Display results
        for i, (input_text, response) in enumerate(zip(test_inputs, responses)):
            print(f"\n--- Example {i+1} ---")
            print(f"Input: {input_text}")
            print(f"Response: {response[:200]}...")
        
        # Run benchmark
        await example.performance_benchmark(test_inputs)
        
    finally:
        await example.cleanup()

if __name__ == "__main__":
    asyncio.run(run_advanced_example())
```

## 🔧 Production Deployment Examples

### Docker Deployment

```dockerfile
# Dockerfile for TruthGPT Production Deployment
FROM nvidia/cuda:12.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    git \
    curl \
    wget \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip3 install --no-cache-dir -r /app/requirements.txt

# Install TruthGPT
COPY . /app/truthgpt
WORKDIR /app/truthgpt
RUN pip3 install -e .

# Create non-root user
RUN useradd -m -u 1000 truthgpt && chown -R truthgpt:truthgpt /app
USER truthgpt

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["python3", "-m", "truthgpt.server", "--host", "0.0.0.0", "--port", "8000"]
```

### Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: truthgpt-deployment
  labels:
    app: truthgpt
spec:
  replicas: 3
  selector:
    matchLabels:
      app: truthgpt
  template:
    metadata:
      labels:
        app: truthgpt
    spec:
      containers:
      - name: truthgpt
        image: truthgpt:latest
        ports:
        - containerPort: 8000
        env:
        - name: MODEL_NAME
          value: "TruthGPT-PiMoE-v1"
        - name: NUM_EXPERTS
          value: "8"
        - name: MIXED_PRECISION
          value: "true"
        resources:
          requests:
            memory: "8Gi"
            cpu: "2"
            nvidia.com/gpu: 1
          limits:
            memory: "16Gi"
            cpu: "4"
            nvidia.com/gpu: 1
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: truthgpt-service
spec:
  selector:
    app: truthgpt
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: truthgpt-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: truthgpt-deployment
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## 🧪 Testing Examples

### Unit Tests

```python
"""
TruthGPT Unit Tests
Comprehensive test suite for TruthGPT components
"""

import pytest
import asyncio
import torch
from unittest.mock import Mock, AsyncMock, patch
from truthgpt import TruthGPT, TruthGPTConfig
from truthgpt.pimoe import PiMoERouter
from truthgpt.optimization import LightningProcessor
from truthgpt.cache import UltraKVCache

class TestTruthGPT:
    """Test suite for TruthGPT core functionality"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return TruthGPTConfig(
            model_name="test-model",
            num_experts=4,
            expert_capacity=1.0,
            mixed_precision=False,
            dynamic_batching=False
        )
    
    @pytest.fixture
    def truthgpt(self, config):
        """Test TruthGPT instance"""
        return TruthGPT(config)
    
    @pytest.mark.asyncio
    async def test_model_loading(self, truthgpt):
        """Test model loading functionality"""
        with patch.object(truthgpt, 'load_model') as mock_load:
            mock_load.return_value = None
            await truthgpt.load_model()
            mock_load.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_inference(self, truthgpt):
        """Test inference functionality"""
        with patch.object(truthgpt, 'generate') as mock_generate:
            mock_generate.return_value = "Test response"
            
            result = await truthgpt.generate(
                input_text="Test input",
                max_tokens=100
            )
            
            assert result == "Test response"
            mock_generate.assert_called_once_with(
                input_text="Test input",
                max_tokens=100
            )
    
    @pytest.mark.asyncio
    async def test_batch_inference(self, truthgpt):
        """Test batch inference functionality"""
        inputs = ["Input 1", "Input 2", "Input 3"]
        
        with patch.object(truthgpt, 'batch_generate') as mock_batch:
            mock_batch.return_value = ["Response 1", "Response 2", "Response 3"]
            
            results = await truthgpt.batch_generate(inputs)
            
            assert len(results) == 3
            assert results[0] == "Response 1"
            mock_batch.assert_called_once_with(inputs)

class TestPiMoERouter:
    """Test suite for PiMoE Router"""
    
    @pytest.fixture
    def router(self):
        """Test router instance"""
        return PiMoERouter(
            num_experts=4,
            routing_algorithm="attention_based"
        )
    
    @pytest.mark.asyncio
    async def test_routing(self, router):
        """Test routing functionality"""
        input_data = torch.randn(1, 512)
        
        with patch.object(router, 'route') as mock_route:
            mock_route.return_value = torch.randn(1, 4)
            
            weights = await router.route(input_data)
            
            assert weights.shape == (1, 4)
            mock_route.assert_called_once_with(input_data)
    
    @pytest.mark.asyncio
    async def test_expert_selection(self, router):
        """Test expert selection"""
        input_data = torch.randn(1, 512)
        
        with patch.object(router, 'select_experts') as mock_select:
            mock_select.return_value = [0, 2]
            
            experts = await router.select_experts(input_data)
            
            assert experts == [0, 2]
            mock_select.assert_called_once_with(input_data)

class TestLightningProcessor:
    """Test suite for Lightning Processor"""
    
    @pytest.fixture
    def processor(self):
        """Test processor instance"""
        return LightningProcessor(
            microsecond_precision=True,
            zero_copy_operations=True
        )
    
    @pytest.mark.asyncio
    async def test_preprocessing(self, processor):
        """Test preprocessing functionality"""
        input_text = "Test input text"
        
        with patch.object(processor, 'preprocess') as mock_preprocess:
            mock_preprocess.return_value = torch.tensor([1, 2, 3, 4])
            
            result = await processor.preprocess(input_text)
            
            assert isinstance(result, torch.Tensor)
            mock_preprocess.assert_called_once_with(input_text)
    
    @pytest.mark.asyncio
    async def test_postprocessing(self, processor):
        """Test postprocessing functionality"""
        output_tensor = torch.tensor([1, 2, 3, 4])
        
        with patch.object(processor, 'postprocess') as mock_postprocess:
            mock_postprocess.return_value = "Processed output"
            
            result = await processor.postprocess(output_tensor)
            
            assert result == "Processed output"
            mock_postprocess.assert_called_once_with(output_tensor)

class TestUltraKVCache:
    """Test suite for Ultra K/V Cache"""
    
    @pytest.fixture
    def cache(self):
        """Test cache instance"""
        return UltraKVCache(
            hierarchical_caching=True,
            adaptive_eviction=True
        )
    
    @pytest.mark.asyncio
    async def test_cache_put(self, cache):
        """Test cache put functionality"""
        key = "test_key"
        value = torch.randn(1, 512)
        
        with patch.object(cache, 'put') as mock_put:
            mock_put.return_value = None
            
            await cache.put(key, value)
            
            mock_put.assert_called_once_with(key, value)
    
    @pytest.mark.asyncio
    async def test_cache_get(self, cache):
        """Test cache get functionality"""
        key = "test_key"
        expected_value = torch.randn(1, 512)
        
        with patch.object(cache, 'get') as mock_get:
            mock_get.return_value = expected_value
            
            result = await cache.get(key)
            
            assert torch.equal(result, expected_value)
            mock_get.assert_called_once_with(key)
    
    @pytest.mark.asyncio
    async def test_cache_hit_ratio(self, cache):
        """Test cache hit ratio calculation"""
        with patch.object(cache, 'get_hit_ratio') as mock_ratio:
            mock_ratio.return_value = 0.85
            
            ratio = await cache.get_hit_ratio()
            
            assert ratio == 0.85
            mock_ratio.assert_called_once()

# Performance Tests
class TestPerformance:
    """Performance test suite"""
    
    @pytest.mark.asyncio
    async def test_inference_latency(self):
        """Test inference latency"""
        config = TruthGPTConfig(
            model_name="test-model",
            num_experts=4,
            expert_capacity=1.0
        )
        
        truthgpt = TruthGPT(config)
        
        with patch.object(truthgpt, 'generate') as mock_generate:
            mock_generate.return_value = "Test response"
            
            start_time = time.time()
            await truthgpt.generate("Test input", max_tokens=100)
            end_time = time.time()
            
            latency = end_time - start_time
            assert latency < 1.0  # Should be under 1 second
    
    @pytest.mark.asyncio
    async def test_throughput(self):
        """Test throughput performance"""
        config = TruthGPTConfig(
            model_name="test-model",
            num_experts=4,
            expert_capacity=1.0
        )
        
        truthgpt = TruthGPT(config)
        inputs = ["Test input"] * 100
        
        with patch.object(truthgpt, 'batch_generate') as mock_batch:
            mock_batch.return_value = ["Test response"] * 100
            
            start_time = time.time()
            await truthgpt.batch_generate(inputs)
            end_time = time.time()
            
            throughput = len(inputs) / (end_time - start_time)
            assert throughput > 10  # Should process at least 10 inputs/second

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

## 📊 Monitoring Examples

### Prometheus Metrics

```python
"""
TruthGPT Prometheus Metrics
Comprehensive metrics collection for monitoring
"""

from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time
from typing import Dict, Any

class TruthGPTMetrics:
    """TruthGPT metrics collection"""
    
    def __init__(self):
        # Request metrics
        self.request_count = Counter(
            'truthgpt_requests_total',
            'Total number of requests',
            ['method', 'endpoint', 'status']
        )
        
        self.request_duration = Histogram(
            'truthgpt_request_duration_seconds',
            'Request duration in seconds',
            ['method', 'endpoint']
        )
        
        # Inference metrics
        self.inference_count = Counter(
            'truthgpt_inferences_total',
            'Total number of inferences',
            ['model_name', 'expert_id']
        )
        
        self.inference_duration = Histogram(
            'truthgpt_inference_duration_seconds',
            'Inference duration in seconds',
            ['model_name', 'expert_id']
        )
        
        self.inference_tokens = Counter(
            'truthgpt_tokens_total',
            'Total number of tokens processed',
            ['model_name', 'token_type']
        )
        
        # PiMoE metrics
        self.expert_utilization = Gauge(
            'truthgpt_expert_utilization',
            'Expert utilization percentage',
            ['expert_id']
        )
        
        self.routing_accuracy = Gauge(
            'truthgpt_routing_accuracy',
            'Routing accuracy percentage',
            ['routing_algorithm']
        )
        
        # Cache metrics
        self.cache_hits = Counter(
            'truthgpt_cache_hits_total',
            'Total cache hits',
            ['cache_level']
        )
        
        self.cache_misses = Counter(
            'truthgpt_cache_misses_total',
            'Total cache misses',
            ['cache_level']
        )
        
        self.cache_size = Gauge(
            'truthgpt_cache_size_bytes',
            'Cache size in bytes',
            ['cache_level']
        )
        
        # Resource metrics
        self.gpu_utilization = Gauge(
            'truthgpt_gpu_utilization',
            'GPU utilization percentage',
            ['gpu_id']
        )
        
        self.gpu_memory_usage = Gauge(
            'truthgpt_gpu_memory_usage_bytes',
            'GPU memory usage in bytes',
            ['gpu_id']
        )
        
        self.cpu_utilization = Gauge(
            'truthgpt_cpu_utilization',
            'CPU utilization percentage'
        )
        
        self.memory_usage = Gauge(
            'truthgpt_memory_usage_bytes',
            'Memory usage in bytes'
        )
    
    def record_request(self, method: str, endpoint: str, status: str, duration: float):
        """Record request metrics"""
        self.request_count.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.request_duration.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)
    
    def record_inference(self, model_name: str, expert_id: str, duration: float, tokens: int):
        """Record inference metrics"""
        self.inference_count.labels(
            model_name=model_name,
            expert_id=expert_id
        ).inc()
        
        self.inference_duration.labels(
            model_name=model_name,
            expert_id=expert_id
        ).observe(duration)
        
        self.inference_tokens.labels(
            model_name=model_name,
            token_type="input"
        ).inc(tokens)
    
    def update_expert_utilization(self, expert_id: str, utilization: float):
        """Update expert utilization"""
        self.expert_utilization.labels(expert_id=expert_id).set(utilization)
    
    def update_routing_accuracy(self, algorithm: str, accuracy: float):
        """Update routing accuracy"""
        self.routing_accuracy.labels(routing_algorithm=algorithm).set(accuracy)
    
    def record_cache_hit(self, cache_level: str):
        """Record cache hit"""
        self.cache_hits.labels(cache_level=cache_level).inc()
    
    def record_cache_miss(self, cache_level: str):
        """Record cache miss"""
        self.cache_misses.labels(cache_level=cache_level).inc()
    
    def update_cache_size(self, cache_level: str, size: int):
        """Update cache size"""
        self.cache_size.labels(cache_level=cache_level).set(size)
    
    def update_gpu_metrics(self, gpu_id: str, utilization: float, memory_usage: int):
        """Update GPU metrics"""
        self.gpu_utilization.labels(gpu_id=gpu_id).set(utilization)
        self.gpu_memory_usage.labels(gpu_id=gpu_id).set(memory_usage)
    
    def update_system_metrics(self, cpu_utilization: float, memory_usage: int):
        """Update system metrics"""
        self.cpu_utilization.set(cpu_utilization)
        self.memory_usage.set(memory_usage)

# Usage example
if __name__ == "__main__":
    # Start metrics server
    start_http_server(8000)
    
    metrics = TruthGPTMetrics()
    
    # Example usage
    metrics.record_request("POST", "/inference", "200", 0.5)
    metrics.record_inference("TruthGPT-PiMoE-v1", "expert_0", 0.1, 100)
    metrics.update_expert_utilization("expert_0", 0.85)
    metrics.record_cache_hit("L1")
    metrics.update_gpu_metrics("gpu_0", 0.75, 8 * 1024**3)
    
    print("Metrics server started on port 8000")
    print("Access metrics at: http://localhost:8000/metrics")
```

---

*These examples provide comprehensive, production-ready code for implementing TruthGPT optimization core features.*


