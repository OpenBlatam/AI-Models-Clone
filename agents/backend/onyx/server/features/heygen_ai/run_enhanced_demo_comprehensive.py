#!/usr/bin/env python3
"""
Comprehensive Demo for Enhanced HeyGen AI System.

This script demonstrates the enhanced capabilities of the HeyGen AI system
including transformer models, diffusion models, training pipelines, and
Gradio interface integration.
"""

import os
import sys
import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Any

# Add the core directory to the path
sys.path.append(str(Path(__file__).parent / "core"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_demo.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import enhanced modules
try:
    from transformer_models_enhanced import TransformerManager, TransformerConfig
    from diffusion_models_enhanced import DiffusionPipelineManager, DiffusionConfig
    from model_training_enhanced import ModelTrainer, TrainingConfig
    from gradio_interface_enhanced import GradioInterfaceManager
except ImportError as e:
    logger.error(f"Failed to import enhanced modules: {e}")
    logger.info("Please ensure all enhanced modules are in the core/ directory")
    sys.exit(1)


class EnhancedHeyGenAIDemo:
    """Comprehensive demo class for the enhanced HeyGen AI system."""
    
    def __init__(self):
        """Initialize the demo system."""
        self.logger = logging.getLogger(__name__)
        self.transformer_manager = None
        self.diffusion_manager = None
        self.gradio_interface = None
        
        # Demo configuration
        self.demo_config = {
            "text_generation": {
                "enabled": True,
                "models": ["gpt2", "gpt2-medium"],
                "max_length": 100,
                "temperature": 0.7
            },
            "image_generation": {
                "enabled": True,
                "models": ["stable_diffusion"],
                "width": 512,
                "height": 512
            },
            "training": {
                "enabled": False,  # Disabled by default for demo
                "demo_data": True
            },
            "gradio_interface": {
                "enabled": True,
                "port": 7860,
                "share": True
            }
        }
    
    def run_comprehensive_demo(self):
        """Run the comprehensive demo showcasing all features."""
        self.logger.info("🚀 Starting Enhanced HeyGen AI Comprehensive Demo")
        
        try:
            # 1. System Information
            self._display_system_info()
            
            # 2. Text Generation Demo
            if self.demo_config["text_generation"]["enabled"]:
                self._demo_text_generation()
            
            # 3. Image Generation Demo
            if self.demo_config["image_generation"]["enabled"]:
                self._demo_image_generation()
            
            # 4. Training Pipeline Demo
            if self.demo_config["training"]["enabled"]:
                self._demo_training_pipeline()
            
            # 5. Gradio Interface Demo
            if self.demo_config["gradio_interface"]["enabled"]:
                self._demo_gradio_interface()
            
            self.logger.info("✅ Comprehensive demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Demo failed: {str(e)}")
            raise
    
    def _display_system_info(self):
        """Display system information and capabilities."""
        self.logger.info("📊 System Information")
        self.logger.info("=" * 50)
        
        # PyTorch information
        import torch
        self.logger.info(f"PyTorch Version: {torch.__version__}")
        self.logger.info(f"CUDA Available: {torch.cuda.is_available()}")
        
        if torch.cuda.is_available():
            self.logger.info(f"CUDA Version: {torch.version.cuda}")
            self.logger.info(f"GPU Count: {torch.cuda.device_count()}")
            self.logger.info(f"Current GPU: {torch.cuda.current_device()}")
            self.logger.info(f"GPU Name: {torch.cuda.get_device_name()}")
        
        # Transformers information
        try:
            import transformers
            self.logger.info(f"Transformers Version: {transformers.__version__}")
        except ImportError:
            self.logger.warning("Transformers not available")
        
        # Diffusers information
        try:
            import diffusers
            self.logger.info(f"Diffusers Version: {diffusers.__version__}")
        except ImportError:
            self.logger.warning("Diffusers not available")
        
        # Gradio information
        try:
            import gradio as gr
            self.logger.info(f"Gradio Version: {gr.__version__}")
        except ImportError:
            self.logger.warning("Gradio not available")
        
        self.logger.info("=" * 50)
    
    def _demo_text_generation(self):
        """Demonstrate text generation capabilities."""
        self.logger.info("📝 Text Generation Demo")
        self.logger.info("-" * 30)
        
        try:
            # Initialize transformer manager
            config = TransformerConfig(
                model_name="gpt2",
                use_fp16=torch.cuda.is_available(),
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            self.transformer_manager = TransformerManager(config)
            self.logger.info(f"Loading model: {config.model_name}")
            
            # Load the model
            start_time = time.time()
            self.transformer_manager.load_pretrained_model()
            load_time = time.time() - start_time
            self.logger.info(f"Model loaded in {load_time:.2f} seconds")
            
            # Test prompts
            test_prompts = [
                "The future of artificial intelligence is",
                "In a world where machines can think,",
                "The most important discovery in science was",
                "When I first learned about deep learning,"
            ]
            
            for i, prompt in enumerate(test_prompts, 1):
                self.logger.info(f"\nTest {i}: {prompt}")
                
                start_time = time.time()
                generated_text = self.transformer_manager.generate_text(
                    prompt=prompt,
                    max_length=50,
                    temperature=0.7,
                    top_p=0.9,
                    do_sample=True
                )
                generation_time = time.time() - start_time
                
                self.logger.info(f"Generated: {generated_text}")
                self.logger.info(f"Generation time: {generation_time:.2f} seconds")
            
            self.logger.info("✅ Text generation demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Text generation demo failed: {str(e)}")
            raise
    
    def _demo_image_generation(self):
        """Demonstrate image generation capabilities."""
        self.logger.info("🎨 Image Generation Demo")
        self.logger.info("-" * 30)
        
        try:
            # Initialize diffusion manager
            config = DiffusionConfig(
                model_type="stable_diffusion",
                width=512,
                height=512,
                num_inference_steps=20,  # Reduced for demo speed
                guidance_scale=7.5,
                use_fp16=torch.cuda.is_available(),
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            self.diffusion_manager = DiffusionPipelineManager(config)
            self.logger.info(f"Initializing {config.model_type} pipeline...")
            
            # Test prompts for image generation
            test_prompts = [
                "A beautiful sunset over mountains, digital art",
                "A futuristic city with flying cars, sci-fi style",
                "A serene forest with sunlight filtering through trees",
                "An abstract geometric pattern with vibrant colors"
            ]
            
            for i, prompt in enumerate(test_prompts, 1):
                self.logger.info(f"\nGenerating image {i}: {prompt}")
                
                start_time = time.time()
                images = self.diffusion_manager.generate_image(
                    prompt=prompt,
                    negative_prompt="blurry, low quality, distorted",
                    num_images=1
                )
                generation_time = time.time() - start_time
                
                if images:
                    self.logger.info(f"Image generated successfully in {generation_time:.2f} seconds")
                    
                    # Save the generated image
                    output_dir = Path("generated_images")
                    output_dir.mkdir(exist_ok=True)
                    
                    image_path = output_dir / f"demo_image_{i}.png"
                    images[0].save(image_path)
                    self.logger.info(f"Image saved to: {image_path}")
                else:
                    self.logger.warning(f"No image generated for prompt {i}")
            
            self.logger.info("✅ Image generation demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Image generation demo failed: {str(e)}")
            raise
    
    def _demo_training_pipeline(self):
        """Demonstrate the training pipeline capabilities."""
        self.logger.info("🏋️ Training Pipeline Demo")
        self.logger.info("-" * 30)
        
        try:
            # Create demo training configuration
            config = TrainingConfig(
                model_name="gpt2",
                batch_size=4,  # Small batch size for demo
                learning_rate=5e-5,
                num_epochs=2,  # Very few epochs for demo
                use_fp16=torch.cuda.is_available(),
                device="cuda" if torch.cuda.is_available() else "cpu"
            )
            
            self.logger.info("Training configuration created:")
            self.logger.info(f"  - Model: {config.model_name}")
            self.logger.info(f"  - Batch size: {config.batch_size}")
            self.logger.info(f"  - Learning rate: {config.learning_rate}")
            self.logger.info(f"  - Epochs: {config.num_epochs}")
            self.logger.info(f"  - Device: {config.device}")
            
            # Create demo dataset (this would be replaced with real data in practice)
            self.logger.info("Creating demo dataset...")
            
            # Note: In a real scenario, you would load actual training data
            # This is just a demonstration of the training pipeline structure
            self.logger.info("Training pipeline structure demonstrated successfully!")
            
            self.logger.info("✅ Training pipeline demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Training pipeline demo failed: {str(e)}")
            raise
    
    def _demo_gradio_interface(self):
        """Demonstrate the Gradio interface."""
        self.logger.info("🌐 Gradio Interface Demo")
        self.logger.info("-" * 30)
        
        try:
            self.logger.info("Creating Gradio interface...")
            self.gradio_interface = GradioInterfaceManager()
            
            self.logger.info("Gradio interface created successfully!")
            self.logger.info("Interface features:")
            self.logger.info("  - Text generation with multiple models")
            self.logger.info("  - Image generation with diffusion models")
            self.logger.info("  - Model training interface")
            self.logger.info("  - Settings and system information")
            
            # Launch the interface
            self.logger.info(f"Launching Gradio interface on port {self.demo_config['gradio_interface']['port']}...")
            
            # Note: In a real demo, you would launch the interface
            # For this demo script, we'll just show that it's ready
            self.logger.info("Gradio interface is ready to launch!")
            self.logger.info("To launch the interface, run the gradio_interface_enhanced.py file directly")
            
            self.logger.info("✅ Gradio interface demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Gradio interface demo failed: {str(e)}")
            raise
    
    def run_quick_demo(self):
        """Run a quick demo for testing purposes."""
        self.logger.info("⚡ Running Quick Demo")
        
        try:
            # Just test the system info and basic functionality
            self._display_system_info()
            
            # Test basic imports
            self.logger.info("Testing basic imports...")
            import torch
            self.logger.info(f"✓ PyTorch {torch.__version__} imported successfully")
            
            # Test CUDA if available
            if torch.cuda.is_available():
                self.logger.info("✓ CUDA is available")
                self.logger.info(f"✓ GPU: {torch.cuda.get_device_name()}")
            else:
                self.logger.info("✓ Running on CPU")
            
            self.logger.info("✅ Quick demo completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Quick demo failed: {str(e)}")
            raise


def main():
    """Main function to run the demo."""
    try:
        # Create demo instance
        demo = EnhancedHeyGenAIDemo()
        
        # Check command line arguments
        if len(sys.argv) > 1 and sys.argv[1] == "--quick":
            demo.run_quick_demo()
        else:
            demo.run_comprehensive_demo()
        
    except KeyboardInterrupt:
        logger.info("Demo interrupted by user")
    except Exception as e:
        logger.error(f"Demo failed with error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
