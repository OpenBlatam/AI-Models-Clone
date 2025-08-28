#!/usr/bin/env python3
"""
🚀 Pydantic V2 Migration Utility - Automated Migration and Optimization
=======================================================================

Automatically migrates Pydantic V1 models to V2, replacing deprecated
validators and optimizing performance with ORJSON integration.
"""

import ast
import re
import os
import sys
from typing import Dict, List, Any, Optional, Tuple, Set
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

# Try to import Pydantic
try:
    import pydantic
    PYDANTIC_VERSION = pydantic.VERSION
    HAS_PYDANTIC = True
except ImportError:
    HAS_PYDANTIC = False
    PYDANTIC_VERSION = "0.0.0"

try:
    import orjson
    HAS_ORJSON = True
except ImportError:
    HAS_ORJSON = False

logger = logging.getLogger(__name__)

# =============================================================================
# Migration Types
# =============================================================================

class MigrationType(Enum):
    """Types of migrations needed."""
    VALIDATOR_TO_FIELD_VALIDATOR = "validator_to_field_validator"
    ROOT_VALIDATOR_TO_MODEL_VALIDATOR = "root_validator_to_model_validator"
    CONFIG_CLASS_TO_CONFIGDICT = "config_class_to_configdict"
    ORJSON_INTEGRATION = "orjson_integration"
    VALIDATE_ASSIGNMENT = "validate_assignment"
    FROZEN_MODELS = "frozen_models"

@dataclass
class MigrationIssue:
    """Represents a migration issue found in code."""
    file_path: str
    line_number: int
    issue_type: MigrationType
    description: str
    old_code: str
    new_code: str
    severity: str = "medium"

@dataclass
class MigrationResult:
    """Result of a migration operation."""
    file_path: str
    issues_found: List[MigrationIssue]
    issues_fixed: List[MigrationIssue]
    errors: List[str]
    success: bool

# =============================================================================
# Code Analysis
# =============================================================================

class PydanticCodeAnalyzer:
    """Analyzes Python code for Pydantic V1 patterns."""
    
    def __init__(self):
        self.issues: List[MigrationIssue] = []
        self.imports_to_add: Set[str] = set()
        self.imports_to_remove: Set[str] = set()
    
    def analyze_file(self, file_path: str) -> List[MigrationIssue]:
        """Analyze a single Python file for Pydantic issues."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            self.issues = []
            self.imports_to_add = set()
            self.imports_to_remove = set()
            
            # Analyze the AST
            self._analyze_ast(tree, file_path)
            
            return self.issues
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def _analyze_ast(self, tree: ast.AST, file_path: str):
        """Analyze AST for Pydantic patterns."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._analyze_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._analyze_class(node, file_path)
            elif isinstance(node, ast.Import):
                self._analyze_import(node, file_path)
            elif isinstance(node, ast.ImportFrom):
                self._analyze_import_from(node, file_path)
    
    def _analyze_function(self, node: ast.FunctionDef, file_path: str):
        """Analyze function for Pydantic validators."""
        # Check for @validator decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'validator':
                    self._add_validator_issue(node, file_path, decorator)
                elif isinstance(decorator.func, ast.Attribute) and decorator.func.attr == 'validator':
                    self._add_validator_issue(node, file_path, decorator)
            
            elif isinstance(decorator, ast.Name) and decorator.id == 'validator':
                self._add_validator_issue(node, file_path, decorator)
            
            elif isinstance(decorator, ast.Name) and decorator.id == 'root_validator':
                self._add_root_validator_issue(node, file_path, decorator)
    
    def _analyze_class(self, node: ast.ClassDef, file_path: str):
        """Analyze class for Pydantic configuration."""
        for item in node.body:
            if isinstance(item, ast.ClassDef) and item.name == 'Config':
                self._add_config_class_issue(node, file_path, item)
    
    def _analyze_import(self, node: ast.Import, file_path: str):
        """Analyze import statements."""
        for alias in node.names:
            if alias.name == 'pydantic':
                self.imports_to_add.add('from pydantic import ConfigDict')
    
    def _analyze_import_from(self, node: ast.ImportFrom, file_path: str):
        """Analyze from-import statements."""
        if node.module == 'pydantic':
            for alias in node.names:
                if alias.name == 'validator':
                    self.imports_to_remove.add('validator')
                    self.imports_to_add.add('field_validator')
                elif alias.name == 'root_validator':
                    self.imports_to_remove.add('root_validator')
                    self.imports_to_add.add('model_validator')
    
    def _add_validator_issue(self, node: ast.FunctionDef, file_path: str, decorator: ast.AST):
        """Add validator migration issue."""
        # Extract field names from decorator
        field_names = []
        if isinstance(decorator, ast.Call) and decorator.args:
            for arg in decorator.args:
                if isinstance(arg, ast.Str):
                    field_names.append(arg.s)
                elif isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    field_names.append(arg.value)
        
        if not field_names:
            field_names = ['unknown_field']
        
        old_code = f"@validator({', '.join(repr(name) for name in field_names)})"
        new_code = f"@field_validator({', '.join(repr(name) for name in field_names)})"
        
        issue = MigrationIssue(
            file_path=file_path,
            line_number=node.lineno,
            issue_type=MigrationType.VALIDATOR_TO_FIELD_VALIDATOR,
            description=f"Replace @validator with @field_validator for fields: {', '.join(field_names)}",
            old_code=old_code,
            new_code=new_code,
            severity="high"
        )
        
        self.issues.append(issue)
    
    def _add_root_validator_issue(self, node: ast.FunctionDef, file_path: str, decorator: ast.AST):
        """Add root_validator migration issue."""
        old_code = "@root_validator"
        new_code = "@model_validator(mode='before')"
        
        issue = MigrationIssue(
            file_path=file_path,
            line_number=node.lineno,
            issue_type=MigrationType.ROOT_VALIDATOR_TO_MODEL_VALIDATOR,
            description="Replace @root_validator with @model_validator(mode='before')",
            old_code=old_code,
            new_code=new_code,
            severity="high"
        )
        
        self.issues.append(issue)
    
    def _add_config_class_issue(self, class_node: ast.ClassDef, file_path: str, config_node: ast.ClassDef):
        """Add Config class migration issue."""
        old_code = "class Config:"
        new_code = "model_config = ConfigDict("
        
        # Extract Config class attributes
        config_attrs = []
        for item in config_node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        config_attrs.append(target.id)
        
        if config_attrs:
            new_code += f"\n    {', '.join(config_attrs)},\n)"
        else:
            new_code += ")"
        
        issue = MigrationIssue(
            file_path=file_path,
            line_number=config_node.lineno,
            issue_type=MigrationType.CONFIG_CLASS_TO_CONFIGDICT,
            description="Replace Config class with model_config = ConfigDict()",
            old_code=old_code,
            new_code=new_code,
            severity="medium"
        )
        
        self.issues.append(issue)

# =============================================================================
# Code Migration
# =============================================================================

class PydanticCodeMigrator:
    """Migrates Pydantic V1 code to V2."""
    
    def __init__(self):
        self.analyzer = PydanticCodeAnalyzer()
    
    def migrate_file(self, file_path: str) -> MigrationResult:
        """Migrate a single Python file."""
        try:
            # Analyze the file
            issues = self.analyzer.analyze_file(file_path)
            
            if not issues:
                return MigrationResult(
                    file_path=file_path,
                    issues_found=[],
                    issues_fixed=[],
                    errors=[],
                    success=True
                )
            
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply migrations
            new_content, fixed_issues, errors = self._apply_migrations(content, issues, file_path)
            
            # Write updated content
            if new_content != content:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
            
            return MigrationResult(
                file_path=file_path,
                issues_found=issues,
                issues_fixed=fixed_issues,
                errors=errors,
                success=len(errors) == 0
            )
            
        except Exception as e:
            return MigrationResult(
                file_path=file_path,
                issues_found=[],
                issues_fixed=[],
                errors=[str(e)],
                success=False
            )
    
    def _apply_migrations(self, content: str, issues: List[MigrationIssue], file_path: str) -> Tuple[str, List[MigrationIssue], List[str]]:
        """Apply all migrations to the content."""
        new_content = content
        fixed_issues = []
        errors = []
        
        # Sort issues by line number (reverse order to avoid line number shifts)
        sorted_issues = sorted(issues, key=lambda x: x.line_number, reverse=True)
        
        for issue in sorted_issues:
            try:
                new_content, success = self._apply_single_migration(new_content, issue)
                if success:
                    fixed_issues.append(issue)
                else:
                    errors.append(f"Failed to apply migration: {issue.description}")
            except Exception as e:
                errors.append(f"Error applying migration: {e}")
        
        # Add ORJSON integration if possible
        if HAS_ORJSON:
            new_content = self._add_orjson_integration(new_content)
        
        return new_content, fixed_issues, errors
    
    def _apply_single_migration(self, content: str, issue: MigrationIssue) -> Tuple[str, bool]:
        """Apply a single migration to the content."""
        lines = content.split('\n')
        
        if issue.line_number > len(lines):
            return content, False
        
        line_index = issue.line_number - 1
        old_line = lines[line_index]
        
        if issue.issue_type == MigrationType.VALIDATOR_TO_FIELD_VALIDATOR:
            # Replace @validator with @field_validator
            new_line = old_line.replace('@validator', '@field_validator')
            if '@field_validator' in new_line:
                # Add @classmethod decorator if not present
                if line_index > 0 and not lines[line_index - 1].strip().startswith('@classmethod'):
                    lines.insert(line_index, '    @classmethod')
                    lines[line_index + 1] = '    ' + new_line
                else:
                    lines[line_index] = new_line
                return '\n'.join(lines), True
        
        elif issue.issue_type == MigrationType.ROOT_VALIDATOR_TO_MODEL_VALIDATOR:
            # Replace @root_validator with @model_validator
            new_line = old_line.replace('@root_validator', '@model_validator(mode=\'before\')')
            if '@model_validator' in new_line:
                # Add @classmethod decorator if not present
                if line_index > 0 and not lines[line_index - 1].strip().startswith('@classmethod'):
                    lines.insert(line_index, '    @classmethod')
                    lines[line_index + 1] = '    ' + new_line
                else:
                    lines[line_index] = new_line
                return '\n'.join(lines), True
        
        elif issue.issue_type == MigrationType.CONFIG_CLASS_TO_CONFIGDICT:
            # Replace Config class with model_config
            # This is more complex and requires parsing the Config class
            return self._migrate_config_class(content, issue)
        
        return content, False
    
    def _migrate_config_class(self, content: str, issue: MigrationIssue) -> Tuple[str, bool]:
        """Migrate Config class to model_config."""
        try:
            # Find the Config class and extract its attributes
            lines = content.split('\n')
            config_start = issue.line_number - 1
            
            # Find the end of the Config class
            config_end = config_start
            indent_level = len(lines[config_start]) - len(lines[config_start].lstrip())
            
            for i in range(config_start + 1, len(lines)):
                if lines[i].strip() == '':
                    continue
                current_indent = len(lines[i]) - len(lines[i].lstrip())
                if current_indent <= indent_level and lines[i].strip():
                    config_end = i
                    break
                config_end = i
            
            # Extract Config attributes
            config_attrs = []
            for i in range(config_start + 1, config_end):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        attr_name = line.split('=')[0].strip()
                        config_attrs.append(attr_name)
            
            # Create model_config line
            if config_attrs:
                model_config_line = f"    model_config = ConfigDict({', '.join(config_attrs)})"
            else:
                model_config_line = "    model_config = ConfigDict()"
            
            # Replace Config class with model_config
            new_lines = lines[:config_start]
            new_lines.append(model_config_line)
            new_lines.extend(lines[config_end:])
            
            return '\n'.join(new_lines), True
            
        except Exception as e:
            logger.error(f"Error migrating Config class: {e}")
            return content, False
    
    def _add_orjson_integration(self, content: str) -> str:
        """Add ORJSON integration for better performance."""
        if 'orjson' not in content and HAS_ORJSON:
            # Add import
            import_pattern = r'from pydantic import'
            if re.search(import_pattern, content):
                content = re.sub(
                    import_pattern,
                    'from pydantic import',
                    content
                )
            
            # Add model_config with ORJSON if not present
            if 'model_config = ConfigDict' not in content:
                # Find the first class definition
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if line.strip().startswith('class ') and ':' in line:
                        # Add model_config after the class definition
                        indent = len(line) - len(line.lstrip())
                        config_line = ' ' * (indent + 4) + 'model_config = ConfigDict(json_encoders={str: str}, json_loads=orjson.loads, json_dumps=orjson.dumps)'
                        lines.insert(i + 1, config_line)
                        break
                
                content = '\n'.join(lines)
        
        return content

# =============================================================================
# Batch Migration
# =============================================================================

class BatchPydanticMigrator:
    """Migrates multiple files in batch."""
    
    def __init__(self, target_directory: str = "."):
        self.target_directory = Path(target_directory)
        self.migrator = PydanticCodeMigrator()
        self.results: List[MigrationResult] = []
    
    def migrate_directory(self, recursive: bool = True) -> List[MigrationResult]:
        """Migrate all Python files in the directory."""
        self.results = []
        
        if recursive:
            python_files = list(self.target_directory.rglob("*.py"))
        else:
            python_files = list(self.target_directory.glob("*.py"))
        
        # Filter out test files and virtual environments
        python_files = [
            f for f in python_files 
            if not any(part.startswith('.') for part in f.parts)
            and 'test' not in f.name.lower()
            and 'venv' not in str(f)
            and 'env' not in str(f)
        ]
        
        logger.info(f"Found {len(python_files)} Python files to migrate")
        
        for file_path in python_files:
            try:
                result = self.migrator.migrate_file(str(file_path))
                self.results.append(result)
                
                if result.success:
                    logger.info(f"✅ Migrated: {file_path}")
                else:
                    logger.warning(f"⚠️  Migration issues in: {file_path}")
                    
            except Exception as e:
                logger.error(f"❌ Error migrating {file_path}: {e}")
                self.results.append(MigrationResult(
                    file_path=str(file_path),
                    issues_found=[],
                    issues_fixed=[],
                    errors=[str(e)],
                    success=False
                ))
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate a migration report."""
        total_files = len(self.results)
        successful_migrations = sum(1 for r in self.results if r.success)
        total_issues = sum(len(r.issues_found) for r in self.results)
        fixed_issues = sum(len(r.issues_fixed) for r in self.results)
        total_errors = sum(len(r.errors) for r in self.results)
        
        report = f"""
🚀 Pydantic V2 Migration Report
================================

📊 Summary:
- Total files processed: {total_files}
- Successful migrations: {successful_migrations}
- Failed migrations: {total_files - successful_migrations}
- Total issues found: {total_issues}
- Issues fixed: {fixed_issues}
- Errors encountered: {total_errors}

📁 Files with issues:
"""
        
        for result in self.results:
            if result.issues_found or result.errors:
                report += f"\n{result.file_path}:\n"
                for issue in result.issues_found:
                    report += f"  - {issue.description} (Line {issue.line_number})\n"
                for error in result.errors:
                    report += f"  - ERROR: {error}\n"
        
        return report

# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """Main CLI function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrate Pydantic V1 code to V2")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to migrate")
    parser.add_argument("--recursive", "-r", action="store_true", help="Recursively migrate subdirectories")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='%(levelname)s: %(message)s')
    
    # Check Pydantic version
    if not HAS_PYDANTIC:
        logger.error("Pydantic is not installed")
        sys.exit(1)
    
    logger.info(f"Pydantic version: {PYDANTIC_VERSION}")
    
    if PYDANTIC_VERSION.startswith('1.'):
        logger.warning("You're running Pydantic V1. Consider upgrading to V2 first.")
    
    # Create migrator
    migrator = BatchPydanticMigrator(args.directory)
    
    if args.dry_run:
        # Just analyze without migrating
        logger.info("DRY RUN MODE - No files will be modified")
        results = []
        python_files = list(Path(args.directory).rglob("*.py") if args.recursive else Path(args.directory).glob("*.py"))
        
        for file_path in python_files:
            if not any(part.startswith('.') for part in file_path.parts):
                issues = migrator.migrator.analyzer.analyze_file(str(file_path))
                if issues:
                    results.append(MigrationResult(
                        file_path=str(file_path),
                        issues_found=issues,
                        issues_fixed=[],
                        errors=[],
                        success=True
                    ))
        
        migrator.results = results
    else:
        # Perform actual migration
        logger.info(f"Starting migration of {args.directory}")
        migrator.migrate_directory(recursive=args.recursive)
    
    # Generate and display report
    report = migrator.generate_report()
    print(report)
    
    # Save report to file
    report_file = Path(args.directory) / "pydantic_migration_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    logger.info(f"Migration report saved to: {report_file}")

if __name__ == "__main__":
    main()
