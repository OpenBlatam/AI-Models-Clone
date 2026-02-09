'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  Square, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  Shield,
  Target,
  Zap,
  Brain,
  Lock,
  Eye,
  Activity,
  Settings,
  Download,
  RefreshCw,
  Clock,
  BarChart3,
  TrendingUp,
  Users,
  Globe,
  Database,
  Server,
  Network,
  Code,
  Bug,
  Search,
  Filter
} from 'lucide-react';

interface SecurityTest {
  id: string;
  name: string;
  description: string;
  category: 'vulnerability' | 'penetration' | 'compliance' | 'performance' | 'integration';
  severity: 'low' | 'medium' | 'high' | 'critical';
  status: 'pending' | 'running' | 'completed' | 'failed' | 'paused';
  progress: number;
  duration: number;
  results: {
    passed: number;
    failed: number;
    warnings: number;
    total: number;
  };
  findings: Array<{
    id: string;
    title: string;
    description: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    status: 'open' | 'fixed' | 'ignored';
    recommendation: string;
  }>;
  createdAt: number;
  startedAt?: number;
  completedAt?: number;
}

interface TestSuite {
  id: string;
  name: string;
  description: string;
  tests: string[];
  status: 'idle' | 'running' | 'completed' | 'failed';
  progress: number;
  createdAt: number;
  lastRun?: number;
}

interface TestResult {
  testId: string;
  testName: string;
  status: 'passed' | 'failed' | 'warning';
  score: number;
  details: string;
  recommendations: string[];
  timestamp: number;
}

export default function AdvancedSecurityTesting() {
  const [tests, setTests] = useState<SecurityTest[]>([]);
  const [testSuites, setTestSuites] = useState<TestSuite[]>([]);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [runningTests, setRunningTests] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTest, setSelectedTest] = useState<SecurityTest | null>(null);
  const [selectedSuite, setSelectedSuite] = useState<TestSuite | null>(null);

  useEffect(() => {
    fetchTestData();
  }, []);

  const fetchTestData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Generate mock test data
      const mockTests: SecurityTest[] = [
        {
          id: '1',
          name: 'SQL Injection Testing',
          description: 'Comprehensive SQL injection vulnerability assessment',
          category: 'vulnerability',
          severity: 'high',
          status: 'completed',
          progress: 100,
          duration: 300,
          results: { passed: 15, failed: 3, warnings: 2, total: 20 },
          findings: [
            {
              id: 'f1',
              title: 'SQL Injection in Login Form',
              description: 'Login form vulnerable to SQL injection attacks',
              severity: 'critical',
              status: 'open',
              recommendation: 'Implement parameterized queries and input validation'
            },
            {
              id: 'f2',
              title: 'Weak Password Policy',
              description: 'Password requirements are not enforced',
              severity: 'medium',
              status: 'open',
              recommendation: 'Implement strong password policy with complexity requirements'
            }
          ],
          createdAt: Date.now() - 3600000,
          startedAt: Date.now() - 3600000,
          completedAt: Date.now() - 3300000
        },
        {
          id: '2',
          name: 'XSS Vulnerability Scan',
          description: 'Cross-site scripting vulnerability detection',
          category: 'vulnerability',
          severity: 'medium',
          status: 'running',
          progress: 65,
          duration: 180,
          results: { passed: 8, failed: 1, warnings: 1, total: 10 },
          findings: [],
          createdAt: Date.now() - 1800000,
          startedAt: Date.now() - 1800000
        },
        {
          id: '3',
          name: 'Authentication Bypass Testing',
          description: 'Test authentication mechanisms for bypass vulnerabilities',
          category: 'penetration',
          severity: 'critical',
          status: 'pending',
          progress: 0,
          duration: 240,
          results: { passed: 0, failed: 0, warnings: 0, total: 12 },
          findings: [],
          createdAt: Date.now() - 900000
        },
        {
          id: '4',
          name: 'API Security Assessment',
          description: 'Comprehensive API security testing',
          category: 'integration',
          severity: 'high',
          status: 'completed',
          progress: 100,
          duration: 420,
          results: { passed: 25, failed: 2, warnings: 3, total: 30 },
          findings: [
            {
              id: 'f3',
              title: 'Missing Rate Limiting',
              description: 'API endpoints lack rate limiting protection',
              severity: 'high',
              status: 'open',
              recommendation: 'Implement rate limiting for all API endpoints'
            }
          ],
          createdAt: Date.now() - 7200000,
          startedAt: Date.now() - 7200000,
          completedAt: Date.now() - 6780000
        },
        {
          id: '5',
          name: 'Performance Security Testing',
          description: 'Security performance under load testing',
          category: 'performance',
          severity: 'medium',
          status: 'failed',
          progress: 45,
          duration: 600,
          results: { passed: 5, failed: 8, warnings: 2, total: 15 },
          findings: [
            {
              id: 'f4',
              title: 'Memory Leak in Security Module',
              description: 'Security module shows memory leak under load',
              severity: 'high',
              status: 'open',
              recommendation: 'Fix memory leak and implement proper resource cleanup'
            }
          ],
          createdAt: Date.now() - 10800000,
          startedAt: Date.now() - 10800000,
          completedAt: Date.now() - 10200000
        }
      ];

      const mockTestSuites: TestSuite[] = [
        {
          id: 'suite1',
          name: 'Complete Security Suite',
          description: 'Comprehensive security testing suite',
          tests: ['1', '2', '3', '4', '5'],
          status: 'idle',
          progress: 0,
          createdAt: Date.now() - 86400000,
          lastRun: Date.now() - 3600000
        },
        {
          id: 'suite2',
          name: 'Vulnerability Assessment',
          description: 'Focused vulnerability testing suite',
          tests: ['1', '2'],
          status: 'running',
          progress: 75,
          createdAt: Date.now() - 172800000,
          lastRun: Date.now() - 1800000
        },
        {
          id: 'suite3',
          name: 'API Security Suite',
          description: 'API-specific security testing',
          tests: ['4'],
          status: 'completed',
          progress: 100,
          createdAt: Date.now() - 259200000,
          lastRun: Date.now() - 7200000
        }
      ];

      const mockTestResults: TestResult[] = [
        {
          testId: '1',
          testName: 'SQL Injection Testing',
          status: 'failed',
          score: 75,
          details: 'Found 3 critical vulnerabilities in database queries',
          recommendations: [
            'Use parameterized queries',
            'Implement input validation',
            'Enable SQL injection protection'
          ],
          timestamp: Date.now() - 3300000
        },
        {
          testId: '2',
          testName: 'XSS Vulnerability Scan',
          status: 'warning',
          score: 85,
          details: 'Minor XSS vulnerabilities found in user input fields',
          recommendations: [
            'Implement output encoding',
            'Add Content Security Policy headers'
          ],
          timestamp: Date.now() - 1800000
        },
        {
          testId: '4',
          testName: 'API Security Assessment',
          status: 'passed',
          score: 92,
          details: 'API security is generally good with minor improvements needed',
          recommendations: [
            'Add rate limiting',
            'Implement API versioning'
          ],
          timestamp: Date.now() - 6780000
        }
      ];

      setTests(mockTests);
      setTestSuites(mockTestSuites);
      setTestResults(mockTestResults);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch test data');
    } finally {
      setLoading(false);
    }
  };

  const runTest = async (testId: string) => {
    setRunningTests(prev => new Set([...prev, testId]));
    
    // Simulate test execution
    setTimeout(() => {
      setTests(prev => prev.map(test => 
        test.id === testId 
          ? { ...test, status: 'running', progress: 50, startedAt: Date.now() }
          : test
      ));
    }, 1000);

    setTimeout(() => {
      setTests(prev => prev.map(test => 
        test.id === testId 
          ? { ...test, status: 'completed', progress: 100, completedAt: Date.now() }
          : test
      ));
      setRunningTests(prev => {
        const newSet = new Set(prev);
        newSet.delete(testId);
        return newSet;
      });
    }, 5000);
  };

  const runTestSuite = async (suiteId: string) => {
    const suite = testSuites.find(s => s.id === suiteId);
    if (!suite) return;

    setTestSuites(prev => prev.map(s => 
      s.id === suiteId 
        ? { ...s, status: 'running', progress: 0 }
        : s
    ));

    // Simulate suite execution
    for (const testId of suite.tests) {
      await runTest(testId);
    }

    setTestSuites(prev => prev.map(s => 
      s.id === suiteId 
        ? { ...s, status: 'completed', progress: 100, lastRun: Date.now() }
        : s
    ));
  };

  const stopTest = (testId: string) => {
    setTests(prev => prev.map(test => 
      test.id === testId 
        ? { ...test, status: 'paused', progress: Math.floor(Math.random() * 50) + 25 }
        : test
    ));
    setRunningTests(prev => {
      const newSet = new Set(prev);
      newSet.delete(testId);
      return newSet;
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      case 'paused': return 'text-yellow-600 bg-yellow-100';
      case 'pending': return 'text-gray-600 bg-gray-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'low': return 'text-green-600 bg-green-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'vulnerability': return <Bug className="h-4 w-4" />;
      case 'penetration': return <Target className="h-4 w-4" />;
      case 'compliance': return <Shield className="h-4 w-4" />;
      case 'performance': return <Activity className="h-4 w-4" />;
      case 'integration': return <Network className="h-4 w-4" />;
      default: return <Code className="h-4 w-4" />;
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8 text-red-600">
        <AlertTriangle className="h-8 w-8 mx-auto mb-4" />
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Advanced Security Testing</h1>
          <p className="text-gray-600">Comprehensive security testing and vulnerability assessment</p>
        </div>
        <div className="flex items-center space-x-4">
          <Button onClick={fetchTestData} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export Results
          </Button>
          <Button>
            <Play className="h-4 w-4 mr-2" />
            Run All Tests
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Tests</CardTitle>
            <Code className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{tests.length}</div>
            <p className="text-xs text-muted-foreground">
              {tests.filter(t => t.status === 'completed').length} completed
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Running Tests</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">{runningTests.size}</div>
            <p className="text-xs text-muted-foreground">
              Currently executing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Critical Findings</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {tests.reduce((acc, test) => acc + test.findings.filter(f => f.severity === 'critical').length, 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              High priority issues
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {tests.length > 0 ? Math.round((tests.filter(t => t.status === 'completed').length / tests.length) * 100) : 0}%
            </div>
            <p className="text-xs text-muted-foreground">
              Test completion rate
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="tests" className="space-y-4">
        <TabsList>
          <TabsTrigger value="tests">Individual Tests</TabsTrigger>
          <TabsTrigger value="suites">Test Suites</TabsTrigger>
          <TabsTrigger value="results">Test Results</TabsTrigger>
          <TabsTrigger value="findings">Security Findings</TabsTrigger>
        </TabsList>

        {/* Individual Tests Tab */}
        <TabsContent value="tests" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Tests</CardTitle>
              <CardDescription>
                Individual security tests and their current status
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tests.map((test) => (
                  <div
                    key={test.id}
                    className={`p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow ${
                      selectedTest?.id === test.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setSelectedTest(test)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4 flex-1">
                        <div className="flex-shrink-0">
                          {getCategoryIcon(test.category)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2 mb-2">
                            <h3 className="font-medium text-gray-900">{test.name}</h3>
                            <Badge className={getSeverityColor(test.severity)}>
                              {test.severity}
                            </Badge>
                            <Badge className={getStatusColor(test.status)}>
                              {test.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">{test.description}</p>
                          <div className="flex items-center space-x-4 text-xs text-gray-500">
                            <span>Duration: {formatDuration(test.duration)}</span>
                            <span>•</span>
                            <span>Results: {test.results.passed}/{test.results.total} passed</span>
                            <span>•</span>
                            <span>Findings: {test.findings.length}</span>
                          </div>
                          {test.status === 'running' && (
                            <div className="mt-2">
                              <Progress value={test.progress} className="h-2" />
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        {test.status === 'pending' && (
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              runTest(test.id);
                            }}
                            disabled={runningTests.has(test.id)}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Run
                          </Button>
                        )}
                        {test.status === 'running' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              stopTest(test.id);
                            }}
                          >
                            <Pause className="h-4 w-4 mr-2" />
                            Pause
                          </Button>
                        )}
                        {test.status === 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              runTest(test.id);
                            }}
                          >
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Re-run
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Test Suites Tab */}
        <TabsContent value="suites" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Suites</CardTitle>
              <CardDescription>
                Predefined test suites for comprehensive security testing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {testSuites.map((suite) => (
                  <div
                    key={suite.id}
                    className={`p-4 border rounded-lg cursor-pointer hover:shadow-md transition-shadow ${
                      selectedSuite?.id === suite.id ? 'ring-2 ring-blue-500' : ''
                    }`}
                    onClick={() => setSelectedSuite(suite)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{suite.name}</h3>
                          <Badge className={getStatusColor(suite.status)}>
                            {suite.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{suite.description}</p>
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span>{suite.tests.length} tests</span>
                          <span>•</span>
                          <span>Created: {formatTimestamp(suite.createdAt)}</span>
                          {suite.lastRun && (
                            <>
                              <span>•</span>
                              <span>Last run: {formatTimestamp(suite.lastRun)}</span>
                            </>
                          )}
                        </div>
                        {suite.status === 'running' && (
                          <div className="mt-2">
                            <Progress value={suite.progress} className="h-2" />
                          </div>
                        )}
                      </div>
                      <div className="flex items-center space-x-2">
                        {suite.status === 'idle' && (
                          <Button
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation();
                              runTestSuite(suite.id);
                            }}
                          >
                            <Play className="h-4 w-4 mr-2" />
                            Run Suite
                          </Button>
                        )}
                        {suite.status === 'running' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              // Stop suite logic here
                            }}
                          >
                            <Square className="h-4 w-4 mr-2" />
                            Stop
                          </Button>
                        )}
                        {suite.status === 'completed' && (
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={(e) => {
                              e.stopPropagation();
                              runTestSuite(suite.id);
                            }}
                          >
                            <RefreshCw className="h-4 w-4 mr-2" />
                            Re-run
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Test Results Tab */}
        <TabsContent value="results" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Test Results</CardTitle>
              <CardDescription>
                Detailed results from completed security tests
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {testResults.map((result) => (
                  <div key={result.testId} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{result.testName}</h3>
                          <Badge className={
                            result.status === 'passed' ? 'text-green-600 bg-green-100' :
                            result.status === 'failed' ? 'text-red-600 bg-red-100' :
                            'text-yellow-600 bg-yellow-100'
                          }>
                            {result.status}
                          </Badge>
                          <Badge className="text-blue-600 bg-blue-100">
                            Score: {result.score}%
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{result.details}</p>
                        <div className="text-xs text-gray-500">
                          Completed: {formatTimestamp(result.timestamp)}
                        </div>
                        {result.recommendations.length > 0 && (
                          <div className="mt-3">
                            <h4 className="text-sm font-medium text-gray-900 mb-2">Recommendations:</h4>
                            <ul className="text-sm text-gray-600 space-y-1">
                              {result.recommendations.map((rec, index) => (
                                <li key={index} className="flex items-start">
                                  <span className="text-blue-500 mr-2">•</span>
                                  {rec}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Findings Tab */}
        <TabsContent value="findings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Findings</CardTitle>
              <CardDescription>
                Security vulnerabilities and issues discovered during testing
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {tests.flatMap(test => test.findings).map((finding) => (
                  <div key={finding.id} className="p-4 border rounded-lg">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h3 className="font-medium text-gray-900">{finding.title}</h3>
                          <Badge className={getSeverityColor(finding.severity)}>
                            {finding.severity}
                          </Badge>
                          <Badge className={
                            finding.status === 'open' ? 'text-red-600 bg-red-100' :
                            finding.status === 'fixed' ? 'text-green-600 bg-green-100' :
                            'text-gray-600 bg-gray-100'
                          }>
                            {finding.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{finding.description}</p>
                        <div className="mt-3">
                          <h4 className="text-sm font-medium text-gray-900 mb-1">Recommendation:</h4>
                          <p className="text-sm text-gray-600">{finding.recommendation}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Button size="sm" variant="outline">
                          <Eye className="h-4 w-4 mr-2" />
                          View Details
                        </Button>
                        {finding.status === 'open' && (
                          <Button size="sm">
                            <CheckCircle className="h-4 w-4 mr-2" />
                            Mark Fixed
                          </Button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

