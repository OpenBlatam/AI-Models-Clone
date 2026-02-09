# Instagram Captions API Documentation System

A comprehensive documentation generation system for the Instagram Captions API v10.0. This system automatically generates API documentation in multiple formats including OpenAPI specification, Markdown, and HTML.

## Features

- **Multi-format Documentation**: Generate documentation in OpenAPI 3.0, Markdown, and HTML formats
- **Comprehensive API Coverage**: Documents all endpoints, data models, and examples
- **Interactive Documentation**: OpenAPI spec compatible with Swagger UI and other tools
- **Automated Generation**: Script-based generation with customizable templates
- **Professional Styling**: Clean, modern documentation design

## Quick Start

### 1. Install Dependencies

```bash
cd documentation
pip install -r requirements.txt
```

### 2. Generate Documentation

```bash
python generate_docs.py
```

This will create a `generated_docs/` directory with all documentation formats.

### 3. View Generated Documentation

- **OpenAPI Spec**: `generated_docs/openapi.json` or `openapi.yaml`
- **Markdown**: `generated_docs/api_documentation.md`
- **HTML**: `generated_docs/api_documentation.html`

## Documentation Formats

### OpenAPI Specification

The OpenAPI 3.0 specification can be used with:
- Swagger UI for interactive API exploration
- Postman for API testing
- Code generation tools
- API management platforms

### Markdown Documentation

Human-readable documentation perfect for:
- GitHub repositories
- Developer portals
- Technical documentation sites
- Print materials

### HTML Documentation

Self-contained HTML files with:
- Responsive design
- Professional styling
- Easy sharing and hosting
- Print-friendly layout

## API Endpoints Documented

### Core Caption Generation
- `POST /api/v10/captions/generate` - Generate single caption
- `POST /api/v10/captions/batch-generate` - Batch caption generation
- `POST /api/v10/captions/translate` - Multi-language translation

### Hashtag Optimization
- `POST /api/v10/hashtags/optimize` - Hashtag analysis and optimization

### Analytics & Engagement
- `POST /api/v10/analytics/engagement` - Engagement prediction
- `POST /api/v10/branding/voice-analysis` - Brand voice analysis

### Templates & Compliance
- `GET /api/v10/templates/captions` - Caption templates
- `POST /api/v10/compliance/check` - Content compliance

### System
- `GET /health` - Health check endpoint

## Data Models

### Request Models
- `CaptionGenerationRequest` - Caption generation parameters
- `HashtagOptimizationRequest` - Hashtag optimization parameters

### Response Models
- `CaptionResponse` - Generated caption with metadata
- `HashtagAnalysis` - Hashtag performance metrics
- `EngagementMetrics` - Engagement analysis results
- `ErrorResponse` - Standard error format

## Customization

### Adding New Endpoints

1. Create an `APIEndpoint` object in `generate_docs.py`
2. Define path, method, summary, and other properties
3. Add to the API documentation using `api_docs.add_endpoint()`

Example:
```python
new_endpoint = APIEndpoint(
    path="/api/v10/new-feature",
    method="POST",
    summary="New Feature Description",
    description="Detailed description of the new feature",
    tags=["new-feature"],
    # ... other properties
)
api_docs.add_endpoint(new_endpoint)
```

### Adding New Data Models

1. Create an `APIModel` object
2. Define properties, types, and validation rules
3. Add to the API documentation using `api_docs.add_model()`

Example:
```python
new_model = APIModel(
    name="NewModel",
    type="object",
    description="Description of the new model",
    properties={
        "field1": {
            "type": "string",
            "description": "Description of field1"
        }
    },
    required=["field1"]
)
api_docs.add_model(new_model)
```

### Customizing Output

Modify the `export_all_formats()` method in `APIDocumentation` class to:
- Change output directory structure
- Add new export formats
- Customize file naming
- Modify content templates

## Advanced Features

### Custom Security Schemes

Add custom authentication methods:
```python
api_docs.add_security_scheme("customAuth", {
    "type": "oauth2",
    "flows": {
        "authorizationCode": {
            "authorizationUrl": "https://example.com/oauth/authorize",
            "tokenUrl": "https://example.com/oauth/token"
        }
    }
})
```

### Server Configurations

Add multiple server environments:
```python
api_docs.add_server("https://api.production.com", "Production")
api_docs.add_server("https://api.staging.com", "Staging")
api_docs.add_server("http://localhost:8000", "Local Development")
```

### Custom Tags

Organize endpoints with custom tags:
```python
api_docs.add_tag("beta", "Beta features - use with caution")
api_docs.add_tag("deprecated", "Deprecated features - will be removed")
```

## Integration

### CI/CD Pipeline

Add to your CI/CD pipeline for automatic documentation updates:
```yaml
# GitHub Actions example
- name: Generate API Documentation
  run: |
    cd documentation
    python generate_docs.py
    
- name: Upload Documentation
  uses: actions/upload-artifact@v2
  with:
    name: api-documentation
    path: documentation/generated_docs/
```

### Webhook Integration

Set up webhooks to regenerate documentation when API changes:
```python
# Example webhook handler
@app.route('/webhook/api-update', methods=['POST'])
def regenerate_docs():
    subprocess.run(['python', 'generate_docs.py'])
    return jsonify({'status': 'Documentation regenerated'})
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **File Permission Errors**: Check write permissions for output directory
3. **YAML Errors**: Verify YAML syntax in custom configurations
4. **Memory Issues**: Large APIs may require more memory for generation

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validation

Validate generated OpenAPI spec:
```bash
# Install openapi-validator
pip install openapi-validator

# Validate the generated spec
openapi-validator generated_docs/openapi.json
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This documentation system is part of the Instagram Captions API project and follows the same license terms.

## Support

For questions and support:
- Create an issue in the repository
- Contact the development team
- Check the API documentation for endpoint details

## Version History

- **v1.0.0** - Initial documentation system
- **v1.1.0** - Added HTML generation and customization options
- **v1.2.0** - Enhanced OpenAPI spec generation
- **v2.0.0** - Complete rewrite with improved architecture
- **v10.0.0** - Full Instagram Captions API coverage






