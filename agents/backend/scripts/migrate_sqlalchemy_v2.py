#!/usr/bin/env python3
"""
SQLAlchemy v2 Migration Script
==============================

Automated migration tool to convert SQLAlchemy v1 patterns to v2.
Supports:
- Import statement updates
- Model definition modernization
- Query pattern migration
- Session management updates
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import logging
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class MigrationResult:
    """Result of migration operation"""
    file_path: Path
    success: bool
    changes_made: List[str]
    errors: List[str]
    backup_path: Optional[Path] = None


class SQLAlchemyV2Migrator:
    """SQLAlchemy v1 to v2 migration tool"""
    
    def __init__(self, project_root: str, dry_run: bool = False, backup: bool = True):
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.backup = backup
        self.changes = []
        self.errors = []
        
        # Migration patterns
        self.import_patterns = {
            # Old imports to new imports
            r'from sqlalchemy\.ext\.declarative import declarative_base': 
                'from sqlalchemy.orm import declarative_base',
            r'from sqlalchemy import create_engine': 
                'from sqlalchemy.ext.asyncio import create_async_engine',
            r'from sqlalchemy\.orm import sessionmaker': 
                'from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession',
        }
        
        # Model patterns
        self.model_patterns = {
            # Column definitions
            r'(\w+)\s*=\s*Column\(([^)]+)\)': 
                r'\1: Mapped[\2] = mapped_column(\2)',
        }
        
        # Query patterns
        self.query_patterns = {
            # session.query() to select()
            r'session\.query\(([^)]+)\)\.filter\(([^)]+)\)\.all\(\)': 
                r'await session.execute(select(\1).where(\2)).scalars().all()',
            r'session\.query\(([^)]+)\)\.all\(\)': 
                r'await session.execute(select(\1)).scalars().all()',
        }
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the project"""
        python_files = []
        
        for pattern in ['**/*.py', '**/*.pyx']:
            python_files.extend(self.project_root.glob(pattern))
        
        # Filter out common directories to skip
        skip_dirs = {'__pycache__', '.git', 'venv', 'env', 'node_modules', '.pytest_cache'}
        filtered_files = []
        
        for file_path in python_files:
            if not any(skip_dir in file_path.parts for skip_dir in skip_dirs):
                filtered_files.append(file_path)
        
        return filtered_files
    
    def needs_migration(self, file_path: Path) -> bool:
        """Check if file needs SQLAlchemy migration"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for SQLAlchemy usage
            sqlalchemy_indicators = [
                'from sqlalchemy',
                'import sqlalchemy',
                'declarative_base',
                'sessionmaker',
                'Column(',
                'relationship(',
                'session.query(',
            ]
            
            return any(indicator in content for indicator in sqlalchemy_indicators)
            
        except Exception as e:
            logger.warning(f"Error reading {file_path}: {e}")
            return False
    
    def migrate_file(self, file_path: Path) -> MigrationResult:
        """Migrate a single Python file to SQLAlchemy v2"""
        result = MigrationResult(
            file_path=file_path,
            success=False,
            changes_made=[],
            errors=[]
        )
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # Apply migrations
            content, changes = self._update_imports(content)
            result.changes_made.extend(changes)
            
            content, changes = self._update_models(content)
            result.changes_made.extend(changes)
            
            content, changes = self._update_queries(content)
            result.changes_made.extend(changes)
            
            content, changes = self._update_session_management(content)
            result.changes_made.extend(changes)
            
            # Check if any changes were made
            if content != original_content:
                if self.backup and not self.dry_run:
                    backup_path = file_path.with_suffix(f'{file_path.suffix}.backup')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(original_content)
                    result.backup_path = backup_path
                
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                result.success = True
                logger.info(f"Migrated {file_path} ({len(result.changes_made)} changes)")
            else:
                logger.debug(f"No changes needed for {file_path}")
                result.success = True
            
        except Exception as e:
            error_msg = f"Error migrating {file_path}: {e}"
            logger.error(error_msg)
            result.errors.append(error_msg)
        
        return result
    
    def _update_imports(self, content: str) -> tuple[str, List[str]]:
        """Update import statements"""
        changes = []
        
        # Apply import pattern replacements
        for old_pattern, new_pattern in self.import_patterns.items():
            if re.search(old_pattern, content):
                content = re.sub(old_pattern, new_pattern, content)
                changes.append(f"Updated import: {old_pattern} -> {new_pattern}")
        
        # Add Mapped and mapped_column imports if needed
        if 'Mapped[' in content and 'from sqlalchemy.orm import' in content:
            if 'Mapped' not in content.split('from sqlalchemy.orm import')[1].split('\n')[0]:
                content = re.sub(
                    r'from sqlalchemy\.orm import (.*)',
                    r'from sqlalchemy.orm import \1, Mapped, mapped_column',
                    content
                )
                changes.append("Added Mapped and mapped_column imports")
        
        return content, changes
    
    def _update_models(self, content: str) -> tuple[str, List[str]]:
        """Update model definitions"""
        changes = []
        
        # Update Column definitions to use Mapped and mapped_column
        if 'Column(' in content:
            # This is a complex transformation that needs AST parsing
            try:
                tree = ast.parse(content)
                updated_content = self._transform_model_ast(tree, content)
                if updated_content != content:
                    content = updated_content
                    changes.append("Updated model column definitions to v2 syntax")
            except SyntaxError:
                logger.warning("Could not parse AST for model updates")
        
        return content, changes
    
    def _transform_model_ast(self, tree: ast.AST, original_content: str) -> str:
        """Transform AST to update model definitions"""
        # This is a simplified version - in practice, you'd need more sophisticated AST manipulation
        # For now, we'll use regex patterns for common cases
        
        # Update Column definitions
        content = original_content
        
        # Pattern: id = Column(Integer, primary_key=True)
        # To: id: Mapped[int] = mapped_column(Integer, primary_key=True)
        column_pattern = r'(\w+)\s*=\s*Column\(([^)]+)\)'
        
        def replace_column(match):
            field_name = match.group(1)
            column_args = match.group(2)
            
            # Try to infer the type from column arguments
            type_mapping = {
                'Integer': 'int',
                'String': 'str',
                'Text': 'str',
                'Boolean': 'bool',
                'Float': 'float',
                'DateTime': 'datetime',
                'Date': 'date',
                'JSON': 'Dict[str, Any]',
            }
            
            # Extract the type
            type_match = re.search(r'(\w+)(?:\([^)]*\))?', column_args)
            if type_match:
                sql_type = type_match.group(1)
                python_type = type_mapping.get(sql_type, 'Any')
            else:
                python_type = 'Any'
            
            return f'{field_name}: Mapped[{python_type}] = mapped_column({column_args})'
        
        content = re.sub(column_pattern, replace_column, content)
        
        return content
    
    def _update_queries(self, content: str) -> tuple[str, List[str]]:
        """Update query patterns"""
        changes = []
        
        # Update session.query() to select()
        if 'session.query(' in content:
            # Add select import if not present
            if 'from sqlalchemy import select' not in content and 'from sqlalchemy import' in content:
                content = re.sub(
                    r'from sqlalchemy import (.*)',
                    r'from sqlalchemy import \1, select',
                    content
                )
                changes.append("Added select import")
            
            # Replace query patterns
            old_patterns = [
                (r'session\.query\(([^)]+)\)\.filter\(([^)]+)\)\.all\(\)', 
                 r'await session.execute(select(\1).where(\2)).scalars().all()'),
                (r'session\.query\(([^)]+)\)\.all\(\)', 
                 r'await session.execute(select(\1)).scalars().all()'),
                (r'session\.query\(([^)]+)\)\.first\(\)', 
                 r'await session.execute(select(\1)).scalar_one_or_none()'),
            ]
            
            for old_pattern, new_pattern in old_patterns:
                if re.search(old_pattern, content):
                    content = re.sub(old_pattern, new_pattern, content)
                    changes.append(f"Updated query pattern: {old_pattern} -> {new_pattern}")
        
        return content, changes
    
    def _update_session_management(self, content: str) -> tuple[str, List[str]]:
        """Update session management patterns"""
        changes = []
        
        # Update sessionmaker to async_sessionmaker
        if 'sessionmaker(' in content:
            content = re.sub(
                r'sessionmaker\(',
                'async_sessionmaker(',
                content
            )
            changes.append("Updated sessionmaker to async_sessionmaker")
        
        # Update session usage to async
        if 'SessionLocal()' in content:
            content = re.sub(
                r'SessionLocal\(\)',
                'session_factory()',
                content
            )
            changes.append("Updated SessionLocal() to session_factory()")
        
        # Add async/await to session operations
        session_operations = [
            (r'session\.commit\(\)', r'await session.commit()'),
            (r'session\.rollback\(\)', r'await session.rollback()'),
            (r'session\.close\(\)', r'await session.close()'),
        ]
        
        for old_op, new_op in session_operations:
            if re.search(old_op, content):
                content = re.sub(old_op, new_op, content)
                changes.append(f"Added async to session operation: {old_op} -> {new_op}")
        
        return content, changes
    
    def migrate_project(self) -> Dict[str, Any]:
        """Migrate entire project"""
        logger.info(f"Starting SQLAlchemy v2 migration for {self.project_root}")
        
        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files")
        
        files_to_migrate = [f for f in python_files if self.needs_migration(f)]
        logger.info(f"Found {len(files_to_migrate)} files that need migration")
        
        results = []
        successful_migrations = 0
        total_changes = 0
        
        for file_path in files_to_migrate:
            result = self.migrate_file(file_path)
            results.append(result)
            
            if result.success:
                successful_migrations += 1
                total_changes += len(result.changes_made)
        
        # Generate summary
        summary = {
            'total_files': len(python_files),
            'files_needing_migration': len(files_to_migrate),
            'successful_migrations': successful_migrations,
            'failed_migrations': len(results) - successful_migrations,
            'total_changes': total_changes,
            'results': results,
            'dry_run': self.dry_run
        }
        
        self._print_summary(summary)
        return summary
    
    def _print_summary(self, summary: Dict[str, Any]):
        """Print migration summary"""
        logger.info("=" * 60)
        logger.info("SQLAlchemy v2 Migration Summary")
        logger.info("=" * 60)
        logger.info(f"Total Python files: {summary['total_files']}")
        logger.info(f"Files needing migration: {summary['files_needing_migration']}")
        logger.info(f"Successful migrations: {summary['successful_migrations']}")
        logger.info(f"Failed migrations: {summary['failed_migrations']}")
        logger.info(f"Total changes made: {summary['total_changes']}")
        logger.info(f"Dry run: {summary['dry_run']}")
        
        if summary['failed_migrations'] > 0:
            logger.warning("Some migrations failed. Check the logs above for details.")
        
        if summary['dry_run']:
            logger.info("This was a dry run. No files were actually modified.")
        else:
            logger.info("Migration completed. Check backup files if needed.")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Migrate SQLAlchemy v1 to v2')
    parser.add_argument('project_root', help='Path to project root directory')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be changed without making changes')
    parser.add_argument('--no-backup', action='store_true', help='Skip creating backup files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate project root
    project_root = Path(args.project_root)
    if not project_root.exists():
        logger.error(f"Project root does not exist: {project_root}")
        sys.exit(1)
    
    # Create migrator and run migration
    migrator = SQLAlchemyV2Migrator(
        project_root=str(project_root),
        dry_run=args.dry_run,
        backup=not args.no_backup
    )
    
    try:
        summary = migrator.migrate_project()
        
        if summary['failed_migrations'] > 0:
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main() 