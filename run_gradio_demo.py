#!/usr/bin/env python3
"""
Simple launcher for the Gradio Image Processing Demo
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['gradio', 'torch', 'numpy', 'opencv-python', 'Pillow']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install them with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def launch_demo():
    """Launch the Gradio demo"""
    try:
        logger.info("Starting Gradio Image Processing Demo...")
        
        # Check if gradio_enhanced_demo.py exists
        demo_file = "gradio_enhanced_demo.py"
        if not os.path.exists(demo_file):
            logger.error(f"Demo file not found: {demo_file}")
            return False
        
        # Launch the demo
        logger.info("Launching demo on http://localhost:7860")
        logger.info("Press Ctrl+C to stop the demo")
        
        # Use subprocess to run the demo
        process = subprocess.Popen([sys.executable, demo_file])
        
        try:
            process.wait()
        except KeyboardInterrupt:
            logger.info("Stopping demo...")
            process.terminate()
            process.wait()
            logger.info("Demo stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to launch demo: {e}")
        return False

def main():
    """Main function"""
    logger.info("Gradio Image Processing Demo Launcher")
    logger.info("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        logger.error("Dependency check failed. Please install missing packages.")
        return 1
    
    # Launch demo
    if launch_demo():
        logger.info("Demo completed successfully")
        return 0
    else:
        logger.error("Demo failed to launch")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


