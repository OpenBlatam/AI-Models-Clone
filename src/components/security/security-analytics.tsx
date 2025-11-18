'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Shield, 
  AlertTriangle,
  Clock,
  Target,
  Users,
  Globe,
  Database,
  Zap,
  Eye,
  Lock,
  Brain,
  Settings,
  Download,
  RefreshCw,
  Calendar,
  Filter
} from 'lucide-react';

interface SecurityAnalytics {
  overview: {
    totalThreats: number;
    threatsBlocked: number;
    threatsDetected: number;
    falsePositives: number;
    averageResponseTime: number;
    systemUptime: number;
    securityScore: number;
  };
  trends: {
    daily: Array<{
      date: string;
      threats: number;
      blocked: number;
      incidents: number;
      alerts: number;
    }>;
    weekly: Array<{
      week: string;
      threats: number;
      blocked: number;
      incidents: number;
      alerts: number;
    }>;
    monthly: Array<{
      month: string;
      threats: number;
      blocked: number;
      incidents: number;
      alerts: number;
    }>;
  };
  threatAnalysis: {
    byType: Record<string, number>;
    bySeverity: Record<string, number>;
    bySource: Record<string, number>;
    byLocation: Record<string, number>;
    topThreats: Array<{
      id: string;
      name: string;
      count: number;
      severity: string;
      trend: 'up' | 'down' | 'stable';
    }>;
  };
  performance: {
    detectionLatency: number;
    processingThroughput: number;
    systemLoad: number;
    memoryUsage: number;
    cpuUsage: number;
    networkLatency: number;
  };
  compliance: {
    overallScore: number;
    frameworks: Array<{
      name: string;
      score: number;
      status: 'compliant' | 'warning' | 'non-compliant';
      lastAssessment: string;
    }>;
    controls: Array<{
      id: string;
      name: string;
      status: 'implemented' | 'partial' | 'not_implemented';
      score: number;
    }>;
  };
}

export default function SecurityAnalytics() {
  const [analytics, setAnalytics] = useState<SecurityAnalytics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('threats');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Generate mock analytics data
      const mockAnalytics: SecurityAnalytics = {
        overview: {
          totalThreats: Math.floor(Math.random() * 1000) + 500,
          threatsBlocked: Math.floor(Math.random() * 800) + 400,
          threatsDetected: Math.floor(Math.random() * 200) + 100,
          falsePositives: Math.floor(Math.random() * 50) + 10,
          averageResponseTime: Math.floor(Math.random() * 100) + 50,
          systemUptime: 99.9,
          securityScore: Math.floor(Math.random() * 20) + 80,
        },
        trends: {
          daily: generateDailyTrends(),
          weekly: generateWeeklyTrends(),
          monthly: generateMonthlyTrends(),
        },
        threatAnalysis: {
          byType: {
            'DDoS': Math.floor(Math.random() * 100) + 50,
            'Malware': Math.floor(Math.random() * 80) + 30,
            'Phishing': Math.floor(Math.random() * 60) + 20,
            'Brute Force': Math.floor(Math.random() * 40) + 15,
            'SQL Injection': Math.floor(Math.random() * 30) + 10,
            'XSS': Math.floor(Math.random() * 25) + 8,
          },
          bySeverity: {
            'Critical': Math.floor(Math.random() * 20) + 5,
            'High': Math.floor(Math.random() * 50) + 20,
            'Medium': Math.floor(Math.random() * 100) + 50,
            'Low': Math.floor(Math.random() * 200) + 100,
          },
          bySource: {
            'External': Math.floor(Math.random() * 300) + 200,
            'Internal': Math.floor(Math.random() * 100) + 50,
            'Unknown': Math.floor(Math.random() * 50) + 20,
          },
          byLocation: {
            'North America': Math.floor(Math.random() * 150) + 100,
            'Europe': Math.floor(Math.random() * 120) + 80,
            'Asia': Math.floor(Math.random() * 100) + 60,
            'Other': Math.floor(Math.random() * 50) + 20,
          },
          topThreats: [
            { id: '1', name: 'DDoS Attack', count: 150, severity: 'high', trend: 'up' },
            { id: '2', name: 'Malware Detection', count: 120, severity: 'critical', trend: 'down' },
            { id: '3', name: 'Phishing Attempt', count: 80, severity: 'medium', trend: 'stable' },
            { id: '4', name: 'Brute Force', count: 60, severity: 'high', trend: 'up' },
            { id: '5', name: 'SQL Injection', count: 40, severity: 'critical', trend: 'down' },
          ],
        },
        performance: {
          detectionLatency: Math.floor(Math.random() * 50) + 10,
          processingThroughput: Math.floor(Math.random() * 1000) + 500,
          systemLoad: Math.random() * 30 + 20,
          memoryUsage: Math.random() * 40 + 30,
          cpuUsage: Math.random() * 50 + 25,
          networkLatency: Math.floor(Math.random() * 20) + 5,
        },
        compliance: {
          overallScore: Math.floor(Math.random() * 20) + 80,
          frameworks: [
            { name: 'ISO27001', score: 92, status: 'compliant', lastAssessment: '2023-10-01' },
            { name: 'SOC2', score: 88, status: 'compliant', lastAssessment: '2023-09-15' },
            { name: 'GDPR', score: 85, status: 'warning', lastAssessment: '2023-10-15' },
            { name: 'HIPAA', score: 90, status: 'compliant', lastAssessment: '2023-09-30' },
            { name: 'PCI-DSS', score: 95, status: 'compliant', lastAssessment: '2023-10-10' },
          ],
          controls: [
            { id: 'A.5.1.1', name: 'Information Security Policies', status: 'implemented', score: 95 },
            { id: 'A.6.1.1', name: 'Information Security Roles', status: 'implemented', score: 90 },
            { id: 'A.8.1.1', name: 'Inventory of Assets', status: 'partial', score: 75 },
            { id: 'A.9.1.1', name: 'Access Control Policy', status: 'implemented', score: 88 },
            { id: 'A.10.1.1', name: 'Cryptographic Controls', status: 'implemented', score: 92 },
          ],
        },
      };

      setAnalytics(mockAnalytics);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics data');
    } finally {
      setLoading(false);
    }
  };

  const generateDailyTrends = () => {
    const trends = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      trends.push({
        date: date.toISOString().split('T')[0],
        threats: Math.floor(Math.random() * 50) + 20,
        blocked: Math.floor(Math.random() * 40) + 15,
        incidents: Math.floor(Math.random() * 10) + 2,
        alerts: Math.floor(Math.random() * 30) + 10,
      });
    }
    return trends;
  };

  const generateWeeklyTrends = () => {
    const trends = [];
    for (let i = 3; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - (i * 7));
      trends.push({
        week: `Week ${4 - i}`,
        threats: Math.floor(Math.random() * 200) + 100,
        blocked: Math.floor(Math.random() * 150) + 80,
        incidents: Math.floor(Math.random() * 20) + 5,
        alerts: Math.floor(Math.random() * 100) + 50,
      });
    }
    return trends;
  };

  const generateMonthlyTrends = () => {
    const trends = [];
    for (let i = 5; i >= 0; i--) {
      const date = new Date();
      date.setMonth(date.getMonth() - i);
      trends.push({
        month: date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' }),
        threats: Math.floor(Math.random() * 500) + 300,
        blocked: Math.floor(Math.random() * 400) + 250,
        incidents: Math.floor(Math.random() * 50) + 20,
        alerts: Math.floor(Math.random() * 200) + 100,
      });
    }
    return trends;
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-red-500" />;
      case 'down': return <TrendingDown className="h-4 w-4 text-green-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'non-compliant': return 'text-red-600 bg-red-100';
      case 'implemented': return 'text-green-600 bg-green-100';
      case 'partial': return 'text-yellow-600 bg-yellow-100';
      case 'not_implemented': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
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

  if (!analytics) return null;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Analytics</h1>
          <p className="text-gray-600">Comprehensive security analytics and insights</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
            <option value="90d">Last 90 Days</option>
          </select>
          <Button onClick={fetchAnalytics} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Threats</CardTitle>
            <Shield className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.totalThreats}</div>
            <p className="text-xs text-muted-foreground">
              {analytics.overview.threatsBlocked} blocked
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Security Score</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{analytics.overview.securityScore}%</div>
            <p className="text-xs text-muted-foreground">
              System uptime: {analytics.overview.systemUptime}%
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Response Time</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{analytics.overview.averageResponseTime}ms</div>
            <p className="text-xs text-muted-foreground">
              Average detection time
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">False Positives</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{analytics.overview.falsePositives}</div>
            <p className="text-xs text-muted-foreground">
              {Math.round((analytics.overview.falsePositives / analytics.overview.totalThreats) * 100)}% of total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs defaultValue="trends" className="space-y-4">
        <TabsList>
          <TabsTrigger value="trends">Trends</TabsTrigger>
          <TabsTrigger value="threats">Threat Analysis</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        {/* Trends Tab */}
        <TabsContent value="trends" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Daily Trends</CardTitle>
                <CardDescription>Security events over the last 7 days</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.trends.daily.map((day, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{day.date}</span>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-red-600">{day.threats} threats</div>
                        <div className="text-sm text-green-600">{day.blocked} blocked</div>
                        <div className="text-sm text-blue-600">{day.incidents} incidents</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Weekly Trends</CardTitle>
                <CardDescription>Security events over the last 4 weeks</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.trends.weekly.map((week, index) => (
                    <div key={index} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{week.week}</span>
                      <div className="flex items-center space-x-4">
                        <div className="text-sm text-red-600">{week.threats} threats</div>
                        <div className="text-sm text-green-600">{week.blocked} blocked</div>
                        <div className="text-sm text-blue-600">{week.incidents} incidents</div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Threat Analysis Tab */}
        <TabsContent value="threats" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Threats by Type</CardTitle>
                <CardDescription>Distribution of threats by category</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(analytics.threatAnalysis.byType).map(([type, count]) => (
                    <div key={type} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{type}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-blue-500 h-2 rounded-full" 
                            style={{ width: `${(count / Math.max(...Object.values(analytics.threatAnalysis.byType))) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Top Threats</CardTitle>
                <CardDescription>Most frequent threat types</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {analytics.threatAnalysis.topThreats.map((threat) => (
                    <div key={threat.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        {getTrendIcon(threat.trend)}
                        <div>
                          <div className="font-medium">{threat.name}</div>
                          <div className="text-sm text-gray-500">{threat.count} occurrences</div>
                        </div>
                      </div>
                      <Badge className={threat.severity === 'critical' ? 'bg-red-100 text-red-800' : 
                                      threat.severity === 'high' ? 'bg-orange-100 text-orange-800' : 
                                      'bg-yellow-100 text-yellow-800'}>
                        {threat.severity}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Threats by Severity</CardTitle>
                <CardDescription>Distribution by severity level</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(analytics.threatAnalysis.bySeverity).map(([severity, count]) => (
                    <div key={severity} className="flex items-center justify-between">
                      <span className="text-sm font-medium capitalize">{severity}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              severity === 'critical' ? 'bg-red-500' :
                              severity === 'high' ? 'bg-orange-500' :
                              severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${(count / Math.max(...Object.values(analytics.threatAnalysis.bySeverity))) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Threats by Source</CardTitle>
                <CardDescription>Distribution by source type</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {Object.entries(analytics.threatAnalysis.bySource).map(([source, count]) => (
                    <div key={source} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{source}</span>
                      <div className="flex items-center space-x-2">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div 
                            className="bg-purple-500 h-2 rounded-full" 
                            style={{ width: `${(count / Math.max(...Object.values(analytics.threatAnalysis.bySource))) * 100}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-gray-600">{count}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Detection Latency</CardTitle>
                <CardDescription>Average threat detection time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-blue-600">{analytics.performance.detectionLatency}ms</div>
                <p className="text-sm text-gray-500 mt-2">Target: &lt;100ms</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Processing Throughput</CardTitle>
                <CardDescription>Events processed per second</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-green-600">{analytics.performance.processingThroughput}</div>
                <p className="text-sm text-gray-500 mt-2">events/sec</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>System Load</CardTitle>
                <CardDescription>Current system utilization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-orange-600">{analytics.performance.systemLoad.toFixed(1)}%</div>
                <p className="text-sm text-gray-500 mt-2">CPU + Memory</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Memory Usage</CardTitle>
                <CardDescription>Current memory utilization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-purple-600">{analytics.performance.memoryUsage.toFixed(1)}%</div>
                <p className="text-sm text-gray-500 mt-2">RAM usage</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>CPU Usage</CardTitle>
                <CardDescription>Current CPU utilization</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-red-600">{analytics.performance.cpuUsage.toFixed(1)}%</div>
                <p className="text-sm text-gray-500 mt-2">Processor usage</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Network Latency</CardTitle>
                <CardDescription>Average network response time</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-indigo-600">{analytics.performance.networkLatency}ms</div>
                <p className="text-sm text-gray-500 mt-2">Round-trip time</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Overview</CardTitle>
              <CardDescription>Overall compliance score and framework status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center mb-6">
                <div className="text-4xl font-bold text-green-600 mb-2">{analytics.compliance.overallScore}%</div>
                <p className="text-gray-600">Overall Compliance Score</p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {analytics.compliance.frameworks.map((framework) => (
                  <div key={framework.name} className="p-4 border rounded-lg">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium">{framework.name}</h3>
                      <Badge className={getStatusColor(framework.status)}>
                        {framework.status}
                      </Badge>
                    </div>
                    <div className="text-2xl font-bold text-blue-600 mb-1">{framework.score}%</div>
                    <p className="text-sm text-gray-500">Last assessment: {framework.lastAssessment}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Control Implementation</CardTitle>
              <CardDescription>Status of individual security controls</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analytics.compliance.controls.map((control) => (
                  <div key={control.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div>
                      <div className="font-medium">{control.id} - {control.name}</div>
                      <div className="text-sm text-gray-500">Score: {control.score}%</div>
                    </div>
                    <Badge className={getStatusColor(control.status)}>
                      {control.status.replace('_', ' ')}
                    </Badge>
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


