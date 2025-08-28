#!/usr/bin/env python3
"""
🎨 Test Script for Diffusers Integration

This script tests the integration of Hugging Face Diffusers library
with the Enhanced AI Model Demos System.
"""

import time
import torch
import traceback
from typing import Dict, List, Any
import os

def print_header():
    """Print test header."""
    print("=" * 80)
    print("🎨 Diffusers Integration Test Suite")
    print("=" * 80)
    print()

def test_imports():
    """Test if all required packages can be imported."""
    print("📦 Testing package imports...")
    
    packages_to_test = [
        ("diffusers", "diffusers"),
        ("transformers", "transformers"),
        ("accelerate", "accelerate"),
        ("safetensors", "safetensors"),
        ("PIL", "PIL"),
        ("cv2", "cv2"),
        ("imageio", "imageio"),
        ("ftfy", "ftfy"),
        ("regex", "regex")
    ]
    
    failed_imports = []
    
    for package_name, import_name in packages_to_test:
        try:
            __import__(import_name)
            print(f"✅ {package_name} imported successfully")
        except ImportError as e:
            print(f"❌ {package_name} failed to import: {e}")
            failed_imports.append(package_name)
    
    if failed_imports:
        print(f"\n⚠️  Failed imports: {', '.join(failed_imports)}")
        return False
    
    print("✅ All packages imported successfully")
    return True

def test_basic_diffusers():
    """Test basic diffusers functionality."""
    print("\n🔧 Testing basic diffusers functionality...")
    
    try:
        from diffusers import StableDiffusionPipeline
        from PIL import Image
        import numpy as np
        
        # Test model loading
        print("Testing Stable Diffusion model loading...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        
        print("✅ Model loaded successfully")
        
        # Test basic generation (with reduced steps for testing)
        print("Testing basic image generation...")
        prompt = "A simple red circle on white background"
        
        # Use CPU for testing to avoid GPU memory issues
        pipe = pipe.to("cpu")
        
        # Generate with minimal steps for testing
        image = pipe(
            prompt,
            num_inference_steps=10,  # Very few steps for testing
            guidance_scale=7.5
        ).images[0]
        
        print(f"✅ Image generation successful - Size: {image.size}")
        
        # Test saving
        test_filename = "test_generated_image.png"
        image.save(test_filename)
        print(f"✅ Image saved as {test_filename}")
        
        # Clean up test file
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Basic diffusers test failed: {e}")
        traceback.print_exc()
        return False

def test_pipelines():
    """Test different diffusers pipelines."""
    print("\n🚀 Testing diffusers pipelines...")
    
    try:
        from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
        from PIL import Image
        import numpy as np
        
        # Test text-to-image pipeline
        print("Testing text-to-image pipeline...")
        pipe_t2i = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        pipe_t2i = pipe_t2i.to("cpu")
        
        # Test img2img pipeline
        print("Testing image-to-image pipeline...")
        pipe_i2i = StableDiffusionImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        pipe_i2i = pipe_i2i.to("cpu")
        
        # Create a simple test image
        test_image = Image.new('RGB', (256, 256), color='red')
        
        # Test img2img generation
        result = pipe_i2i(
            prompt="Turn this into a blue square",
            image=test_image,
            strength=0.5,
            guidance_scale=7.5,
            num_inference_steps=10
        )
        
        print(f"✅ Image-to-image pipeline working - Output size: {result.images[0].size}")
        
        return True
        
    except Exception as e:
        print(f"❌ Pipelines test failed: {e}")
        traceback.print_exc()
        return False

def test_advanced_features():
    """Test advanced diffusers features."""
    print("\n🎨 Testing advanced features...")
    
    try:
        from diffusers import StableDiffusionPipeline, DPMSolverMultistepScheduler
        from diffusers.utils import randn_tensor
        
        # Test scheduler configuration
        print("Testing scheduler configuration...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        
        # Change scheduler
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        print("✅ Scheduler changed successfully")
        
        # Test memory optimizations
        print("Testing memory optimizations...")
        try:
            pipe.enable_attention_slicing()
            print("✅ Attention slicing enabled")
        except Exception as e:
            print(f"⚠️  Attention slicing failed: {e}")
        
        # Test model configuration
        print("Testing model configuration...")
        config = pipe.config
        print(f"✅ Model config loaded - UNet: {config.unet_config}")
        
        return True
        
    except Exception as e:
        print(f"❌ Advanced features test failed: {e}")
        traceback.print_exc()
        return False

def test_controlnet_integration():
    """Test ControlNet integration."""
    print("\n🔬 Testing ControlNet integration...")
    
    try:
        from diffusers import StableDiffusionControlNetPipeline, ControlNetModel
        from PIL import Image
        import cv2
        import numpy as np
        
        # Test ControlNet model loading
        print("Testing ControlNet model loading...")
        controlnet = ControlNetModel.from_pretrained(
            "lllyasviel/sd-controlnet-canny",
            torch_dtype=torch.float16
        )
        print("✅ ControlNet model loaded successfully")
        
        # Test pipeline with ControlNet
        print("Testing ControlNet pipeline...")
        pipe = StableDiffusionControlNetPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            controlnet=controlnet,
            torch_dtype=torch.float16
        )
        pipe = pipe.to("cpu")
        
        # Create test image and detect edges
        test_image = Image.new('RGB', (256, 256), color='white')
        image_array = np.array(test_image)
        
        # Simple edge detection
        edges = cv2.Canny(image_array, 100, 200)
        edges = edges[:, :, None]
        edges = np.concatenate([edges, edges, edges], axis=2)
        edges_image = Image.fromarray(edges)
        
        print("✅ ControlNet pipeline created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ ControlNet integration test failed: {e}")
        traceback.print_exc()
        return False

def test_performance_optimization():
    """Test performance optimization features."""
    print("\n⚡ Testing performance optimization...")
    
    try:
        from diffusers import StableDiffusionPipeline
        import time
        
        # Test model loading with optimizations
        print("Testing model loading with optimizations...")
        pipe = StableDiffusionPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",
            torch_dtype=torch.float16
        )
        
        # Apply optimizations
        pipe.enable_attention_slicing()
        print("✅ Attention slicing enabled")
        
        # Test generation timing
        print("Testing generation timing...")
        prompt = "A simple test image"
        
        start_time = time.time()
        image = pipe(
            prompt,
            num_inference_steps=10,
            guidance_scale=7.5
        ).images[0]
        end_time = time.time()
        
        generation_time = end_time - start_time
        print(f"✅ Generation completed in {generation_time:.2f} seconds")
        
        # Test memory usage (if CUDA available)
        if torch.cuda.is_available():
            print("Testing GPU memory management...")
            torch.cuda.empty_cache()
            print(f"✅ GPU memory cleared. Current: {torch.cuda.memory_allocated()/1024**2:.2f}MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance optimization test failed: {e}")
        traceback.print_exc()
        return False

def test_error_handling():
    """Test error handling and edge cases."""
    print("\n🚨 Testing error handling...")
    
    try:
        from diffusers import StableDiffusionPipeline
        
        # Test invalid model name
        print("Testing invalid model handling...")
        try:
            pipe = StableDiffusionPipeline.from_pretrained("invalid-model-name")
            print("❌ Should have failed with invalid model name")
            return False
        except Exception as e:
            print(f"✅ Correctly handled invalid model: {type(e).__name__}")
        
        # Test empty prompt
        print("Testing empty prompt handling...")
        try:
            pipe = StableDiffusionPipeline.from_pretrained(
                "runwayml/stable-diffusion-v1-5",
                torch_dtype=torch.float16
            )
            pipe = pipe.to("cpu")
            
            # This should work but generate poor results
            image = pipe("", num_inference_steps=5).images[0]
            print("✅ Empty prompt handled (generated poor quality image)")
            
        except Exception as e:
            print(f"❌ Empty prompt handling failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        traceback.print_exc()
        return False

def run_performance_benchmarks():
    """Run performance benchmarks for different models."""
    print("\n📊 Running performance benchmarks...")
    
    try:
        from diffusers import StableDiffusionPipeline
        import time
        
        models_to_benchmark = [
            "runwayml/stable-diffusion-v1-5",
            "CompVis/stable-diffusion-v1-4"
        ]
        
        benchmark_results = {}
        
        for model_name in models_to_benchmark:
            print(f"Benchmarking {model_name}...")
            
            try:
                # Load model
                start_time = time.time()
                pipe = StableDiffusionPipeline.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16
                )
                pipe = pipe.to("cpu")
                load_time = time.time() - start_time
                
                # Prepare input
                prompt = "A simple test image for benchmarking"
                
                # Warmup
                _ = pipe(prompt, num_inference_steps=5)
                
                # Benchmark inference
                start_time = time.time()
                _ = pipe(prompt, num_inference_steps=10)
                inference_time = time.time() - start_time
                
                benchmark_results[model_name] = {
                    "load_time": load_time,
                    "inference_time": inference_time
                }
                
                print(f"✅ {model_name}: {inference_time:.2f}s inference, {load_time:.2f}s load")
                
            except Exception as e:
                print(f"❌ {model_name} benchmark failed: {e}")
                benchmark_results[model_name] = {"error": str(e)}
        
        # Print summary
        print("\n📈 Benchmark Summary:")
        print("-" * 60)
        for model_name, results in benchmark_results.items():
            if "error" in results:
                print(f"{model_name}: ❌ {results['error']}")
            else:
                print(f"{model_name}: {results['inference_time']:.2f}s inference, {results['load_time']:.2f}s load")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance benchmarks failed: {e}")
        traceback.print_exc()
        return False

def test_image_processing():
    """Test image processing capabilities."""
    print("\n🖼️ Testing image processing...")
    
    try:
        from PIL import Image
        import cv2
        import numpy as np
        
        # Test PIL operations
        print("Testing PIL operations...")
        test_image = Image.new('RGB', (512, 512), color='blue')
        test_image = test_image.resize((256, 256))
        print(f"✅ PIL operations - Image size: {test_image.size}")
        
        # Test OpenCV operations
        print("Testing OpenCV operations...")
        image_array = np.array(test_image)
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        print(f"✅ OpenCV operations - Grayscale shape: {gray.shape}")
        
        # Test image saving/loading
        print("Testing image I/O...")
        test_filename = "test_image_processing.png"
        test_image.save(test_filename)
        
        loaded_image = Image.open(test_filename)
        print(f"✅ Image I/O - Loaded size: {loaded_image.size}")
        
        # Clean up
        if os.path.exists(test_filename):
            os.remove(test_filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print_header()
    
    # Check if CUDA is available
    if torch.cuda.is_available():
        print(f"🖥️  CUDA available: {torch.cuda.device_count()} GPU(s)")
        print(f"   Primary GPU: {torch.cuda.get_device_name(0)}")
        print(f"   CUDA version: {torch.version.cuda}")
    else:
        print("ℹ️  CUDA not available, using CPU")
    
    print()
    
    # Run tests
    tests = [
        ("Package Imports", test_imports),
        ("Basic Diffusers", test_basic_diffusers),
        ("Pipelines", test_pipelines),
        ("Advanced Features", test_advanced_features),
        ("ControlNet Integration", test_controlnet_integration),
        ("Performance Optimization", test_performance_optimization),
        ("Error Handling", test_error_handling),
        ("Image Processing", test_image_processing),
        ("Performance Benchmarks", run_performance_benchmarks)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        print(f"🧪 Running: {test_name}")
        try:
            if test_func():
                passed_tests += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
            traceback.print_exc()
        
        print("-" * 60)
    
    # Print results
    print("\n" + "=" * 80)
    print("🎯 TEST RESULTS SUMMARY")
    print("=" * 80)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! Diffusers integration is working perfectly!")
    else:
        print(f"\n⚠️  {total_tests - passed_tests} test(s) failed. Check the output above for details.")
    
    print("\n📚 Next steps:")
    print("1. Check failed tests and resolve any issues")
    print("2. Review the DIFFUSERS_INTEGRATION_GUIDE.md for detailed usage")
    print("3. Integrate diffusers into your enhanced UI demos")
    print("4. Start building image generation applications!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Testing interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc()
