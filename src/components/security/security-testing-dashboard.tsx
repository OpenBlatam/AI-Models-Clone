'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Shield, 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Clock, 
  Play, 
  RefreshCw,
  BarChart3,
  TestTube,
  Lock,
  Eye,
  Zap,
  FileText,
  Settings
} from 'lucide-react';

interface SecurityTestResult {
  testId: string;
  status: 'pass' | 'fail' | 'warning' | 'error' | 'skipped';
  score: number;
  message: string;
  details: string;
  duration: number;
  timestamp: Date;
  evidence: string[];
  recommendations: string[];
  metadata: Record<string, any>;
}

interface SecurityTestSummary {
  total: number;
  passed: number;
  failed: number;
  warnings: number;
  errors: number;
  skipped: number;
  overallScore: number;
  duration: number;
  categories: Record<string, { total: number; passed: number; failed: number; score: number }>;
  criticalIssues: string[];
  recommendations: string[];
}

interface SecurityTest {
  id: string;
  name: string;
  description: string;
  category: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  tags: string[];
}

export default function SecurityTestingDashboard() {
  const [testResults, setTestResults] = useState<SecurityTestResult[]>([]);
  const [testSummary, setTestSummary] = useState<SecurityTestSummary | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedTest, setSelectedTest] = useState<string | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [refreshInterval, setRefreshInterval] = useState(30);

  // Mock test data
  const mockTests: SecurityTest[] = [
    {
      id: 'auth-001',
      name: 'JWT Token Validation',
      description: 'Test JWT token validation and expiration',
      category: 'authentication',
      severity: 'high',
      tags: ['jwt', 'token', 'authentication'],
    },
    {
      id: 'auth-002',
      name: 'Password Strength Validation',
      description: 'Test password strength requirements',
      category: 'authentication',
      severity: 'medium',
      tags: ['password', 'strength', 'validation'],
    },
    {
      id: 'auth-003',
      name: 'Multi-Factor Authentication',
      description: 'Test MFA implementation and validation',
      category: 'authentication',
      severity: 'high',
      tags: ['mfa', '2fa', 'authentication'],
    },
    {
      id: 'authz-001',
      name: 'Role-Based Access Control',
      description: 'Test RBAC implementation and enforcement',
      category: 'authorization',
      severity: 'high',
      tags: ['rbac', 'roles', 'permissions'],
    },
    {
      id: 'authz-002',
      name: 'API Endpoint Authorization',
      description: 'Test API endpoint access control',
      category: 'authorization',
      severity: 'critical',
      tags: ['api', 'endpoints', 'authorization'],
    },
    {
      id: 'input-001',
      name: 'SQL Injection Prevention',
      description: 'Test SQL injection attack prevention',
      category: 'input_validation',
      severity: 'critical',
      tags: ['sql', 'injection', 'prevention'],
    },
    {
      id: 'input-002',
      name: 'XSS Prevention',
      description: 'Test cross-site scripting prevention',
      category: 'input_validation',
      severity: 'high',
      tags: ['xss', 'prevention', 'validation'],
    },
    {
      id: 'rate-001',
      name: 'API Rate Limiting',
      description: 'Test API rate limiting implementation',
      category: 'rate_limiting',
      severity: 'medium',
      tags: ['rate', 'limiting', 'api'],
    },
    {
      id: 'encrypt-001',
      name: 'Data Encryption at Rest',
      description: 'Test data encryption at rest implementation',
      category: 'encryption',
      severity: 'critical',
      tags: ['encryption', 'data', 'rest'],
    },
    {
      id: 'encrypt-002',
      name: 'Data Encryption in Transit',
      description: 'Test data encryption in transit (TLS/SSL)',
      category: 'encryption',
      severity: 'critical',
      tags: ['encryption', 'tls', 'ssl', 'transit'],
    },
  ];

  const mockResults: SecurityTestResult[] = [
    {
      testId: 'auth-001',
      status: 'pass',
      score: 100,
      message: 'JWT validation working correctly',
      details: 'Token structure and signature validation passed',
      duration: 150,
      timestamp: new Date(),
      evidence: ['valid_token_format', 'signature_verified'],
      recommendations: [],
      metadata: { tokenLength: 200 },
    },
    {
      testId: 'auth-002',
      status: 'pass',
      score: 100,
      message: 'Password strength validation working correctly',
      details: 'Weak passwords blocked, strong passwords accepted',
      duration: 200,
      timestamp: new Date(),
      evidence: ['weak_passwords_blocked', 'strong_passwords_accepted'],
      recommendations: [],
      metadata: { weakDetected: 3, strongAccepted: 2 },
    },
    {
      testId: 'auth-003',
      status: 'warning',
      score: 75,
      message: 'MFA implementation needs improvement',
      details: 'MFA enabled but validation could be stronger',
      duration: 300,
      timestamp: new Date(),
      evidence: ['mfa_enabled', 'validation_weak'],
      recommendations: ['Strengthen MFA validation', 'Add backup codes'],
      metadata: { mfaEnabled: true, mfaValidation: false },
    },
    {
      testId: 'authz-001',
      status: 'pass',
      score: 100,
      message: 'RBAC implementation working correctly',
      details: 'Role-based access control properly implemented',
      duration: 180,
      timestamp: new Date(),
      evidence: ['rbac_implemented', 'roles_defined', 'permissions_enforced'],
      recommendations: [],
      metadata: {},
    },
    {
      testId: 'authz-002',
      status: 'fail',
      score: 0,
      message: 'API endpoint authorization failed',
      details: 'Some API endpoints are not properly protected',
      duration: 250,
      timestamp: new Date(),
      evidence: ['endpoints_unprotected'],
      recommendations: ['Secure unprotected endpoints', 'Implement proper authorization'],
      metadata: { unprotectedEndpoints: 2 },
    },
    {
      testId: 'input-001',
      status: 'pass',
      score: 100,
      message: 'SQL injection prevention working correctly',
      details: 'SQL injection attacks properly blocked',
      duration: 120,
      timestamp: new Date(),
      evidence: ['sql_injection_blocked', 'parameterized_queries'],
      recommendations: [],
      metadata: {},
    },
    {
      testId: 'input-002',
      status: 'pass',
      score: 100,
      message: 'XSS prevention working correctly',
      details: 'Cross-site scripting attacks properly prevented',
      duration: 140,
      timestamp: new Date(),
      evidence: ['xss_prevented', 'input_sanitized'],
      recommendations: [],
      metadata: {},
    },
    {
      testId: 'rate-001',
      status: 'pass',
      score: 100,
      message: 'API rate limiting working correctly',
      details: 'API rate limiting properly implemented',
      duration: 160,
      timestamp: new Date(),
      evidence: ['rate_limits_enforced', 'throttling_working'],
      recommendations: [],
      metadata: {},
    },
    {
      testId: 'encrypt-001',
      status: 'pass',
      score: 100,
      message: 'Data encryption at rest working correctly',
      details: 'Data properly encrypted at rest',
      duration: 220,
      timestamp: new Date(),
      evidence: ['data_encrypted', 'encryption_keys_managed'],
      recommendations: [],
      metadata: {},
    },
    {
      testId: 'encrypt-002',
      status: 'pass',
      score: 100,
      message: 'Data encryption in transit working correctly',
      details: 'Data properly encrypted in transit',
      duration: 190,
      timestamp: new Date(),
      evidence: ['tls_enabled', 'ssl_certificates_valid'],
      recommendations: [],
      metadata: {},
    },
  ];

  const mockSummary: SecurityTestSummary = {
    total: 10,
    passed: 8,
    failed: 1,
    warnings: 1,
    errors: 0,
    skipped: 0,
    overallScore: 87.5,
    duration: 1910,
    categories: {
      authentication: { total: 3, passed: 2, failed: 0, score: 83.3 },
      authorization: { total: 2, passed: 1, failed: 1, score: 50.0 },
      input_validation: { total: 2, passed: 2, failed: 0, score: 100.0 },
      rate_limiting: { total: 1, passed: 1, failed: 0, score: 100.0 },
      encryption: { total: 2, passed: 2, failed: 0, score: 100.0 },
    },
    criticalIssues: ['API endpoint authorization failed'],
    recommendations: ['Strengthen MFA validation', 'Add backup codes', 'Secure unprotected endpoints', 'Implement proper authorization'],
  };

  useEffect(() => {
    setTestResults(mockResults);
    setTestSummary(mockSummary);
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(() => {
        runTests();
      }, refreshInterval * 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, refreshInterval]);

  const runTests = async () => {
    setIsRunning(true);
    // Simulate test execution
    await new Promise(resolve => setTimeout(resolve, 2000));
    setIsRunning(false);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pass':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'fail':
        return <XCircle className="h-5 w-5 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Clock className="h-5 w-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass':
        return 'text-green-600 bg-green-50';
      case 'fail':
        return 'text-red-600 bg-red-50';
      case 'warning':
        return 'text-yellow-600 bg-yellow-50';
      case 'error':
        return 'text-red-700 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'text-red-600 bg-red-50';
      case 'high':
        return 'text-orange-600 bg-orange-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'low':
        return 'text-green-600 bg-green-50';
      default:
        return 'text-gray-600 bg-gray-50';
    }
  };

  const selectedTestResult = testResults.find(r => r.testId === selectedTest);
  const selectedTestInfo = mockTests.find(t => t.id === selectedTest);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Testing Dashboard</h1>
          <p className="text-gray-600">Comprehensive security testing and validation</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium">Auto-refresh:</label>
            <input
              type="checkbox"
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
              className="rounded"
            />
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium">Interval:</label>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-1 border rounded-md text-sm"
            >
              <option value={10}>10s</option>
              <option value={30}>30s</option>
              <option value={60}>1m</option>
              <option value={300}>5m</option>
            </select>
          </div>
          <button
            onClick={runTests}
            disabled={isRunning}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isRunning ? <RefreshCw className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
            <span>{isRunning ? 'Running...' : 'Run Tests'}</span>
          </button>
        </div>
      </div>

      {/* Summary Cards */}
      {testSummary && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Score</CardTitle>
              <BarChart3 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{testSummary.overallScore.toFixed(1)}%</div>
              <Progress value={testSummary.overallScore} className="mt-2" />
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tests Passed</CardTitle>
              <CheckCircle className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">{testSummary.passed}</div>
              <p className="text-xs text-muted-foreground">out of {testSummary.total} tests</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Tests Failed</CardTitle>
              <XCircle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{testSummary.failed}</div>
              <p className="text-xs text-muted-foreground">{testSummary.warnings} warnings</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Issues</CardTitle>
              <AlertTriangle className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">{testSummary.criticalIssues.length}</div>
              <p className="text-xs text-muted-foreground">require immediate attention</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Critical Issues Alert */}
      {testSummary && testSummary.criticalIssues.length > 0 && (
        <Alert className="border-red-200 bg-red-50">
          <AlertTriangle className="h-4 w-4 text-red-600" />
          <AlertDescription className="text-red-800">
            <strong>Critical Issues Detected:</strong>
            <ul className="mt-2 list-disc list-inside">
              {testSummary.criticalIssues.map((issue, index) => (
                <li key={index}>{issue}</li>
              ))}
            </ul>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content */}
      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="tests">Test Results</TabsTrigger>
          <TabsTrigger value="categories">Categories</TabsTrigger>
          <TabsTrigger value="details">Test Details</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Category Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Category Performance</CardTitle>
                <CardDescription>Security test results by category</CardDescription>
              </CardHeader>
              <CardContent>
                {testSummary && Object.entries(testSummary.categories).map(([category, data]) => (
                  <div key={category} className="mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium capitalize">{category.replace('_', ' ')}</span>
                      <span className="text-sm text-gray-600">{data.score.toFixed(1)}%</span>
                    </div>
                    <Progress value={data.score} className="h-2" />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>{data.passed}/{data.total} passed</span>
                      <span>{data.failed} failed</span>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle>Recommendations</CardTitle>
                <CardDescription>Security improvement suggestions</CardDescription>
              </CardHeader>
              <CardContent>
                {testSummary && testSummary.recommendations.length > 0 ? (
                  <ul className="space-y-2">
                    {testSummary.recommendations.map((recommendation, index) => (
                      <li key={index} className="flex items-start space-x-2">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mt-2 flex-shrink-0" />
                        <span className="text-sm">{recommendation}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 text-sm">No recommendations at this time.</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="tests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Results</CardTitle>
              <CardDescription>Detailed results for all security tests</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {testResults.map((result) => {
                  const testInfo = mockTests.find(t => t.id === result.testId);
                  return (
                    <div
                      key={result.testId}
                      className={`p-4 border rounded-lg cursor-pointer hover:bg-gray-50 ${
                        selectedTest === result.testId ? 'ring-2 ring-blue-500' : ''
                      }`}
                      onClick={() => setSelectedTest(result.testId)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          {getStatusIcon(result.status)}
                          <div>
                            <h3 className="font-medium">{testInfo?.name}</h3>
                            <p className="text-sm text-gray-600">{testInfo?.description}</p>
                          </div>
                        </div>
                        <div className="flex items-center space-x-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(testInfo?.severity || 'low')}`}>
                            {testInfo?.severity}
                          </span>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(result.status)}`}>
                            {result.status}
                          </span>
                          <span className="text-sm text-gray-600">{result.score}%</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="categories" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {testSummary && Object.entries(testSummary.categories).map(([category, data]) => (
              <Card key={category}>
                <CardHeader>
                  <CardTitle className="capitalize">{category.replace('_', ' ')}</CardTitle>
                  <CardDescription>
                    {data.total} tests • {data.passed} passed • {data.failed} failed
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm mb-1">
                        <span>Score</span>
                        <span>{data.score.toFixed(1)}%</span>
                      </div>
                      <Progress value={data.score} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-green-600 font-medium">{data.passed}</div>
                        <div className="text-gray-500">Passed</div>
                      </div>
                      <div>
                        <div className="text-red-600 font-medium">{data.failed}</div>
                        <div className="text-gray-500">Failed</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="details" className="space-y-4">
          {selectedTestResult && selectedTestInfo ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Test Information</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <h3 className="font-medium">{selectedTestInfo.name}</h3>
                    <p className="text-sm text-gray-600">{selectedTestInfo.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-sm text-gray-500">Category</div>
                      <div className="font-medium capitalize">{selectedTestInfo.category.replace('_', ' ')}</div>
                    </div>
                    <div>
                      <div className="text-sm text-gray-500">Severity</div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getSeverityColor(selectedTestInfo.severity)}`}>
                        {selectedTestInfo.severity}
                      </span>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Tags</div>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {selectedTestInfo.tags.map((tag, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Test Result</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(selectedTestResult.status)}
                    <div>
                      <div className="font-medium">{selectedTestResult.message}</div>
                      <div className="text-sm text-gray-600">Score: {selectedTestResult.score}%</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Details</div>
                    <div className="text-sm">{selectedTestResult.details}</div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Duration</div>
                    <div className="text-sm">{selectedTestResult.duration}ms</div>
                  </div>
                  {selectedTestResult.evidence.length > 0 && (
                    <div>
                      <div className="text-sm text-gray-500">Evidence</div>
                      <ul className="text-sm list-disc list-inside">
                        {selectedTestResult.evidence.map((evidence, index) => (
                          <li key={index}>{evidence}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedTestResult.recommendations.length > 0 && (
                    <div>
                      <div className="text-sm text-gray-500">Recommendations</div>
                      <ul className="text-sm list-disc list-inside">
                        {selectedTestResult.recommendations.map((recommendation, index) => (
                          <li key={index}>{recommendation}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          ) : (
            <Card>
              <CardContent className="py-12 text-center">
                <TestTube className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a Test</h3>
                <p className="text-gray-600">Choose a test from the Test Results tab to view detailed information.</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}