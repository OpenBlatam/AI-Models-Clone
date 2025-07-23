#!/usr/bin/env python3
"""
Apply PEP 8 Fixes to Python Files

This script automatically applies PEP 8 formatting fixes to Python files
in the codebase using black and isort.
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def install_pep8_tools() -> bool:
    """Install PEP 8 compliance tools.
    
    Returns:
        True if installation successful, False otherwise
    """
    tools = ["black", "isort", "flake8"]
    
    for tool in tools:
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", tool],
                check=True,
                capture_output=True
            )
            logger.info(f"✅ Installed {tool}")
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install {tool}: {e}")
            return False
    
    return True


def find_python_files(
    root_dir: str = ".",
    exclude_dirs: Optional[List[str]] = None
) -> List[Path]:
    """Find all Python files in the directory tree.
    
    Args:
        root_dir: Root directory to search
        exclude_dirs: Directories to exclude
        
    Returns:
        List of Python file paths
    """
    if exclude_dirs is None:
        exclude_dirs = [
            ".git", "__pycache__", "build", "dist", ".venv",
            "venv", "env", ".pytest_cache", ".mypy_cache"
        ]
    
    python_files = []
    root_path = Path(root_dir).resolve()
    
    for root, dirs, files in os.walk(root_path):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(Path(root) / file)
    
    return python_files


def apply_black_formatting(files: List[Path]) -> bool:
    """Apply black formatting to Python files.
    
    Args:
        files: List of Python files to format
        
    Returns:
        True if formatting successful, False otherwise
    """
    logger.info("Applying black formatting...")
    
    try:
        # Create black configuration
        black_config = """[tool.black]
line-length = 79
target-version = ['py38']
include = '\\.pyi?$'
extend-exclude = '''
/(
  # directories
  \\.eggs
| \\.git
| \\.hg
| \\.mypy_cache
| \\.tox
| \\.venv
| build
| dist
)/
'''
"""
        
        # Write black configuration
        with open("pyproject.toml", "w") as f:
            f.write(black_config)
        
        # Apply black formatting
        cmd = ["black"] + [str(f) for f in files]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Black formatting applied successfully")
            return True
        else:
            logger.error(f"❌ Black formatting failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error applying black formatting: {e}")
        return False


def apply_isort_sorting(files: List[Path]) -> bool:
    """Apply isort import sorting to Python files.
    
    Args:
        files: List of Python files to sort imports for
        
    Returns:
        True if sorting successful, False otherwise
    """
    logger.info("Applying isort import sorting...")
    
    try:
        # Create isort configuration
        isort_config = """[tool.isort]
profile = "black"
line_length = 79
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true
"""
        
        # Update pyproject.toml with isort config
        with open("pyproject.toml", "a") as f:
            f.write("\n" + isort_config)
        
        # Apply isort sorting
        cmd = ["isort"] + [str(f) for f in files]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ Isort import sorting applied successfully")
            return True
        else:
            logger.error(f"❌ Isort sorting failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error applying isort sorting: {e}")
        return False


def create_flake8_config() -> bool:
    """Create flake8 configuration file.
    
    Returns:
        True if configuration created successfully, False otherwise
    """
    try:
        flake8_config = """[flake8]
max-line-length = 79
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv,venv,env
"""
        
        with open(".flake8", "w") as f:
            f.write(flake8_config)
        
        logger.info("✅ Created .flake8 configuration")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating flake8 config: {e}")
        return False


def run_flake8_check(files: List[Path]) -> bool:
    """Run flake8 linting check.
    
    Args:
        files: List of Python files to check
        
    Returns:
        True if no violations found, False otherwise
    """
    logger.info("Running flake8 linting check...")
    
    try:
        cmd = ["flake8", "--max-line-length=79", "--extend-ignore=E203,W503"]
        cmd.extend([str(f) for f in files])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ No PEP 8 violations found")
            return True
        else:
            logger.warning("⚠️ PEP 8 violations found:")
            print(result.stdout)
            return False
            
    except Exception as e:
        logger.error(f"❌ Error running flake8: {e}")
        return False


def create_precommit_config() -> bool:
    """Create pre-commit configuration file.
    
    Returns:
        True if configuration created successfully, False otherwise
    """
    try:
        precommit_config = """repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
"""
        
        with open(".pre-commit-config.yaml", "w") as f:
            f.write(precommit_config)
        
        logger.info("✅ Created .pre-commit-config.yaml")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating pre-commit config: {e}")
        return False


def main():
    """Main function to apply PEP 8 fixes."""
    logger.info("Starting PEP 8 fixes application...")
    
    # Check if tools are installed
    try:
        import black
        import isort
        import flake8
        logger.info("✅ PEP 8 tools already installed")
    except ImportError:
        logger.info("Installing PEP 8 tools...")
        if not install_pep8_tools():
            logger.error("❌ Failed to install PEP 8 tools")
            sys.exit(1)
    
    # Find Python files
    python_files = find_python_files()
    logger.info(f"Found {len(python_files)} Python files")
    
    if not python_files:
        logger.warning("No Python files found")
        return
    
    # Apply fixes
    success = True
    
    # Apply black formatting
    if not apply_black_formatting(python_files):
        success = False
    
    # Apply isort sorting
    if not apply_isort_sorting(python_files):
        success = False
    
    # Create flake8 configuration
    if not create_flake8_config():
        success = False
    
    # Run flake8 check
    if not run_flake8_check(python_files):
        success = False
    
    # Create pre-commit configuration
    if not create_precommit_config():
        success = False
    
    # Summary
    if success:
        logger.info("✅ All PEP 8 fixes applied successfully")
        logger.info("📝 Next steps:")
        logger.info("   1. Review the changes")
        logger.info("   2. Install pre-commit hooks: pre-commit install")
        logger.info("   3. Run tests to ensure functionality is preserved")
    else:
        logger.error("❌ Some PEP 8 fixes failed")
        sys.exit(1)


if __name__ == "__main__":
    main() 