#!/usr/bin/env python3
"""
Simple Installation Launcher for Email Sequence AI System

Usage:
    python install.py                    # Interactive installation
    python install.py --profile minimal  # Install minimal profile
    python install.py --profile all      # Install all features
"""

import sys
from pathlib import Path

# Add scripts directory to path
scripts_dir = Path(__file__).parent / "scripts"
sys.path.insert(0, str(scripts_dir))

try:
    from install_dependencies import DependencyInstaller, main
except ImportError:
    print("❌ Could not import installation script.")
    print("Please run: python scripts/install_dependencies.py")
    sys.exit(1)

if __name__ == "__main__":
    main() 