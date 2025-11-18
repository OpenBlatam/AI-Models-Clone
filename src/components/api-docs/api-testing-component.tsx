'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Play, 
  Copy, 
  Check, 
  Download, 
  Settings,
  Code,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { documentationService, ApiEndpoint } from '@/lib/api-docs/documentation-service';

interface ApiTestResult {
  status: number;
  statusText: string;
  headers: Record<string, string>;
  data: any;
  duration: number;
  timestamp: Date;
  error?: string;
}

interface ApiTestingComponentProps {
  endpoint?: ApiEndpoint;
  className?: string;
}

export function ApiTestingComponent({ endpoint, className }: ApiTestingComponentProps) {
  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint | null>(endpoint || null);
  const [requestBody, setRequestBody] = useState('{\n  "example": "data"\n}');
  const [headers, setHeaders] = useState('{\n  "Content-Type": "application/json"\n}');
  const [authToken, setAuthToken] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [testResults, setTestResults] = useState<ApiTestResult[]>([]);
  const [copiedResult, setCopiedResult] = useState<string | null>(null);
  const [availableEndpoints, setAvailableEndpoints] = useState<ApiEndpoint[]>([]);

  useEffect(() => {
    // Load available endpoints
    const metrics = documentationService.getDocumentationMetrics();
    const endpoints: ApiEndpoint[] = [];
    
    // Extract endpoints from OpenAPI spec
    const openApiSpec = documentationService.getOpenApiSpec();
    Object.entries(openApiSpec.paths).forEach(([path, pathItem]) => {
      Object.entries(pathItem).forEach(([method, operation]) => {
        if (typeof operation === 'object' && operation !== null) {
          endpoints.push({
            path,
            method: method.toUpperCase() as any,
            summary: operation.summary || '',
            description: operation.description || '',
            tags: operation.tags || [],
            parameters: operation.parameters,
            requestBody: operation.requestBody,
            responses: operation.responses || {},
            security: operation.security,
            deprecated: operation.deprecated || false,
            operationId: operation.operationId,
          });
        }
      });
    });
    
    setAvailableEndpoints(endpoints);
    if (!selectedEndpoint && endpoints.length > 0) {
      setSelectedEndpoint(endpoints[0]);
    }
  }, []);

  const testEndpoint = async () => {
    if (!selectedEndpoint) return;

    setIsLoading(true);
    const startTime = Date.now();

    try {
      const baseUrl = process.env.NODE_ENV === 'production' 
        ? 'https://api.blatam-academy.com' 
        : 'http://localhost:3000';

      const url = `${baseUrl}${selectedEndpoint.path}`;
      
      // Parse headers
      let parsedHeaders: Record<string, string> = {};
      try {
        parsedHeaders = JSON.parse(headers);
      } catch (e) {
        toast.error('Invalid headers JSON');
        return;
      }

      // Add authentication if provided
      if (authToken) {
        parsedHeaders['Authorization'] = `Bearer ${authToken}`;
      }

      // Parse request body
      let body: string | undefined;
      if (selectedEndpoint.method === 'POST' || selectedEndpoint.method === 'PUT' || selectedEndpoint.method === 'PATCH') {
        try {
          JSON.parse(requestBody);
          body = requestBody;
        } catch (e) {
          toast.error('Invalid request body JSON');
          return;
        }
      }

      const response = await fetch(url, {
        method: selectedEndpoint.method,
        headers: parsedHeaders,
        body,
      });

      const duration = Date.now() - startTime;
      const responseData = await response.text();
      
      let parsedData: any;
      try {
        parsedData = JSON.parse(responseData);
      } catch (e) {
        parsedData = responseData;
      }

      const result: ApiTestResult = {
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
        data: parsedData,
        duration,
        timestamp: new Date(),
      };

      setTestResults(prev => [result, ...prev.slice(0, 9)]); // Keep last 10 results

      if (response.ok) {
        toast.success(`✅ ${selectedEndpoint.method} ${selectedEndpoint.path} - ${response.status}`);
      } else {
        toast.error(`❌ ${selectedEndpoint.method} ${selectedEndpoint.path} - ${response.status}`);
      }

    } catch (error) {
      const duration = Date.now() - startTime;
      const result: ApiTestResult = {
        status: 0,
        statusText: 'Network Error',
        headers: {},
        data: null,
        duration,
        timestamp: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };

      setTestResults(prev => [result, ...prev.slice(0, 9)]);
      toast.error(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setIsLoading(false);
    }
  };

  const copyResult = async (result: ApiTestResult) => {
    const resultText = JSON.stringify(result, null, 2);
    try {
      await navigator.clipboard.writeText(resultText);
      setCopiedResult(result.timestamp.toISOString());
      toast.success('Result copied to clipboard!');
      setTimeout(() => setCopiedResult(null), 2000);
    } catch (err) {
      toast.error('Failed to copy result');
    }
  };

  const exportResults = () => {
    const exportData = {
      endpoint: selectedEndpoint,
      timestamp: new Date().toISOString(),
      results: testResults,
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `api-test-results-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    toast.success('Test results exported!');
  };

  const getStatusIcon = (status: number) => {
    if (status >= 200 && status < 300) {
      return <CheckCircle className="h-4 w-4 text-green-500" />;
    } else if (status >= 400 && status < 500) {
      return <AlertCircle className="h-4 w-4 text-yellow-500" />;
    } else if (status >= 500) {
      return <XCircle className="h-4 w-4 text-red-500" />;
    } else {
      return <XCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: number) => {
    if (status >= 200 && status < 300) {
      return 'bg-green-100 text-green-800 border-green-200';
    } else if (status >= 400 && status < 500) {
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    } else if (status >= 500) {
      return 'bg-red-100 text-red-800 border-red-200';
    } else {
      return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">API Testing</h2>
          <p className="text-muted-foreground">
            Test API endpoints with real requests and view responses
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={exportResults} disabled={testResults.length === 0}>
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Request Configuration */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5" />
                Request Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Endpoint Selection */}
              <div className="space-y-2">
                <Label htmlFor="endpoint-select">Select Endpoint</Label>
                <select
                  id="endpoint-select"
                  value={selectedEndpoint ? `${selectedEndpoint.method} ${selectedEndpoint.path}` : ''}
                  onChange={(e) => {
                    const [method, ...pathParts] = e.target.value.split(' ');
                    const path = pathParts.join(' ');
                    const endpoint = availableEndpoints.find(ep => ep.method === method && ep.path === path);
                    setSelectedEndpoint(endpoint || null);
                  }}
                  className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                >
                  <option value="">Select an endpoint...</option>
                  {availableEndpoints.map((ep, index) => (
                    <option key={index} value={`${ep.method} ${ep.path}`}>
                      {ep.method} {ep.path} - {ep.summary}
                    </option>
                  ))}
                </select>
              </div>

              {selectedEndpoint && (
                <>
                  {/* Endpoint Info */}
                  <div className="p-3 bg-muted rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                        {selectedEndpoint.method}
                      </Badge>
                      <code className="text-sm font-mono">{selectedEndpoint.path}</code>
                    </div>
                    <p className="text-sm text-muted-foreground">{selectedEndpoint.description}</p>
                    {selectedEndpoint.security && (
                      <Badge variant="outline" className="mt-2 text-xs">
                        🔒 Authentication Required
                      </Badge>
                    )}
                  </div>

                  {/* Authentication */}
                  <div className="space-y-2">
                    <Label htmlFor="auth-token">Authentication Token (Optional)</Label>
                    <Input
                      id="auth-token"
                      type="password"
                      placeholder="Bearer token or JWT"
                      value={authToken}
                      onChange={(e) => setAuthToken(e.target.value)}
                    />
                  </div>

                  {/* Headers */}
                  <div className="space-y-2">
                    <Label htmlFor="headers">Headers (JSON)</Label>
                    <textarea
                      id="headers"
                      className="w-full min-h-[100px] rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                      value={headers}
                      onChange={(e) => setHeaders(e.target.value)}
                      placeholder='{\n  "Content-Type": "application/json"\n}'
                    />
                  </div>

                  {/* Request Body */}
                  {(selectedEndpoint.method === 'POST' || selectedEndpoint.method === 'PUT' || selectedEndpoint.method === 'PATCH') && (
                    <div className="space-y-2">
                      <Label htmlFor="request-body">Request Body (JSON)</Label>
                      <textarea
                        id="request-body"
                        className="w-full min-h-[150px] rounded-md border border-input bg-background px-3 py-2 text-sm font-mono"
                        value={requestBody}
                        onChange={(e) => setRequestBody(e.target.value)}
                        placeholder='{\n  "example": "data"\n}'
                      />
                    </div>
                  )}

                  {/* Test Button */}
                  <Button 
                    onClick={testEndpoint} 
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isLoading ? (
                      <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    ) : (
                      <Play className="h-4 w-4 mr-2" />
                    )}
                    {isLoading ? 'Testing...' : 'Test Endpoint'}
                  </Button>
                </>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Test Results */}
        <div className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Code className="h-5 w-5" />
                Test Results
                {testResults.length > 0 && (
                  <Badge variant="secondary">{testResults.length}</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {testResults.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Play className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No test results yet. Run a test to see results here.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {testResults.map((result, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-2">
                          {getStatusIcon(result.status)}
                          <Badge className={getStatusColor(result.status)}>
                            {result.status} {result.statusText}
                          </Badge>
                          <span className="text-sm text-muted-foreground">
                            {result.duration}ms
                          </span>
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">
                            {result.timestamp.toLocaleTimeString()}
                          </span>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => copyResult(result)}
                          >
                            {copiedResult === result.timestamp.toISOString() ? (
                              <Check className="h-3 w-3" />
                            ) : (
                              <Copy className="h-3 w-3" />
                            )}
                          </Button>
                        </div>
                      </div>

                      <Tabs defaultValue="response" className="w-full">
                        <TabsList className="grid w-full grid-cols-3">
                          <TabsTrigger value="response">Response</TabsTrigger>
                          <TabsTrigger value="headers">Headers</TabsTrigger>
                          <TabsTrigger value="raw">Raw</TabsTrigger>
                        </TabsList>
                        
                        <TabsContent value="response" className="space-y-2">
                          <pre className="bg-muted p-3 rounded text-sm overflow-x-auto max-h-64">
                            <code>{JSON.stringify(result.data, null, 2)}</code>
                          </pre>
                        </TabsContent>
                        
                        <TabsContent value="headers" className="space-y-2">
                          <pre className="bg-muted p-3 rounded text-sm overflow-x-auto max-h-64">
                            <code>{JSON.stringify(result.headers, null, 2)}</code>
                          </pre>
                        </TabsContent>
                        
                        <TabsContent value="raw" className="space-y-2">
                          <pre className="bg-muted p-3 rounded text-sm overflow-x-auto max-h-64">
                            <code>{JSON.stringify(result, null, 2)}</code>
                          </pre>
                        </TabsContent>
                      </Tabs>

                      {result.error && (
                        <Alert className="mt-3">
                          <AlertCircle className="h-4 w-4" />
                          <AlertDescription>{result.error}</AlertDescription>
                        </Alert>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}


