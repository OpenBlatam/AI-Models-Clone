from typing_extensions import Literal, TypedDict
from typing import Any, List, Dict, Optional, Union, Tuple
import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
import argparse
import logging
from typing import AsyncGenerator
from fastapi import FastAPI
import logging
from typing import Any, List, Dict, Optional
import asyncio
#!/usr/bin/env python3
"""
Lifespan Migration Script
Automatically migrates FastAPI applications from @app.on_event() decorators
to modern lifespan context managers.
"""


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LifespanMigrator:
    """Migrates FastAPI apps from app.on_event() to lifespan context managers."""
    
    def __init__(self, target_dir: str):
        
    """__init__ function."""
self.target_dir = Path(target_dir)
        self.migration_stats = {
            'files_processed': 0,
            'files_migrated': 0,
            'startup_events_found': 0,
            'shutdown_events_found': 0,
            'errors': []
        }
    
    def find_python_files(self) -> List[Path]:
        """Find all Python files in the target directory."""
        python_files = []
        for root, dirs, files in os.walk(self.target_dir):
            # Skip common directories to avoid
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'venv', 'env', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def parse_file(self, file_path: Path) -> Optional[ast.AST]:
        """Parse a Python file and return the AST."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
                content = f.read()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            return ast.parse(content)
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            self.migration_stats['errors'].append(f"Parse error in {file_path}: {e}")
            return None
    
    def find_on_event_decorators(self, tree: ast.AST) -> List[Dict]:
        """Find all @app.on_event() decorators in the AST."""
        events = []
        
        class OnEventVisitor(ast.NodeVisitor):
            def __init__(self) -> Any:
                self.events = []
            
            def visit_FunctionDef(self, node) -> Any:
                # Check if function has decorators
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            if (isinstance(decorator.func.value, ast.Name) and 
                                decorator.func.value.id in ['app', 'self', 'cls'] and
                                decorator.func.attr == 'on_event'):
                                
                                # Extract event type
                                if decorator.args and isinstance(decorator.args[0], ast.Constant):
                                    event_type = decorator.args[0].value
                                    self.events.append({
                                        'function_name': node.name,
                                        'event_type': event_type,
                                        'function_node': node,
                                        'decorator_node': decorator
                                    })
        
        visitor = OnEventVisitor()
        visitor.visit(tree)
        return visitor.events
    
    def extract_function_code(self, node: ast.FunctionDef, source_lines: List[str]) -> str:
        """Extract the function code as a string."""
        start_line = node.lineno - 1  # AST lines are 1-indexed
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 1
        
        # Get the function code
        function_lines = source_lines[start_line:end_line]
        return '\n'.join(function_lines)
    
    def generate_lifespan_context_manager(self, startup_events: List[Dict], shutdown_events: List[Dict], source_lines: List[str]) -> str:
        """Generate a lifespan context manager from the events."""
        
        lifespan_code = []
        lifespan_code.append("@asynccontextmanager")
        lifespan_code.append("async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:")
        lifespan_code.append("    \"\"\"Application lifespan context manager.\"\"\"")
        
        # Startup section
        if startup_events:
            lifespan_code.append("    # Startup phase")
            lifespan_code.append("    logger.info(\"Application starting up\")")
            lifespan_code.append("    try:")
            
            for event in startup_events:
                function_code = self.extract_function_code(event['function_node'], source_lines)
                # Extract the function body (remove decorator and function definition)
                lines = function_code.split('\n')
                body_lines = []
                in_body = False
                indent_level = None
                
                for line in lines:
                    if line.strip().startswith('async def ') or line.strip().startswith('def '):
                        in_body = True
                        # Find the indentation level
                        indent_level = len(line) - len(line.lstrip())
                        continue
                    
                    if in_body:
                        if line.strip() == '':
                            body_lines.append(line)
                        else:
                            # Adjust indentation to match lifespan context
                            current_indent = len(line) - len(line.lstrip())
                            if current_indent > indent_level:
                                # This is part of the function body
                                adjusted_line = ' ' * 8 + line[indent_level + 4:]  # 8 spaces for lifespan body
                                body_lines.append(adjusted_line)
                            else:
                                # End of function body
                                break
                
                # Add the function body to lifespan
                for line in body_lines:
                    lifespan_code.append(line)
            
            lifespan_code.append("        yield")
            lifespan_code.append("    finally:")
            
        else:
            lifespan_code.append("    try:")
            lifespan_code.append("        yield")
            lifespan_code.append("    finally:")
        
        # Shutdown section
        if shutdown_events:
            lifespan_code.append("        # Shutdown phase")
            lifespan_code.append("        logger.info(\"Application shutting down\")")
            
            for event in shutdown_events:
                function_code = self.extract_function_code(event['function_node'], source_lines)
                # Extract the function body (remove decorator and function definition)
                lines = function_code.split('\n')
                body_lines = []
                in_body = False
                indent_level = None
                
                for line in lines:
                    if line.strip().startswith('async def ') or line.strip().startswith('def '):
                        in_body = True
                        # Find the indentation level
                        indent_level = len(line) - len(line.lstrip())
                        continue
                    
                    if in_body:
                        if line.strip() == '':
                            body_lines.append(line)
                        else:
                            # Adjust indentation to match lifespan context
                            current_indent = len(line) - len(line.lstrip())
                            if current_indent > indent_level:
                                # This is part of the function body
                                adjusted_line = ' ' * 12 + line[indent_level + 4:]  # 12 spaces for finally block
                                body_lines.append(adjusted_line)
                            else:
                                # End of function body
                                break
                
                # Add the function body to lifespan
                for line in body_lines:
                    lifespan_code.append(line)
        
        return '\n'.join(lifespan_code)
    
    def generate_imports(self) -> str:
        """Generate necessary imports for lifespan."""
        return """from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)"""
    
    def migrate_file(self, file_path: Path) -> bool:
        """Migrate a single file from app.on_event() to lifespan."""
        logger.info(f"Processing {file_path}")
        
        # Parse the file
        tree = self.parse_file(file_path)
        if not tree:
            return False
        
        # Read source lines for code extraction
        with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            source_lines = f.readlines()
        
        # Find on_event decorators
        events = self.find_on_event_decorators(tree)
        if not events:
            logger.info(f"No on_event decorators found in {file_path}")
            return False
        
        # Separate startup and shutdown events
        startup_events = [e for e in events if e['event_type'] == 'startup']
        shutdown_events = [e for e in events if e['event_type'] == 'shutdown']
        
        self.migration_stats['startup_events_found'] += len(startup_events)
        self.migration_stats['shutdown_events_found'] += len(shutdown_events)
        
        logger.info(f"Found {len(startup_events)} startup and {len(shutdown_events)} shutdown events")
        
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            content = f.read()
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        
        # Generate new content
        new_content = self.migrate_content(content, startup_events, shutdown_events, source_lines)
        
        # Write backup
        backup_path = file_path.with_suffix('.py.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            f.write(content)
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        
        # Write migrated content
        with open(file_path, 'w', encoding='utf-8') as f:
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
            f.write(new_content)
    try:
        pass
    except Exception as e:
        print(f"Error: {e}")
        
        logger.info(f"Migrated {file_path} (backup saved to {backup_path})")
        return True
    
    def migrate_content(self, content: str, startup_events: List[Dict], shutdown_events: List[Dict], source_lines: List[str]) -> str:
        """Migrate the file content."""
        
        # Add imports if needed
        if startup_events or shutdown_events:
            if 'from contextlib import asynccontextmanager' not in content:
                # Find the best place to add imports
                lines = content.split('\n')
                import_section_end = 0
                
                for i, line in enumerate(lines):
                    if line.strip().startswith('import ') or line.strip().startswith('from '):
                        import_section_end = i + 1
                    elif line.strip() and not line.startswith('#'):
                        break
                
                # Insert imports
                imports = self.generate_imports()
                lines.insert(import_section_end, '')
                lines.insert(import_section_end, imports)
                content = '\n'.join(lines)
        
        # Generate lifespan context manager
        lifespan_code = self.generate_lifespan_context_manager(startup_events, shutdown_events, source_lines)
        
        # Remove the original event functions
        lines = content.split('\n')
        new_lines = []
        skip_lines = set()
        
        for event in startup_events + shutdown_events:
            start_line = event['function_node'].lineno - 1
            end_line = event['function_node'].end_lineno if hasattr(event['function_node'], 'end_lineno') else start_line + 1
            
            # Mark lines to skip
            for i in range(start_line, end_line):
                skip_lines.add(i)
        
        # Build new content without the event functions
        for i, line in enumerate(lines):
            if i not in skip_lines:
                new_lines.append(line)
        
        # Find where to insert the lifespan code
        # Look for FastAPI app creation
        app_creation_line = -1
        for i, line in enumerate(new_lines):
            if 'FastAPI(' in line and 'app' in line:
                app_creation_line = i
                break
        
        if app_creation_line >= 0:
            # Insert lifespan code before app creation
            lifespan_lines = lifespan_code.split('\n')
            new_lines.insert(app_creation_line, '')
            for line in reversed(lifespan_lines):
                new_lines.insert(app_creation_line, line)
            
            # Modify the FastAPI app creation to include lifespan
            for i in range(app_creation_line + len(lifespan_lines) + 1, len(new_lines)):
                if 'FastAPI(' in new_lines[i] and 'app' in new_lines[i]:
                    # Add lifespan parameter
                    if 'lifespan=' not in new_lines[i]:
                        new_lines[i] = new_lines[i].replace('FastAPI(', 'FastAPI(lifespan=lifespan, ')
                    break
        
        return '\n'.join(new_lines)
    
    def migrate(self) -> Dict:
        """Migrate all files in the target directory."""
        logger.info(f"Starting migration in {self.target_dir}")
        
        python_files = self.find_python_files()
        logger.info(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            self.migration_stats['files_processed'] += 1
            try:
                if self.migrate_file(file_path):
                    self.migration_stats['files_migrated'] += 1
            except Exception as e:
                logger.error(f"Error migrating {file_path}: {e}")
                self.migration_stats['errors'].append(f"Migration error in {file_path}: {e}")
        
        logger.info("Migration completed")
        logger.info(f"Files processed: {self.migration_stats['files_processed']}")
        logger.info(f"Files migrated: {self.migration_stats['files_migrated']}")
        logger.info(f"Startup events found: {self.migration_stats['startup_events_found']}")
        logger.info(f"Shutdown events found: {self.migration_stats['shutdown_events_found']}")
        
        if self.migration_stats['errors']:
            logger.warning(f"Errors encountered: {len(self.migration_stats['errors'])}")
            for error in self.migration_stats['errors']:
                logger.error(error)
        
        return self.migration_stats

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Migrate FastAPI apps from app.on_event() to lifespan')
    parser.add_argument('target_dir', help='Target directory to migrate')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    parser.add_argument('--backup', action='store_true', default=True, help='Create backup files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.target_dir):
        logger.error(f"Target directory does not exist: {args.target_dir}")
        sys.exit(1)
    
    migrator = LifespanMigrator(args.target_dir)
    
    if args.dry_run:
        logger.info("DRY RUN MODE - No changes will be made")
        # For dry run, just find and report what would be migrated
        python_files = migrator.find_python_files()
        total_events = 0
        
        for file_path in python_files:
            tree = migrator.parse_file(file_path)
            if tree:
                events = migrator.find_on_event_decorators(tree)
                if events:
                    logger.info(f"Would migrate {file_path}: {len(events)} events")
                    total_events += len(events)
        
        logger.info(f"Total events found: {total_events}")
    else:
        stats = migrator.migrate()
        
        if stats['errors']:
            sys.exit(1)

match __name__:
    case '__main__':
    main() 