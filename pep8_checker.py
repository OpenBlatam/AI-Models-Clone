#!/usr/bin/env python3
"""
PEP 8 Compliance Checker and Fixer

This script checks and fixes PEP 8 compliance issues in the Python codebase.
It uses black for formatting, isort for import sorting, and flake8 for linting.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PEP8Checker:
    """PEP 8 compliance checker and fixer."""
    
    def __init__(self, project_root: str = "."):
        """Initialize the PEP 8 checker.
        
        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        self.python_files = []
        self.issues = []
        
    def find_python_files(self, exclude_dirs: Optional[List[str]] = None) -> List[Path]:
        """Find all Python files in the project.
        
        Args:
            exclude_dirs: Directories to exclude from search
            
        Returns:
            List of Python file paths
        """
        if exclude_dirs is None:
            exclude_dirs = [
                ".git", "__pycache__", "build", "dist", ".venv", 
                "venv", "env", ".pytest_cache", ".mypy_cache"
            ]
        
        python_files = []
        
        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        self.python_files = python_files
        logger.info(f"Found {len(python_files)} Python files")
        return python_files
    
    def check_imports(self, fix: bool = False) -> Dict[str, Any]:
        """Check and fix import sorting using isort.
        
        Args:
            fix: Whether to fix import issues automatically
            
        Returns:
            Dictionary with check results
        """
        logger.info("Checking import sorting...")
        
        try:
            cmd = ["isort", "--check-only", "--diff"]
            if fix:
                cmd = ["isort"]
            
            cmd.extend([str(f) for f in self.python_files])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ Import sorting is correct")
                return {"status": "passed", "output": result.stdout}
            else:
                logger.warning("⚠️ Import sorting issues found")
                if fix:
                    logger.info("✅ Import sorting fixed")
                return {"status": "failed", "output": result.stdout}
                
        except FileNotFoundError:
            logger.error("❌ isort not found. Install with: pip install isort")
            return {"status": "error", "message": "isort not installed"}
    
    def check_formatting(self, fix: bool = False) -> Dict[str, Any]:
        """Check and fix code formatting using black.
        
        Args:
            fix: Whether to fix formatting issues automatically
            
        Returns:
            Dictionary with check results
        """
        logger.info("Checking code formatting...")
        
        try:
            cmd = ["black", "--check", "--diff"]
            if fix:
                cmd = ["black"]
            
            cmd.extend([str(f) for f in self.python_files])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ Code formatting is correct")
                return {"status": "passed", "output": result.stdout}
            else:
                logger.warning("⚠️ Code formatting issues found")
                if fix:
                    logger.info("✅ Code formatting fixed")
                return {"status": "failed", "output": result.stdout}
                
        except FileNotFoundError:
            logger.error("❌ black not found. Install with: pip install black")
            return {"status": "error", "message": "black not installed"}
    
    def check_linting(self) -> Dict[str, Any]:
        """Check code with flake8 for PEP 8 violations.
        
        Returns:
            Dictionary with check results
        """
        logger.info("Checking PEP 8 linting...")
        
        try:
            cmd = ["flake8", "--max-line-length=79", "--extend-ignore=E203,W503"]
            cmd.extend([str(f) for f in self.python_files])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ No PEP 8 violations found")
                return {"status": "passed", "output": result.stdout}
            else:
                logger.warning("⚠️ PEP 8 violations found")
                return {"status": "failed", "output": result.stdout}
                
        except FileNotFoundError:
            logger.error("❌ flake8 not found. Install with: pip install flake8")
            return {"status": "error", "message": "flake8 not installed"}
    
    def check_type_hints(self) -> Dict[str, Any]:
        """Check type hints using mypy.
        
        Returns:
            Dictionary with check results
        """
        logger.info("Checking type hints...")
        
        try:
            cmd = ["mypy", "--ignore-missing-imports", "--no-strict-optional"]
            cmd.extend([str(f) for f in self.python_files])
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=self.project_root
            )
            
            if result.returncode == 0:
                logger.info("✅ Type hints are correct")
                return {"status": "passed", "output": result.stdout}
            else:
                logger.warning("⚠️ Type hint issues found")
                return {"status": "failed", "output": result.stdout}
                
        except FileNotFoundError:
            logger.error("❌ mypy not found. Install with: pip install mypy")
            return {"status": "error", "message": "mypy not installed"}
    
    def generate_report(self, results: Dict[str, Dict[str, Any]]) -> str:
        """Generate a comprehensive report of all checks.
        
        Args:
            results: Dictionary with check results
            
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 60)
        report.append("PEP 8 COMPLIANCE REPORT")
        report.append("=" * 60)
        report.append("")
        
        total_checks = len(results)
        passed_checks = sum(1 for r in results.values() if r["status"] == "passed")
        failed_checks = sum(1 for r in results.values() if r["status"] == "failed")
        error_checks = sum(1 for r in results.values() if r["status"] == "error")
        
        report.append(f"Total Checks: {total_checks}")
        report.append(f"✅ Passed: {passed_checks}")
        report.append(f"⚠️ Failed: {failed_checks}")
        report.append(f"❌ Errors: {error_checks}")
        report.append("")
        
        for check_name, result in results.items():
            status_icon = {
                "passed": "✅",
                "failed": "⚠️",
                "error": "❌"
            }.get(result["status"], "❓")
            
            report.append(f"{status_icon} {check_name.upper()}: {result['status']}")
            
            if result["status"] == "failed" and "output" in result:
                report.append("   Details:")
                for line in result["output"].split("\n")[:10]:  # Show first 10 lines
                    if line.strip():
                        report.append(f"   {line}")
                if len(result["output"].split("\n")) > 10:
                    report.append("   ... (truncated)")
                report.append("")
        
        report.append("=" * 60)
        return "\n".join(report)
    
    def run_all_checks(self, fix: bool = False) -> Dict[str, Any]:
        """Run all PEP 8 compliance checks.
        
        Args:
            fix: Whether to fix issues automatically where possible
            
        Returns:
            Dictionary with all check results
        """
        logger.info("Starting PEP 8 compliance check...")
        
        # Find Python files
        self.find_python_files()
        
        # Run all checks
        results = {
            "imports": self.check_imports(fix=fix),
            "formatting": self.check_formatting(fix=fix),
            "linting": self.check_linting(),
            "type_hints": self.check_type_hints()
        }
        
        # Generate report
        report = self.generate_report(results)
        
        return {
            "results": results,
            "report": report,
            "summary": {
                "total_files": len(self.python_files),
                "passed_checks": sum(1 for r in results.values() if r["status"] == "passed"),
                "failed_checks": sum(1 for r in results.values() if r["status"] == "failed"),
                "error_checks": sum(1 for r in results.values() if r["status"] == "error")
            }
        }


def create_config_files():
    """Create configuration files for PEP 8 tools."""
    
    # Create pyproject.toml
    pyproject_content = '''[tool.black]
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

[tool.isort]
profile = "black"
line_length = 79
multi_line_output = 3
include_trailing_comma = true
force_grid_wrap = 0
use_parentheses = true
ensure_newline_before_comments = true

[tool.flake8]
max-line-length = 79
extend-ignore = ["E203", "W503"]
exclude = .git,__pycache__,build,dist,.venv,venv,env
'''
    
    # Create .flake8
    flake8_content = '''[flake8]
max-line-length = 79
extend-ignore = E203, W503
exclude = .git,__pycache__,build,dist,.venv,venv,env
'''
    
    # Create .pre-commit-config.yaml
    precommit_content = '''repos:
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
'''
    
    configs = {
        "pyproject.toml": pyproject_content,
        ".flake8": flake8_content,
        ".pre-commit-config.yaml": precommit_content
    }
    
    for filename, content in configs.items():
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(content)
            logger.info(f"Created {filename}")
        else:
            logger.info(f"{filename} already exists")


def main():
    """Main function to run PEP 8 compliance checks."""
    parser = argparse.ArgumentParser(description="PEP 8 Compliance Checker")
    parser.add_argument(
        "--fix", 
        action="store_true", 
        help="Automatically fix formatting and import issues"
    )
    parser.add_argument(
        "--create-configs", 
        action="store_true", 
        help="Create configuration files for PEP 8 tools"
    )
    parser.add_argument(
        "--project-root", 
        default=".", 
        help="Project root directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    if args.create_configs:
        create_config_files()
        return
    
    # Run PEP 8 checks
    checker = PEP8Checker(args.project_root)
    results = checker.run_all_checks(fix=args.fix)
    
    # Print report
    print(results["report"])
    
    # Exit with appropriate code
    if results["summary"]["failed_checks"] > 0 or results["summary"]["error_checks"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main() 