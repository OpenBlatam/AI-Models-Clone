#!/usr/bin/env python3
"""
Simple Demo Launcher for the Enhanced Gradio Image Processing System

This script provides an easy way to launch the Gradio demo with proper
error handling and dependency checking.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print a nice banner for the demo launcher"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                🚀 Enhanced Image Processing Demo             ║
║                                                              ║
║  AI-powered image enhancement with comprehensive error      ║
║  handling, PyTorch integration, and advanced debugging      ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        logger.error(f"Current version: {sys.version}")
        return False
    logger.info(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = {
        'gradio': 'Gradio web interface',
        'torch': 'PyTorch deep learning framework',
        'numpy': 'Numerical computing',
        'PIL': 'Image processing (Pillow)',
        'cv2': 'Computer vision (OpenCV)'
    }
    
    missing_packages = []
    
    for package, description in required_packages.items():
        try:
            if package == 'PIL':
                import PIL
            elif package == 'cv2':
                import cv2
            else:
                __import__(package)
            logger.info(f"✅ {description}: {package}")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"❌ Missing: {description} ({package})")
    
    if missing_packages:
        logger.error("\n📦 Install missing packages with:")
        logger.error(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_demo_file():
    """Check if the demo file exists"""
    demo_file = "gradio_enhanced_demo.py"
    
    if not os.path.exists(demo_file):
        logger.error(f"❌ Demo file not found: {demo_file}")
        logger.error("Make sure you're in the correct directory")
        return False
    
    logger.info(f"✅ Demo file found: {demo_file}")
    return True

def launch_demo():
    """Launch the Gradio demo"""
    try:
        logger.info("🚀 Starting Gradio Image Processing Demo...")
        logger.info("📱 The demo will open in your web browser")
        logger.info("🌐 Local URL: http://localhost:7860")
        logger.info("⏹️  Press Ctrl+C to stop the demo")
        logger.info("-" * 50)
        
        # Launch the demo
        demo_file = "gradio_enhanced_demo.py"
        process = subprocess.Popen([sys.executable, demo_file])
        
        try:
            # Wait for the process to complete
            process.wait()
        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopping demo...")
            process.terminate()
            process.wait()
            logger.info("✅ Demo stopped successfully")
        
        return True
        
    except Exception as error:
        logger.error(f"❌ Failed to launch demo: {error}")
        return False

def main():
    """Main function"""
    print_banner()
    
    logger.info("🔍 Checking system requirements...")
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check demo file
    if not check_demo_file():
        return 1
    
    logger.info("✅ All checks passed!")
    logger.info("")
    
    # Launch demo
    if launch_demo():
        logger.info("🎉 Demo completed successfully")
        return 0
    else:
        logger.error("💥 Demo failed to launch")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\n👋 Demo launcher interrupted by user")
        sys.exit(0)
    except Exception as error:
        logger.error(f"💥 Unexpected error: {error}")
        sys.exit(1)


