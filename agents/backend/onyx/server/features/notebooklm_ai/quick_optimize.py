#!/usr/bin/env python3
"""
Quick Optimize - NotebookLM AI
==============================

One-command optimization script for NotebookLM AI system.
Run this script to automatically optimize your system for maximum performance.

Usage:
    python quick_optimize.py
"""

import asyncio
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def quick_optimize():
    """Quick optimization function"""
    print("🚀 Starting Quick Optimization for NotebookLM AI...")
    print("="*60)
    
    try:
        # Import and run the main optimizer
        from optimize_system import SystemOptimizer
        
        optimizer = SystemOptimizer()
        await optimizer.run_full_optimization()
        
        print("\n🎉 Quick optimization completed successfully!")
        print("Your NotebookLM AI system is now optimized for maximum performance!")
        
    except Exception as e:
        print(f"\n❌ Quick optimization failed: {e}")
        print("Please check the error messages above and try again.")
        return False
    
    return True

def main():
    """Main function"""
    print("NotebookLM AI - Quick Optimizer")
    print("="*40)
    
    # Check if we're in the right directory
    if not Path("ultra_optimized_engine.py").exists():
        print("❌ Error: Please run this script from the notebooklm_ai directory")
        print("Current directory:", os.getcwd())
        print("Expected files: ultra_optimized_engine.py")
        return False
    
    # Run optimization
    success = asyncio.run(quick_optimize())
    
    if success:
        print("\n✅ Optimization completed! Your system is ready.")
        print("\nNext steps:")
        print("1. Run: python demo_ultra_optimization.py")
        print("2. Run: python main_production_advanced.py")
        print("3. Check: optimization_report.json for detailed results")
    else:
        print("\n❌ Optimization failed. Please check the errors above.")
    
    return success

if __name__ == "__main__":
    main() 