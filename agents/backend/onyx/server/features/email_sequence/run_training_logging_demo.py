#!/usr/bin/env python3
"""
Training Logging System Launcher

Simple launcher script to run the training logging demonstration
and showcase the comprehensive logging capabilities.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

def main():
    """Main function to run the training logging demonstration"""
    
    print("🚀 Email Sequence AI System - Training Logging Demonstration")
    print("=" * 70)
    
    try:
        # Import and run the demo
        from examples.training_logging_demo import TrainingLoggingDemo
        
        print("✅ Successfully imported training logging demo")
        
        # Create and run the demo
        demo = TrainingLoggingDemo()
        demo.run_full_demo()
        
        print("\n🎉 Training logging demonstration completed successfully!")
        print("The system demonstrated comprehensive logging for:")
        print("  • Training progress tracking")
        print("  • Error handling and reporting")
        print("  • Performance monitoring")
        print("  • Resource usage tracking")
        print("  • Visualization generation")
        print("  • Log analysis and insights")
        print("  • Enhanced training optimizer integration")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all required modules are available.")
        print("Required packages: torch, numpy, matplotlib, seaborn, psutil")
        return 1
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        print("The training logging system encountered an error.")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 