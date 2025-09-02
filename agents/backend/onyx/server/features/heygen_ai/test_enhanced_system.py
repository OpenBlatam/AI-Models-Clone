#!/usr/bin/env python3
"""
Test script for Enhanced Advanced Distributed AI System
Tests core functionality and verifies system components
"""

import sys
import os
import logging
from pathlib import Path

# Add the core directory to the path
sys.path.append(str(Path(__file__).parent / "core"))

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        # Test core system import
        from advanced_distributed_ai_system import (
            AdvancedDistributedAISystem,
            DistributedAIConfig,
            AITaskType,
            NodeType,
            PrivacyLevel,
            CoordinationStrategy,
            QuantumBackend
        )
        print("✅ Core system imports successful")
        
        # Test factory functions
        from advanced_distributed_ai_system import (
            create_enhanced_distributed_ai_config,
            create_quantum_enhanced_distributed_ai_system,
            create_neuromorphic_enhanced_distributed_ai_system,
            create_hybrid_quantum_neuromorphic_system,
            create_minimal_distributed_ai_config,
            create_maximum_distributed_ai_config
        )
        print("✅ Factory function imports successful")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_config_creation():
    """Test configuration creation functions."""
    print("\n🔧 Testing configuration creation...")
    
    try:
        from advanced_distributed_ai_system import (
            create_minimal_distributed_ai_config,
            create_maximum_distributed_ai_config
        )
        
        # Test minimal config
        minimal_config = create_minimal_distributed_ai_config()
        print(f"✅ Minimal config created: {type(minimal_config)}")
        
        # Test maximum config
        maximum_config = create_maximum_distributed_ai_config()
        print(f"✅ Maximum config created: {type(maximum_config)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        return False

def test_system_initialization():
    """Test system initialization."""
    print("\n🚀 Testing system initialization...")
    
    try:
        from advanced_distributed_ai_system import (
            create_quantum_enhanced_distributed_ai_system,
            create_neuromorphic_enhanced_distributed_ai_system,
            create_hybrid_quantum_neuromorphic_system
        )
        
        # Test quantum system
        quantum_system = create_quantum_enhanced_distributed_ai_system()
        print(f"✅ Quantum system created: {type(quantum_system)}")
        
        # Test neuromorphic system
        neuromorphic_system = create_neuromorphic_enhanced_distributed_ai_system()
        print(f"✅ Neuromorphic system created: {type(neuromorphic_system)}")
        
        # Test hybrid system
        hybrid_system = create_hybrid_quantum_neuromorphic_system()
        print(f"✅ Hybrid system created: {type(hybrid_system)}")
        
        return True
        
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return False

def test_basic_functionality():
    """Test basic system functionality."""
    print("\n⚡ Testing basic functionality...")
    
    try:
        from advanced_distributed_ai_system import (
            create_hybrid_quantum_neuromorphic_system,
            AITaskType,
            NodeType,
            PrivacyLevel,
            CoordinationStrategy
        )
        
        # Create hybrid system
        system = create_hybrid_quantum_neuromorphic_system()
        
        # Test system status
        status = system.get_system_status()
        print(f"✅ System status retrieved: {type(status)}")
        
        # Test basic operations
        print(f"✅ System initialized: {system.initialized}")
        print(f"✅ System logger: {system.logger}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_demo_import():
    """Test that the enhanced demo can be imported."""
    print("\n🎭 Testing enhanced demo import...")
    
    try:
        # Test demo import
        demo_path = Path(__file__).parent / "run_enhanced_distributed_ai_demo.py"
        if demo_path.exists():
            print("✅ Enhanced demo file exists")
            
            # Try to import demo components
            sys.path.append(str(Path(__file__).parent))
            from run_enhanced_distributed_ai_demo import EnhancedDistributedAIDemo
            print("✅ Enhanced demo class imported successfully")
            
            return True
        else:
            print("❌ Enhanced demo file not found")
            return False
            
    except Exception as e:
        print(f"❌ Enhanced demo import failed: {e}")
        return False

def test_config_file():
    """Test that the enhanced configuration file exists."""
    print("\n📁 Testing configuration file...")
    
    try:
        config_path = Path(__file__).parent / "configs" / "enhanced_distributed_ai_config.yaml"
        if config_path.exists():
            print("✅ Enhanced configuration file exists")
            
            # Check file size
            file_size = config_path.stat().st_size
            print(f"✅ Configuration file size: {file_size} bytes")
            
            return True
        else:
            print("❌ Enhanced configuration file not found")
            return False
            
    except Exception as e:
        print(f"❌ Configuration file test failed: {e}")
        return False

def test_requirements_file():
    """Test that the enhanced requirements file exists."""
    print("\n📦 Testing requirements file...")
    
    try:
        req_path = Path(__file__).parent / "requirements_enhanced_distributed_ai.txt"
        if req_path.exists():
            print("✅ Enhanced requirements file exists")
            
            # Check file size
            file_size = req_path.stat().st_size
            print(f"✅ Requirements file size: {file_size} bytes")
            
            return True
        else:
            print("❌ Enhanced requirements file not found")
            return False
            
    except Exception as e:
        print(f"❌ Requirements file test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Enhanced Advanced Distributed AI System - System Test")
    print("=" * 60)
    
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    
    # Run tests
    tests = [
        ("Module Imports", test_imports),
        ("Configuration Creation", test_config_creation),
        ("System Initialization", test_system_initialization),
        ("Basic Functionality", test_basic_functionality),
        ("Enhanced Demo Import", test_demo_import),
        ("Configuration File", test_config_file),
        ("Requirements File", test_requirements_file)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"⚠️  {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Enhanced system is ready.")
        return 0
    else:
        print(f"⚠️  {total - passed} tests failed. Please check the system.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
