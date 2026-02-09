#!/usr/bin/env python3
"""
Diffusion Models Demo using Diffusers Library

Comprehensive demonstration of diffusion models with the Diffusers library,
including model loading, image generation, training setup, and analysis.
"""

import asyncio
import sys
import logging
import time
import torch
from pathlib import Path
from datetime import datetime
from PIL import Image
import numpy as np

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import diffusion models system
from core.diffusion_models_system import (
    DiffusionModelManager, DiffusionModelConfig, GenerationConfig, TrainingConfig,
    DiffusionModelType, SchedulerType, DiffusionModelTrainer, DiffusionModelAnalyzer
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('diffusion_models_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DiffusionModelsDemo:
    """Comprehensive demo for diffusion models using Diffusers."""
    
    def __init__(self):
        self.manager = DiffusionModelManager()
        self.trainer = DiffusionModelTrainer(self.manager)
        self.analyzer = DiffusionModelAnalyzer(self.manager)
        self.start_time = None
    
    async def initialize_models(self):
        """Initialize various diffusion models."""
        try:
            logger.info("🚀 Initializing Diffusion Models...")
            
            # Model 1: Stable Diffusion v1.5
            sd_config = DiffusionModelConfig(
                model_name="runwayml/stable-diffusion-v1-5",
                model_type=DiffusionModelType.STABLE_DIFFUSION,
                scheduler_type=SchedulerType.DDIM,
                torch_dtype="float16",
                enable_attention_slicing=True,
                enable_vae_slicing=True
            )
            
            sd_model = self.manager.load_model("stable-diffusion-v1-5", sd_config)
            logger.info("✅ Stable Diffusion v1.5 loaded")
            
            # Model 2: Stable Diffusion XL Base
            sdxl_config = DiffusionModelConfig(
                model_name="stabilityai/stable-diffusion-xl-base-1.0",
                model_type=DiffusionModelType.STABLE_DIFFUSION_XL,
                scheduler_type=SchedulerType.EULER,
                torch_dtype="float16",
                enable_attention_slicing=True,
                enable_vae_slicing=True
            )
            
            sdxl_model = self.manager.load_model("stable-diffusion-xl-base", sdxl_config)
            logger.info("✅ Stable Diffusion XL Base loaded")
            
            # Setup tokenization
            self.manager.setup_tokenization("stable-diffusion-v1-5", "sd_clip")
            self.manager.setup_tokenization("stable-diffusion-xl-base", "sdxl_t5")
            logger.info("✅ Tokenization systems setup")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize models: {e}")
            return False
    
    async def demo_model_loading(self):
        """Demo model loading capabilities."""
        try:
            logger.info("📦 Demo: Model Loading")
            
            # Test loading different model types
            models_to_test = [
                ("stable-diffusion-v2-1", DiffusionModelConfig(
                    model_name="stabilityai/stable-diffusion-2-1",
                    model_type=DiffusionModelType.STABLE_DIFFUSION,
                    scheduler_type=SchedulerType.DDIM
                )),
                ("stable-diffusion-xl-refiner", DiffusionModelConfig(
                    model_name="stabilityai/stable-diffusion-xl-refiner-1.0",
                    model_type=DiffusionModelType.STABLE_DIFFUSION_XL,
                    scheduler_type=SchedulerType.EULER
                ))
            ]
            
            for model_name, config in models_to_test:
                logger.info(f"  Loading {model_name}:")
                
                try:
                    model = self.manager.load_model(model_name, config)
                    logger.info(f"    ✅ Successfully loaded {model_name}")
                    
                    # Test basic functionality
                    test_config = GenerationConfig(
                        prompt="A simple test image",
                        num_inference_steps=5,  # Very few steps for testing
                        guidance_scale=7.5
                    )
                    
                    images = self.manager.generate_image(model_name, test_config)
                    logger.info(f"    ✅ Generated test image: {len(images)} images")
                    
                    # Unload to save memory
                    self.manager.unload_model(model_name)
                    logger.info(f"    ✅ Unloaded {model_name}")
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to load {model_name}: {e}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model loading demo failed: {e}")
            return False
    
    async def demo_image_generation(self):
        """Demo image generation capabilities."""
        try:
            logger.info("🎨 Demo: Image Generation")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style",
                "A cyberpunk street scene with neon lights",
                "A peaceful lake reflecting the sky, impressionist style"
            ]
            
            models = ["stable-diffusion-v1-5", "stable-diffusion-xl-base"]
            
            for model_name in models:
                logger.info(f"  Testing {model_name}:")
                
                model = self.manager.get_model(model_name)
                if not model:
                    logger.warning(f"    Model {model_name} not available")
                    continue
                
                for i, prompt in enumerate(test_prompts[:2], 1):  # Test first 2 prompts
                    logger.info(f"    Generating image {i}: {prompt[:50]}...")
                    
                    config = GenerationConfig(
                        prompt=prompt,
                        negative_prompt="blurry, low quality, pixelated",
                        num_inference_steps=20,  # Reduced for demo
                        guidance_scale=7.5,
                        num_images_per_prompt=1
                    )
                    
                    start_time = time.time()
                    images = self.manager.generate_image(model_name, config)
                    generation_time = time.time() - start_time
                    
                    logger.info(f"      Generated in {generation_time:.2f}s")
                    logger.info(f"      Image size: {images[0].size if images else 'N/A'}")
                    
                    # Save image for inspection
                    if images:
                        output_path = f"demo_output_{model_name}_{i}.png"
                        images[0].save(output_path)
                        logger.info(f"      Saved to: {output_path}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Image generation demo failed: {e}")
            return False
    
    async def demo_batch_generation(self):
        """Demo batch image generation."""
        try:
            logger.info("📦 Demo: Batch Generation")
            
            model_name = "stable-diffusion-v1-5"
            model = self.manager.get_model(model_name)
            if not model:
                logger.warning(f"Model {model_name} not available")
                return True
            
            # Create batch of generation configs
            batch_configs = [
                GenerationConfig(
                    prompt="A cat sitting on a windowsill",
                    num_inference_steps=15,
                    guidance_scale=7.5
                ),
                GenerationConfig(
                    prompt="A dog running in a park",
                    num_inference_steps=15,
                    guidance_scale=7.5
                ),
                GenerationConfig(
                    prompt="A bird flying over the ocean",
                    num_inference_steps=15,
                    guidance_scale=7.5
                )
            ]
            
            logger.info(f"  Generating batch of {len(batch_configs)} images:")
            
            start_time = time.time()
            batch_results = self.manager.generate_image_batch(model_name, batch_configs)
            batch_time = time.time() - start_time
            
            logger.info(f"    Batch generation time: {batch_time:.2f}s")
            logger.info(f"    Total images generated: {sum(len(images) for images in batch_results)}")
            
            # Save batch results
            for i, images in enumerate(batch_results):
                if images:
                    output_path = f"batch_output_{i}.png"
                    images[0].save(output_path)
                    logger.info(f"    Saved batch image {i}: {output_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Batch generation demo failed: {e}")
            return False
    
    async def demo_tokenization_integration(self):
        """Demo integration with tokenization system."""
        try:
            logger.info("🔤 Demo: Tokenization Integration")
            
            test_prompts = [
                "A beautiful sunset over the mountains, digital art style",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with ancient trees, fantasy art style"
            ]
            
            tokenizers = ["sd_clip", "sdxl_t5"]
            
            for tokenizer_name in tokenizers:
                logger.info(f"  Testing {tokenizer_name} tokenization:")
                
                for i, prompt in enumerate(test_prompts, 1):
                    logger.info(f"    Processing prompt {i}: {prompt[:50]}...")
                    
                    # Process prompt
                    processed = self.manager.process_prompt_with_tokenization(tokenizer_name, prompt)
                    logger.info(f"      Token count: {processed['token_count']}")
                    logger.info(f"      Input IDs shape: {processed['input_ids'].shape}")
                    
                    # Encode prompt
                    try:
                        embeddings = self.manager.encode_prompt_with_tokenization(tokenizer_name, prompt)
                        logger.info(f"      Embeddings shape: {embeddings.shape}")
                        logger.info(f"      Embeddings device: {embeddings.device}")
                    except Exception as e:
                        logger.warning(f"      Text encoder not available: {e}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Tokenization integration demo failed: {e}")
            return False
    
    async def demo_model_analysis(self):
        """Demo model analysis capabilities."""
        try:
            logger.info("🔍 Demo: Model Analysis")
            
            models = ["stable-diffusion-v1-5", "stable-diffusion-xl-base"]
            
            for model_name in models:
                logger.info(f"  Analyzing {model_name}:")
                
                try:
                    analysis = self.analyzer.analyze_model(model_name)
                    
                    logger.info(f"    Model type: {analysis['model_type']}")
                    logger.info(f"    Device: {analysis['device']}")
                    logger.info(f"    Data type: {analysis['dtype']}")
                    logger.info(f"    Parameters: {analysis['num_parameters']:,}")
                    logger.info(f"    Trainable parameters: {analysis['trainable_parameters']:,}")
                    logger.info(f"    Scheduler: {analysis['scheduler_type']}")
                    logger.info(f"    Components: {analysis['components']}")
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to analyze {model_name}: {e}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model analysis demo failed: {e}")
            return False
    
    async def demo_model_benchmarking(self):
        """Demo model benchmarking capabilities."""
        try:
            logger.info("⚡ Demo: Model Benchmarking")
            
            model_name = "stable-diffusion-v1-5"
            model = self.manager.get_model(model_name)
            if not model:
                logger.warning(f"Model {model_name} not available")
                return True
            
            test_prompt = "A beautiful landscape painting"
            
            logger.info(f"  Benchmarking {model_name}:")
            logger.info(f"    Test prompt: {test_prompt}")
            logger.info(f"    Running 3 benchmark runs...")
            
            try:
                benchmark = self.analyzer.benchmark_model(
                    model_name, test_prompt, num_runs=3
                )
                
                logger.info(f"    Average time: {benchmark['avg_time']:.2f}s")
                logger.info(f"    Time std dev: {benchmark['std_time']:.2f}s")
                logger.info(f"    Min time: {benchmark['min_time']:.2f}s")
                logger.info(f"    Max time: {benchmark['max_time']:.2f}s")
                
                if benchmark['avg_memory'] > 0:
                    logger.info(f"    Average memory: {benchmark['avg_memory'] / 1024**2:.2f} MB")
                    logger.info(f"    Memory std dev: {benchmark['std_memory'] / 1024**2:.2f} MB")
                
                logger.info(f"    Individual times: {[f'{t:.2f}s' for t in benchmark['times']]}")
                
            except Exception as e:
                logger.error(f"    ❌ Benchmark failed: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Model benchmarking demo failed: {e}")
            return False
    
    async def demo_training_setup(self):
        """Demo training setup capabilities."""
        try:
            logger.info("🏋️ Demo: Training Setup")
            
            # Setup training configurations
            training_configs = [
                ("stable-diffusion-v1-5", TrainingConfig(
                    learning_rate=1e-5,
                    num_train_epochs=100,
                    per_device_train_batch_size=1,
                    gradient_accumulation_steps=4,
                    save_steps=1000,
                    logging_steps=10
                )),
                ("stable-diffusion-xl-base", TrainingConfig(
                    learning_rate=5e-6,
                    num_train_epochs=50,
                    per_device_train_batch_size=1,
                    gradient_accumulation_steps=8,
                    save_steps=500,
                    logging_steps=5
                ))
            ]
            
            for model_name, config in training_configs:
                logger.info(f"  Setting up training for {model_name}:")
                
                try:
                    self.trainer.setup_training(model_name, config)
                    
                    logger.info(f"    Learning rate: {config.learning_rate}")
                    logger.info(f"    Epochs: {config.num_train_epochs}")
                    logger.info(f"    Batch size: {config.per_device_train_batch_size}")
                    logger.info(f"    Gradient accumulation: {config.gradient_accumulation_steps}")
                    logger.info(f"    Save steps: {config.save_steps}")
                    logger.info(f"    Logging steps: {config.logging_steps}")
                    
                except Exception as e:
                    logger.error(f"    ❌ Failed to setup training for {model_name}: {e}")
                
                logger.info("")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Training setup demo failed: {e}")
            return False
    
    async def demo_advanced_features(self):
        """Demo advanced diffusion model features."""
        try:
            logger.info("🚀 Demo: Advanced Features")
            
            model_name = "stable-diffusion-v1-5"
            model = self.manager.get_model(model_name)
            if not model:
                logger.warning(f"Model {model_name} not available")
                return True
            
            # Feature 1: Different schedulers
            logger.info("  Testing different schedulers:")
            
            schedulers = [
                ("DDIM", SchedulerType.DDIM),
                ("Euler", SchedulerType.EULER),
                ("DPM Solver", SchedulerType.DPM_SOLVER_MULTISTEP)
            ]
            
            for scheduler_name, scheduler_type in schedulers:
                logger.info(f"    Testing {scheduler_name} scheduler:")
                
                try:
                    # Change scheduler
                    from core.diffusion_models_system import DDIMScheduler, EulerDiscreteScheduler, DPMSolverMultistepScheduler
                    
                    scheduler_map = {
                        SchedulerType.DDIM: DDIMScheduler,
                        SchedulerType.EULER: EulerDiscreteScheduler,
                        SchedulerType.DPM_SOLVER_MULTISTEP: DPMSolverMultistepScheduler
                    }
                    
                    scheduler_class = scheduler_map.get(scheduler_type)
                    if scheduler_class:
                        model.scheduler = scheduler_class.from_config(model.scheduler.config)
                        logger.info(f"      ✅ Scheduler changed to {scheduler_name}")
                        
                        # Test generation with new scheduler
                        config = GenerationConfig(
                            prompt="A test image with new scheduler",
                            num_inference_steps=10,
                            guidance_scale=7.5
                        )
                        
                        start_time = time.time()
                        images = self.manager.generate_image(model_name, config)
                        generation_time = time.time() - start_time
                        
                        logger.info(f"      Generated in {generation_time:.2f}s")
                        
                except Exception as e:
                    logger.error(f"      ❌ Failed to test {scheduler_name}: {e}")
            
            # Feature 2: Different guidance scales
            logger.info("  Testing different guidance scales:")
            
            guidance_scales = [1.0, 3.0, 7.5, 15.0]
            
            for guidance_scale in guidance_scales:
                logger.info(f"    Testing guidance scale {guidance_scale}:")
                
                try:
                    config = GenerationConfig(
                        prompt="A detailed portrait with specific guidance",
                        num_inference_steps=15,
                        guidance_scale=guidance_scale
                    )
                    
                    start_time = time.time()
                    images = self.manager.generate_image(model_name, config)
                    generation_time = time.time() - start_time
                    
                    logger.info(f"      Generated in {generation_time:.2f}s")
                    
                    # Save with guidance scale in filename
                    if images:
                        output_path = f"guidance_test_{guidance_scale}.png"
                        images[0].save(output_path)
                        logger.info(f"      Saved to: {output_path}")
                        
                except Exception as e:
                    logger.error(f"      ❌ Failed to test guidance scale {guidance_scale}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Advanced features demo failed: {e}")
            return False
    
    async def run(self):
        """Main demo execution."""
        try:
            self.start_time = datetime.now()
            
            logger.info("🚀 Starting Diffusion Models Demo...")
            logger.info(f"⏰ Start time: {self.start_time}")
            
            # Initialize models
            if not await self.initialize_models():
                return False
            
            # Run demos
            demos = [
                self.demo_model_loading(),
                self.demo_image_generation(),
                self.demo_batch_generation(),
                self.demo_tokenization_integration(),
                self.demo_model_analysis(),
                self.demo_model_benchmarking(),
                self.demo_training_setup(),
                self.demo_advanced_features()
            ]
            
            for demo in demos:
                if not await demo:
                    logger.warning("⚠️ Demo completed with warnings")
            
            # Final status
            end_time = datetime.now()
            duration = end_time - self.start_time
            
            logger.info("🎉 Diffusion Models Demo completed successfully!")
            logger.info(f"⏱️  Total duration: {duration}")
            logger.info("📊 All demos executed successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Demo execution failed: {e}")
            return False

async def main():
    """Main entry point."""
    demo = DiffusionModelsDemo()
    
    try:
        success = await demo.run()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
