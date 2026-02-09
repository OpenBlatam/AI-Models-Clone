#!/usr/bin/env python3
"""
Command Line Interface for the API Documentation System.
Provides easy access to documentation generation and management.
"""
import sys
import os
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from documentation.api_documentation import APIDocumentation
from documentation.generate_docs import create_instagram_captions_api_docs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False, quiet: bool = False):
    """Setup logging based on verbosity flags."""
    if quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    else:
        logging.getLogger().setLevel(logging.INFO)

def generate_instagram_docs(output_dir: str, formats: List[str]) -> bool:
    """Generate Instagram Captions API documentation."""
    try:
        logger.info("Creating Instagram Captions API documentation...")
        
        # Create API documentation
        api_docs = create_instagram_captions_api_docs()
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export requested formats
        success = True
        
        if "all" in formats or "openapi" in formats:
            logger.info("Generating OpenAPI specification...")
            success &= api_docs.save_openapi_spec(str(output_path / "openapi.json"), "json")
            success &= api_docs.save_openapi_spec(str(output_path / "openapi.yaml"), "yaml")
        
        if "all" in formats or "markdown" in formats:
            logger.info("Generating Markdown documentation...")
            success &= api_docs.save_markdown_docs(str(output_path / "api_documentation.md"))
        
        if "all" in formats or "html" in formats:
            logger.info("Generating HTML documentation...")
            success &= api_docs.save_html_docs(str(output_path / "api_documentation.html"))
        
        if success:
            # Get statistics
            stats = api_docs.get_statistics()
            logger.info("Documentation generation completed successfully!")
            logger.info(f"Generated {stats['total_endpoints']} endpoints")
            logger.info(f"Generated {stats['total_models']} data models")
            logger.info(f"Generated {stats['total_tags']} API tags")
            logger.info(f"Documentation saved to: {output_path.absolute()}")
            
            # List generated files
            generated_files = list(output_path.glob("*"))
            logger.info("Generated files:")
            for file_path in generated_files:
                logger.info(f"  - {file_path.name}")
            
            return True
        else:
            logger.error("Some documentation formats failed to generate!")
            return False
            
    except Exception as e:
        logger.error(f"Error generating Instagram API documentation: {e}")
        return False

def generate_custom_docs(title: str, version: str, output_dir: str, formats: List[str]) -> bool:
    """Generate custom API documentation."""
    try:
        logger.info(f"Creating custom API documentation: {title} v{version}")
        
        # Create API documentation
        api_docs = APIDocumentation(title=title, version=version)
        
        # Set basic info
        api_docs.set_info(
            description=f"API documentation for {title}",
            contact={"name": "API Team", "email": "api@example.com"}
        )
        
        # Add sample server
        api_docs.add_server("https://api.example.com", "Production Server")
        
        # Add sample tag
        api_docs.add_tag("api", "API endpoints")
        
        # Add sample model
        sample_model = {
            "name": "SampleModel",
            "type": "object",
            "description": "A sample data model",
            "properties": {
                "id": {"type": "string", "description": "Unique identifier"},
                "name": {"type": "string", "description": "Model name"}
            },
            "required": ["id", "name"]
        }
        
        from documentation.api_documentation import APIModel
        model = APIModel(**sample_model)
        api_docs.add_model(model)
        
        # Add sample endpoint
        sample_endpoint = {
            "path": "/sample",
            "method": "GET",
            "summary": "Sample endpoint",
            "description": "A sample API endpoint",
            "tags": ["api"],
            "responses": {
                "200": {
                    "description": "Success",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/SampleModel"}
                        }
                    }
                }
            }
        }
        
        from documentation.api_documentation import APIEndpoint
        endpoint = APIEndpoint(**sample_endpoint)
        api_docs.add_endpoint(endpoint)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Export requested formats
        success = True
        
        if "all" in formats or "openapi" in formats:
            logger.info("Generating OpenAPI specification...")
            success &= api_docs.save_openapi_spec(str(output_path / "openapi.json"), "json")
            success &= api_docs.save_openapi_spec(str(output_path / "openapi.yaml"), "yaml")
        
        if "all" in formats or "markdown" in formats:
            logger.info("Generating Markdown documentation...")
            success &= api_docs.save_markdown_docs(str(output_path / "api_documentation.md"))
        
        if "all" in formats or "html" in formats:
            logger.info("Generating HTML documentation...")
            success &= api_docs.save_html_docs(str(output_path / "api_documentation.html"))
        
        if success:
            logger.info("Custom documentation generation completed successfully!")
            logger.info(f"Documentation saved to: {output_path.absolute()}")
            return True
        else:
            logger.error("Some documentation formats failed to generate!")
            return False
            
    except Exception as e:
        logger.error(f"Error generating custom API documentation: {e}")
        return False

def validate_openapi_spec(file_path: str) -> bool:
    """Validate an OpenAPI specification file."""
    try:
        import json
        import yaml
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() == '.json':
                spec = json.load(f)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                spec = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
        
        # Basic validation
        required_fields = ['openapi', 'info', 'paths']
        for field in required_fields:
            if field not in spec:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate OpenAPI version
        if not spec['openapi'].startswith('3.'):
            logger.error(f"Unsupported OpenAPI version: {spec['openapi']}")
            return False
        
        # Validate info
        if 'title' not in spec['info'] or 'version' not in spec['info']:
            logger.error("Missing required info fields: title and version")
            return False
        
        # Validate paths
        if not spec['paths']:
            logger.warning("No API paths defined")
        
        logger.info("OpenAPI specification validation passed!")
        logger.info(f"Title: {spec['info']['title']}")
        logger.info(f"Version: {spec['info']['version']}")
        logger.info(f"OpenAPI Version: {spec['openapi']}")
        logger.info(f"Paths: {len(spec['paths'])}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating OpenAPI specification: {e}")
        return False

def show_statistics(file_path: str) -> bool:
    """Show statistics for an OpenAPI specification file."""
    try:
        import json
        import yaml
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        # Read and parse the file
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix.lower() == '.json':
                spec = json.load(f)
            elif file_path.suffix.lower() in ['.yaml', '.yml']:
                spec = yaml.safe_load(f)
            else:
                logger.error(f"Unsupported file format: {file_path.suffix}")
                return False
        
        # Calculate statistics
        total_paths = len(spec.get('paths', {}))
        total_schemas = len(spec.get('components', {}).get('schemas', {}))
        total_tags = len(spec.get('tags', []))
        
        # Count endpoints by method
        methods_count = {}
        for path, methods in spec.get('paths', {}).items():
            for method in methods.keys():
                methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1
        
        # Display statistics
        print(f"\n📊 API Documentation Statistics")
        print(f"   File: {file_path.name}")
        print(f"   Title: {spec.get('info', {}).get('title', 'Unknown')}")
        print(f"   Version: {spec.get('info', {}).get('version', 'Unknown')}")
        print(f"   OpenAPI Version: {spec.get('openapi', 'Unknown')}")
        print(f"   Total Paths: {total_paths}")
        print(f"   Total Schemas: {total_schemas}")
        print(f"   Total Tags: {total_tags}")
        
        if methods_count:
            print(f"   Methods:")
            for method, count in sorted(methods_count.items()):
                print(f"     {method}: {count}")
        
        # Show paths
        if total_paths > 0:
            print(f"\n   Paths:")
            for path in sorted(spec.get('paths', {}).keys()):
                methods = list(spec['paths'][path].keys())
                print(f"     {path} [{', '.join(methods)}]")
        
        return True
        
    except Exception as e:
        logger.error(f"Error showing statistics: {e}")
        return False

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="API Documentation System CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Instagram API documentation in all formats
  python cli.py generate instagram --output docs --formats all
  
  # Generate custom API documentation
  python cli.py generate custom --title "My API" --version "1.0.0" --output docs
  
  # Validate OpenAPI specification
  python cli.py validate openapi.json
  
  # Show statistics for OpenAPI specification
  python cli.py stats openapi.json
        """
    )
    
    # Global options
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Suppress all output except errors'
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    generate_parser = subparsers.add_parser('generate', help='Generate API documentation')
    generate_subparsers = generate_parser.add_subparsers(dest='type', help='Documentation type')
    
    # Instagram API docs
    instagram_parser = generate_subparsers.add_parser('instagram', help='Generate Instagram Captions API documentation')
    instagram_parser.add_argument(
        '--output', '-o',
        default='generated_docs',
        help='Output directory (default: generated_docs)'
    )
    instagram_parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['all', 'openapi', 'markdown', 'html'],
        default=['all'],
        help='Output formats (default: all)'
    )
    
    # Custom API docs
    custom_parser = generate_subparsers.add_parser('custom', help='Generate custom API documentation')
    custom_parser.add_argument(
        '--title', '-t',
        required=True,
        help='API title'
    )
    custom_parser.add_argument(
        '--version', '-V',
        required=True,
        help='API version'
    )
    custom_parser.add_argument(
        '--output', '-o',
        default='generated_docs',
        help='Output directory (default: generated_docs)'
    )
    custom_parser.add_argument(
        '--formats', '-f',
        nargs='+',
        choices=['all', 'openapi', 'markdown', 'html'],
        default=['all'],
        help='Output formats (default: all)'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate OpenAPI specification')
    validate_parser.add_argument(
        'file',
        help='OpenAPI specification file to validate'
    )
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show API documentation statistics')
    stats_parser.add_argument(
        'file',
        help='OpenAPI specification file to analyze'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose, args.quiet)
    
    # Handle commands
    if args.command == 'generate':
        if args.type == 'instagram':
            success = generate_instagram_docs(args.output, args.formats)
        elif args.type == 'custom':
            success = generate_custom_docs(args.title, args.version, args.output, args.formats)
        else:
            logger.error("Invalid documentation type")
            return 1
        
        return 0 if success else 1
        
    elif args.command == 'validate':
        success = validate_openapi_spec(args.file)
        return 0 if success else 1
        
    elif args.command == 'stats':
        success = show_statistics(args.file)
        return 0 if success else 1
        
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)






