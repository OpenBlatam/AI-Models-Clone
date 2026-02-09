#!/usr/bin/env python3
"""
Diffusion Demo Launcher
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🎨 Launching Diffusion Models Demo...")
    
    try:
        from agents.backend.onyx.server.features.image_process.diffusion_demo import create_diffusion_demo
        
        demo = create_diffusion_demo()
        demo.launch(server_name="0.0.0.0", server_port=7861, share=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure diffusion modules are available")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()


