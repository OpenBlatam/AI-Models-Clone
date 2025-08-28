#!/usr/bin/env python3
"""
Gradio Diffusion Demo Launcher

This script launches the comprehensive Gradio interface for diffusion models
with proper error handling and configuration.
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main launcher function."""
    try:
        logger.info("🚀 Launching Gradio Diffusion Interface...")
        
        # Import the interface
        from core.gradio_diffusion_interface import GradioDiffusionInterface
        
        # Create and launch the interface
        demo = GradioDiffusionInterface()
        
        logger.info("✅ Interface created successfully")
        logger.info("🌐 Launching on http://localhost:7860")
        logger.info("📱 Use Ctrl+C to stop the server")
        
        # Launch with production settings
        demo.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,
            debug=False,
            show_error=True,
            enable_queue=True,
            max_threads=4
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("Make sure all required dependencies are installed:")
        logger.error("pip install gradio torch diffusers transformers pillow")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Launch error: {e}")
        logger.error("Check the logs above for more details")
        sys.exit(1)

if __name__ == "__main__":
    main()
