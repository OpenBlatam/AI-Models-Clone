#!/usr/bin/env python3
"""
Pydantic v2 Migration Script
Automated migration from Pydantic v1 to v2 patterns with performance optimizations.
"""

import ast
import astor
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import argparse
import logging
from dataclasses import dataclass
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MigrationStats:
    """Statistics for migration process."""
    files_processed: int = 0
    files_modified: int = 0
    validators_migrated: int = 0
    config_classes_migrated: int = 0
    imports_updated: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    def add_error(self, error: str) -> None:
        """Add an error to the stats."""
        self.errors.append(error)
    
    def print_summary(self) -> None:
        """Print migration summary."""
        print("\n" + "="*60)
        print("PYDANTIC V2 MIGRATION SUMMARY")
        print("="*60)
        print(f"Files processed: {self.files_processed}")
        print(f"Files modified: {self.files_modified}")
        print(f"Validators migrated: {self.validators_migrated}")
        print(f"Config classes migrated: {self.config_classes_migrated}")
        print(f"Imports updated: {self.imports_updated}")
        
        if self.errors:
            print(f"\nErrors encountered: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

class PydanticV2Migrator(ast.NodeTransformer):
    """AST transformer for migrating Pydantic v1 to v2 patterns."""
    
    def __init__(self, stats: MigrationStats):
        self.stats = stats
        self.current_class = None
        self.imports_to_add = set()
        self.imports_to_remove = set()
        self.validator_mappings = {
            'validator': 'field_validator',
            'root_validator': 'model_validator'
        }
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> ast.ImportFrom:
        """Update import statements."""
        if node.module == 'pydantic':
            # Track imports to update
            for alias in node.names:
                if alias.name in self.validator_mappings:
                    self.imports_to_remove.add(alias.name)
                    self.imports_to_add.add(self.validator_mappings[alias.name])
                    self.stats.imports_updated += 1
                
                # Add ConfigDict if not present
                if alias.name == 'BaseModel' and 'ConfigDict' not in [a.name for a in node.names]:
                    self.imports_to_add.add('ConfigDict')
                    self.stats.imports_updated += 1
        
        return node
    
    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Process class definitions."""
        self.current_class = node.name
        
        # Process class body
        node.body = [self.visit(stmt) for stmt in node.body]
        
        # Check for Config class
        config_class = self._find_config_class(node)
        if config_class:
            node = self._migrate_config_class(node, config_class)
        
        self.current_class = None
        return node
    
    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Process function definitions (validators)."""
        # Check if this is a validator
        if self._is_validator(node):
            node = self._migrate_validator(node)
        
        return node
    
    def _is_validator(self, node: ast.FunctionDef) -> bool:
        """Check if function is a validator."""
        if not node.decorator_list:
            return False
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id in ['validator', 'root_validator']:
                        return True
            elif isinstance(decorator, ast.Name):
                if decorator.id in ['validator', 'root_validator']:
                    return True
        
        return False
    
    def _migrate_validator(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Migrate validator to v2 syntax."""
        new_decorators = []
        
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name):
                    if decorator.func.id == 'validator':
                        # Convert @validator to @field_validator
                        new_decorator = ast.Call(
                            func=ast.Name(id='field_validator', ctx=ast.Load()),
                            args=decorator.args,
                            keywords=decorator.keywords
                        )
                        new_decorators.append(new_decorator)
                        self.stats.validators_migrated += 1
                        
                        # Add @classmethod decorator
                        new_decorators.append(ast.Name(id='classmethod', ctx=ast.Load()))
                        
                    elif decorator.func.id == 'root_validator':
                        # Convert @root_validator to @model_validator
                        new_decorator = ast.Call(
                            func=ast.Name(id='model_validator', ctx=ast.Load()),
                            args=[],
                            keywords=[ast.keyword(arg='mode', value=ast.Constant(value='after'))]
                        )
                        new_decorators.append(new_decorator)
                        self.stats.validators_migrated += 1
                        
                        # Add @classmethod decorator
                        new_decorators.append(ast.Name(id='classmethod', ctx=ast.Load()))
                        
                    else:
                        new_decorators.append(decorator)
                else:
                    new_decorators.append(decorator)
            else:
                new_decorators.append(decorator)
        
        node.decorator_list = new_decorators
        return node
    
    def _find_config_class(self, node: ast.ClassDef) -> Optional[ast.ClassDef]:
        """Find Config class within a model class."""
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == 'Config':
                return stmt
        return None
    
    def _migrate_config_class(self, node: ast.ClassDef, config_class: ast.ClassDef) -> ast.ClassDef:
        """Migrate Config class to model_config."""
        # Remove Config class from body
        node.body = [stmt for stmt in node.body if stmt != config_class]
        
        # Create model_config assignment
        config_dict_args = []
        config_dict_keywords = []
        
        for stmt in config_class.body:
            if isinstance(stmt, ast.Assign):
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        config_dict_keywords.append(
                            ast.keyword(
                                arg=target.id,
                                value=stmt.value
                            )
                        )
        
        model_config_assign = ast.Assign(
            targets=[ast.Name(id='model_config', ctx=ast.Store())],
            value=ast.Call(
                func=ast.Name(id='ConfigDict', ctx=ast.Load()),
                args=config_dict_args,
                keywords=config_dict_keywords
            )
        )
        
        # Insert model_config at the beginning of the class
        node.body.insert(0, model_config_assign)
        self.stats.config_classes_migrated += 1
        
        return node

class PydanticMigrationAnalyzer:
    """Analyzer for Pydantic usage patterns."""
    
    def __init__(self):
        self.patterns = {
            'old_validators': [],
            'config_classes': [],
            'base_model_usage': [],
            'import_patterns': []
        }
    
    def analyze_file(self, file_path: Path) -> Dict[str, Any]:
        """Analyze a single file for Pydantic patterns."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            analyzer = PydanticPatternAnalyzer()
            analyzer.visit(tree)
            
            return {
                'file_path': str(file_path),
                'patterns': analyzer.patterns,
                'has_pydantic': analyzer.has_pydantic,
                'needs_migration': analyzer.needs_migration
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            return {
                'file_path': str(file_path),
                'error': str(e),
                'needs_migration': False
            }
    
    def analyze_directory(self, directory: Path) -> List[Dict[str, Any]]:
        """Analyze all Python files in a directory."""
        results = []
        
        for file_path in directory.rglob("*.py"):
            if "migrations" not in str(file_path) and "venv" not in str(file_path):
                result = self.analyze_file(file_path)
                results.append(result)
        
        return results

class PydanticPatternAnalyzer(ast.NodeVisitor):
    """AST visitor for analyzing Pydantic patterns."""
    
    def __init__(self):
        self.patterns = {
            'old_validators': [],
            'config_classes': [],
            'base_model_usage': [],
            'import_patterns': []
        }
        self.has_pydantic = False
        self.needs_migration = False
    
    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Analyze import statements."""
        if node.module == 'pydantic':
            self.has_pydantic = True
            for alias in node.names:
                if alias.name in ['validator', 'root_validator']:
                    self.patterns['old_validators'].append(alias.name)
                    self.needs_migration = True
                elif alias.name == 'BaseModel':
                    self.patterns['base_model_usage'].append('BaseModel')
    
    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Analyze class definitions."""
        # Check for Config class
        for stmt in node.body:
            if isinstance(stmt, ast.ClassDef) and stmt.name == 'Config':
                self.patterns['config_classes'].append(node.name)
                self.needs_migration = True
        
        # Check for validator decorators
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef):
                for decorator in stmt.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Name):
                            if decorator.func.id in ['validator', 'root_validator']:
                                self.patterns['old_validators'].append(f"{node.name}.{stmt.name}")
                                self.needs_migration = True

def migrate_file(file_path: Path, stats: MigrationStats, dry_run: bool = False) -> bool:
    """Migrate a single file to Pydantic v2."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST
        tree = ast.parse(content)
        
        # Apply migrations
        migrator = PydanticV2Migrator(stats)
        new_tree = migrator.visit(tree)
        
        # Update imports
        new_tree = update_imports(new_tree, migrator.imports_to_add, migrator.imports_to_remove)
        
        # Generate new code
        new_content = astor.to_source(new_tree)
        
        # Check if content changed
        if new_content != content:
            if not dry_run:
                # Create backup
                backup_path = file_path.with_suffix('.py.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # Write new content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                logger.info(f"Migrated: {file_path}")
                stats.files_modified += 1
            else:
                logger.info(f"Would migrate: {file_path}")
            
            return True
        
        return False
        
    except Exception as e:
        error_msg = f"Error migrating {file_path}: {e}"
        logger.error(error_msg)
        stats.add_error(error_msg)
        return False

def update_imports(tree: ast.Module, to_add: set, to_remove: set) -> ast.Module:
    """Update import statements in the AST."""
    new_body = []
    
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module == 'pydantic':
            # Update existing pydantic import
            new_names = []
            for alias in node.names:
                if alias.name not in to_remove:
                    new_names.append(alias)
            
            # Add new imports
            for name in to_add:
                if name not in [alias.name for alias in new_names]:
                    new_names.append(ast.alias(name=name, asname=None))
            
            if new_names:
                new_node = ast.ImportFrom(
                    module='pydantic',
                    names=new_names,
                    level=0
                )
                new_body.append(new_node)
        else:
            new_body.append(node)
    
    tree.body = new_body
    return tree

def create_migration_report(analysis_results: List[Dict[str, Any]], output_file: Optional[Path] = None) -> None:
    """Create a detailed migration report."""
    report_lines = [
        "# Pydantic v2 Migration Report",
        "",
        "## Summary",
        f"- Files analyzed: {len(analysis_results)}",
        f"- Files needing migration: {sum(1 for r in analysis_results if r.get('needs_migration', False))}",
        f"- Files with errors: {sum(1 for r in analysis_results if 'error' in r)}",
        "",
        "## Files Requiring Migration",
        ""
    ]
    
    for result in analysis_results:
        if result.get('needs_migration', False):
            report_lines.append(f"### {result['file_path']}")
            
            patterns = result.get('patterns', {})
            if patterns.get('old_validators'):
                report_lines.append(f"- Old validators: {', '.join(patterns['old_validators'])}")
            if patterns.get('config_classes'):
                report_lines.append(f"- Config classes: {', '.join(patterns['config_classes'])}")
            if patterns.get('base_model_usage'):
                report_lines.append(f"- BaseModel usage: {', '.join(patterns['base_model_usage'])}")
            
            report_lines.append("")
    
    # Files with errors
    error_files = [r for r in analysis_results if 'error' in r]
    if error_files:
        report_lines.extend([
            "## Files with Errors",
            ""
        ])
        for result in error_files:
            report_lines.append(f"- {result['file_path']}: {result['error']}")
        report_lines.append("")
    
    report_content = "\n".join(report_lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_content)
        logger.info(f"Migration report written to: {output_file}")
    else:
        print(report_content)

def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate Pydantic v1 to v2")
    parser.add_argument("path", help="Path to file or directory to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be migrated without making changes")
    parser.add_argument("--analyze-only", action="store_true", help="Only analyze files, don't migrate")
    parser.add_argument("--report", help="Output file for migration report")
    parser.add_argument("--backup", action="store_true", help="Create backups of modified files")
    
    args = parser.parse_args()
    
    path = Path(args.path)
    if not path.exists():
        logger.error(f"Path does not exist: {path}")
        sys.exit(1)
    
    stats = MigrationStats()
    
    if path.is_file():
        # Single file migration
        if path.suffix == '.py':
            stats.files_processed = 1
            migrate_file(path, stats, args.dry_run)
        else:
            logger.error("File must be a Python file")
            sys.exit(1)
    
    elif path.is_dir():
        # Directory migration
        analyzer = PydanticMigrationAnalyzer()
        analysis_results = analyzer.analyze_directory(path)
        
        if args.analyze_only:
            create_migration_report(analysis_results, args.report)
            return
        
        # Migrate files that need it
        for result in analysis_results:
            if result.get('needs_migration', False) and 'error' not in result:
                file_path = Path(result['file_path'])
                stats.files_processed += 1
                migrate_file(file_path, stats, args.dry_run)
    
    # Print summary
    stats.print_summary()
    
    if args.dry_run:
        print("\nThis was a dry run. No files were modified.")
    elif stats.files_modified > 0:
        print(f"\nMigration completed. {stats.files_modified} files were modified.")
        if args.backup:
            print("Backup files were created with .backup extension.")

if __name__ == "__main__":
    main() 