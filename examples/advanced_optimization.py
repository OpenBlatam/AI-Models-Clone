#!/usr/bin/env python3
"""
Advanced TruthGPT Optimization Examples

This module demonstrates advanced optimization techniques for TruthGPT.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional, Callable
import logging
import time
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Gradient Checkpointing
# ============================================================================

class CheckpointedModel(nn.Module):
    """Model with gradient checkpointing."""
    
    def __init__(self, num_layers: int = 10):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Linear(100, 100) for _ in range(num_layers)
        ])
        self.checkpoint_gradient = True
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward with optional gradient checkpointing."""
        for i, layer in enumerate(self.layers):
            if self.checkpoint_gradient and self.training:
                # Use gradient checkpointing every other layer
                if i % 2 == 0:
                    x = torch.utils.checkpoint.checkpoint(
                        layer, x, use_reentrant=False
                    )
                else:
                    x = layer(x)
            else:
                x = layer(x)
        
        return x


def example_1_gradient_checkpointing():
    """Example 1: Gradient checkpointing."""
    logger.info("=" * 60)
    logger.info("Example 1: Gradient Checkpointing")
    logger.info("=" * 60)
    
    model = CheckpointedModel(num_layers=10)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    
    # Enable checkpointing
    model.checkpoint_gradient = True
    
    # Measure memory with checkpointing
    if torch.cuda.is_available():
        model = model.cuda()
        
        # Measure peak memory
        torch.cuda.reset_peak_memory_stats()
        
        # Training step
        model.train()
        x = torch.randn(32, 100).cuda()
        y = torch.randn(32, 100).cuda()
        
        optimizer.zero_grad()
        output = model(x)
        loss = nn.functional.mse_loss(output, y)
        loss.backward()
        optimizer.step()
        
        peak_memory = torch.cuda.max_memory_allocated() / 1e9
        logger.info(f"Peak memory with checkpointing: {peak_memory:.2f} GB")
    
    logger.info("Example 1 completed!")


# ============================================================================
# Example 2: Expert Routing in PiMoE
# ============================================================================

@dataclass
class Expert:
    """Expert configuration."""
    expert_id: int
    capacity: int
    specialization: str


class ExpertRouter:
    """Router for expert assignment in PiMoE."""
    
    def __init__(self, num_experts: int = 4):
        self.num_experts = num_experts
        self.experts = [
            Expert(i, capacity=32, specialization=f"expert_{i}")
            for i in range(num_experts)
        ]
        self.routing_history = []
    
    def route_tokens(self, tokens: torch.Tensor, k: int = 2) -> Dict[int, torch.Tensor]:
        """Route tokens to top-k experts."""
        batch_size, seq_len = tokens.shape
        
        # Simple routing: hash-based assignment
        expert_assignments = {}
        for i in range(batch_size):
            for j in range(seq_len):
                # Hash-based routing
                expert_idx = int(tokens[i, j].item()) % self.num_experts
                
                if expert_idx not in expert_assignments:
                    expert_assignments[expert_idx] = []
                expert_assignments[expert_idx].append(tokens[i, j].item())
        
        # Convert to tensors
        expert_tokens = {}
        for expert_idx, token_list in expert_assignments.items():
            expert_tokens[expert_idx] = torch.tensor(token_list)
        
        return expert_tokens
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        return {
            'num_experts': self.num_experts,
            'expert_load': {
                i: len(self.experts[i].specialization)
                for i in range(self.num_experts)
            }
        }


def example_2_expert_routing():
    """Example 2: Expert routing in PiMoE."""
    logger.info("=" * 60)
    logger.info("Example 2: Expert Routing in PiMoE")
    logger.info("=" * 60)
    
    router = ExpertRouter(num_experts=4)
    
    # Create sample tokens
    tokens = torch.randint(0, 100, (4, 32))
    
    # Route tokens
    expert_tokens = router.route_tokens(tokens, k=2)
    
    logger.info(f"Routed tokens to {len(expert_tokens)} experts")
    for expert_idx, expert_token_list in expert_tokens.items():
        logger.info(f"Expert {expert_idx}: {len(expert_token_list)} tokens")
    
    # Get routing stats
    stats = router.get_routing_stats()
    logger.info(f"Routing statistics: {stats}")
    
    logger.info("Example 2 completed!")


# ============================================================================
# Example 3: Hierarchical K/V Cache
# ============================================================================

class HierarchicalCache:
    """Hierarchical K/V cache with multiple levels."""
    
    def __init__(self):
        self.hot_cache = {}  # Level 1: GPU memory
        self.warm_cache = {}  # Level 2: SSD
        self.cold_cache = {}  # Level 3: Disk
        self.hot_limit = 100
        self.warm_limit = 1000
    
    def get(self, key: str) -> Optional[torch.Tensor]:
        """Get from cache with hierarchical lookup."""
        # Check hot cache first
        if key in self.hot_cache:
            return self.hot_cache[key]
        
        # Check warm cache
        if key in self.warm_cache:
            value = self.warm_cache[key]
            # Promote to hot cache
            self._promote_to_hot(key, value)
            return value
        
        # Check cold cache
        if key in self.cold_cache:
            value = self.cold_cache[key]
            # Promote to warm cache
            self._promote_to_warm(key, value)
            return value
        
        return None
    
    def put(self, key: str, value: torch.Tensor) -> None:
        """Put in cache with hierarchical management."""
        # Add to hot cache
        if len(self.hot_cache) >= self.hot_limit:
            # Evict oldest from hot to warm
            oldest_key = next(iter(self.hot_cache))
            self.warm_cache[oldest_key] = self.hot_cache.pop(oldest_key)
        
        if len(self.warm_cache) >= self.warm_limit:
            # Evict oldest from warm to cold
            oldest_key = next(iter(self.warm_cache))
            self.cold_cache[oldest_key] = self.warm_cache.pop(oldest_key)
        
        self.hot_cache[key] = value
    
    def _promote_to_hot(self, key: str, value: torch.Tensor):
        """Promote value to hot cache."""
        if len(self.hot_cache) >= self.hot_limit:
            oldest_key = next(iter(self.hot_cache))
            self.warm_cache[oldest_key] = self.hot_cache.pop(oldest_key)
        
        self.hot_cache[key] = value
        if key in self.warm_cache:
            del self.warm_cache[key]
    
    def _promote_to_warm(self, key: str, value: torch.Tensor):
        """Promote value to warm cache."""
        if len(self.warm_cache) >= self.warm_limit:
            oldest_key = next(iter(self.warm_cache))
            self.cold_cache[oldest_key] = self.warm_cache.pop(oldest_key)
        
        self.warm_cache[key] = value
        if key in self.cold_cache:
            del self.cold_cache[key]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'hot_cache_size': len(self.hot_cache),
            'warm_cache_size': len(self.warm_cache),
            'cold_cache_size': len(self.cold_cache),
            'total_size': len(self.hot_cache) + len(self.warm_cache) + len(self.cold_cache)
        }


def example_3_hierarchical_cache():
    """Example 3: Hierarchical K/V cache."""
    logger.info("=" * 60)
    logger.info("Example 3: Hierarchical K/V Cache")
    logger.info("=" * 60)
    
    cache = HierarchicalCache()
    
    # Simulate cache operations
    for i in range(500):
        key = f"key_{i}"
        value = torch.randn(10)
        cache.put(key, value)
    
    # Test cache retrieval
    test_keys = ["key_0", "key_100", "key_200", "key_400"]
    for key in test_keys:
        value = cache.get(key)
        if value is not None:
            logger.info(f"Retrieved {key} from cache")
        else:
            logger.info(f"Cache miss for {key}")
    
    # Display statistics
    stats = cache.get_stats()
    logger.info(f"Cache statistics: {stats}")
    
    logger.info("Example 3 completed!")


# ============================================================================
# Example 4: Advanced TorchScript Compilation
# ============================================================================

def example_4_torchscript_compilation():
    """Example 4: Advanced TorchScript compilation."""
    logger.info("=" * 60)
    logger.info("Example 4: Advanced TorchScript Compilation")
    logger.info("=" * 60)
    
    # Create a more complex model
    class ComplexModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Conv1d(10, 20, kernel_size=3)
            self.lstm = nn.LSTM(20, 50, num_layers=2, batch_first=True)
            self.fc = nn.Linear(50, 10)
        
        def forward(self, x: torch.Tensor) -> torch.Tensor:
            x = self.conv(x)
            x = x.transpose(1, 2)
            x, _ = self.lstm(x)
            x = self.fc(x[:, -1, :])
            return x
    
    model = ComplexModel()
    model.eval()
    
    # Compile model
    try:
        # Method 1: torch.jit.script
        traced_model = torch.jit.trace(model, torch.randn(1, 10, 100))
        
        # Test compiled model
        with torch.no_grad():
            output = traced_model(torch.randn(1, 10, 100))
            logger.info(f"Traced model output shape: {output.shape}")
        
        # Method 2: torch.jit.script (for control flow)
        scripted_model = torch.jit.script(model)
        
        # Test scripted model
        with torch.no_grad():
            output = scripted_model(torch.randn(1, 10, 100))
            logger.info(f"Scripted model output shape: {output.shape}")
        
        logger.info("Model compilation successful!")
    
    except Exception as e:
        logger.error(f"Compilation failed: {e}")
    
    logger.info("Example 4 completed!")


# ============================================================================
# Example 5: Performance Benchmarking
# ============================================================================

class PerformanceBenchmark:
    """Performance benchmarking utilities."""
    
    @staticmethod
    def benchmark_inference(model: nn.Module, input_shape: tuple, num_runs: int = 100):
        """Benchmark model inference."""
        model.eval()
        
        # Warm-up
        with torch.no_grad():
            dummy_input = torch.randn(*input_shape)
            if torch.cuda.is_available():
                dummy_input = dummy_input.cuda()
                model = model.cuda()
            _ = model(dummy_input)
        
        # Benchmark
        if torch.cuda.is_available():
            torch.cuda.synchronize()
        
        times = []
        for _ in range(num_runs):
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            start = time.time()
            
            with torch.no_grad():
                output = model(dummy_input)
            
            if torch.cuda.is_available():
                torch.cuda.synchronize()
            
            end = time.time()
            times.append((end - start) * 1000)  # Convert to ms
        
        return {
            'mean': sum(times) / len(times),
            'std': (sum((t - sum(times) / len(times))**2 for t in times) / len(times))**0.5,
            'min': min(times),
            'max': max(times),
            'p50': sorted(times)[len(times)//2],
            'p95': sorted(times)[int(len(times) * 0.95)],
            'p99': sorted(times)[int(len(times) * 0.99)]
        }


def example_5_benchmarking():
    """Example 5: Performance benchmarking."""
    logger.info("=" * 60)
    logger.info("Example 5: Performance Benchmarking")
    logger.info("=" * 60)
    
    benchmark = PerformanceBenchmark()
    
    # Create model
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.layers = nn.ModuleList([
                nn.Linear(100, 100) for _ in range(5)
            ])
        
        def forward(self, x):
            for layer in self.layers:
                x = torch.relu(layer(x))
            return x
    
    model = TestModel()
    
    # Benchmark
    stats = benchmark.benchmark_inference(model, (32, 100), num_runs=100)
    
    logger.info("Inference Statistics:")
    logger.info(f"  Mean: {stats['mean']:.2f} ms")
    logger.info(f"  Std: {stats['std']:.2f} ms")
    logger.info(f"  Min: {stats['min']:.2f} ms")
    logger.info(f"  Max: {stats['max']:.2f} ms")
    logger.info(f"  P50: {stats['p50']:.2f} ms")
    logger.info(f"  P95: {stats['p95']:.2f} ms")
    logger.info(f"  P99: {stats['p99']:.2f} ms")
    
    logger.info("Example 5 completed!")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all advanced examples."""
    logger.info("Starting TruthGPT Advanced Optimization Examples")
    logger.info("=" * 60)
    
    try:
        example_1_gradient_checkpointing()
        example_2_expert_routing()
        example_3_hierarchical_cache()
        example_4_torchscript_compilation()
        example_5_benchmarking()
        
        logger.info("=" * 60)
        logger.info("All advanced examples completed successfully!")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


if __name__ == "__main__":
    main()



