'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield, 
  AlertTriangle, 
  CheckCircle, 
  XCircle, 
  Activity, 
  Eye, 
  Lock, 
  Brain,
  Database,
  Globe,
  Users,
  Settings
} from 'lucide-react';

interface SecurityMetrics {
  totalRequests: number;
  blockedRequests: number;
  threatLevel: 'low' | 'medium' | 'high' | 'critical';
  riskScore: number;
  trustScore: number;
  biometricVerified: number;
  quantumEncrypted: number;
  aiAnalysis: number;
  blockchainHash: number;
  securityLayers: string[];
  processingTime: number;
}

interface SecurityEvent {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  details: any;
  timestamp: string;
  resolved: boolean;
  tags: string[];
}

interface ComplianceStatus {
  overall: number;
  standards: Array<{
    name: string;
    score: number;
    status: 'compliant' | 'non-compliant' | 'warning';
    violations: number;
  }>;
}

export default function SecurityDashboard() {
  const [metrics, setMetrics] = useState<SecurityMetrics | null>(null);
  const [events, setEvents] = useState<SecurityEvent[]>([]);
  const [compliance, setCompliance] = useState<ComplianceStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('24h');

  useEffect(() => {
    fetchSecurityData();
    const interval = setInterval(fetchSecurityData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [timeRange]);

  const fetchSecurityData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch security status
      const statusResponse = await fetch('/api/security/status');
      const statusData = await statusResponse.json();

      if (!statusResponse.ok) {
        throw new Error(statusData.error || 'Failed to fetch security status');
      }

      setMetrics(statusData.security);

      // Fetch dashboard data
      const dashboardResponse = await fetch(`/api/security/dashboard?timeRange=${timeRange}`);
      const dashboardData = await dashboardResponse.json();

      if (dashboardResponse.ok) {
        setEvents(dashboardData.data.dashboard?.events || []);
      }

      // Fetch compliance status
      const complianceResponse = await fetch('/api/security/compliance');
      const complianceData = await complianceResponse.json();

      if (complianceResponse.ok) {
        setCompliance(complianceData.data.compliance);
      }

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch security data');
    } finally {
      setLoading(false);
    }
  };

  const getThreatLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'text-green-600 bg-green-100';
      case 'medium': return 'text-yellow-600 bg-yellow-100';
      case 'high': return 'text-orange-600 bg-orange-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getComplianceColor = (status: string) => {
    switch (status) {
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'non-compliant': return 'text-red-600 bg-red-100';
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
      <Alert className="border-red-200 bg-red-50">
        <AlertTriangle className="h-4 w-4 text-red-600" />
        <AlertDescription className="text-red-800">
          {error}
        </AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Security Dashboard</h1>
          <p className="text-gray-600">Real-time security monitoring and analysis</p>
        </div>
        <div className="flex items-center space-x-4">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="1h">Last Hour</option>
            <option value="24h">Last 24 Hours</option>
            <option value="7d">Last 7 Days</option>
            <option value="30d">Last 30 Days</option>
          </select>
          <Button onClick={fetchSecurityData} variant="outline">
            <Activity className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>

      {/* Security Status Overview */}
      {metrics && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Threat Level</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="flex items-center space-x-2">
                <div className={`w-3 h-3 rounded-full ${getThreatLevelColor(metrics.threatLevel)}`}></div>
                <span className="text-2xl font-bold capitalize">{metrics.threatLevel}</span>
              </div>
              <p className="text-xs text-muted-foreground">
                Risk Score: {(metrics.riskScore * 100).toFixed(1)}%
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Trust Score</CardTitle>
              <CheckCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{(metrics.trustScore * 100).toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                Biometric: {metrics.biometricVerified ? 'Verified' : 'Not Verified'}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Security Layers</CardTitle>
              <Lock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.securityLayers.length}</div>
              <p className="text-xs text-muted-foreground">
                Active: {metrics.securityLayers.join(', ')}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Processing Time</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{metrics.processingTime}ms</div>
              <p className="text-xs text-muted-foreground">
                Quantum: {metrics.quantumEncrypted ? 'Encrypted' : 'Not Encrypted'}
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs defaultValue="events" className="space-y-4">
        <TabsList>
          <TabsTrigger value="events">Security Events</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="threats">Threat Intelligence</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Security Events Tab */}
        <TabsContent value="events" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Events</CardTitle>
              <CardDescription>
                Real-time security events and alerts
              </CardDescription>
            </CardHeader>
            <CardContent>
              {events.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  No security events in the selected time range
                </div>
              ) : (
                <div className="space-y-4">
                  {events.slice(0, 10).map((event) => (
                    <div key={event.id} className="flex items-center justify-between p-4 border rounded-lg">
                      <div className="flex items-center space-x-4">
                        <div className={`w-2 h-2 rounded-full ${getThreatLevelColor(event.severity)}`}></div>
                        <div>
                          <div className="font-medium">{event.type}</div>
                          <div className="text-sm text-gray-500">
                            {event.source} • {new Date(event.timestamp).toLocaleString()}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={getSeverityColor(event.severity)}>
                          {event.severity}
                        </Badge>
                        {event.resolved ? (
                          <CheckCircle className="h-4 w-4 text-green-500" />
                        ) : (
                          <XCircle className="h-4 w-4 text-red-500" />
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Status</CardTitle>
              <CardDescription>
                Current compliance status across all standards
              </CardDescription>
            </CardHeader>
            <CardContent>
              {compliance ? (
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-lg font-medium">Overall Compliance</span>
                    <span className="text-2xl font-bold">{compliance.overall}%</span>
                  </div>
                  <div className="space-y-3">
                    {compliance.standards.map((standard) => (
                      <div key={standard.name} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <div className="font-medium">{standard.name.toUpperCase()}</div>
                          <div className="text-sm text-gray-500">
                            {standard.violations} violations
                          </div>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-lg font-bold">{standard.score}%</span>
                          <Badge className={getComplianceColor(standard.status)}>
                            {standard.status}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  No compliance data available
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threat Intelligence Tab */}
        <TabsContent value="threats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Threat Intelligence</CardTitle>
              <CardDescription>
                Real-time threat analysis and intelligence
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Brain className="h-5 w-5 text-blue-500" />
                    <span className="font-medium">AI Analysis</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {metrics?.aiAnalysis ? 'Active' : 'Inactive'}
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Database className="h-5 w-5 text-green-500" />
                    <span className="font-medium">Blockchain</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {metrics?.blockchainHash ? 'Active' : 'Inactive'}
                  </div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Globe className="h-5 w-5 text-purple-500" />
                    <span className="font-medium">Threat Feeds</span>
                  </div>
                  <div className="text-sm text-gray-600">4 Active</div>
                </div>
                <div className="p-4 border rounded-lg">
                  <div className="flex items-center space-x-2 mb-2">
                    <Users className="h-5 w-5 text-orange-500" />
                    <span className="font-medium">Biometric</span>
                  </div>
                  <div className="text-sm text-gray-600">
                    {metrics?.biometricVerified ? 'Verified' : 'Not Verified'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
              <CardDescription>
                Configure security parameters and thresholds
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Enhanced Security</div>
                    <div className="text-sm text-gray-500">ML-powered threat detection</div>
                  </div>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Biometric Authentication</div>
                    <div className="text-sm text-gray-500">Multi-factor biometric verification</div>
                  </div>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Threat Intelligence</div>
                    <div className="text-sm text-gray-500">Real-time threat analysis</div>
                  </div>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </Button>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <div className="font-medium">Quantum Encryption</div>
                    <div className="text-sm text-gray-500">Post-quantum cryptography</div>
                  </div>
                  <Button variant="outline" size="sm">
                    <Settings className="h-4 w-4 mr-2" />
                    Configure
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Advanced Security Tools</CardTitle>
              <CardDescription>
                Access comprehensive security tools and dashboards
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">Security Monitoring</div>
                    <div className="text-sm text-gray-500">Real-time alerts and incidents</div>
                  </div>
                  <Button asChild size="sm">
                    <a href="/security/monitoring">
                      <Activity className="h-4 w-4 mr-2" />
                      Open
                    </a>
                  </Button>
                </div>
                
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">Security Analytics</div>
                    <div className="text-sm text-gray-500">Threat intelligence and insights</div>
                  </div>
                  <Button asChild size="sm">
                    <a href="/security/analytics">
                      <BarChart3 className="h-4 w-4 mr-2" />
                      Open
                    </a>
                  </Button>
                </div>
                
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">Security Testing</div>
                    <div className="text-sm text-gray-500">Vulnerability assessment tools</div>
                  </div>
                  <Button asChild size="sm">
                    <a href="/security/testing">
                      <Target className="h-4 w-4 mr-2" />
                      Open
                    </a>
                  </Button>
                </div>
                
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div>
                    <div className="font-medium">Security Examples</div>
                    <div className="text-sm text-gray-500">Demo and usage examples</div>
                  </div>
                  <Button asChild size="sm">
                    <a href="/security/examples">
                      <Eye className="h-4 w-4 mr-2" />
                      Open
                    </a>
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

