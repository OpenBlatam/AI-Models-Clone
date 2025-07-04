#!/usr/bin/env python3
"""
NotebookLM AI - Dependency Management Script

This script helps manage the installation and updates of NotebookLM AI dependencies.
"""

import argparse
import subprocess
import sys
import os
from pathlib import Path
from typing import List, Optional


class DependencyManager:
    """Manages NotebookLM AI dependencies."""
    
    def __init__(self, requirements_dir: str = "requirements"):
        self.requirements_dir = Path(requirements_dir)
        self.available_modules = {
            "base": "base.txt",
            "ai-ml": "ai-ml.txt", 
            "document-processing": "document-processing.txt",
            "web-api": "web-api.txt",
            "multimedia": "multimedia.txt",
            "cloud-deployment": "cloud-deployment.txt",
            "development": "development.txt",
            "complete": "requirements.txt",
            "production": "production.txt",
            "minimal": "minimal.txt"
        }
    
    def list_modules(self) -> None:
        """List all available dependency modules."""
        print("📦 Available dependency modules:")
        print()
        for module, filename in self.available_modules.items():
            filepath = self.requirements_dir / filename
            if filepath.exists():
                print(f"  ✅ {module:20} -> {filename}")
            else:
                print(f"  ❌ {module:20} -> {filename} (missing)")
        print()
    
    def install_module(self, module: str, upgrade: bool = False, user: bool = False) -> bool:
        """Install a specific dependency module."""
        if module not in self.available_modules:
            print(f"❌ Error: Module '{module}' not found.")
            return False
        
        filename = self.available_modules[module]
        filepath = self.requirements_dir / filename
        
        if not filepath.exists():
            print(f"❌ Error: Requirements file '{filename}' not found.")
            return False
        
        cmd = [sys.executable, "-m", "pip", "install"]
        
        if upgrade:
            cmd.append("--upgrade")
        
        if user:
            cmd.append("--user")
        
        cmd.extend(["-r", str(filepath)])
        
        print(f"📦 Installing {module} dependencies...")
        print(f"   Command: {' '.join(cmd)}")
        print()
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("✅ Installation completed successfully!")
            if result.stdout:
                print(result.stdout)
            return True
        except subprocess.CalledProcessError as e:
            print("❌ Installation failed!")
            if e.stdout:
                print("STDOUT:", e.stdout)
            if e.stderr:
                print("STDERR:", e.stderr)
            return False
    
    def install_multiple_modules(self, modules: List[str], upgrade: bool = False, user: bool = False) -> bool:
        """Install multiple dependency modules."""
        success = True
        for module in modules:
            print(f"\n{'='*50}")
            if not self.install_module(module, upgrade, user):
                success = False
                print(f"⚠️  Failed to install {module}, continuing with other modules...")
        
        if success:
            print(f"\n{'='*50}")
            print("✅ All modules installed successfully!")
        else:
            print(f"\n{'='*50}")
            print("⚠️  Some modules failed to install. Check the output above.")
        
        return success
    
    def check_installed(self, module: str) -> bool:
        """Check if a module's dependencies are installed."""
        if module not in self.available_modules:
            return False
        
        filename = self.available_modules[module]
        filepath = self.requirements_dir / filename
        
        if not filepath.exists():
            return False
        
        # Read requirements and check if packages are installed
        try:
            with open(filepath, 'r') as f:
                requirements = f.readlines()
            
            missing_packages = []
            for line in requirements:
                line = line.strip()
                if line and not line.startswith('#') and not line.startswith('-r'):
                    package = line.split('==')[0].split('[')[0].strip()
                    
                    try:
                        __import__(package.replace('-', '_'))
                    except ImportError:
                        missing_packages.append(package)
            
            if missing_packages:
                print(f"❌ Module '{module}' has missing packages: {', '.join(missing_packages)}")
                return False
            else:
                print(f"✅ Module '{module}' dependencies are installed.")
                return True
                
        except Exception as e:
            print(f"❌ Error checking module '{module}': {e}")
            return False
    
    def update_all(self, user: bool = False) -> bool:
        """Update all dependencies to latest versions."""
        print("🔄 Updating all dependencies...")
        return self.install_multiple_modules(list(self.available_modules.keys()), upgrade=True, user=user)
    
    def create_requirements_lock(self, output_file: str = "requirements.lock") -> bool:
        """Create a locked requirements file with exact versions."""
        try:
            cmd = [
                sys.executable, "-m", "pip", "freeze"
            ]
            
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            with open(output_file, 'w') as f:
                f.write("# NotebookLM AI - Locked Requirements\n")
                f.write("# Generated by install.py\n\n")
                f.write(result.stdout)
            
            print(f"✅ Locked requirements saved to {output_file}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create requirements lock: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description="NotebookLM AI Dependency Manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python install.py list                           # List all modules
  python install.py install minimal                # Install minimal dependencies
  python install.py install complete               # Install all dependencies
  python install.py install ai-ml web-api          # Install specific modules
  python install.py install production --upgrade   # Install production deps with upgrade
  python install.py check ai-ml                    # Check if AI/ML module is installed
  python install.py update                         # Update all dependencies
  python install.py lock                           # Create requirements.lock file
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all available dependency modules')
    
    # Install command
    install_parser = subparsers.add_parser('install', help='Install dependency modules')
    install_parser.add_argument('modules', nargs='+', help='Modules to install')
    install_parser.add_argument('--upgrade', '-U', action='store_true', help='Upgrade packages')
    install_parser.add_argument('--user', action='store_true', help='Install to user directory')
    
    # Check command
    check_parser = subparsers.add_parser('check', help='Check if modules are installed')
    check_parser.add_argument('modules', nargs='+', help='Modules to check')
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update all dependencies')
    update_parser.add_argument('--user', action='store_true', help='Install to user directory')
    
    # Lock command
    subparsers.add_parser('lock', help='Create requirements.lock file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    manager = DependencyManager()
    
    if args.command == 'list':
        manager.list_modules()
    
    elif args.command == 'install':
        success = manager.install_multiple_modules(
            args.modules, 
            upgrade=args.upgrade, 
            user=args.user
        )
        sys.exit(0 if success else 1)
    
    elif args.command == 'check':
        all_installed = True
        for module in args.modules:
            if not manager.check_installed(module):
                all_installed = False
        sys.exit(0 if all_installed else 1)
    
    elif args.command == 'update':
        success = manager.update_all(user=args.user)
        sys.exit(0 if success else 1)
    
    elif args.command == 'lock':
        success = manager.create_requirements_lock()
        sys.exit(0 if success else 1)


if __name__ == "__main__":
    main() 
    