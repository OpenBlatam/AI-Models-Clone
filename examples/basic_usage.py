#!/usr/bin/env python3
"""
Basic TruthGPT Usage Examples

This module demonstrates basic usage patterns for the TruthGPT optimization core.
"""

import torch
import torch.nn as nn
from typing import Dict, List, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# Example 1: Basic Model Creation
# ============================================================================

class SimpleModel(nn.Module):
    """Simple model example."""
    
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass."""
        x = self.relu(self.fc1(x))
        x = self.fc2(x)
        return x


def example_1_basic_usage():
    """Example 1: Basic model creation and training."""
    logger.info("=" * 60)
    logger.info("Example 1: Basic Model Usage")
    logger.info("=" * 60)
    
    # Create model
    model = SimpleModel(input_size=784, hidden_size=128, output_size=10)
    logger.info(f"Model created: {model}")
    
    # Create sample data
    batch_size = 32
    sample_input = torch.randn(batch_size, 784)
    
    # Forward pass
    with torch.no_grad():
        output = model(sample_input)
        logger.info(f"Input shape: {sample_input.shape}")
        logger.info(f"Output shape: {output.shape}")
    
    logger.info("Example 1 completed successfully!")


# ============================================================================
# Example 2: Mixed Precision Training
# ============================================================================

def example_2_mixed_precision():
    """Example 2: Mixed precision training."""
    logger.info("=" * 60)
    logger.info("Example 2: Mixed Precision Training")
    logger.info("=" * 60)
    
    model = SimpleModel(784, 128, 10)
    model = model.cuda() if torch.cuda.is_available() else model
    
    # Create optimizer
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()
    
    # Create scaler for mixed precision
    scaler = torch.cuda.amp.GradScaler()
    
    # Training loop with mixed precision
    model.train()
    for epoch in range(3):
        # Sample training data
        inputs = torch.randn(32, 784).cuda() if torch.cuda.is_available() else torch.randn(32, 784)
        targets = torch.randint(0, 10, (32,))
        targets = targets.cuda() if torch.cuda.is_available() else targets
        
        optimizer.zero_grad()
        
        # Use autocast for mixed precision
        with torch.cuda.amp.autocast():
            outputs = model(inputs)
            loss = criterion(outputs, targets)
        
        # Scale loss and backpropagate
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        logger.info(f"Epoch {epoch+1}/3, Loss: {loss.item():.4f}")
    
    logger.info("Example 2 completed successfully!")


# ============================================================================
# Example 3: Model Compilation
# ============================================================================

def example_3_model_compilation():
    """Example 3: Model compilation with TorchScript."""
    logger.info("=" * 60)
    logger.info("Example 3: Model Compilation")
    logger.info("=" * 60)
    
    model = SimpleModel(784, 128, 10)
    model.eval()
    
    # Compile model with TorchScript
    try:
        compiled_model = torch.jit.script(model)
        logger.info("Model compiled successfully with TorchScript")
        
        # Test compiled model
        sample_input = torch.randn(1, 784)
        with torch.no_grad():
            output = compiled_model(sample_input)
            logger.info(f"Compiled model output shape: {output.shape}")
    
    except Exception as e:
        logger.error(f"Compilation failed: {e}")
    
    logger.info("Example 3 completed!")


# ============================================================================
# Example 4: Dynamic Batching
# ============================================================================

class DynamicBatcher:
    """Dynamic batching for variable-length inputs."""
    
    def __init__(self, max_batch_size: int = 32):
        self.max_batch_size = max_batch_size
        self.pending_requests = []
    
    def add_request(self, request: Dict[str, Any]) -> None:
        """Add request to batch."""
        self.pending_requests.append(request)
    
    def should_batch(self) -> bool:
        """Check if we should create a batch."""
        return len(self.pending_requests) >= self.max_batch_size
    
    def create_batch(self) -> List[Dict[str, Any]]:
        """Create batch from pending requests."""
        batch = self.pending_requests[:self.max_batch_size]
        self.pending_requests = self.pending_requests[self.max_batch_size:]
        return batch


def example_4_dynamic_batching():
    """Example 4: Dynamic batching."""
    logger.info("=" * 60)
    logger.info("Example 4: Dynamic Batching")
    logger.info("=" * 60)
    
    batcher = DynamicBatcher(max_batch_size=4)
    
    # Add requests
    for i in range(10):
        request = {"input": torch.randn(10), "id": i}
        batcher.add_request(request)
        logger.info(f"Added request {i+1}")
        
        if batcher.should_batch():
            batch = batcher.create_batch()
            logger.info(f"Created batch with {len(batch)} requests")
    
    logger.info("Example 4 completed!")


# ============================================================================
# Example 5: K/V Cache Usage
# ============================================================================

class KVCache:
    """Simple K/V cache implementation."""
    
    def __init__(self, max_size: int = 1000):
        self.cache = {}
        self.max_size = max_size
        self.hits = 0
        self.misses = 0
    
    def get(self, key: str) -> Optional[torch.Tensor]:
        """Get value from cache."""
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        else:
            self.misses += 1
            return None
    
    def put(self, key: str, value: torch.Tensor) -> None:
        """Put value in cache."""
        if len(self.cache) >= self.max_size:
            # Simple eviction: remove oldest
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = value
    
    def get_stats(self) -> Dict[str, float]:
        """Get cache statistics."""
        total = self.hits + self.misses
        hit_rate = self.hits / total if total > 0 else 0
        return {
            'hits': self.hits,
            'misses': self.misses,
            'hit_rate': hit_rate,
            'size': len(self.cache)
        }


def example_5_kv_cache():
    """Example 5: K/V cache usage."""
    logger.info("=" * 60)
    logger.info("Example 5: K/V Cache Usage")
    logger.info("=" * 60)
    
    cache = KVCache(max_size=10)
    
    # Simulate cache operations
    for i in range(20):
        key = f"token_{i}"
        
        # Try to get from cache
        value = cache.get(key)
        
        if value is None:
            # Cache miss - compute value
            value = torch.randn(10)
            cache.put(key, value)
            logger.info(f"Cache miss for {key}, computed value")
        else:
            logger.info(f"Cache hit for {key}")
    
    # Display statistics
    stats = cache.get_stats()
    logger.info(f"Cache statistics: {stats}")
    
    logger.info("Example 5 completed!")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples."""
    logger.info("Starting TruthGPT Basic Usage Examples")
    logger.info("=" * 60)
    
    try:
        # Example 1: Basic usage
        example_1_basic_usage()
        
        # Example 2: Mixed precision
        if torch.cuda.is_available():
            example_2_mixed_precision()
        else:
            logger.warning("CUDA not available, skipping mixed precision example")
        
        # Example 3: Model compilation
        example_3_model_compilation()
        
        # Example 4: Dynamic batching
        example_4_dynamic_batching()
        
        # Example 5: K/V cache
        example_5_kv_cache()
        
        logger.info("=" * 60)
        logger.info("All examples completed successfully!")
        logger.info("=" * 60)
    
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


if __name__ == "__main__":
    main()



