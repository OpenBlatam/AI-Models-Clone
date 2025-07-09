#!/usr/bin/env python3
"""
Code Profiling Demo Launcher

Launcher script for the comprehensive code profiling demonstration.
"""

import sys
import os
import asyncio
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def main():
    """Main launcher function"""
    
    print("Code Profiling Demo Launcher")
    print("="*50)
    
    try:
        # Import the demo
        from examples.code_profiling_demo import main as demo_main
        
        # Run the demo
        asyncio.run(demo_main())
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure you're running this from the correct directory.")
        sys.exit(1)
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 