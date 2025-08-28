#!/usr/bin/env python3
"""
Ultra-Optimized AI Demo Runner
==============================

Comprehensive demo runner showcasing:
- Ultra-optimized deep learning modules
- Transformers with LoRA and P-tuning
- Diffusion models with custom schedulers
- Gradio interface with real-time inference
- Performance metrics and benchmarking
- Error handling and logging
"""

import os
import sys
import time
import argparse
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass

import torch
import numpy as np
from tqdm import tqdm
import structlog

# Import our ultra-optimized modules
try:
    from ultra_optimized_deep_learning import (
        UltraOptimizedTransformerModel, 
        UltraTrainingConfig,
        UltraOptimizedDiffusionModel,
        UltraOptimizedDataset,
        UltraOptimizedTrainer,
        UltraOptimizedInference
    )
    from ultra_optimized_transformers import (
        UltraOptimizedTransformerModel as UltraTransformerModel,
        UltraTransformersConfig,
        UltraOptimizedTokenizer,
        train_ultra_optimized_model
    )
    from ultra_optimized_diffusion import (
        UltraOptimizedDiffusionPipeline,
        UltraDiffusionConfig,
        UltraOptimizedDDIMScheduler,
        UltraOptimizedEulerScheduler,
        UltraOptimizedDPMSolverScheduler
    )
    from ultra_optimized_gradio_interface import (
        UltraOptimizedGradioInterface,
        UltraGradioConfig
    )
except ImportError as e:
    print(f"Warning: Could not import ultra-optimized modules: {e}")
    print("Some demos may not be available.")

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# =============================================================================
# Demo Configuration
# =============================================================================

@dataclass
class DemoConfig:
    """Configuration for ultra-optimized demos."""
    
    # Demo settings
    demo_type: str = "all"  # all, deep_learning, transformers, diffusion, gradio
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    num_runs: int = 3
    batch_size: int = 4
    
    # Model settings
    model_name: str = "gpt2"
    diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    
    # Performance settings
    enable_profiling: bool = True
    enable_benchmarking: bool = True
    save_results: bool = True
    
    # Output settings
    output_dir: str = "./demo_outputs"
    log_level: str = "INFO"
    
    # Gradio settings
    gradio_port: int = 7860
    gradio_share: bool = False

# =============================================================================
# Performance Metrics
# =============================================================================

class PerformanceMetrics:
    """Performance metrics collection and analysis."""
    
    def __init__(self):
        self.metrics = {}
        self.start_time = None
    
    def start_timer(self, name: str):
        """Start timing for a specific operation."""
        if self.start_time is None:
            self.start_time = time.time()
        self.metrics[name] = {"start": time.time()}
    
    def end_timer(self, name: str):
        """End timing for a specific operation."""
        if name in self.metrics and "start" in self.metrics[name]:
            self.metrics[name]["end"] = time.time()
            self.metrics[name]["duration"] = self.metrics[name]["end"] - self.metrics[name]["start"]
    
    def add_metric(self, name: str, value: float, unit: str = ""):
        """Add a custom metric."""
        self.metrics[name] = {"value": value, "unit": unit}
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {
            "total_duration": time.time() - self.start_time if self.start_time else 0,
            "metrics": {}
        }
        
        for name, data in self.metrics.items():
            if "duration" in data:
                summary["metrics"][name] = f"{data['duration']:.4f}s"
            elif "value" in data:
                summary["metrics"][name] = f"{data['value']:.4f}{data.get('unit', '')}"
        
        return summary
    
    def print_summary(self):
        """Print performance summary."""
        summary = self.get_summary()
        logger.info("Performance Summary", **summary)

# =============================================================================
# Demo Runner
# =============================================================================

class UltraOptimizedDemoRunner:
    """Ultra-optimized demo runner with comprehensive testing."""
    
    def __init__(self, config: DemoConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        
        # Create output directory
        os.makedirs(config.output_dir, exist_ok=True)
        
        logger.info("Ultra-optimized demo runner initialized", config=vars(config))
    
    def run_deep_learning_demo(self):
        """Run deep learning demo."""
        logger.info("Starting deep learning demo")
        self.metrics.start_timer("deep_learning_demo")
        
        try:
            # Initialize configuration
            config = UltraTrainingConfig()
            config.device = self.config.device
            config.batch_size = self.config.batch_size
            
            # Load tokenizer
            from transformers import AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(config.model_name)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            # Initialize model
            model = UltraOptimizedTransformerModel(config.model_name, config=config)
            
            # Create sample data
            texts = ["This is a positive review", "This is a negative review"] * 50
            labels = [1, 0] * 50
            
            # Create dataset and dataloader
            dataset = UltraOptimizedDataset(texts, labels, tokenizer, config.max_length)
            dataloader = torch.utils.data.DataLoader(
                dataset, 
                batch_size=config.batch_size, 
                shuffle=True,
                num_workers=2
            )
            
            # Initialize trainer
            trainer = UltraOptimizedTrainer(model, config)
            
            # Training loop
            for epoch in range(2):  # Short training for demo
                avg_loss = trainer.train_epoch(dataloader, epoch)
                logger.info("Training epoch completed", epoch=epoch, avg_loss=avg_loss)
            
            # Initialize inference
            inference = UltraOptimizedInference(model, tokenizer, config)
            
            # Test inference
            test_texts = [
                "This is a great product",
                "I don't like this at all",
                "The quality is excellent",
                "This is terrible"
            ]
            
            for text in test_texts:
                result = inference.predict(text)
                logger.info("Inference result", text=text, result=result)
            
            self.metrics.end_timer("deep_learning_demo")
            logger.info("Deep learning demo completed successfully")
            
        except Exception as e:
            logger.error("Deep learning demo failed", error=str(e))
            raise
    
    def run_transformers_demo(self):
        """Run transformers demo."""
        logger.info("Starting transformers demo")
        self.metrics.start_timer("transformers_demo")
        
        try:
            # Initialize configuration
            config = UltraTransformersConfig()
            config.device = self.config.device
            config.use_lora = True
            config.use_prompt_tuning = True
            
            # Initialize tokenizer
            tokenizer = UltraOptimizedTokenizer(config.model_name, config)
            
            # Initialize model
            model = UltraTransformerModel(config.model_name, config=config)
            
            # Create sample data
            texts = ["This is a positive review", "This is a negative review"] * 50
            labels = [1, 0] * 50
            
            # Tokenize data
            encodings = tokenizer.tokenize_batch(texts)
            encodings["labels"] = torch.tensor(labels)
            
            # Create dataset
            dataset = torch.utils.data.TensorDataset(
                encodings["input_ids"],
                encodings["attention_mask"],
                encodings["labels"]
            )
            
            # Create dataloaders
            train_size = int(0.8 * len(dataset))
            val_size = len(dataset) - train_size
            train_dataset, val_dataset = torch.utils.data.random_split(dataset, [train_size, val_size])
            
            train_dataloader = torch.utils.data.DataLoader(train_dataset, batch_size=config.batch_size, shuffle=True)
            val_dataloader = torch.utils.data.DataLoader(val_dataset, batch_size=config.batch_size, shuffle=False)
            
            # Train model
            trained_model = train_ultra_optimized_model(model, train_dataloader, val_dataloader, config)
            
            # Test generation
            if hasattr(trained_model, 'generate'):
                test_input = tokenizer.tokenize_single("The movie was")
                generated = trained_model.generate(test_input["input_ids"], max_length=50)
                generated_text = tokenizer.tokenizer.decode(generated[0], skip_special_tokens=True)
                logger.info("Generated text", text=generated_text)
            
            self.metrics.end_timer("transformers_demo")
            logger.info("Transformers demo completed successfully")
            
        except Exception as e:
            logger.error("Transformers demo failed", error=str(e))
            raise
    
    def run_diffusion_demo(self):
        """Run diffusion demo."""
        logger.info("Starting diffusion demo")
        self.metrics.start_timer("diffusion_demo")
        
        try:
            # Initialize configuration
            config = UltraDiffusionConfig()
            config.device = self.config.device
            config.model_name = self.config.diffusion_model
            
            # Initialize pipeline
            pipeline = UltraOptimizedDiffusionPipeline(config)
            
            # Test prompts
            test_prompts = [
                "A beautiful landscape with mountains and a lake, high quality, detailed",
                "A futuristic city skyline at night with neon lights",
                "A serene forest with sunlight filtering through trees",
                "An astronaut floating in space with Earth in background"
            ]
            
            negative_prompt = "blurry, low quality, distorted"
            
            # Generate images
            for i, prompt in enumerate(test_prompts):
                logger.info("Generating image", prompt=prompt)
                
                image = pipeline.generate_image(
                    prompt=prompt,
                    negative_prompt=negative_prompt,
                    num_inference_steps=30  # Faster for demo
                )
                
                # Save image
                output_path = os.path.join(self.config.output_dir, f"diffusion_image_{i}.png")
                image.save(output_path)
                logger.info("Image saved", path=output_path)
            
            # Test batch generation
            logger.info("Testing batch generation")
            images = pipeline.generate_image_batch(test_prompts[:2], [negative_prompt] * 2)
            
            for i, image in enumerate(images):
                output_path = os.path.join(self.config.output_dir, f"batch_image_{i}.png")
                image.save(output_path)
                logger.info("Batch image saved", path=output_path)
            
            self.metrics.end_timer("diffusion_demo")
            logger.info("Diffusion demo completed successfully")
            
        except Exception as e:
            logger.error("Diffusion demo failed", error=str(e))
            raise
    
    def run_gradio_demo(self):
        """Run Gradio interface demo."""
        logger.info("Starting Gradio demo")
        self.metrics.start_timer("gradio_demo")
        
        try:
            # Initialize configuration
            config = UltraGradioConfig()
            
            # Create interface
            interface = UltraOptimizedGradioInterface(config)
            
            logger.info("Launching Gradio interface", port=self.config.gradio_port)
            
            # Launch interface
            interface.launch(
                server_port=self.config.gradio_port,
                share=self.config.gradio_share,
                show_error=True
            )
            
            self.metrics.end_timer("gradio_demo")
            logger.info("Gradio demo completed successfully")
            
        except Exception as e:
            logger.error("Gradio demo failed", error=str(e))
            raise
    
    def run_benchmarking_demo(self):
        """Run comprehensive benchmarking demo."""
        logger.info("Starting benchmarking demo")
        self.metrics.start_timer("benchmarking_demo")
        
        try:
            # Memory usage
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                initial_memory = torch.cuda.memory_allocated()
                self.metrics.add_metric("initial_memory_mb", initial_memory / 1024**2, "MB")
            
            # Model loading time
            self.metrics.start_timer("model_loading")
            
            config = UltraTrainingConfig()
            config.device = self.config.device
            
            model = UltraOptimizedTransformerModel(config.model_name, config=config)
            
            self.metrics.end_timer("model_loading")
            
            # Inference speed test
            self.metrics.start_timer("inference_speed_test")
            
            # Create test inputs
            test_inputs = torch.randint(0, 1000, (self.config.batch_size, 128)).to(self.config.device)
            
            # Warmup
            with torch.no_grad():
                for _ in range(10):
                    _ = model(test_inputs)
            
            # Benchmark
            times = []
            for _ in range(self.config.num_runs):
                start_time = time.time()
                with torch.no_grad():
                    _ = model(test_inputs)
                torch.cuda.synchronize() if torch.cuda.is_available() else None
                times.append(time.time() - start_time)
            
            self.metrics.end_timer("inference_speed_test")
            
            # Calculate metrics
            avg_time = np.mean(times)
            std_time = np.std(times)
            throughput = self.config.batch_size / avg_time
            
            self.metrics.add_metric("avg_inference_time_ms", avg_time * 1000, "ms")
            self.metrics.add_metric("std_inference_time_ms", std_time * 1000, "ms")
            self.metrics.add_metric("throughput_samples_per_sec", throughput, "samples/sec")
            
            # Memory usage after inference
            if torch.cuda.is_available():
                final_memory = torch.cuda.memory_allocated()
                self.metrics.add_metric("final_memory_mb", final_memory / 1024**2, "MB")
                self.metrics.add_metric("memory_increase_mb", (final_memory - initial_memory) / 1024**2, "MB")
            
            self.metrics.end_timer("benchmarking_demo")
            logger.info("Benchmarking demo completed successfully")
            
        except Exception as e:
            logger.error("Benchmarking demo failed", error=str(e))
            raise
    
    def run_all_demos(self):
        """Run all available demos."""
        logger.info("Starting all demos")
        self.metrics.start_timer("all_demos")
        
        try:
            # Run individual demos
            if hasattr(self, 'run_deep_learning_demo'):
                self.run_deep_learning_demo()
            
            if hasattr(self, 'run_transformers_demo'):
                self.run_transformers_demo()
            
            if hasattr(self, 'run_diffusion_demo'):
                self.run_diffusion_demo()
            
            if hasattr(self, 'run_benchmarking_demo'):
                self.run_benchmarking_demo()
            
            self.metrics.end_timer("all_demos")
            
            # Print final summary
            self.metrics.print_summary()
            
            logger.info("All demos completed successfully")
            
        except Exception as e:
            logger.error("All demos failed", error=str(e))
            raise
    
    def save_results(self):
        """Save demo results and metrics."""
        try:
            import json
            
            results = {
                "config": vars(self.config),
                "performance": self.metrics.get_summary(),
                "timestamp": time.time()
            }
            
            output_path = os.path.join(self.config.output_dir, "demo_results.json")
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info("Results saved", path=output_path)
            
        except Exception as e:
            logger.error("Failed to save results", error=str(e))

# =============================================================================
# Command Line Interface
# =============================================================================

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Ultra-Optimized AI Demo Runner")
    
    parser.add_argument(
        "--demo-type",
        type=str,
        default="all",
        choices=["all", "deep_learning", "transformers", "diffusion", "gradio", "benchmarking"],
        help="Type of demo to run"
    )
    
    parser.add_argument(
        "--device",
        type=str,
        default="cuda" if torch.cuda.is_available() else "cpu",
        help="Device to run on (cuda/cpu)"
    )
    
    parser.add_argument(
        "--num-runs",
        type=int,
        default=3,
        help="Number of runs for benchmarking"
    )
    
    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help="Batch size for testing"
    )
    
    parser.add_argument(
        "--model-name",
        type=str,
        default="gpt2",
        help="Model name for transformers"
    )
    
    parser.add_argument(
        "--diffusion-model",
        type=str,
        default="runwayml/stable-diffusion-v1-5",
        help="Diffusion model name"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./demo_outputs",
        help="Output directory for results"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level"
    )
    
    parser.add_argument(
        "--gradio-port",
        type=int,
        default=7860,
        help="Port for Gradio interface"
    )
    
    parser.add_argument(
        "--gradio-share",
        action="store_true",
        help="Share Gradio interface"
    )
    
    parser.add_argument(
        "--no-profiling",
        action="store_true",
        help="Disable profiling"
    )
    
    parser.add_argument(
        "--no-benchmarking",
        action="store_true",
        help="Disable benchmarking"
    )
    
    parser.add_argument(
        "--no-save-results",
        action="store_true",
        help="Don't save results"
    )
    
    return parser.parse_args()

# =============================================================================
# Main Function
# =============================================================================

def main():
    """Main function to run ultra-optimized demos."""
    try:
        # Parse arguments
        args = parse_args()
        
        # Create configuration
        config = DemoConfig(
            demo_type=args.demo_type,
            device=args.device,
            num_runs=args.num_runs,
            batch_size=args.batch_size,
            model_name=args.model_name,
            diffusion_model=args.diffusion_model,
            output_dir=args.output_dir,
            log_level=args.log_level,
            gradio_port=args.gradio_port,
            gradio_share=args.gradio_share,
            enable_profiling=not args.no_profiling,
            enable_benchmarking=not args.no_benchmarking,
            save_results=not args.no_save_results
        )
        
        # Set log level
        logging.getLogger().setLevel(getattr(logging, config.log_level))
        
        # Create demo runner
        runner = UltraOptimizedDemoRunner(config)
        
        # Run demos based on type
        if config.demo_type == "all":
            runner.run_all_demos()
        elif config.demo_type == "deep_learning":
            runner.run_deep_learning_demo()
        elif config.demo_type == "transformers":
            runner.run_transformers_demo()
        elif config.demo_type == "diffusion":
            runner.run_diffusion_demo()
        elif config.demo_type == "gradio":
            runner.run_gradio_demo()
        elif config.demo_type == "benchmarking":
            runner.run_benchmarking_demo()
        
        # Save results if requested
        if config.save_results:
            runner.save_results()
        
        logger.info("Demo runner completed successfully")
        
    except Exception as e:
        logger.error("Demo runner failed", error=str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()


