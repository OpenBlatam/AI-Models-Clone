#!/usr/bin/env python3
"""
Enhanced Image Processing Demo Launcher

This script launches the enhanced Gradio demo with proper configuration
and error handling for production use.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def setup_environment():
    """Setup environment variables and logging"""
    
    # Set default environment variables
    if os.getenv('DEBUG_MODE') is None:
        os.environ['DEBUG_MODE'] = 'False'
    
    if os.getenv('GRADIO_SERVER_PORT') is None:
        os.environ['GRADIO_SERVER_PORT'] = '7860'
    
    if os.getenv('GRADIO_SERVER_NAME') is None:
        os.environ['GRADIO_SERVER_NAME'] = '0.0.0.0'
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('enhanced_demo.log'),
            logging.StreamHandler()
        ]
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Environment setup completed")
    
    return logger

def check_dependencies():
    """Check if all required dependencies are available"""
    required_packages = [
        'torch', 'torchvision', 'gradio', 'PIL', 'numpy', 
        'psutil', 'scipy', 'scikit-image'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'PIL':
                import PIL
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    print("✅ All required packages are available")
    return True

def launch_demo(debug_mode=False, port=7860, share=False):
    """Launch the enhanced Gradio demo"""
    
    try:
        # Import the demo
        from gradio_enhanced_demo import create_enhanced_gradio_interface
        
        # Set debug mode
        os.environ['DEBUG_MODE'] = str(debug_mode).lower()
        
        # Create interface
        print("🚀 Creating enhanced Gradio interface...")
        interface = create_enhanced_gradio_interface()
        
        # Launch with configuration
        print(f"🌐 Launching demo on port {port}...")
        print(f"🔧 Debug mode: {'Enabled' if debug_mode else 'Disabled'}")
        print(f"📡 Share mode: {'Enabled' if share else 'Disabled'}")
        print("\n" + "="*50)
        print("🎯 Demo is starting up...")
        print("📱 Open your browser and navigate to the displayed URL")
        print("🛡️ Error handling and debugging tools are active")
        print("="*50 + "\n")
        
        interface.launch(
            server_name=os.getenv('GRADIO_SERVER_NAME', '0.0.0.0'),
            server_port=int(port),
            share=share,
            debug=False,  # Keep Gradio debug off for production
            show_error=True,
            quiet=False
        )
        
    except ImportError as e:
        print(f"❌ Failed to import demo: {e}")
        print("Make sure all required files are in the current directory")
        return False
        
    except Exception as e:
        print(f"❌ Failed to launch demo: {e}")
        return False
    
    return True

def main():
    """Main function with command line argument parsing"""
    
    parser = argparse.ArgumentParser(
        description="Enhanced Image Processing Demo Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_enhanced_demo.py                    # Launch with default settings
  python run_enhanced_demo.py --debug            # Enable debug mode
  python run_enhanced_demo.py --port 8080       # Use custom port
  python run_enhanced_demo.py --share           # Enable public sharing
  python run_enhanced_demo.py --debug --port 8080 --share  # All options
        """
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode with PyTorch anomaly detection'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Port to run the demo on (default: 7860)'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='Enable public sharing (creates public URL)'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check dependencies and exit'
    )
    
    args = parser.parse_args()
    
    # Setup environment
    logger = setup_environment()
    
    # Check dependencies if requested
    if args.check_deps:
        if check_dependencies():
            print("✅ All dependencies are satisfied")
            sys.exit(0)
        else:
            print("❌ Dependency check failed")
            sys.exit(1)
    
    # Check dependencies before launching
    if not check_dependencies():
        print("❌ Cannot launch demo due to missing dependencies")
        sys.exit(1)
    
    # Launch demo
    print("🚀 Enhanced Image Processing Demo Launcher")
    print("=" * 50)
    
    success = launch_demo(
        debug_mode=args.debug,
        port=args.port,
        share=args.share
    )
    
    if not success:
        print("❌ Demo launch failed")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


