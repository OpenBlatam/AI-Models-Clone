'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  BookOpen, 
  Code, 
  Play, 
  Download, 
  Copy, 
  Check, 
  ExternalLink,
  Server,
  Shield,
  Zap,
  Users,
  FileText,
  Brain,
  Activity,
  Settings,
  Search,
  Filter,
  RefreshCw
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ApiEndpoint {
  path: string;
  method: string;
  summary: string;
  description: string;
  tags: string[];
  parameters?: any[];
  responses: any;
  security?: any[];
}

interface ApiDocumentationDashboardProps {
  className?: string;
}

export function ApiDocumentationDashboard({ className }: ApiDocumentationDashboardProps) {
  const [activeTab, setActiveTab] = useState('overview');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTag, setSelectedTag] = useState('all');
  const [showOnlyAuthenticated, setShowOnlyAuthenticated] = useState(false);
  const [copiedEndpoint, setCopiedEndpoint] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [apiStats, setApiStats] = useState({
    totalEndpoints: 0,
    authenticatedEndpoints: 0,
    publicEndpoints: 0,
    tags: [] as string[]
  });

  // Mock API endpoints data (in real app, this would come from the OpenAPI spec)
  const apiEndpoints: ApiEndpoint[] = [
    {
      path: '/api/health',
      method: 'GET',
      summary: 'Health Check',
      description: 'Check the health status of the API service',
      tags: ['System'],
      responses: {
        '200': { description: 'Service is healthy' },
        '500': { description: 'Service is unhealthy' }
      }
    },
    {
      path: '/api/auth/[...nextauth]',
      method: 'GET',
      summary: 'NextAuth.js Authentication',
      description: 'Handle authentication requests using NextAuth.js',
      tags: ['Authentication'],
      responses: {
        '200': { description: 'Authentication successful' },
        '401': { description: 'Authentication failed' }
      }
    },
    {
      path: '/api/user',
      method: 'DELETE',
      summary: 'Delete User Account',
      description: 'Permanently delete the authenticated user account',
      tags: ['User Management'],
      security: [{ bearerAuth: [] }],
      responses: {
        '200': { description: 'User deleted successfully' },
        '401': { description: 'Not authenticated' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/contact',
      method: 'POST',
      summary: 'Submit Contact Form',
      description: 'Submit a contact form with spam protection and rate limiting',
      tags: ['System'],
      responses: {
        '200': { description: 'Contact form submitted successfully' },
        '400': { description: 'Validation failed' },
        '429': { description: 'Too many requests' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/notes',
      method: 'GET',
      summary: 'Get User Notes',
      description: 'Retrieve all notes for the authenticated user',
      tags: ['Content Management'],
      security: [{ bearerAuth: [] }],
      responses: {
        '200': { description: 'Notes retrieved successfully' },
        '401': { description: 'Not authenticated' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/notes',
      method: 'POST',
      summary: 'Create New Note',
      description: 'Create a new note for the authenticated user',
      tags: ['Content Management'],
      security: [{ bearerAuth: [] }],
      responses: {
        '200': { description: 'Note created successfully' },
        '400': { description: 'Missing required fields' },
        '401': { description: 'Not authenticated' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/notes/{id}',
      method: 'GET',
      summary: 'Get Note by ID',
      description: 'Retrieve a specific note by its ID',
      tags: ['Content Management'],
      security: [{ bearerAuth: [] }],
      responses: {
        '200': { description: 'Note retrieved successfully' },
        '401': { description: 'Not authenticated' },
        '404': { description: 'Note not found' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/chat',
      method: 'POST',
      summary: 'Chat with AI',
      description: 'Send messages to the AI chat system powered by OpenAI',
      tags: ['AI Integration'],
      responses: {
        '200': { description: 'AI response generated successfully' },
        '400': { description: 'Invalid request' },
        '500': { description: 'Internal server error' }
      }
    },
    {
      path: '/api/notifications',
      method: 'GET',
      summary: 'Get Notifications',
      description: 'Retrieve user notifications',
      tags: ['System'],
      security: [{ bearerAuth: [] }],
      responses: {
        '200': { description: 'Notifications retrieved successfully' },
        '401': { description: 'Not authenticated' },
        '500': { description: 'Internal server error' }
      }
    }
  ];

  useEffect(() => {
    // Calculate API statistics
    const stats = {
      totalEndpoints: apiEndpoints.length,
      authenticatedEndpoints: apiEndpoints.filter(ep => ep.security).length,
      publicEndpoints: apiEndpoints.filter(ep => !ep.security).length,
      tags: Array.from(new Set(apiEndpoints.flatMap(ep => ep.tags)))
    };
    setApiStats(stats);
  }, []);

  const filteredEndpoints = apiEndpoints.filter(endpoint => {
    const matchesSearch = endpoint.path.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         endpoint.summary.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         endpoint.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    const matchesTag = selectedTag === 'all' || endpoint.tags.includes(selectedTag);
    
    const matchesAuth = !showOnlyAuthenticated || endpoint.security;
    
    return matchesSearch && matchesTag && matchesAuth;
  });

  const getMethodColor = (method: string) => {
    switch (method) {
      case 'GET': return 'bg-green-100 text-green-800 border-green-200';
      case 'POST': return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'PUT': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'DELETE': return 'bg-red-100 text-red-800 border-red-200';
      case 'PATCH': return 'bg-purple-100 text-purple-800 border-purple-200';
      default: return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTagColor = (tag: string) => {
    const colors = {
      'Authentication': 'bg-red-100 text-red-800',
      'User Management': 'bg-blue-100 text-blue-800',
      'Content Management': 'bg-green-100 text-green-800',
      'AI Integration': 'bg-purple-100 text-purple-800',
      'System': 'bg-gray-100 text-gray-800',
      'Real-time Features': 'bg-orange-100 text-orange-800',
      'Analytics': 'bg-indigo-100 text-indigo-800',
      'Security': 'bg-pink-100 text-pink-800'
    };
    return colors[tag as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  const copyToClipboard = async (text: string, type: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedEndpoint(type);
      toast.success(`${type} copied to clipboard!`);
      setTimeout(() => setCopiedEndpoint(null), 2000);
    } catch (err) {
      toast.error('Failed to copy to clipboard');
    }
  };

  const generateCurlExample = (endpoint: ApiEndpoint) => {
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://api.blatam-academy.com' 
      : 'http://localhost:3000';
    
    let curl = `curl -X ${endpoint.method} "${baseUrl}${endpoint.path}"`;
    
    if (endpoint.security) {
      curl += ` \\\n  -H "Authorization: Bearer YOUR_JWT_TOKEN"`;
    }
    
    if (endpoint.method === 'POST' || endpoint.method === 'PUT') {
      curl += ` \\\n  -H "Content-Type: application/json"`;
      curl += ` \\\n  -d '{"example": "data"}'`;
    }
    
    return curl;
  };

  const generateJavaScriptExample = (endpoint: ApiEndpoint) => {
    const baseUrl = process.env.NODE_ENV === 'production' 
      ? 'https://api.blatam-academy.com' 
      : 'http://localhost:3000';
    
    let js = `const response = await fetch('${baseUrl}${endpoint.path}', {\n`;
    js += `  method: '${endpoint.method}',\n`;
    
    if (endpoint.security) {
      js += `  headers: {\n`;
      js += `    'Authorization': 'Bearer YOUR_JWT_TOKEN',\n`;
      if (endpoint.method === 'POST' || endpoint.method === 'PUT') {
        js += `    'Content-Type': 'application/json',\n`;
      }
      js += `  },\n`;
    } else if (endpoint.method === 'POST' || endpoint.method === 'PUT') {
      js += `  headers: {\n`;
      js += `    'Content-Type': 'application/json',\n`;
      js += `  },\n`;
    }
    
    if (endpoint.method === 'POST' || endpoint.method === 'PUT') {
      js += `  body: JSON.stringify({\n`;
      js += `    // Your data here\n`;
      js += `  }),\n`;
    }
    
    js += `});\n\n`;
    js += `const data = await response.json();\n`;
    js += `console.log(data);`;
    
    return js;
  };

  const testEndpoint = async (endpoint: ApiEndpoint) => {
    setIsLoading(true);
    try {
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? 'https://api.blatam-academy.com' 
        : 'http://localhost:3000';
      
      const response = await fetch(`${baseUrl}${endpoint.path}`, {
        method: endpoint.method,
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      const data = await response.json();
      
      if (response.ok) {
        toast.success(`✅ ${endpoint.method} ${endpoint.path} - ${response.status}`);
      } else {
        toast.error(`❌ ${endpoint.method} ${endpoint.path} - ${response.status}`);
      }
      
      console.log('API Response:', data);
    } catch (error) {
      toast.error(`❌ Error testing ${endpoint.method} ${endpoint.path}`);
      console.error('API Test Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">API Documentation</h2>
          <p className="text-muted-foreground">
            Comprehensive API documentation for Blatam Academy platform
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export OpenAPI
          </Button>
          <Button variant="outline" size="sm">
            <ExternalLink className="h-4 w-4 mr-2" />
            View Swagger UI
          </Button>
        </div>
      </div>

      {/* API Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Endpoints</CardTitle>
            <Server className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiStats.totalEndpoints}</div>
            <p className="text-xs text-muted-foreground">
              Available API endpoints
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Authenticated</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiStats.authenticatedEndpoints}</div>
            <p className="text-xs text-muted-foreground">
              Require authentication
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Public</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiStats.publicEndpoints}</div>
            <p className="text-xs text-muted-foreground">
              Publicly accessible
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Categories</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{apiStats.tags.length}</div>
            <p className="text-xs text-muted-foreground">
              API categories
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Search & Filter
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <Label htmlFor="search">Search endpoints</Label>
              <Input
                id="search"
                placeholder="Search by path, summary, or description..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="mt-1"
              />
            </div>
            <div className="sm:w-48">
              <Label htmlFor="tag-filter">Filter by category</Label>
              <select
                id="tag-filter"
                value={selectedTag}
                onChange={(e) => setSelectedTag(e.target.value)}
                className="mt-1 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              >
                <option value="all">All Categories</option>
                {apiStats.tags.map(tag => (
                  <option key={tag} value={tag}>{tag}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Switch
              id="auth-filter"
              checked={showOnlyAuthenticated}
              onCheckedChange={setShowOnlyAuthenticated}
            />
            <Label htmlFor="auth-filter">Show only authenticated endpoints</Label>
          </div>
        </CardContent>
      </Card>

      {/* API Endpoints */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">
            API Endpoints ({filteredEndpoints.length})
          </h3>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSearchQuery('');
              setSelectedTag('all');
              setShowOnlyAuthenticated(false);
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Clear Filters
          </Button>
        </div>

        {filteredEndpoints.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-muted-foreground">No endpoints found matching your criteria.</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredEndpoints.map((endpoint, index) => (
              <Card key={`${endpoint.method}-${endpoint.path}-${index}`}>
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Badge className={getMethodColor(endpoint.method)}>
                          {endpoint.method}
                        </Badge>
                        <code className="text-sm font-mono bg-muted px-2 py-1 rounded">
                          {endpoint.path}
                        </code>
                        {endpoint.security && (
                          <Badge variant="outline" className="text-xs">
                            <Shield className="h-3 w-3 mr-1" />
                            Auth Required
                          </Badge>
                        )}
                      </div>
                      <CardTitle className="text-lg">{endpoint.summary}</CardTitle>
                      <CardDescription>{endpoint.description}</CardDescription>
                      <div className="flex flex-wrap gap-1">
                        {endpoint.tags.map(tag => (
                          <Badge key={tag} variant="secondary" className={getTagColor(tag)}>
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => testEndpoint(endpoint)}
                        disabled={isLoading}
                      >
                        <Play className="h-4 w-4 mr-2" />
                        Test
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="responses" className="w-full">
                    <TabsList className="grid w-full grid-cols-4">
                      <TabsTrigger value="responses">Responses</TabsTrigger>
                      <TabsTrigger value="curl">cURL</TabsTrigger>
                      <TabsTrigger value="javascript">JavaScript</TabsTrigger>
                      <TabsTrigger value="typescript">TypeScript</TabsTrigger>
                    </TabsList>
                    
                    <TabsContent value="responses" className="space-y-2">
                      <h4 className="font-medium">Response Codes</h4>
                      <div className="space-y-2">
                        {Object.entries(endpoint.responses).map(([code, response]: [string, any]) => (
                          <div key={code} className="flex items-center justify-between p-2 bg-muted rounded">
                            <div className="flex items-center gap-2">
                              <Badge variant={code.startsWith('2') ? 'default' : 'destructive'}>
                                {code}
                              </Badge>
                              <span className="text-sm">{response.description}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                    
                    <TabsContent value="curl" className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">cURL Example</h4>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(generateCurlExample(endpoint), 'cURL')}
                        >
                          {copiedEndpoint === 'cURL' ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                        <code>{generateCurlExample(endpoint)}</code>
                      </pre>
                    </TabsContent>
                    
                    <TabsContent value="javascript" className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">JavaScript Example</h4>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(generateJavaScriptExample(endpoint), 'JavaScript')}
                        >
                          {copiedEndpoint === 'JavaScript' ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                        <code>{generateJavaScriptExample(endpoint)}</code>
                      </pre>
                    </TabsContent>
                    
                    <TabsContent value="typescript" className="space-y-2">
                      <div className="flex items-center justify-between">
                        <h4 className="font-medium">TypeScript Example</h4>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => copyToClipboard(generateJavaScriptExample(endpoint), 'TypeScript')}
                        >
                          {copiedEndpoint === 'TypeScript' ? (
                            <Check className="h-4 w-4" />
                          ) : (
                            <Copy className="h-4 w-4" />
                          )}
                        </Button>
                      </div>
                      <pre className="bg-muted p-4 rounded-lg text-sm overflow-x-auto">
                        <code>{generateJavaScriptExample(endpoint)}</code>
                      </pre>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Quick Start Guide */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BookOpen className="h-5 w-5" />
            Quick Start Guide
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h4 className="font-medium">Authentication</h4>
              <p className="text-sm text-muted-foreground">
                Most endpoints require authentication. Use NextAuth.js session tokens or JWT tokens.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Rate Limiting</h4>
              <p className="text-sm text-muted-foreground">
                API calls are rate limited. Check response headers for current limits.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Error Handling</h4>
              <p className="text-sm text-muted-foreground">
                All errors return consistent JSON responses with error codes and messages.
              </p>
            </div>
            <div className="space-y-2">
              <h4 className="font-medium">Base URL</h4>
              <p className="text-sm text-muted-foreground">
                Development: http://localhost:3000<br />
                Production: https://api.blatam-academy.com
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}


