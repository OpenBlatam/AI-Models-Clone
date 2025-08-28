"""
API Documentation for Instagram Captions API v10.0
OpenAPI spec generation and interactive documentation.
"""
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import logging
import inspect
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class APIEndpoint:
    """Represents an API endpoint."""
    
    path: str
    method: str
    summary: str
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    parameters: List[Dict[str, Any]] = field(default_factory=list)
    request_body: Optional[Dict[str, Any]] = None
    responses: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    security: List[Dict[str, List[str]]] = field(default_factory=list)
    deprecated: bool = False
    operation_id: Optional[str] = None
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        endpoint_spec = {
            'summary': self.summary,
            'tags': self.tags,
            'parameters': self.parameters,
            'responses': self.responses,
            'deprecated': self.deprecated
        }
        
        if self.description:
            endpoint_spec['description'] = self.description
        
        if self.request_body:
            endpoint_spec['requestBody'] = self.request_body
        
        if self.security:
            endpoint_spec['security'] = self.security
        
        if self.operation_id:
            endpoint_spec['operationId'] = self.operation_id
        
        return endpoint_spec

@dataclass
class APIModel:
    """Represents an API data model."""
    
    name: str
    type: str
    description: Optional[str] = None
    properties: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    required: List[str] = field(default_factory=list)
    example: Optional[Dict[str, Any]] = None
    
    def to_openapi(self) -> Dict[str, Any]:
        """Convert to OpenAPI specification format."""
        model_spec = {
            'type': self.type,
            'properties': self.properties
        }
        
        if self.description:
            model_spec['description'] = self.description
        
        if self.required:
            model_spec['required'] = self.required
        
        if self.example:
            model_spec['example'] = self.example
        
        return model_spec

class APIDocumentation:
    """Generates and manages API documentation."""
    
    def __init__(self, title: str = "API Documentation", version: str = "1.0.0"):
        self.title = title
        self.version = version
        self.description = ""
        self.contact = {}
        self.license = {}
        self.servers: List[Dict[str, str]] = []
        self.endpoints: Dict[str, Dict[str, APIEndpoint]] = {}
        self.models: Dict[str, APIModel] = {}
        self.security_schemes: Dict[str, Dict[str, Any]] = {}
        self.tags: List[Dict[str, str]] = []
        
        # Default security schemes
        self._setup_default_security()
    
    def _setup_default_security(self):
        """Setup default security schemes."""
        self.security_schemes = {
            'bearerAuth': {
                'type': 'http',
                'scheme': 'bearer',
                'bearerFormat': 'JWT'
            },
            'apiKeyAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'X-API-Key'
            }
        }
    
    def add_endpoint(self, endpoint: APIEndpoint):
        """Add an API endpoint."""
        if endpoint.path not in self.endpoints:
            self.endpoints[endpoint.path] = {}
        
        self.endpoints[endpoint.path][endpoint.method.lower()] = endpoint
        logger.debug(f"Added endpoint: {endpoint.method} {endpoint.path}")
    
    def add_model(self, model: APIModel):
        """Add an API data model."""
        self.models[model.name] = model
        logger.debug(f"Added model: {model.name}")
    
    def add_security_scheme(self, name: str, scheme: Dict[str, Any]):
        """Add a security scheme."""
        self.security_schemes[name] = scheme
        logger.debug(f"Added security scheme: {name}")
    
    def add_tag(self, name: str, description: str):
        """Add an API tag."""
        self.tags.append({
            'name': name,
            'description': description
        })
        logger.debug(f"Added tag: {name}")
    
    def set_info(self, description: str, contact: Optional[Dict[str, str]] = None,
                 license_info: Optional[Dict[str, str]] = None):
        """Set API information."""
        self.description = description
        
        if contact:
            self.contact = contact
        
        if license_info:
            self.license = license_info
    
    def add_server(self, url: str, description: str = ""):
        """Add a server configuration."""
        server = {'url': url}
        if description:
            server['description'] = description
        
        self.servers.append(server)
        logger.debug(f"Added server: {url}")
    
    def generate_openapi_spec(self) -> Dict[str, Any]:
        """Generate OpenAPI specification."""
        openapi_spec = {
            'openapi': '3.0.3',
            'info': {
                'title': self.title,
                'version': self.version,
                'description': self.description
            },
            'servers': self.servers,
            'paths': {},
            'components': {
                'schemas': {},
                'securitySchemes': self.security_schemes
            },
            'tags': self.tags
        }
        
        # Add contact info if available
        if self.contact:
            openapi_spec['info']['contact'] = self.contact
        
        # Add license info if available
        if self.license:
            openapi_spec['info']['license'] = self.license
        
        # Add paths
        for path, methods in self.endpoints.items():
            openapi_spec['paths'][path] = {}
            for method, endpoint in methods.items():
                openapi_spec['paths'][path][method] = endpoint.to_openapi()
        
        # Add schemas
        for model_name, model in self.models.items():
            openapi_spec['components']['schemas'][model_name] = model.to_openapi()
        
        return openapi_spec
    
    def save_openapi_spec(self, file_path: str, format: str = "json") -> bool:
        """Save OpenAPI specification to file."""
        try:
            spec = self.generate_openapi_spec()
            
            if format.lower() == "json":
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(spec, f, ensure_ascii=False, indent=2, default=str)
            
            elif format.lower() == "yaml":
                with open(file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(spec, f, default_flow_style=False, allow_unicode=True, indent=2)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"OpenAPI specification saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving OpenAPI specification: {e}")
            return False
    
    def generate_markdown_docs(self) -> str:
        """Generate Markdown API documentation."""
        md_content = f"""# {self.title}

**Version:** {self.version}

{self.description}

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
- [Models](#models)
- [Examples](#examples)

## Authentication

{self._format_authentication_md()}

## Endpoints

{self._format_endpoints_md()}

## Models

{self._format_models_md()}

## Examples

{self._format_examples_md()}

---
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return md_content
    
    def _format_authentication_md(self) -> str:
        """Format authentication section for Markdown."""
        if not self.security_schemes:
            return "No authentication required."
        
        auth_docs = []
        for scheme_name, scheme in self.security_schemes.items():
            if scheme['type'] == 'http':
                auth_docs.append(f"""### Bearer Token Authentication

**Scheme:** {scheme['scheme']}  
**Format:** {scheme.get('bearerFormat', 'JWT')}

Include the token in the Authorization header:
```
Authorization: Bearer <your-token>
```
""")
            elif scheme['type'] == 'apiKey':
                auth_docs.append(f"""### API Key Authentication

**Location:** {scheme['in']}  
**Header Name:** {scheme['name']}

Include the API key in the request headers:
```
{scheme['name']}: <your-api-key>
```
""")
        
        return '\n\n'.join(auth_docs)
    
    def _format_endpoints_md(self) -> str:
        """Format endpoints section for Markdown."""
        if not self.endpoints:
            return "No endpoints documented."
        
        endpoint_docs = []
        for path, methods in self.endpoints.items():
            for method, endpoint in methods.items():
                doc = f"""### {endpoint.summary}

**Method:** `{method.upper()}`  
**Path:** `{path}`

{endpoint.description or 'No description provided.'}

"""
                
                # Parameters
                if endpoint.parameters:
                    doc += "**Parameters:**\n"
                    for param in endpoint.parameters:
                        doc += f"- `{param['name']}` ({param.get('type', 'string')})"
                        if param.get('required', False):
                            doc += " **Required**"
                        if param.get('description'):
                            doc += f": {param['description']}"
                        doc += "\n"
                    doc += "\n"
                
                # Request Body
                if endpoint.request_body:
                    doc += "**Request Body:**\n"
                    doc += f"```json\n{json.dumps(endpoint.request_body, indent=2)}\n```\n\n"
                
                # Responses
                if endpoint.responses:
                    doc += "**Responses:**\n"
                    for status_code, response in endpoint.responses.items():
                        doc += f"- **{status_code}**: {response.get('description', 'No description')}\n"
                    doc += "\n"
                
                # Security
                if endpoint.security:
                    doc += "**Security:**\n"
                    for security in endpoint.security:
                        for scheme, scopes in security.items():
                            doc += f"- `{scheme}`"
                            if scopes:
                                doc += f" (scopes: {', '.join(scopes)})"
                            doc += "\n"
                    doc += "\n"
                
                # Tags
                if endpoint.tags:
                    doc += f"**Tags:** {', '.join(endpoint.tags)}\n\n"
                
                endpoint_docs.append(doc)
        
        return '\n'.join(endpoint_docs)
    
    def _format_models_md(self) -> str:
        """Format models section for Markdown."""
        if not self.models:
            return "No models documented."
        
        model_docs = []
        for model_name, model in self.models.items():
            doc = f"""### {model_name}

**Type:** {model.type}

{model.description or 'No description provided.'}

"""
            
            if model.properties:
                doc += "**Properties:**\n"
                for prop_name, prop_info in model.properties.items():
                    doc += f"- `{prop_name}` ({prop_info.get('type', 'string')})"
                    if prop_name in model.required:
                        doc += " **Required**"
                    if prop_info.get('description'):
                        doc += f": {prop_info['description']}"
                    doc += "\n"
                doc += "\n"
            
            if model.example:
                doc += "**Example:**\n"
                doc += f"```json\n{json.dumps(model.example, indent=2)}\n```\n\n"
            
            model_docs.append(doc)
        
        return '\n'.join(model_docs)
    
    def _format_examples_md(self) -> str:
        """Format examples section for Markdown."""
        examples = []
        
        # Generate examples for each endpoint
        for path, methods in self.endpoints.items():
            for method, endpoint in methods.items():
                example = f"""### {endpoint.summary}

**Request:**
```bash
curl -X {method.upper()} "{path}" \\
  -H "Content-Type: application/json"
"""
                
                if endpoint.request_body:
                    example += f"  -d '{json.dumps(endpoint.request_body, indent=2)}'"
                
                example += "\n\n**Response:**\n"
                
                # Find a successful response
                success_response = None
                for status_code, response in endpoint.responses.items():
                    if status_code.startswith('2'):
                        success_response = response
                        break
                
                if success_response:
                    example += f"```json\n{json.dumps(success_response, indent=2)}\n```"
                else:
                    example += "```json\n{\n  \"message\": \"Response example\"\n}\n```"
                
                examples.append(example)
        
        if not examples:
            return "No examples provided."
        
        return '\n\n'.join(examples)
    
    def save_markdown_docs(self, file_path: str) -> bool:
        """Save Markdown documentation to file."""
        try:
            md_content = self.generate_markdown_docs()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(md_content)
            
            logger.info(f"Markdown documentation saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving Markdown documentation: {e}")
            return False
    
    def generate_html_docs(self, template_path: Optional[str] = None) -> str:
        """Generate HTML documentation."""
        # Basic HTML template
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .endpoint {{ border: 1px solid #ddd; margin: 10px 0; padding: 15px; border-radius: 5px; }}
        .method {{ display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }}
        .get {{ background-color: #61affe; }}
        .post {{ background-color: #49cc90; }}
        .put {{ background-color: #fca130; }}
        .delete {{ background-color: #f93e3e; }}
        .path {{ font-family: monospace; font-size: 16px; margin: 10px 0; }}
        .description {{ color: #666; margin: 10px 0; }}
        .parameters {{ background-color: #f5f5f5; padding: 10px; border-radius: 3px; margin: 10px 0; }}
        .responses {{ background-color: #f0f8ff; padding: 10px; border-radius: 3px; margin: 10px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p><strong>Version:</strong> {version}</p>
        <p>{description}</p>
        
        <h2>Endpoints</h2>
        {endpoints_html}
        
        <h2>Models</h2>
        {models_html}
    </div>
</body>
</html>
"""
        
        # Generate endpoints HTML
        endpoints_html = ""
        for path, methods in self.endpoints.items():
            for method, endpoint in methods.items():
                endpoints_html += f"""
                <div class="endpoint">
                    <span class="method {method.lower()}">{method.upper()}</span>
                    <div class="path">{path}</div>
                    <div class="description">{endpoint.summary}</div>
                    {self._generate_endpoint_html(endpoint)}
                </div>
                """
        
        # Generate models HTML
        models_html = ""
        for model_name, model in self.models.items():
            models_html += f"""
            <div class="endpoint">
                <h3>{model_name}</h3>
                <p><strong>Type:</strong> {model.type}</p>
                <p>{model.description or 'No description'}</p>
            </div>
            """
        
        # Fill template
        html_content = html_template.format(
            title=self.title,
            version=self.version,
            description=self.description,
            endpoints_html=endpoints_html,
            models_html=models_html
        )
        
        return html_content
    
    def _generate_endpoint_html(self, endpoint: APIEndpoint) -> str:
        """Generate HTML for a single endpoint."""
        html = ""
        
        if endpoint.parameters:
            html += '<div class="parameters">'
            html += '<strong>Parameters:</strong><ul>'
            for param in endpoint.parameters:
                html += f'<li><code>{param["name"]}</code> ({param.get("type", "string")})'
                if param.get("required", False):
                    html += ' <strong>Required</strong>'
                if param.get("description"):
                    html += f': {param["description"]}'
                html += '</li>'
            html += '</ul></div>'
        
        if endpoint.responses:
            html += '<div class="responses">'
            html += '<strong>Responses:</strong><ul>'
            for status_code, response in endpoint.responses.items():
                html += f'<li><strong>{status_code}</strong>: {response.get("description", "No description")}</li>'
            html += '</ul></div>'
        
        return html
    
    def save_html_docs(self, file_path: str) -> bool:
        """Save HTML documentation to file."""
        try:
            html_content = self.generate_html_docs()
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML documentation saved to {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving HTML documentation: {e}")
            return False
    
    def export_all_formats(self, output_dir: str) -> bool:
        """Export documentation in all formats."""
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Save OpenAPI spec
            self.save_openapi_spec(str(output_path / "openapi.json"), "json")
            self.save_openapi_spec(str(output_path / "openapi.yaml"), "yaml")
            
            # Save documentation
            self.save_markdown_docs(str(output_path / "api_documentation.md"))
            self.save_html_docs(str(output_path / "api_documentation.html"))
            
            logger.info(f"All documentation formats exported to {output_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting documentation: {e}")
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get API documentation statistics."""
        total_endpoints = sum(len(methods) for methods in self.endpoints.values())
        total_models = len(self.models)
        total_tags = len(self.tags)
        
        # Count endpoints by method
        methods_count = {}
        for methods in self.endpoints.values():
            for method in methods.keys():
                methods_count[method.upper()] = methods_count.get(method.upper(), 0) + 1
        
        return {
            'total_endpoints': total_endpoints,
            'total_models': total_models,
            'total_tags': total_tags,
            'endpoints_by_method': methods_count,
            'endpoints_by_path': len(self.endpoints),
            'security_schemes': len(self.security_schemes)
        }






