'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Code, Shield, Lock, Activity, Target, CheckCircle, Copy, Download, RefreshCw, Lightbulb } from 'lucide-react';

export default function SecurityExamplesDemo() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Examples & Demos</h1>
          <p className="text-gray-600">Comprehensive security implementation examples and code samples</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Download All
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {['authentication', 'encryption', 'monitoring', 'testing', 'compliance', 'integration'].map((category) => (
          <Card key={category} className="cursor-pointer hover:shadow-md transition-shadow">
            <CardContent className="p-4 text-center">
              <Shield className="h-4 w-4 mx-auto" />
              <h3 className="font-medium mt-2 capitalize">{category}</h3>
              <p className="text-sm text-gray-500">3 examples</p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Security Examples</CardTitle>
              <CardDescription>Select an example to view implementation details</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="p-3 border rounded-lg cursor-pointer hover:shadow-md transition-shadow ring-2 ring-blue-500">
                  <div className="flex items-start space-x-3">
                    <Shield className="h-4 w-4 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-gray-900 truncate">Biometric Authentication Setup</h3>
                      <p className="text-sm text-gray-600 line-clamp-2">Implement WebAuthn biometric authentication</p>
                      <div className="flex items-center space-x-2 mt-2">
                        <Badge className="text-yellow-600 bg-yellow-100">intermediate</Badge>
                        <Badge variant="outline">typescript</Badge>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="lg:col-span-2">
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle className="flex items-center space-x-2">
                      <Shield className="h-4 w-4" />
                      <span>Biometric Authentication Setup</span>
                    </CardTitle>
                    <CardDescription className="mt-2">Implement WebAuthn biometric authentication with fingerprint and face recognition</CardDescription>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge className="text-yellow-600 bg-yellow-100">intermediate</Badge>
                    <Badge variant="outline">typescript</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Use Cases</h4>
                    <div className="flex flex-wrap gap-2">
                      <Badge variant="outline">Secure user authentication</Badge>
                      <Badge variant="outline">Passwordless login</Badge>
                      <Badge variant="outline">Multi-factor authentication</Badge>
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Prerequisites</h4>
                    <ul className="text-sm text-gray-600 space-y-1">
                      <li className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        HTTPS enabled
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        WebAuthn compatible browser
                      </li>
                      <li className="flex items-start">
                        <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                        Biometric device
                      </li>
                    </ul>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center space-x-2">
                    <Code className="h-5 w-5" />
                    <span>Implementation Code</span>
                  </CardTitle>
                  <Button size="sm" variant="outline">
                    <Copy className="h-4 w-4 mr-2" />
                    Copy Code
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto text-sm">
                  <code>{`// Biometric Authentication Example
import { WebAuthnService } from '@/lib/security/biometric-auth';

const webauthn = new WebAuthnService({
  rpId: 'localhost',
  rpName: 'Blatam Academy',
  origin: 'https://localhost:3000'
});

async function registerBiometric(userId: string, username: string) {
  try {
    const credential = await webauthn.createCredential({
      userId: userId,
      username: username,
      displayName: username,
      attestation: 'direct'
    });
    
    await fetch('/api/auth/biometric/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, credential })
    });
    
    console.log('Biometric credential registered successfully');
  } catch (error) {
    console.error('Biometric registration failed:', error);
  }
}`}</code>
                </pre>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Lightbulb className="h-5 w-5" />
                  <span>Explanation</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700 leading-relaxed">
                  This example demonstrates how to implement WebAuthn biometric authentication. It includes credential registration and authentication flows using the WebAuthn API for secure, passwordless authentication.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}