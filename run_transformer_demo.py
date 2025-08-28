#!/usr/bin/env python3
"""
Transformer-Enhanced Demo Launcher

This script launches the transformer-enhanced Gradio demo with
pre-trained models and tokenizers from the Transformers library.
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
    required_packages = [
        'gradio', 'torch', 'transformers', 'numpy', 
        'opencv-python', 'Pillow', 'tokenizers'
    ]
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'opencv-python':
                import cv2
            elif package == 'Pillow':
                import PIL
            else:
                __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        logger.error(f"Missing required packages: {', '.join(missing_packages)}")
        logger.info("Install them with: pip install -r requirements.txt")
        return False
    
    return True

def launch_demo():
    """Launch the transformer-enhanced Gradio demo"""
    try:
        logger.info("Starting Transformer-Enhanced Image Processing Demo...")
        
        demo_file = "transformer_enhanced_demo.py"
        if not os.path.exists(demo_file):
            logger.error(f"Demo file not found: {demo_file}")
            return False
        
        logger.info("Launching demo on http://localhost:7860")
        logger.info("Press Ctrl+C to stop the demo")
        logger.info("")
        logger.info("Features:")
        logger.info("- Image Classification with Vision Transformers")
        logger.info("- Image-Text Similarity with CLIP models")
        logger.info("- Text Generation with pre-trained language models")
        logger.info("")
        
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
    logger.info("Transformer-Enhanced Image Processing Demo Launcher")
    logger.info("=" * 50)
    
    if not check_dependencies():
        logger.error("Dependency check failed. Please install missing packages.")
        return 1
    
    if launch_demo():
        logger.info("Demo completed successfully")
        return 0
    else:
        logger.error("Demo failed to launch")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)


