#!/usr/bin/env python3
"""
Demo script for the Instagram Captions API Documentation System.
Shows how to use the system programmatically.
"""
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

def demo_basic_usage():
    """Demonstrate basic usage of the documentation system."""
    print("🚀 Instagram Captions API Documentation System Demo")
    print("=" * 60)
    
    try:
        from documentation.api_documentation import APIDocumentation, APIEndpoint, APIModel
        
        # Create a simple API documentation
        print("\n1. Creating basic API documentation...")
        api_docs = APIDocumentation(
            title="Demo API",
            version="1.0.0"
        )
        
        # Add information
        api_docs.set_info(
            description="A demo API for showcasing the documentation system",
            contact={"name": "Demo Team", "email": "demo@example.com"}
        )
        
        # Add server
        api_docs.add_server("https://demo-api.com", "Demo Server")
        
        # Add tag
        api_docs.add_tag("demo", "Demo endpoints")
        
        # Add a simple model
        print("2. Adding data models...")
        user_model = APIModel(
            name="User",
            type="object",
            description="A user in the system",
            properties={
                "id": {"type": "string", "description": "User ID"},
                "name": {"type": "string", "description": "User name"},
                "email": {"type": "string", "description": "User email"}
            },
            required=["id", "name", "email"],
            example={
                "id": "user_123",
                "name": "John Doe",
                "email": "john@example.com"
            }
        )
        api_docs.add_model(user_model)
        
        # Add an endpoint
        print("3. Adding API endpoints...")
        get_user_endpoint = APIEndpoint(
            path="/users/{id}",
            method="GET",
            summary="Get user by ID",
            description="Retrieve a user from the system by their ID",
            tags=["demo"],
            parameters=[
                {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "User ID"
                }
            ],
            responses={
                "200": {
                    "description": "User found successfully",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"}
                        }
                    }
                },
                "404": {
                    "description": "User not found",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        )
        api_docs.add_endpoint(get_user_endpoint)
        
        # Generate documentation
        print("4. Generating documentation...")
        
        # Create output directory
        output_dir = Path("demo_output")
        output_dir.mkdir(exist_ok=True)
        
        # Generate OpenAPI spec
        print("   - OpenAPI specification...")
        api_docs.save_openapi_spec(str(output_dir / "demo_openapi.json"), "json")
        api_docs.save_openapi_spec(str(output_dir / "demo_openapi.yaml"), "yaml")
        
        # Generate Markdown
        print("   - Markdown documentation...")
        api_docs.save_markdown_docs(str(output_dir / "demo_documentation.md"))
        
        # Generate HTML
        print("   - HTML documentation...")
        api_docs.save_html_docs(str(output_dir / "demo_documentation.html"))
        
        # Show statistics
        print("5. Documentation statistics:")
        stats = api_docs.get_statistics()
        print(f"   - Total endpoints: {stats['total_endpoints']}")
        print(f"   - Total models: {stats['total_models']}")
        print(f"   - Total tags: {stats['total_tags']}")
        print(f"   - Methods: {', '.join([f'{k}: {v}' for k, v in stats['endpoints_by_method'].items()])}")
        
        print(f"\n✅ Demo completed successfully!")
        print(f"📁 Documentation saved to: {output_dir.absolute()}")
        
        # List generated files
        generated_files = list(output_dir.glob("*"))
        print("\n📄 Generated files:")
        for file_path in generated_files:
            print(f"   - {file_path.name}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_instagram_api():
    """Demonstrate Instagram API documentation generation."""
    print("\n🎯 Instagram Captions API Documentation Demo")
    print("=" * 60)
    
    try:
        from documentation.generate_docs import create_instagram_captions_api_docs
        
        print("1. Creating Instagram Captions API documentation...")
        instagram_docs = create_instagram_captions_api_docs()
        
        print("2. Generating documentation...")
        
        # Create output directory
        output_dir = Path("instagram_demo_output")
        output_dir.mkdir(exist_ok=True)
        
        # Export all formats
        success = instagram_docs.export_all_formats(str(output_dir))
        
        if success:
            # Show statistics
            stats = instagram_docs.get_statistics()
            print(f"\n✅ Instagram API documentation generated successfully!")
            print(f"📊 Statistics:")
            print(f"   - Total endpoints: {stats['total_endpoints']}")
            print(f"   - Total models: {stats['total_models']}")
            print(f"   - Total tags: {stats['total_tags']}")
            print(f"   - Methods: {', '.join([f'{k}: {v}' for k, v in stats['endpoints_by_method'].items()])}")
            
            print(f"\n📁 Documentation saved to: {output_dir.absolute()}")
            
            # List generated files
            generated_files = list(output_dir.glob("*"))
            print("\n📄 Generated files:")
            for file_path in generated_files:
                print(f"   - {file_path.name}")
            
            return True
        else:
            print("❌ Failed to generate Instagram API documentation")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        return False
        
    except Exception as e:
        print(f"❌ Error during Instagram API demo: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_cli_usage():
    """Demonstrate CLI usage."""
    print("\n🖥️  CLI Interface Demo")
    print("=" * 60)
    
    print("The documentation system includes a powerful CLI interface:")
    print()
    print("Available commands:")
    print("  python cli.py generate instagram --output docs --formats all")
    print("  python cli.py generate custom --title 'My API' --version '1.0.0'")
    print("  python cli.py validate openapi.json")
    print("  python cli.py stats openapi.json")
    print()
    print("For help:")
    print("  python cli.py --help")
    print("  python cli.py generate --help")
    print()

def main():
    """Main demo function."""
    print("🎉 Welcome to the Instagram Captions API Documentation System Demo!")
    print("This demo will show you how to use the documentation system.")
    print()
    
    # Demo 1: Basic usage
    success1 = demo_basic_usage()
    
    if success1:
        print("\n" + "="*60)
        
        # Demo 2: Instagram API
        success2 = demo_instagram_api()
        
        if success2:
            print("\n" + "="*60)
            
            # Demo 3: CLI usage
            demo_cli_usage()
            
            print("🎊 All demos completed successfully!")
            print("\n📚 Next steps:")
            print("1. Explore the generated documentation files")
            print("2. Try the CLI interface: python cli.py --help")
            print("3. Run tests: python test_docs.py")
            print("4. Generate your own API documentation")
            
        else:
            print("\n⚠️  Instagram API demo failed, but basic demo succeeded")
    else:
        print("\n❌ Basic demo failed. Please check your setup.")
        print("Try running: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("Demo completed!")

if __name__ == "__main__":
    main()






