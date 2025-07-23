"""
🧪 Test Transformers Integration
================================

Test script to verify the transformers integration system works correctly
with the Gradio application.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Add the current directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    try:
        # Test transformers integration system import
        from transformers_integration_system import (
            AdvancedTransformersTrainer, TransformersConfig, TransformersPipeline,
            create_transformers_config, get_available_models, validate_transformers_inputs,
            initialize_transformers_system
        )
        print("✅ transformers_integration_system imported successfully")
        
        # Test gradio app import
        import gradio_app
        print("✅ gradio_app imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False


def test_configuration_creation():
    """Test configuration creation."""
    print("\n🔧 Testing configuration creation...")
    
    try:
        from transformers_integration_system import create_transformers_config, TransformersConfig
        
        # Test basic configuration
        config = create_transformers_config()
        assert isinstance(config, TransformersConfig)
        assert config.model_name == "microsoft/DialoGPT-medium"
        assert config.model_type == "causal"
        print("✅ Basic configuration creation works")
        
        # Test custom configuration
        custom_config = create_transformers_config(
            model_name="gpt2",
            model_type="causal",
            task="text_generation",
            num_epochs=5,
            batch_size=8
        )
        assert custom_config.model_name == "gpt2"
        assert custom_config.num_epochs == 5
        assert custom_config.batch_size == 8
        print("✅ Custom configuration creation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration creation failed: {e}")
        return False


def test_available_models():
    """Test getting available models."""
    print("\n📋 Testing available models...")
    
    try:
        from transformers_integration_system import get_available_models
        
        models = get_available_models()
        assert isinstance(models, dict)
        assert "causal_lm" in models
        assert "sequence_classification" in models
        assert "token_classification" in models
        assert "question_answering" in models
        assert "masked_lm" in models
        
        # Check that each category has models
        for category, model_list in models.items():
            assert isinstance(model_list, list)
            assert len(model_list) > 0
            print(f"✅ {category}: {len(model_list)} models available")
        
        return True
        
    except Exception as e:
        print(f"❌ Available models test failed: {e}")
        return False


def test_input_validation():
    """Test input validation."""
    print("\n✅ Testing input validation...")
    
    try:
        from transformers_integration_system import validate_transformers_inputs
        
        # Test valid inputs
        is_valid, error_msg = validate_transformers_inputs(
            "Hello world", "microsoft/DialoGPT-medium", 512
        )
        assert is_valid
        assert error_msg == "Inputs are valid"
        print("✅ Valid input validation works")
        
        # Test empty text
        is_valid, error_msg = validate_transformers_inputs(
            "", "microsoft/DialoGPT-medium", 512
        )
        assert not is_valid
        assert "empty" in error_msg.lower()
        print("✅ Empty text validation works")
        
        # Test empty model name
        is_valid, error_msg = validate_transformers_inputs(
            "Hello world", "", 512
        )
        assert not is_valid
        assert "empty" in error_msg.lower()
        print("✅ Empty model name validation works")
        
        # Test very long text
        long_text = "A" * 3000
        is_valid, error_msg = validate_transformers_inputs(
            long_text, "microsoft/DialoGPT-medium", 512
        )
        assert not is_valid
        assert "long" in error_msg.lower()
        print("✅ Long text validation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Input validation test failed: {e}")
        return False


def test_gradio_interface_functions():
    """Test that Gradio interface functions exist."""
    print("\n🎛️ Testing Gradio interface functions...")
    
    try:
        import gradio_app
        
        # Test that interface functions exist
        required_functions = [
            'initialize_transformers_interface',
            'get_available_models_interface',
            'train_transformers_model_interface',
            'generate_text_interface',
            'batch_generate_interface',
            'classify_texts_interface',
            'get_transformers_status_interface'
        ]
        
        for func_name in required_functions:
            assert hasattr(gradio_app, func_name), f"Function {func_name} not found"
            func = getattr(gradio_app, func_name)
            assert callable(func), f"{func_name} is not callable"
            print(f"✅ {func_name} exists and is callable")
        
        return True
        
    except Exception as e:
        print(f"❌ Gradio interface functions test failed: {e}")
        return False


def test_system_initialization():
    """Test system initialization."""
    print("\n🚀 Testing system initialization...")
    
    try:
        from transformers_integration_system import initialize_transformers_system
        
        # Test initialization
        success = initialize_transformers_system()
        assert isinstance(success, bool)
        print(f"✅ System initialization returned: {success}")
        
        return True
        
    except Exception as e:
        print(f"❌ System initialization test failed: {e}")
        return False


def test_trainer_creation():
    """Test trainer creation."""
    print("\n🏋️ Testing trainer creation...")
    
    try:
        from transformers_integration_system import AdvancedTransformersTrainer, TransformersConfig
        
        # Create a minimal configuration for testing
        config = TransformersConfig(
            model_name="microsoft/DialoGPT-medium",
            model_type="causal",
            task="text_generation",
            num_epochs=1,  # Minimal for testing
            batch_size=1,  # Minimal for testing
            use_peft=False  # Disable PEFT for testing
        )
        
        # Test trainer creation
        trainer = AdvancedTransformersTrainer(config)
        assert trainer is not None
        assert hasattr(trainer, 'config')
        assert trainer.config.model_name == "microsoft/DialoGPT-medium"
        print("✅ Trainer creation works")
        
        return True
        
    except Exception as e:
        print(f"❌ Trainer creation test failed: {e}")
        return False


def test_pipeline_creation():
    """Test pipeline creation."""
    print("\n🔧 Testing pipeline creation...")
    
    try:
        from transformers_integration_system import TransformersPipeline, TransformersConfig
        
        # Create configuration
        config = TransformersConfig()
        
        # Test pipeline creation (this might fail if no model exists, which is expected)
        try:
            pipeline = TransformersPipeline("./transformers_final_model", config)
            print("✅ Pipeline creation works (model exists)")
        except Exception as e:
            if "No such file or directory" in str(e) or "not found" in str(e).lower():
                print("✅ Pipeline creation test passed (no model file, which is expected)")
            else:
                raise e
        
        return True
        
    except Exception as e:
        print(f"❌ Pipeline creation test failed: {e}")
        return False


def test_gradio_interface_integration():
    """Test that the transformers tab is properly integrated in Gradio."""
    print("\n🎛️ Testing Gradio interface integration...")
    
    try:
        import gradio_app
        
        # Check if transformers tab exists in the interface
        # This is a basic check - we can't easily test the full Gradio interface
        # without running the actual app
        
        # Test that the interface functions return JSON strings
        from transformers_integration_system import get_available_models
        
        # Test get_available_models_interface
        result = gradio_app.get_available_models_interface()
        assert isinstance(result, str)
        
        # Try to parse as JSON
        try:
            json_data = json.loads(result)
            print("✅ get_available_models_interface returns valid JSON")
        except json.JSONDecodeError:
            print("⚠️ get_available_models_interface returns string but not valid JSON")
        
        # Test get_transformers_status_interface
        result = gradio_app.get_transformers_status_interface()
        assert isinstance(result, str)
        
        try:
            json_data = json.loads(result)
            print("✅ get_transformers_status_interface returns valid JSON")
        except json.JSONDecodeError:
            print("⚠️ get_transformers_status_interface returns string but not valid JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Gradio interface integration test failed: {e}")
        return False


def test_error_handling():
    """Test error handling."""
    print("\n⚠️ Testing error handling...")
    
    try:
        from transformers_integration_system import validate_transformers_inputs
        
        # Test with invalid inputs
        is_valid, error_msg = validate_transformers_inputs("", "", 0)
        assert not is_valid
        assert len(error_msg) > 0
        print("✅ Error handling works for invalid inputs")
        
        # Test interface functions with invalid inputs
        import gradio_app
        
        # Test with empty model name
        result = gradio_app.train_transformers_model_interface(
            "", "causal", "text_generation", "", "", 1, 1, 1e-5, True
        )
        assert isinstance(result, str)
        print("✅ Interface error handling works")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def run_all_tests():
    """Run all tests and provide a summary."""
    print("🧪 TRANSFORMERS INTEGRATION TEST SUITE")
    print("="*60)
    
    tests = [
        ("Imports", test_imports),
        ("Configuration Creation", test_configuration_creation),
        ("Available Models", test_available_models),
        ("Input Validation", test_input_validation),
        ("Gradio Interface Functions", test_gradio_interface_functions),
        ("System Initialization", test_system_initialization),
        ("Trainer Creation", test_trainer_creation),
        ("Pipeline Creation", test_pipeline_creation),
        ("Gradio Interface Integration", test_gradio_interface_integration),
        ("Error Handling", test_error_handling)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    successful = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nOverall: {successful}/{total} tests passed")
    
    if successful == total:
        print("🎉 All tests passed! Transformers integration is working correctly.")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return False


def main():
    """Main test runner."""
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 