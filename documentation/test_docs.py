#!/usr/bin/env python3
"""
Test script for the API Documentation system.
Verifies that all components work correctly.
"""
import sys
import os
from pathlib import Path
import tempfile
import shutil
import json
import yaml

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from documentation.api_documentation import (
    APIDocumentation, APIEndpoint, APIModel
)

def test_basic_functionality():
    """Test basic API documentation functionality."""
    print("🧪 Testing basic functionality...")
    
    # Create API documentation
    api_docs = APIDocumentation(
        title="Test API",
        version="1.0.0"
    )
    
    # Test setting info
    api_docs.set_info(
        description="Test API for testing purposes",
        contact={"name": "Test Team", "email": "test@example.com"}
    )
    
    # Test adding server
    api_docs.add_server("https://test-api.com", "Test Server")
    
    # Test adding tag
    api_docs.add_tag("test", "Test endpoints")
    
    # Test adding model
    test_model = APIModel(
        name="TestModel",
        type="object",
        description="A test model",
        properties={
            "id": {"type": "string"},
            "name": {"type": "string"}
        },
        required=["id", "name"]
    )
    api_docs.add_model(test_model)
    
    # Test adding endpoint
    test_endpoint = APIEndpoint(
        path="/test",
        method="GET",
        summary="Test endpoint",
        description="A test endpoint",
        tags=["test"],
        responses={
            "200": {
                "description": "Success",
                "content": {
                    "application/json": {
                        "schema": {"$ref": "#/components/schemas/TestModel"}
                    }
                }
            }
        }
    )
    api_docs.add_endpoint(test_endpoint)
    
    print("✅ Basic functionality tests passed")
    return api_docs

def test_openapi_generation(api_docs):
    """Test OpenAPI specification generation."""
    print("🧪 Testing OpenAPI generation...")
    
    # Generate OpenAPI spec
    spec = api_docs.generate_openapi_spec()
    
    # Verify required fields
    assert "openapi" in spec
    assert "info" in spec
    assert "paths" in spec
    assert "components" in spec
    
    # Verify info
    assert spec["info"]["title"] == "Test API"
    assert spec["info"]["version"] == "1.0.0"
    
    # Verify paths
    assert "/test" in spec["paths"]
    assert "get" in spec["paths"]["/test"]
    
    # Verify components
    assert "TestModel" in spec["components"]["schemas"]
    
    print("✅ OpenAPI generation tests passed")
    return spec

def test_file_export(api_docs):
    """Test file export functionality."""
    print("🧪 Testing file export...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Test JSON export
        json_path = os.path.join(temp_dir, "test.json")
        success = api_docs.save_openapi_spec(json_path, "json")
        assert success
        assert os.path.exists(json_path)
        
        # Verify JSON content
        with open(json_path, 'r') as f:
            content = json.load(f)
            assert content["info"]["title"] == "Test API"
        
        # Test YAML export
        yaml_path = os.path.join(temp_dir, "test.yaml")
        success = api_docs.save_openapi_spec(yaml_path, "yaml")
        assert success
        assert os.path.exists(yaml_path)
        
        # Verify YAML content
        with open(yaml_path, 'r') as f:
            content = yaml.safe_load(f)
            assert content["info"]["title"] == "Test API"
        
        # Test Markdown export
        md_path = os.path.join(temp_dir, "test.md")
        success = api_docs.save_markdown_docs(md_path)
        assert success
        assert os.path.exists(md_path)
        
        # Verify Markdown content
        with open(md_path, 'r') as f:
            content = f.read()
            assert "Test API" in content
            assert "## Endpoints" in content
        
        # Test HTML export
        html_path = os.path.join(temp_dir, "test.html")
        success = api_docs.save_html_docs(html_path)
        assert success
        assert os.path.exists(html_path)
        
        # Verify HTML content
        with open(html_path, 'r') as f:
            content = f.read()
            assert "<title>Test API</title>" in content
            assert "Test endpoint" in content
    
    print("✅ File export tests passed")

def test_statistics(api_docs):
    """Test statistics functionality."""
    print("🧪 Testing statistics...")
    
    stats = api_docs.get_statistics()
    
    # Verify statistics
    assert stats["total_endpoints"] == 1
    assert stats["total_models"] == 1
    assert stats["total_tags"] == 1
    assert stats["endpoints_by_method"]["get"] == 1
    
    print("✅ Statistics tests passed")

def test_instagram_api_docs():
    """Test Instagram API documentation generation."""
    print("🧪 Testing Instagram API documentation...")
    
    try:
        # Import and test the Instagram API docs generator
        from documentation.generate_docs import create_instagram_captions_api_docs
        
        # Generate Instagram API docs
        instagram_docs = create_instagram_captions_api_docs()
        
        # Verify it has the expected content
        assert instagram_docs.title == "Instagram Captions API"
        assert instagram_docs.version == "10.0.0"
        
        # Check for key endpoints
        stats = instagram_docs.get_statistics()
        assert stats["total_endpoints"] > 0
        assert stats["total_models"] > 0
        
        # Verify specific endpoints exist
        paths = instagram_docs.endpoints.keys()
        assert "/api/v10/captions/generate" in paths
        assert "/api/v10/hashtags/optimize" in paths
        
        print("✅ Instagram API documentation tests passed")
        return instagram_docs
        
    except ImportError as e:
        print(f"⚠️  Could not import Instagram docs generator: {e}")
        return None

def test_export_all_formats(api_docs):
    """Test exporting all formats at once."""
    print("🧪 Testing export all formats...")
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Export all formats
        success = api_docs.export_all_formats(temp_dir)
        assert success
        
        # Verify all files were created
        expected_files = [
            "openapi.json",
            "openapi.yaml", 
            "api_documentation.md",
            "api_documentation.html"
        ]
        
        for filename in expected_files:
            file_path = os.path.join(temp_dir, filename)
            assert os.path.exists(file_path), f"Missing file: {filename}"
        
        print("✅ Export all formats test passed")

def run_all_tests():
    """Run all tests."""
    print("🚀 Starting API Documentation System Tests\n")
    
    try:
        # Test 1: Basic functionality
        api_docs = test_basic_functionality()
        
        # Test 2: OpenAPI generation
        spec = test_openapi_generation(api_docs)
        
        # Test 3: File export
        test_file_export(api_docs)
        
        # Test 4: Statistics
        test_statistics(api_docs)
        
        # Test 5: Export all formats
        test_export_all_formats(api_docs)
        
        # Test 6: Instagram API docs (if available)
        instagram_docs = test_instagram_api_docs()
        
        print("\n🎉 All tests passed successfully!")
        
        # Show final statistics
        if instagram_docs:
            stats = instagram_docs.get_statistics()
            print(f"\n📊 Instagram API Documentation Statistics:")
            print(f"   - Total Endpoints: {stats['total_endpoints']}")
            print(f"   - Total Models: {stats['total_models']}")
            print(f"   - Total Tags: {stats['total_tags']}")
            print(f"   - Methods: {', '.join([f'{k}: {v}' for k, v in stats['endpoints_by_method'].items()])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)






