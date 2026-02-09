import { Metadata } from 'next';
import { ApiDocumentationDashboard } from '@/components/api-docs/api-documentation-dashboard';
import { SwaggerUIComponent } from '@/components/api-docs/swagger-ui-component';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { BookOpen, Code, Zap } from 'lucide-react';

export const metadata: Metadata = {
  title: 'API Documentation | Blatam Academy',
  description: 'Comprehensive API documentation for Blatam Academy platform with interactive testing and examples.',
  keywords: ['API', 'Documentation', 'REST', 'OpenAPI', 'Swagger', 'Blatam Academy'],
  openGraph: {
    title: 'API Documentation | Blatam Academy',
    description: 'Comprehensive API documentation for Blatam Academy platform',
    type: 'website',
  },
};

export default function ApiDocsPage() {
  return (
    <div className="container mx-auto py-8 px-4">
      <div className="space-y-8">
        {/* Page Header */}
        <div className="text-center space-y-4">
          <h1 className="text-4xl font-bold tracking-tight">
            API Documentation
          </h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Comprehensive API documentation for the Blatam Academy platform. 
            Explore endpoints, test functionality, and integrate with our powerful educational APIs.
          </p>
        </div>

        {/* API Documentation Tabs */}
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <BookOpen className="h-4 w-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="interactive" className="flex items-center gap-2">
              <Code className="h-4 w-4" />
              Interactive
            </TabsTrigger>
            <TabsTrigger value="reference" className="flex items-center gap-2">
              <Zap className="h-4 w-4" />
              Reference
            </TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <ApiDocumentationDashboard />
          </TabsContent>

          <TabsContent value="interactive" className="space-y-6">
            <SwaggerUIComponent />
          </TabsContent>

          <TabsContent value="reference" className="space-y-6">
            <div className="space-y-6">
              {/* API Reference Content */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Authentication */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold">Authentication</h2>
                  <div className="space-y-3">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">JWT Tokens</h3>
                      <p className="text-sm text-muted-foreground">
                        Most endpoints require authentication using JWT tokens obtained from the authentication endpoints.
                      </p>
                      <code className="text-xs bg-muted px-2 py-1 rounded mt-2 block">
                        Authorization: Bearer YOUR_JWT_TOKEN
                      </code>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">NextAuth.js Sessions</h3>
                      <p className="text-sm text-muted-foreground">
                        Web applications can use NextAuth.js session cookies for authentication.
                      </p>
                    </div>
                  </div>
                </div>

                {/* Rate Limiting */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold">Rate Limiting</h2>
                  <div className="space-y-3">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">Default Limits</h3>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• 100 requests per minute per IP</li>
                        <li>• 1000 requests per hour per user</li>
                        <li>• Burst allowance: 10 requests per second</li>
                      </ul>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">Headers</h3>
                      <code className="text-xs bg-muted px-2 py-1 rounded block">
                        X-RateLimit-Limit: 100<br/>
                        X-RateLimit-Remaining: 95<br/>
                        X-RateLimit-Reset: 1640995200
                      </code>
                    </div>
                  </div>
                </div>

                {/* Error Handling */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold">Error Handling</h2>
                  <div className="space-y-3">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">Error Response Format</h3>
                      <pre className="text-xs bg-muted p-3 rounded overflow-x-auto">
{`{
  "error": "Error message",
  "details": [
    {
      "field": "email",
      "message": "Invalid email address"
    }
  ],
  "code": "VALIDATION_ERROR",
  "timestamp": "2024-01-15T10:30:00.000Z"
}`}
                      </pre>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">HTTP Status Codes</h3>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• 200: Success</li>
                        <li>• 400: Bad Request</li>
                        <li>• 401: Unauthorized</li>
                        <li>• 403: Forbidden</li>
                        <li>• 404: Not Found</li>
                        <li>• 429: Too Many Requests</li>
                        <li>• 500: Internal Server Error</li>
                      </ul>
                    </div>
                  </div>
                </div>

                {/* SDKs and Tools */}
                <div className="space-y-4">
                  <h2 className="text-2xl font-bold">SDKs & Tools</h2>
                  <div className="space-y-3">
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">Client SDKs</h3>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• JavaScript/TypeScript</li>
                        <li>• Python</li>
                        <li>• Java</li>
                        <li>• C#/.NET</li>
                        <li>• Go</li>
                      </ul>
                    </div>
                    <div className="p-4 border rounded-lg">
                      <h3 className="font-semibold">Development Tools</h3>
                      <ul className="text-sm text-muted-foreground space-y-1">
                        <li>• Postman Collection</li>
                        <li>• Insomnia Workspace</li>
                        <li>• OpenAPI Generator</li>
                        <li>• Swagger Codegen</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              {/* Base URLs */}
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Base URLs</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold">Development</h3>
                    <code className="text-sm bg-muted px-2 py-1 rounded">
                      http://localhost:3000
                    </code>
                  </div>
                  <div className="p-4 border rounded-lg">
                    <h3 className="font-semibold">Production</h3>
                    <code className="text-sm bg-muted px-2 py-1 rounded">
                      https://api.blatam-academy.com
                    </code>
                  </div>
                </div>
              </div>

              {/* Support */}
              <div className="space-y-4">
                <h2 className="text-2xl font-bold">Support</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg text-center">
                    <h3 className="font-semibold">Documentation</h3>
                    <p className="text-sm text-muted-foreground">
                      Comprehensive guides and tutorials
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg text-center">
                    <h3 className="font-semibold">Community</h3>
                    <p className="text-sm text-muted-foreground">
                      Join our developer community
                    </p>
                  </div>
                  <div className="p-4 border rounded-lg text-center">
                    <h3 className="font-semibold">Support</h3>
                    <p className="text-sm text-muted-foreground">
                      Get help from our support team
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}


