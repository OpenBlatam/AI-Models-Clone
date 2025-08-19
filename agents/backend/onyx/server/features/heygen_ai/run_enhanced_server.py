#!/usr/bin/env python3
"""
Enhanced HeyGen AI Server Runner
Script to start the enhanced HeyGen AI FastAPI server with proper configuration.
"""

import os
import sys
import asyncio
import logging
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnhancedHeyGenServer:
    """Enhanced HeyGen AI server runner with environment setup and validation."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.requirements_file = self.project_root / "requirements-enhanced.txt"
        self.main_file = self.project_root / "main_enhanced.py"
        self.env_file = self.project_root / ".env"
        
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            logger.error(f"Python 3.8+ required, found {version.major}.{version.minor}")
            return False
        
        logger.info(f"Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    
    def check_system_requirements(self) -> Dict[str, bool]:
        """Check system requirements and capabilities."""
        requirements = {
            "python_version": self.check_python_version(),
            "gpu_available": False,
            "ffmpeg_available": False,
            "torch_available": False
        }
        
        # Check GPU availability
        try:
            import torch
            if torch.cuda.is_available():
                requirements["gpu_available"] = True
                logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            else:
                logger.info("GPU not available, using CPU")
        except ImportError:
            logger.warning("PyTorch not installed")
        
        # Check FFmpeg
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"], 
                capture_output=True, 
                text=True, 
                timeout=5
            )
            if result.returncode == 0:
                requirements["ffmpeg_available"] = True
                logger.info("FFmpeg available")
            else:
                logger.warning("FFmpeg not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("FFmpeg not found")
        
        # Check PyTorch
        try:
            import torch
            requirements["torch_available"] = True
            logger.info(f"PyTorch version: {torch.__version__}")
        except ImportError:
            logger.warning("PyTorch not installed")
        
        return requirements
    
    def create_env_file(self) -> bool:
        """Create .env file with default configuration if it doesn't exist."""
        if self.env_file.exists():
            logger.info(".env file already exists")
            return True
        
        try:
            env_content = """# Enhanced HeyGen AI Configuration
HEYGEN_ENV=development
HEYGEN_DEBUG=true
HEYGEN_API_HOST=0.0.0.0
HEYGEN_API_PORT=8000
HEYGEN_API_WORKERS=1

# LangChain and OpenRouter Settings
OPENROUTER_API_KEY=your_openrouter_api_key_here
LANGCHAIN_ENABLED=true
LANGCHAIN_CACHE_DIR=./langchain_cache

# AI Model Settings
HEYGEN_MODEL_CACHE_DIR=./models
HEYGEN_GPU_ENABLED=true
HEYGEN_MAX_BATCH_SIZE=2

# Video Settings
HEYGEN_DEFAULT_RESOLUTION=1080p
HEYGEN_DEFAULT_FORMAT=mp4
HEYGEN_MAX_VIDEO_DURATION=600
HEYGEN_TEMP_DIR=./temp

# Audio Settings
HEYGEN_DEFAULT_SAMPLE_RATE=22050
HEYGEN_AUDIO_QUALITY=high

# Storage Settings
HEYGEN_STORAGE_TYPE=local
HEYGEN_TEMP_DIR=./temp

# Logging
HEYGEN_LOG_LEVEL=INFO
"""
            
            with open(self.env_file, 'w') as f:
                f.write(env_content)
            
            logger.info("Created .env file with default configuration")
            logger.warning("Please update OPENROUTER_API_KEY in .env file")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create .env file: {e}")
            return False
    
    def install_dependencies(self) -> bool:
        """Install required dependencies."""
        if not self.requirements_file.exists():
            logger.error(f"Requirements file not found: {self.requirements_file}")
            return False
        
        try:
            logger.info("Installing dependencies...")
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(self.requirements_file)
            ], check=True, capture_output=True, text=True)
            
            logger.info("Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install dependencies: {e}")
            logger.error(f"Error output: {e.stderr}")
            return False
    
    def validate_installation(self) -> bool:
        """Validate that all required packages are installed."""
        required_packages = [
            "fastapi", "uvicorn", "torch", "transformers", "diffusers",
            "TTS", "opencv-python", "moviepy", "librosa", "pydub"
        ]
        
        missing_packages = []
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                logger.debug(f"✓ {package}")
            except ImportError:
                missing_packages.append(package)
                logger.warning(f"✗ {package}")
        
        if missing_packages:
            logger.error(f"Missing packages: {missing_packages}")
            return False
        
        logger.info("All required packages are installed")
        return True
    
    def start_server(self) -> bool:
        """Start the enhanced HeyGen AI server."""
        if not self.main_file.exists():
            logger.error(f"Main file not found: {self.main_file}")
            return False
        
        try:
            logger.info("Starting Enhanced HeyGen AI server...")
            
            # Change to project directory
            os.chdir(self.project_root)
            
            # Start server with uvicorn
            cmd = [
                sys.executable, "-m", "uvicorn",
                "main_enhanced:app",
                "--host", "0.0.0.0",
                "--port", "8000",
                "--reload",
                "--log-level", "info"
            ]
            
            logger.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Server failed to start: {e}")
            return False
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            return True
    
    def run(self) -> bool:
        """Run the complete setup and start process."""
        logger.info("=" * 60)
        logger.info("Enhanced HeyGen AI Server Setup")
        logger.info("=" * 60)
        
        # Check system requirements
        logger.info("Checking system requirements...")
        requirements = self.check_system_requirements()
        
        if not requirements["python_version"]:
            return False
        
        # Create environment file
        logger.info("Setting up environment...")
        if not self.create_env_file():
            logger.warning("Continuing without .env file...")
        
        # Install dependencies
        logger.info("Checking dependencies...")
        if not self.validate_installation():
            logger.info("Installing missing dependencies...")
            if not self.install_dependencies():
                logger.error("Failed to install dependencies")
                return False
        
        # Final validation
        if not self.validate_installation():
            logger.error("Dependency validation failed")
            return False
        
        # Start server
        logger.info("=" * 60)
        logger.info("Starting Enhanced HeyGen AI Server")
        logger.info("=" * 60)
        logger.info("Server will be available at: http://localhost:8000")
        logger.info("API Documentation: http://localhost:8000/docs")
        logger.info("Health Check: http://localhost:8000/api/v1/health")
        logger.info("Press Ctrl+C to stop the server")
        logger.info("=" * 60)
        
        return self.start_server()

def main():
    """Main entry point."""
    server = EnhancedHeyGenServer()
    
    try:
        success = server.run()
        if success:
            logger.info("Server completed successfully")
        else:
            logger.error("Server failed")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
