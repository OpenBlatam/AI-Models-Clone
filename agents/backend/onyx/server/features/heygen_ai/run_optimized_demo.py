#!/usr/bin/env python3
"""
Optimized Deep Learning Demo Runner
=================================

Comprehensive demo showcasing all optimized components:
- Text generation with transformers
- Image generation with diffusion models
- Attention analysis
- Gradio interface
- Performance monitoring
"""

import os
import sys
import logging
import time
import torch
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import optimized modules
from deep_learning_optimized import (
    OptimizedTransformerModel, OptimizedDiffusionModel,
    OptimizedTrainer, TrainingConfig
)
from attention_mechanisms_optimized import OptimizedTransformerModel as AttentionModel
from diffusion_models_optimized import OptimizedDiffusionPipeline
from gradio_interface_optimized import OptimizedGradioInterface

# =============================================================================
# Demo Configuration
# =============================================================================

class DemoConfig:
    """Configuration for the optimized demo."""
    
    # Hardware settings
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    USE_MIXED_PRECISION = True
    
    # Model settings
    TEXT_MODEL_NAME = "gpt2"
    DIFFUSION_MODEL_NAME = "runwayml/stable-diffusion-v1-5"
    
    # Demo settings
    ENABLE_TEXT_GENERATION = True
    ENABLE_IMAGE_GENERATION = True
    ENABLE_ATTENTION_ANALYSIS = True
    ENABLE_GRADIO_INTERFACE = True
    
    # Performance settings
    MAX_TEXT_LENGTH = 256
    MAX_IMAGE_SIZE = 512
    NUM_INFERENCE_STEPS = 30
    
    # Logging settings
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# =============================================================================
# Optimized Demo Runner
# =============================================================================

class OptimizedDemoRunner:
    """Production-ready demo runner with comprehensive features."""
    
    def __init__(self, config: DemoConfig):
        self.config = config
        self.logger = self._setup_logging()
        self.models = {}
        self.performance_metrics = {}
        
        self.logger.info(f"Initializing demo on device: {self.config.DEVICE}")
        self._initialize_models()
    
    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging."""
        logging.basicConfig(
            level=self.config.LOG_LEVEL,
            format=self.config.LOG_FORMAT,
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler("demo.log")
            ]
        )
        return logging.getLogger(__name__)
    
    def _initialize_models(self):
        """Initialize all models with error handling."""
        try:
            if self.config.ENABLE_TEXT_GENERATION:
                self.logger.info("Initializing text generation model...")
                self.models["text_generator"] = OptimizedTransformerModel(
                    model_name=self.config.TEXT_MODEL_NAME
                )
            
            if self.config.ENABLE_IMAGE_GENERATION:
                self.logger.info("Initializing diffusion model...")
                self.models["image_generator"] = OptimizedDiffusionPipeline(
                    model_name=self.config.DIFFUSION_MODEL_NAME,
                    device=self.config.DEVICE
                )
            
            if self.config.ENABLE_ATTENTION_ANALYSIS:
                self.logger.info("Initializing attention model...")
                self.models["attention_model"] = AttentionModel(
                    vocab_size=50000,
                    embed_dim=512,
                    num_layers=6,
                    num_heads=8,
                    ff_dim=2048
                )
            
            self.logger.info("All models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize models: {e}")
            raise
    
    def run_text_generation_demo(self) -> Dict[str, Any]:
        """Run text generation demo with performance monitoring."""
        if not self.config.ENABLE_TEXT_GENERATION:
            return {"status": "disabled"}
        
        try:
            self.logger.info("Running text generation demo...")
            
            # Sample prompts
            prompts = [
                "The future of artificial intelligence is",
                "In a world where technology advances rapidly,",
                "The most important thing about machine learning is"
            ]
            
            results = []
            start_time = time.time()
            
            for prompt in prompts:
                prompt_start = time.time()
                
                # Generate text
                generated_text = self.models["text_generator"].generate_text(
                    prompt=prompt,
                    max_length=self.config.MAX_TEXT_LENGTH,
                    temperature=0.8,
                    do_sample=True
                )
                
                prompt_time = time.time() - prompt_start
                
                results.append({
                    "prompt": prompt,
                    "generated_text": generated_text,
                    "generation_time": prompt_time
                })
                
                self.logger.info(f"Generated text for: {prompt[:50]}...")
            
            total_time = time.time() - start_time
            
            self.performance_metrics["text_generation"] = {
                "total_time": total_time,
                "avg_time_per_prompt": total_time / len(prompts),
                "num_prompts": len(prompts)
            }
            
            return {
                "status": "success",
                "results": results,
                "performance": self.performance_metrics["text_generation"]
            }
            
        except Exception as e:
            self.logger.error(f"Text generation demo failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_image_generation_demo(self) -> Dict[str, Any]:
        """Run image generation demo with performance monitoring."""
        if not self.config.ENABLE_IMAGE_GENERATION:
            return {"status": "disabled"}
        
        try:
            self.logger.info("Running image generation demo...")
            
            # Sample prompts
            prompts = [
                "A beautiful sunset over mountains, high quality, detailed",
                "A futuristic city skyline at night, neon lights",
                "A serene forest with sunlight filtering through trees"
            ]
            
            results = []
            start_time = time.time()
            
            for prompt in prompts:
                prompt_start = time.time()
                
                # Generate image
                images = self.models["image_generator"].generate_image(
                    prompt=prompt,
                    num_inference_steps=self.config.NUM_INFERENCE_STEPS,
                    width=self.config.MAX_IMAGE_SIZE,
                    height=self.config.MAX_IMAGE_SIZE,
                    seed=42  # Fixed seed for reproducibility
                )
                
                prompt_time = time.time() - prompt_start
                
                # Save image
                if images:
                    image_path = f"generated_image_{len(results)}.png"
                    images[0].save(image_path)
                    
                    results.append({
                        "prompt": prompt,
                        "image_path": image_path,
                        "generation_time": prompt_time
                    })
                    
                    self.logger.info(f"Generated image for: {prompt[:50]}...")
            
            total_time = time.time() - start_time
            
            self.performance_metrics["image_generation"] = {
                "total_time": total_time,
                "avg_time_per_image": total_time / len(prompts),
                "num_images": len(prompts)
            }
            
            return {
                "status": "success",
                "results": results,
                "performance": self.performance_metrics["image_generation"]
            }
            
        except Exception as e:
            self.logger.error(f"Image generation demo failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_attention_analysis_demo(self) -> Dict[str, Any]:
        """Run attention analysis demo with performance monitoring."""
        if not self.config.ENABLE_ATTENTION_ANALYSIS:
            return {"status": "disabled"}
        
        try:
            self.logger.info("Running attention analysis demo...")
            
            # Sample texts for analysis
            texts = [
                "The quick brown fox jumps over the lazy dog.",
                "Artificial intelligence is transforming the world.",
                "Machine learning models require careful attention to detail."
            ]
            
            results = []
            start_time = time.time()
            
            for text in texts:
                text_start = time.time()
                
                # Analyze attention
                attention_result = self.models["attention_model"].analyze_attention(
                    text=text,
                    max_length=128
                )
                
                text_time = time.time() - text_start
                
                results.append({
                    "text": text,
                    "attention_analysis": attention_result,
                    "analysis_time": text_time
                })
                
                self.logger.info(f"Analyzed attention for: {text[:50]}...")
            
            total_time = time.time() - start_time
            
            self.performance_metrics["attention_analysis"] = {
                "total_time": total_time,
                "avg_time_per_text": total_time / len(texts),
                "num_texts": len(texts)
            }
            
            return {
                "status": "success",
                "results": results,
                "performance": self.performance_metrics["attention_analysis"]
            }
            
        except Exception as e:
            self.logger.error(f"Attention analysis demo failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_gradio_interface_demo(self) -> Dict[str, Any]:
        """Run Gradio interface demo."""
        if not self.config.ENABLE_GRADIO_INTERFACE:
            return {"status": "disabled"}
        
        try:
            self.logger.info("Launching Gradio interface...")
            
            # Create and launch interface
            interface = OptimizedGradioInterface(device=self.config.DEVICE)
            
            self.logger.info("Gradio interface launched successfully")
            
            return {
                "status": "success",
                "message": "Gradio interface is running"
            }
            
        except Exception as e:
            self.logger.error(f"Gradio interface demo failed: {e}")
            return {"status": "error", "error": str(e)}
    
    def run_comprehensive_demo(self) -> Dict[str, Any]:
        """Run comprehensive demo with all components."""
        self.logger.info("Starting comprehensive demo...")
        
        demo_results = {
            "text_generation": self.run_text_generation_demo(),
            "image_generation": self.run_image_generation_demo(),
            "attention_analysis": self.run_attention_analysis_demo(),
            "gradio_interface": self.run_gradio_interface_demo()
        }
        
        # Calculate overall performance
        total_time = sum(
            metrics.get("total_time", 0) 
            for metrics in self.performance_metrics.values()
        )
        
        overall_performance = {
            "total_demo_time": total_time,
            "components": self.performance_metrics,
            "success_rate": sum(
                1 for result in demo_results.values() 
                if result.get("status") == "success"
            ) / len(demo_results)
        }
        
        demo_results["overall_performance"] = overall_performance
        
        self.logger.info("Comprehensive demo completed")
        self._print_demo_summary(demo_results)
        
        return demo_results
    
    def _print_demo_summary(self, results: Dict[str, Any]):
        """Print comprehensive demo summary."""
        print("\n" + "="*60)
        print("🎯 OPTIMIZED DEEP LEARNING DEMO SUMMARY")
        print("="*60)
        
        for component, result in results.items():
            if component == "overall_performance":
                continue
                
            status = result.get("status", "unknown")
            status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️"
            
            print(f"\n{status_icon} {component.upper().replace('_', ' ')}: {status}")
            
            if status == "success" and "performance" in result:
                perf = result["performance"]
                print(f"   ⏱️  Total time: {perf.get('total_time', 0):.2f}s")
                print(f"   📊 Average time: {perf.get('avg_time_per_prompt', perf.get('avg_time_per_image', perf.get('avg_time_per_text', 0))):.2f}s")
        
        if "overall_performance" in results:
            overall = results["overall_performance"]
            print(f"\n🎯 OVERALL PERFORMANCE:")
            print(f"   ⏱️  Total demo time: {overall['total_demo_time']:.2f}s")
            print(f"   📈 Success rate: {overall['success_rate']:.1%}")
        
        print("\n" + "="*60)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report."""
        return {
            "performance_metrics": self.performance_metrics,
            "device_info": {
                "device": self.config.DEVICE,
                "cuda_available": torch.cuda.is_available(),
                "cuda_device_count": torch.cuda.device_count() if torch.cuda.is_available() else 0
            },
            "model_info": {
                "text_model": self.config.TEXT_MODEL_NAME,
                "diffusion_model": self.config.DIFFUSION_MODEL_NAME,
                "mixed_precision": self.config.USE_MIXED_PRECISION
            }
        }

# =============================================================================
# Demo Examples
# =============================================================================

def run_quick_demo():
    """Run a quick demo with minimal components."""
    config = DemoConfig()
    config.ENABLE_IMAGE_GENERATION = False  # Skip for speed
    config.ENABLE_GRADIO_INTERFACE = False  # Skip for speed
    
    runner = OptimizedDemoRunner(config)
    results = runner.run_comprehensive_demo()
    
    return results

def run_full_demo():
    """Run full demo with all components."""
    config = DemoConfig()
    
    runner = OptimizedDemoRunner(config)
    results = runner.run_comprehensive_demo()
    
    return results

def run_gradio_only():
    """Run only the Gradio interface."""
    config = DemoConfig()
    config.ENABLE_TEXT_GENERATION = False
    config.ENABLE_IMAGE_GENERATION = False
    config.ENABLE_ATTENTION_ANALYSIS = False
    
    runner = OptimizedDemoRunner(config)
    results = runner.run_gradio_interface_demo()
    
    return results

# =============================================================================
# Main Function
# =============================================================================

def main():
    """Main function with command line argument parsing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Optimized Deep Learning Demo")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "gradio"],
        default="quick",
        help="Demo mode to run"
    )
    parser.add_argument(
        "--device",
        choices=["cpu", "cuda"],
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to run on"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level"
    )
    
    args = parser.parse_args()
    
    # Update config based on arguments
    config = DemoConfig()
    config.DEVICE = args.device
    config.LOG_LEVEL = getattr(logging, args.log_level)
    
    print(f"🚀 Starting Optimized Deep Learning Demo")
    print(f"📱 Mode: {args.mode}")
    print(f"💻 Device: {config.DEVICE}")
    print(f"📝 Log Level: {args.log_level}")
    print("-" * 50)
    
    try:
        if args.mode == "quick":
            results = run_quick_demo()
        elif args.mode == "full":
            results = run_full_demo()
        elif args.mode == "gradio":
            results = run_gradio_only()
        
        print("\n🎉 Demo completed successfully!")
        
        # Save results to file
        import json
        with open("demo_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        print("📄 Results saved to demo_results.json")
        
    except KeyboardInterrupt:
        print("\n⏹️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        logging.error(f"Demo failed: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()


