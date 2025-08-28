"""
Documentation Generator for Instagram Captions API v10.0
Automatic documentation generation and code analysis.
"""
import ast
import inspect
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
import re

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes Python code using AST."""
    
    def __init__(self):
        self.imports: List[str] = []
        self.classes: List[Dict[str, Any]] = []
        self.functions: List[Dict[str, Any]] = []
        self.variables: List[Dict[str, Any]] = []
        self.comments: List[str] = []
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Reset state
            self.imports.clear()
            self.classes.clear()
            self.functions.clear()
            self.variables.clear()
            self.comments.clear()
            
            # Extract comments
            self._extract_comments(content)
            
            # Visit AST nodes
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self._analyze_import(node)
                elif isinstance(node, ast.ImportFrom):
                    self._analyze_import_from(node)
                elif isinstance(node, ast.ClassDef):
                    self._analyze_class(node)
                elif isinstance(node, ast.FunctionDef):
                    self._analyze_function(node)
                elif isinstance(node, ast.Assign):
                    self._analyze_assignment(node)
            
            return {
                'file_path': file_path,
                'imports': self.imports,
                'classes': self.classes,
                'functions': self.functions,
                'variables': self.variables,
                'comments': self.comments,
                'total_lines': len(content.splitlines()),
                'analyzed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing file {file_path}: {e}")
            return {'file_path': file_path, 'error': str(e)}
    
    def _extract_comments(self, content: str):
        """Extract comments from code."""
        lines = content.splitlines()
        for i, line in enumerate(lines):
            line = line.strip()
            if line.startswith('#'):
                self.comments.append({
                    'line': i + 1,
                    'comment': line[1:].strip()
                })
    
    def _analyze_import(self, node: ast.Import):
        """Analyze import statement."""
        for alias in node.names:
            self.imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
    
    def _analyze_import_from(self, node: ast.ImportFrom):
        """Analyze from import statement."""
        module = node.module or ''
        for alias in node.names:
            self.imports.append({
                'type': 'from_import',
                'module': module,
                'name': alias.name,
                'alias': alias.asname,
                'line': node.lineno
            })
    
    def _analyze_class(self, node: ast.ClassDef):
        """Analyze class definition."""
        class_info = {
            'name': node.name,
            'line': node.lineno,
            'bases': [self._get_name(base) for base in node.bases],
            'docstring': ast.get_docstring(node),
            'methods': [],
            'attributes': [],
            'decorators': [self._get_name(decorator) for decorator in node.decorator_list]
        }
        
        # Analyze class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                method_info = self._analyze_function(item)
                class_info['methods'].append(method_info)
            elif isinstance(item, ast.Assign):
                attr_info = self._analyze_assignment(item)
                class_info['attributes'].append(attr_info)
        
        self.classes.append(class_info)
    
    def _analyze_function(self, node: ast.FunctionDef) -> Dict[str, Any]:
        """Analyze function definition."""
        function_info = {
            'name': node.name,
            'line': node.lineno,
            'docstring': ast.get_docstring(node),
            'args': self._analyze_arguments(node.args),
            'returns': self._get_annotation(node.returns),
            'decorators': [self._get_name(decorator) for decorator in node.decorator_list],
            'body_lines': len(node.body) if node.body else 0
        }
        
        # Check if it's a method
        if hasattr(node, 'parent') and isinstance(node.parent, ast.ClassDef):
            function_info['is_method'] = True
            function_info['class_name'] = node.parent.name
        else:
            function_info['is_method'] = False
            self.functions.append(function_info)
        
        return function_info
    
    def _analyze_arguments(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Analyze function arguments."""
        arguments = []
        
        # Positional arguments
        for arg in args.posonlyargs + args.args:
            arguments.append({
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation),
                'default': None,
                'kind': 'positional'
            })
        
        # Keyword arguments
        for arg in args.kwonlyargs:
            arguments.append({
                'name': arg.arg,
                'annotation': self._get_annotation(arg.annotation),
                'default': None,
                'kind': 'keyword'
            })
        
        # Default values
        defaults = args.defaults + args.kw_defaults
        for i, default in enumerate(defaults):
            if i < len(arguments):
                arguments[i]['default'] = self._get_value(default)
        
        # Varargs and kwargs
        if args.vararg:
            arguments.append({
                'name': args.vararg.arg,
                'annotation': self._get_annotation(args.vararg.annotation),
                'default': None,
                'kind': 'varargs'
            })
        
        if args.kwarg:
            arguments.append({
                'name': args.kwarg.arg,
                'annotation': self._get_annotation(args.kwarg.annotation),
                'default': None,
                'kind': 'kwargs'
            })
        
        return arguments
    
    def _analyze_assignment(self, node: ast.Assign) -> Dict[str, Any]:
        """Analyze assignment statement."""
        targets = [self._get_name(target) for target in node.targets]
        value = self._get_value(node.value)
        
        assignment_info = {
            'targets': targets,
            'value': value,
            'line': node.lineno,
            'type': self._infer_type(value)
        }
        
        self.variables.append(assignment_info)
        return assignment_info
    
    def _get_name(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get name from AST node."""
        if node is None:
            return None
        elif isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        else:
            return str(node)
    
    def _get_annotation(self, node: Optional[ast.AST]) -> Optional[str]:
        """Get type annotation from AST node."""
        if node is None:
            return None
        return self._get_name(node)
    
    def _get_value(self, node: ast.AST) -> Any:
        """Get value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._get_value(item) for item in node.elts]
        elif isinstance(node, ast.Dict):
            return {
                self._get_value(k): self._get_value(v) 
                for k, v in zip(node.keys, node.values)
            }
        elif isinstance(node, ast.Tuple):
            return tuple(self._get_value(item) for item in node.elts)
        else:
            return self._get_name(node)
    
    def _infer_type(self, value: Any) -> str:
        """Infer type from value."""
        if value is None:
            return 'None'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif isinstance(value, (list, tuple)):
            return 'list' if isinstance(value, list) else 'tuple'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'unknown'

class DocumentationGenerator:
    """Generates comprehensive documentation."""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.code_analyzer = CodeAnalyzer()
        self.docs_dir = self.base_path / "docs"
        self.docs_dir.mkdir(exist_ok=True)
        
        # Documentation templates
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load documentation templates."""
        return {
            'readme': """# {project_name}

{description}

## Features

{features}

## Installation

{installation}

## Usage

{usage}

## API Reference

{api_reference}

## Contributing

{contributing}

## License

{license}
""",
            'api_docs': """# API Documentation

## Overview

{overview}

## Endpoints

{endpoints}

## Models

{models}

## Authentication

{auth_info}

## Examples

{examples}
""",
            'code_docs': """# Code Documentation

## Overview

This document provides detailed information about the codebase structure and implementation.

## Modules

{modules}

## Classes

{classes}

## Functions

{functions}

## Dependencies

{dependencies}
"""
        }
    
    def generate_project_documentation(self, project_info: Dict[str, Any]) -> bool:
        """Generate comprehensive project documentation."""
        try:
            # Create documentation directory structure
            self._create_docs_structure()
            
            # Generate README
            self._generate_readme(project_info)
            
            # Generate API documentation
            self._generate_api_docs(project_info)
            
            # Generate code documentation
            self._generate_code_docs()
            
            # Generate user guide
            self._generate_user_guide(project_info)
            
            # Generate developer guide
            self._generate_developer_guide(project_info)
            
            logger.info("Project documentation generated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error generating project documentation: {e}")
            return False
    
    def _create_docs_structure(self):
        """Create documentation directory structure."""
        directories = [
            'api',
            'code',
            'guides',
            'examples',
            'images',
            'assets'
        ]
        
        for directory in directories:
            (self.docs_dir / directory).mkdir(exist_ok=True)
    
    def _generate_readme(self, project_info: Dict[str, Any]):
        """Generate README.md file."""
        readme_content = self.templates['readme'].format(
            project_name=project_info.get('name', 'Project'),
            description=project_info.get('description', 'A Python project'),
            features=self._format_features(project_info.get('features', [])),
            installation=self._format_installation(project_info.get('installation', {})),
            usage=self._format_usage(project_info.get('usage', {})),
            api_reference=self._format_api_reference(project_info.get('api', {})),
            contributing=project_info.get('contributing', 'Contributions are welcome!'),
            license=project_info.get('license', 'MIT License')
        )
        
        readme_path = self.base_path / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        logger.info(f"Generated README.md at {readme_path}")
    
    def _generate_api_docs(self, project_info: Dict[str, Any]):
        """Generate API documentation."""
        api_content = self.templates['api_docs'].format(
            overview=project_info.get('api', {}).get('overview', 'API Overview'),
            endpoints=self._format_endpoints(project_info.get('api', {}).get('endpoints', [])),
            models=self._format_models(project_info.get('api', {}).get('models', [])),
            auth_info=self._format_auth_info(project_info.get('api', {}).get('auth', {})),
            examples=self._format_examples(project_info.get('api', {}).get('examples', []))
        )
        
        api_docs_path = self.docs_dir / "api" / "README.md"
        with open(api_docs_path, 'w', encoding='utf-8') as f:
            f.write(api_content)
        
        logger.info(f"Generated API documentation at {api_docs_path}")
    
    def _generate_code_docs(self):
        """Generate code documentation."""
        # Analyze Python files
        python_files = list(self.base_path.rglob("*.py"))
        code_analysis = {}
        
        for py_file in python_files:
            if 'venv' not in str(py_file) and 'env' not in str(py_file):
                analysis = self.code_analyzer.analyze_file(str(py_file))
                code_analysis[str(py_file)] = analysis
        
        # Generate code documentation
        code_content = self._format_code_documentation(code_analysis)
        
        code_docs_path = self.docs_dir / "code" / "README.md"
        with open(code_docs_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        # Generate detailed analysis
        self._generate_detailed_code_analysis(code_analysis)
        
        logger.info(f"Generated code documentation at {code_docs_path}")
    
    def _generate_user_guide(self, project_info: Dict[str, Any]):
        """Generate user guide."""
        user_guide = f"""# User Guide

## Getting Started

{project_info.get('getting_started', 'Follow the installation instructions to get started.')}

## Basic Usage

{project_info.get('basic_usage', 'Basic usage examples will be provided here.')}

## Advanced Features

{project_info.get('advanced_features', 'Advanced features will be documented here.')}

## Troubleshooting

{project_info.get('troubleshooting', 'Common issues and solutions will be listed here.')}

## FAQ

{project_info.get('faq', 'Frequently asked questions will be answered here.')}
"""
        
        user_guide_path = self.docs_dir / "guides" / "user_guide.md"
        with open(user_guide_path, 'w', encoding='utf-8') as f:
            f.write(user_guide)
        
        logger.info(f"Generated user guide at {user_guide_path}")
    
    def _generate_developer_guide(self, project_info: Dict[str, Any]):
        """Generate developer guide."""
        dev_guide = f"""# Developer Guide

## Development Setup

{project_info.get('dev_setup', 'Instructions for setting up the development environment.')}

## Architecture

{project_info.get('architecture', 'System architecture overview.')}

## Code Style

{project_info.get('code_style', 'Coding standards and conventions.')}

## Testing

{project_info.get('testing', 'Testing guidelines and procedures.')}

## Deployment

{project_info.get('deployment', 'Deployment instructions and procedures.')}

## Contributing

{project_info.get('contributing_dev', 'Guidelines for contributors.')}
"""
        
        dev_guide_path = self.docs_dir / "guides" / "developer_guide.md"
        with open(dev_guide_path, 'w', encoding='utf-8') as f:
            f.write(dev_guide)
        
        logger.info(f"Generated developer guide at {dev_guide_path}")
    
    def _format_features(self, features: List[str]) -> str:
        """Format features list."""
        if not features:
            return "- Feature 1\n- Feature 2\n- Feature 3"
        
        return '\n'.join(f"- {feature}" for feature in features)
    
    def _format_installation(self, installation: Dict[str, Any]) -> str:
        """Format installation instructions."""
        if not installation:
            return "```bash\npip install -r requirements.txt\n```"
        
        instructions = []
        if 'requirements' in installation:
            instructions.append(f"```bash\npip install -r {installation['requirements']}\n```")
        
        if 'commands' in installation:
            for command in installation['commands']:
                instructions.append(f"```bash\n{command}\n```")
        
        return '\n\n'.join(instructions)
    
    def _format_usage(self, usage: Dict[str, Any]) -> str:
        """Format usage examples."""
        if not usage:
            return "```python\n# Basic usage example\nfrom project import main\nmain()\n```"
        
        examples = []
        if 'examples' in usage:
            for example in usage['examples']:
                examples.append(f"```python\n{example}\n```")
        
        return '\n\n'.join(examples)
    
    def _format_api_reference(self, api: Dict[str, Any]) -> str:
        """Format API reference."""
        if not api:
            return "See the [API Documentation](docs/api/README.md) for detailed information."
        
        return f"See the [API Documentation](docs/api/README.md) for detailed information about {len(api.get('endpoints', []))} endpoints."
    
    def _format_endpoints(self, endpoints: List[Dict[str, Any]]) -> str:
        """Format API endpoints."""
        if not endpoints:
            return "No endpoints documented."
        
        endpoint_docs = []
        for endpoint in endpoints:
            doc = f"""### {endpoint.get('name', 'Unknown')}

**Method:** {endpoint.get('method', 'GET')}  
**Path:** {endpoint.get('path', '/')}  
**Description:** {endpoint.get('description', 'No description')}

**Parameters:**
{self._format_parameters(endpoint.get('parameters', []))}

**Response:**
{self._format_response(endpoint.get('response', {}))}
"""
            endpoint_docs.append(doc)
        
        return '\n\n'.join(endpoint_docs)
    
    def _format_parameters(self, parameters: List[Dict[str, Any]]) -> str:
        """Format endpoint parameters."""
        if not parameters:
            return "No parameters"
        
        param_docs = []
        for param in parameters:
            doc = f"- **{param.get('name', 'Unknown')}** ({param.get('type', 'string')}): {param.get('description', 'No description')}"
            param_docs.append(doc)
        
        return '\n'.join(param_docs)
    
    def _format_response(self, response: Dict[str, Any]) -> str:
        """Format endpoint response."""
        if not response:
            return "No response details"
        
        return f"**Status:** {response.get('status', '200')}  
**Type:** {response.get('type', 'application/json')}  
**Schema:** {response.get('schema', 'No schema')}"
    
    def _format_models(self, models: List[Dict[str, Any]]) -> str:
        """Format API models."""
        if not models:
            return "No models documented."
        
        model_docs = []
        for model in models:
            doc = f"""### {model.get('name', 'Unknown')}

**Description:** {model.get('description', 'No description')}

**Properties:**
{self._format_model_properties(model.get('properties', []))}
"""
            model_docs.append(doc)
        
        return '\n\n'.join(model_docs)
    
    def _format_model_properties(self, properties: List[Dict[str, Any]]) -> str:
        """Format model properties."""
        if not properties:
            return "No properties"
        
        prop_docs = []
        for prop in properties:
            doc = f"- **{prop.get('name', 'Unknown')}** ({prop.get('type', 'string')}): {prop.get('description', 'No description')}"
            prop_docs.append(doc)
        
        return '\n'.join(prop_docs)
    
    def _format_auth_info(self, auth: Dict[str, Any]) -> str:
        """Format authentication information."""
        if not auth:
            return "No authentication required."
        
        return f"""**Type:** {auth.get('type', 'Unknown')}  
**Description:** {auth.get('description', 'No description')}  
**Required:** {'Yes' if auth.get('required', False) else 'No'}"""
    
    def _format_examples(self, examples: List[Dict[str, Any]]) -> str:
        """Format API examples."""
        if not examples:
            return "No examples provided."
        
        example_docs = []
        for example in examples:
            doc = f"""### {example.get('title', 'Example')}

**Description:** {example.get('description', 'No description')}

**Request:**
```bash
{example.get('request', 'No request example')}
```

**Response:**
```json
{example.get('response', 'No response example')}
```
"""
            example_docs.append(doc)
        
        return '\n\n'.join(example_docs)
    
    def _format_code_documentation(self, code_analysis: Dict[str, Any]) -> str:
        """Format code documentation."""
        # Count totals
        total_files = len(code_analysis)
        total_classes = sum(len(analysis.get('classes', [])) for analysis in code_analysis.values())
        total_functions = sum(len(analysis.get('functions', [])) for analysis in code_analysis.values())
        total_imports = sum(len(analysis.get('imports', [])) for analysis in code_analysis.values())
        
        # Generate summary
        summary = f"""# Code Documentation

## Overview

This project contains {total_files} Python files with:
- {total_classes} classes
- {total_functions} functions
- {total_imports} imports

## File Analysis

"""
        
        # Add file summaries
        for file_path, analysis in code_analysis.items():
            if 'error' not in analysis:
                summary += f"""### {Path(file_path).name}

**Path:** {file_path}  
**Lines:** {analysis.get('total_lines', 0)}  
**Classes:** {len(analysis.get('classes', []))}  
**Functions:** {len(analysis.get('functions', []))}  
**Imports:** {len(analysis.get('imports', []))}

"""
        
        return summary
    
    def _generate_detailed_code_analysis(self, code_analysis: Dict[str, Any]):
        """Generate detailed code analysis files."""
        for file_path, analysis in code_analysis.items():
            if 'error' in analysis:
                continue
            
            # Create detailed analysis file
            file_name = Path(file_path).stem
            analysis_path = self.docs_dir / "code" / f"{file_name}_analysis.md"
            
            analysis_content = f"""# {file_name} Analysis

## File Information

**Path:** {file_path}  
**Total Lines:** {analysis.get('total_lines', 0)}  
**Analyzed:** {analysis.get('analyzed_at', 'Unknown')}

## Imports

{self._format_imports(analysis.get('imports', []))}

## Classes

{self._format_classes(analysis.get('classes', []))}

## Functions

{self._format_functions(analysis.get('functions', []))}

## Variables

{self._format_variables(analysis.get('variables', []))}

## Comments

{self._format_comments(analysis.get('comments', []))}
"""
            
            with open(analysis_path, 'w', encoding='utf-8') as f:
                f.write(analysis_content)
    
    def _format_imports(self, imports: List[Dict[str, Any]]) -> str:
        """Format imports for documentation."""
        if not imports:
            return "No imports"
        
        import_docs = []
        for imp in imports:
            if imp['type'] == 'import':
                doc = f"- `import {imp['module']}`"
                if imp['alias']:
                    doc += f" as `{imp['alias']}`"
            else:
                doc = f"- `from {imp['module']} import {imp['name']}`"
                if imp['alias']:
                    doc += f" as `{imp['alias']}`"
            
            doc += f" (line {imp['line']})"
            import_docs.append(doc)
        
        return '\n'.join(import_docs)
    
    def _format_classes(self, classes: List[Dict[str, Any]]) -> str:
        """Format classes for documentation."""
        if not classes:
            return "No classes"
        
        class_docs = []
        for cls in classes:
            doc = f"""### {cls['name']}

**Line:** {cls['line']}  
**Bases:** {', '.join(cls['bases']) if cls['bases'] else 'None'}  
**Docstring:** {cls['docstring'] or 'No docstring'}

**Decorators:** {', '.join(cls['decorators']) if cls['decorators'] else 'None'}

**Methods:** {len(cls['methods'])}  
**Attributes:** {len(cls['attributes'])}

"""
            
            if cls['methods']:
                doc += "**Methods:**\n"
                for method in cls['methods']:
                    doc += f"- {method['name']} (line {method['line']})\n"
                doc += "\n"
            
            class_docs.append(doc)
        
        return '\n'.join(class_docs)
    
    def _format_functions(self, functions: List[Dict[str, Any]]) -> str:
        """Format functions for documentation."""
        if not functions:
            return "No functions"
        
        func_docs = []
        for func in functions:
            doc = f"""### {func['name']}

**Line:** {func['line']}  
**Docstring:** {func['docstring'] or 'No docstring'}  
**Returns:** {func['returns'] or 'None'}  
**Body Lines:** {func['body_lines']}

**Arguments:**
{self._format_function_arguments(func['args'])}

**Decorators:** {', '.join(func['decorators']) if func['decorators'] else 'None'}

"""
            func_docs.append(doc)
        
        return '\n'.join(func_docs)
    
    def _format_function_arguments(self, args: List[Dict[str, Any]]) -> str:
        """Format function arguments for documentation."""
        if not args:
            return "No arguments"
        
        arg_docs = []
        for arg in args:
            doc = f"- **{arg['name']}** ({arg['kind']})"
            if arg['annotation']:
                doc += f": {arg['annotation']}"
            if arg['default'] is not None:
                doc += f" = {arg['default']}"
            arg_docs.append(doc)
        
        return '\n'.join(arg_docs)
    
    def _format_variables(self, variables: List[Dict[str, Any]]) -> str:
        """Format variables for documentation."""
        if not variables:
            return "No variables"
        
        var_docs = []
        for var in variables:
            doc = f"- **{', '.join(var['targets'])}** = {var['value']} ({var['type']}) (line {var['line']})"
            var_docs.append(doc)
        
        return '\n'.join(var_docs)
    
    def _format_comments(self, comments: List[Dict[str, Any]]) -> str:
        """Format comments for documentation."""
        if not comments:
            return "No comments"
        
        comment_docs = []
        for comment in comments:
            doc = f"- Line {comment['line']}: {comment['comment']}"
            comment_docs.append(doc)
        
        return '\n'.join(comment_docs)
    
    def export_documentation(self, output_path: str, format: str = "markdown") -> bool:
        """Export documentation to a specific format."""
        try:
            output_dir = Path(output_path)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy documentation files
            import shutil
            shutil.copytree(self.docs_dir, output_dir / "docs", dirs_exist_ok=True)
            
            # Copy README
            readme_src = self.base_path / "README.md"
            if readme_src.exists():
                shutil.copy2(readme_src, output_dir / "README.md")
            
            logger.info(f"Documentation exported to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting documentation: {e}")
            return False






