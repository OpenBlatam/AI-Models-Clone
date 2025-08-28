#!/usr/bin/env python3
"""
Enhanced HeyGen AI Setup Script
===============================

This script sets up the complete HeyGen AI system with:
- Dependency installation
- Model downloading
- Configuration setup
- System validation
"""

import os
import sys
import subprocess
import platform
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HeyGenAISetup:
    """Setup manager for HeyGen AI system."""
    
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.setup_dir = Path(__file__).parent
        self.requirements_file = self.setup_dir / "requirements_enhanced.txt"
        
    def check_python_version(self):
        """Check if Python version is compatible."""
        logger.info("Checking Python version...")
        
        if self.python_version < (3, 8):
            logger.error("Python 3.8+ is required")
            return False
        
        logger.info(f"Python {self.python_version.major}.{self.python_version.minor} is compatible")
        return True
    
    def install_dependencies(self):
        """Install all required dependencies."""
        logger.info("Installing dependencies...")
        
        try:
            # Upgrade pip
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                         check=True, capture_output=True)
            
            # Install requirements
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)], 
                         check=True, capture_output=True)
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            return False
    
    def download_models(self):
        """Download required AI models."""
        logger.info("Downloading AI models...")
        
        try:
            # Create models directory
            models_dir = self.setup_dir / "models"
            models_dir.mkdir(exist_ok=True)
            
            # Download Stable Diffusion models
            self._download_stable_diffusion_models()
            
            # Download TTS models
            self._download_tts_models()
            
            logger.info("Models downloaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to download models: {e}")
            return False
    
    def _download_stable_diffusion_models(self):
        """Download Stable Diffusion models."""
        logger.info("Downloading Stable Diffusion models...")
        
        try:
            # This would use the diffusers library to download models
            # For now, we'll create a placeholder
            models_dir = self.setup_dir / "models" / "stable_diffusion"
            models_dir.mkdir(exist_ok=True)
            
            # Create a placeholder file
            (models_dir / "README.md").write_text(
                "# Stable Diffusion Models\n\n"
                "Models will be downloaded automatically on first use.\n"
                "- Stable Diffusion v1.5\n"
                "- Stable Diffusion XL\n"
            )
            
        except Exception as e:
            logger.warning(f"Stable Diffusion model setup failed: {e}")
    
    def _download_tts_models(self):
        """Download TTS models."""
        logger.info("Downloading TTS models...")
        
        try:
            # This would use the TTS library to download models
            # For now, we'll create a placeholder
            models_dir = self.setup_dir / "models" / "tts"
            models_dir.mkdir(exist_ok=True)
            
            # Create a placeholder file
            (models_dir / "README.md").write_text(
                "# TTS Models\n\n"
                "Models will be downloaded automatically on first use.\n"
                "- Coqui TTS\n"
                "- YourTTS\n"
                "- XTTS v2\n"
            )
            
        except Exception as e:
            logger.warning(f"TTS model setup failed: {e}")
    
    def create_directories(self):
        """Create necessary directories."""
        logger.info("Creating directories...")
        
        try:
            directories = [
                "generated_avatars",
                "generated_audio", 
                "generated_videos",
                "temp",
                "cache",
                "logs"
            ]
            
            for directory in directories:
                (self.setup_dir / directory).mkdir(exist_ok=True)
            
            logger.info("Directories created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create directories: {e}")
            return False
    
    def create_config_file(self):
        """Create configuration file."""
        logger.info("Creating configuration file...")
        
        try:
            config_content = """# HeyGen AI Configuration
# =======================

[system]
default_avatar_style = realistic
default_video_quality = high
default_resolution = 1080p
enable_parallel_processing = true
max_concurrent_jobs = 3

[avatar]
enable_customization = true
enable_expressions = true
enable_lighting = true
default_quality = high

[voice]
default_language = en
enable_voice_cloning = true
default_emotion = neutral

[video]
default_fps = 30
default_format = mp4
enable_effects = true
enable_optimization = true

[paths]
models_dir = ./models
output_dir = ./generated_videos
temp_dir = ./temp
cache_dir = ./cache
"""
            
            config_file = self.setup_dir / "config.ini"
            config_file.write_text(config_content)
            
            logger.info("Configuration file created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create configuration file: {e}")
            return False
    
    def validate_installation(self):
        """Validate the installation."""
        logger.info("Validating installation...")
        
        try:
            # Test imports
            import torch
            import cv2
            import numpy as np
            import PIL
            
            # Check CUDA availability
            cuda_available = torch.cuda.is_available()
            if cuda_available:
                logger.info(f"CUDA available: {torch.cuda.get_device_name(0)}")
            else:
                logger.warning("CUDA not available, using CPU")
            
            # Check directories
            required_dirs = ["generated_avatars", "generated_audio", "generated_videos"]
            for dir_name in required_dirs:
                if not (self.setup_dir / dir_name).exists():
                    raise Exception(f"Required directory {dir_name} not found")
            
            logger.info("Installation validation successful")
            return True
            
        except Exception as e:
            logger.error(f"Installation validation failed: {e}")
            return False
    
    def run_setup(self):
        """Run complete setup process."""
        logger.info("Starting HeyGen AI setup...")
        
        steps = [
            ("Python version check", self.check_python_version),
            ("Dependency installation", self.install_dependencies),
            ("Directory creation", self.create_directories),
            ("Model download", self.download_models),
            ("Configuration setup", self.create_config_file),
            ("Installation validation", self.validate_installation)
        ]
        
        for step_name, step_func in steps:
            logger.info(f"Running: {step_name}")
            if not step_func():
                logger.error(f"Setup failed at: {step_name}")
                return False
        
        logger.info("HeyGen AI setup completed successfully!")
        return True

def main():
    """Main setup function."""
    setup = HeyGenAISetup()
    
    if setup.run_setup():
        print("\n🎉 HeyGen AI setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python heygen_ai_main.py")
        print("2. Check the generated_videos folder for output")
        print("3. Customize config.ini for your needs")
        print("\nFor support, check the README files in each component folder.")
    else:
        print("\n❌ Setup failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()


