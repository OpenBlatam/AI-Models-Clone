
import sys
import os
from pathlib import Path

# Add project root to path
# CWD should be optimization_core
sys.path.append(os.getcwd())

from modules.truthgpt.integration import TruthGPTIntegrationConfig
from modules.truthgpt.optimization_utils import TruthGPTOptimizationConfig
from modules.feed_forward.optimization.ultra_optimization.zero_copy_optimizer import ZeroCopyConfig
from modules.feed_forward.optimization.ultra_optimization.model_compiler import CompilationConfig
from modules.feed_forward.optimization.ultra_optimization.dynamic_batcher import BatchingConfig

def test_pydantic_configs():
    print("🧪 Testing Pydantic Configs...")
    
    configs = [
        ("TruthGPTIntegrationConfig", TruthGPTIntegrationConfig()),
        ("TruthGPTOptimizationConfig", TruthGPTOptimizationConfig()),
        ("ZeroCopyConfig", ZeroCopyConfig()),
        ("CompilationConfig", CompilationConfig()),
        ("BatchingConfig", BatchingConfig())
    ]
    
    for name, config in configs:
        print(f"  Checking {name}...")
        # Test instantiation
        assert config is not None
        # Test model_dump
        data = config.model_dump()
        assert isinstance(data, dict)
        print(f"    ✅ {name} instantiated and dumped successfully.")
        
    print("\n🚀 All Pydantic config tests passed!")

if __name__ == "__main__":
    try:
        test_pydantic_configs()
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
