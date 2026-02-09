'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  ExternalLink, 
  Download, 
  RefreshCw, 
  Settings,
  Code,
  BookOpen,
  Zap
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import openApiSpec from '@/lib/api-docs/openapi-spec';

interface SwaggerUIComponentProps {
  className?: string;
}

export function SwaggerUIComponent({ className }: SwaggerUIComponentProps) {
  const swaggerRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [swaggerLoaded, setSwaggerLoaded] = useState(false);

  useEffect(() => {
    const loadSwaggerUI = async () => {
      if (typeof window === 'undefined') return;
      
      try {
        setIsLoading(true);
        
        // Dynamically import Swagger UI
        const SwaggerUIBundle = (await import('swagger-ui-dist/swagger-ui-bundle.js')).default;
        
        if (swaggerRef.current) {
          // Clear previous content
          swaggerRef.current.innerHTML = '';
          
          // Initialize Swagger UI
          SwaggerUIBundle({
            url: undefined, // We'll use spec instead of URL
            spec: openApiSpec,
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
              SwaggerUIBundle.presets.apis,
              SwaggerUIBundle.presets.standalone
            ],
            plugins: [
              SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: 'StandaloneLayout',
            tryItOutEnabled: true,
            requestInterceptor: (request: any) => {
              // Add authentication headers if available
              const token = localStorage.getItem('auth-token');
              if (token) {
                request.headers.Authorization = `Bearer ${token}`;
              }
              return request;
            },
            responseInterceptor: (response: any) => {
              // Handle responses
              return response;
            },
            onComplete: () => {
              setSwaggerLoaded(true);
              setIsLoading(false);
            },
            onFailure: (error: any) => {
              console.error('Swagger UI failed to load:', error);
              setIsLoading(false);
              toast.error('Failed to load Swagger UI');
            }
          });
        }
      } catch (error) {
        console.error('Error loading Swagger UI:', error);
        setIsLoading(false);
        toast.error('Failed to load API documentation');
      }
    };

    loadSwaggerUI();
  }, []);

  const downloadOpenAPISpec = () => {
    const specString = JSON.stringify(openApiSpec, null, 2);
    const blob = new Blob([specString], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'blatam-academy-api-spec.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('OpenAPI specification downloaded!');
  };

  const refreshSwagger = () => {
    if (swaggerRef.current) {
      swaggerRef.current.innerHTML = '';
      setSwaggerLoaded(false);
      // Reload Swagger UI
      window.location.reload();
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Interactive API Documentation</h2>
          <p className="text-muted-foreground">
            Explore and test the Blatam Academy API with Swagger UI
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={downloadOpenAPISpec}>
            <Download className="h-4 w-4 mr-2" />
            Download Spec
          </Button>
          <Button variant="outline" size="sm" onClick={refreshSwagger}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* API Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Version</CardTitle>
            <Code className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{openApiSpec.info.version}</div>
            <p className="text-xs text-muted-foreground">
              Current API version
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">OpenAPI Spec</CardTitle>
            <BookOpen className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{openApiSpec.openapi}</div>
            <p className="text-xs text-muted-foreground">
              OpenAPI specification version
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Endpoints</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {Object.keys(openApiSpec.paths).length}
            </div>
            <p className="text-xs text-muted-foreground">
              Available endpoints
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Loading State */}
      {isLoading && (
        <Card>
          <CardContent className="py-8 text-center">
            <div className="flex items-center justify-center space-x-2">
              <RefreshCw className="h-6 w-6 animate-spin" />
              <span>Loading Swagger UI...</span>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Error State */}
      {!isLoading && !swaggerLoaded && (
        <Alert>
          <Settings className="h-4 w-4" />
          <AlertDescription>
            Swagger UI failed to load. Please refresh the page or check your internet connection.
          </AlertDescription>
        </Alert>
      )}

      {/* Swagger UI Container */}
      <Card>
        <CardHeader>
          <CardTitle>Interactive API Explorer</CardTitle>
          <CardDescription>
            Test API endpoints directly from this interface. Authentication tokens will be automatically included if available.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div 
            ref={swaggerRef}
            id="swagger-ui"
            className="swagger-ui-container"
            style={{ minHeight: '600px' }}
          />
        </CardContent>
      </Card>

      {/* API Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              API Features
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge variant="outline">RESTful</Badge>
              <span className="text-sm">RESTful API design</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">JSON</Badge>
              <span className="text-sm">JSON request/response format</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">JWT</Badge>
              <span className="text-sm">JWT-based authentication</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Rate Limited</Badge>
              <span className="text-sm">Built-in rate limiting</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">CORS</Badge>
              <span className="text-sm">Cross-origin resource sharing</span>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant="outline">Validation</Badge>
              <span className="text-sm">Request/response validation</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Development Tools
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <h4 className="font-medium">SDK Generation</h4>
              <p className="text-sm text-muted-foreground">
                Generate client SDKs for multiple languages using the OpenAPI specification.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Testing</h4>
              <p className="text-sm text-muted-foreground">
                Use the interactive interface to test endpoints before integration.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Documentation</h4>
              <p className="text-sm text-muted-foreground">
                Comprehensive documentation with examples and schemas.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Validation</h4>
              <p className="text-sm text-muted-foreground">
                Built-in request/response validation and error handling.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Links */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Links</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="justify-start">
              <ExternalLink className="h-4 w-4 mr-2" />
              Postman Collection
            </Button>
            <Button variant="outline" className="justify-start">
              <Code className="h-4 w-4 mr-2" />
              SDK Generator
            </Button>
            <Button variant="outline" className="justify-start">
              <BookOpen className="h-4 w-4 mr-2" />
              API Guide
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
