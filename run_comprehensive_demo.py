#!/usr/bin/env python3
"""
Comprehensive Demo Launcher
"""

import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    print("🚀 Launching Comprehensive AI System Demo...")
    
    try:
        from agents.backend.onyx.server.features.image_process.comprehensive_demo import create_comprehensive_demo_interface
        
        demo = create_comprehensive_demo_interface()
        demo.launch(server_name="0.0.0.0", server_port=7860, share=True)
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all modules are available")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
