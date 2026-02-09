'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield, 
  Eye, 
  Search, 
  FileText, 
  BarChart3, 
  Settings, 
  AlertTriangle,
  CheckCircle,
  Clock,
  Users,
  Activity,
  Brain,
  Zap,
  Target,
  Lock,
  Globe,
  Database,
  Cpu,
  Network,
  Smartphone,
  Cloud,
  Code,
  TestTube,
  TrendingUp,
  AlertCircle,
  RefreshCw,
  Play,
  Pause,
  Stop
} from 'lucide-react';

interface SecurityStats {
  totalThreats: number;
  activeIncidents: number;
  securityScore: number;
  complianceRate: number;
  riskLevel: string;
  lastUpdate: string;
}

interface SecurityModule {
  id: string;
  name: string;
  status: 'active' | 'inactive' | 'error';
  health: 'healthy' | 'degraded' | 'unhealthy';
  metrics: {
    uptime: number;
    performance: number;
    errors: number;
  };
}

export default function UltimateSecurityDashboard() {
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [modules, setModules] = useState<SecurityModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadSecurityData();
    
    if (autoRefresh) {
      const interval = setInterval(loadSecurityData, 30000); // Refresh every 30 seconds
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadSecurityData = async () => {
    try {
      setLoading(true);
      
      // Simulate API calls for different security modules
      const [statsRes, modulesRes] = await Promise.all([
        fetch('/api/security/stats'),
        fetch('/api/security/modules')
      ]);

      const [statsData, modulesData] = await Promise.all([
        statsRes.json(),
        modulesRes.json()
      ]);

      setStats(statsData);
      setModules(modulesData);
    } catch (error) {
      console.error('Error loading security data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy': return 'text-green-600';
      case 'degraded': return 'text-yellow-600';
      case 'unhealthy': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'low': return 'text-green-600';
      case 'medium': return 'text-yellow-600';
      case 'high': return 'text-orange-600';
      case 'critical': return 'text-red-600';
      default: return 'text-gray-600';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ultimate Security Dashboard</h1>
          <p className="text-gray-600">Comprehensive security monitoring, intelligence, and response</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
          </Button>
          <Button variant="outline" size="sm" onClick={loadSecurityData}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
        </div>
      </div>

      {/* Stats Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Shield className="h-8 w-8 text-blue-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Security Score</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.securityScore}/100</p>
                </div>
              </div>
              <div className="mt-2">
                <Progress value={stats.securityScore} className="h-2" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <AlertTriangle className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Threats</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalThreats}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <FileText className="h-8 w-8 text-red-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Incidents</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeIncidents}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <CheckCircle className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Compliance Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.complianceRate}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Risk Level Alert */}
      {stats && stats.riskLevel !== 'low' && (
        <Alert variant={stats.riskLevel === 'critical' ? 'destructive' : 'default'}>
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            Current risk level: <span className={getRiskLevelColor(stats.riskLevel)}>{stats.riskLevel.toUpperCase()}</span>
            {stats.riskLevel === 'critical' && ' - Immediate action required'}
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
          <TabsTrigger value="forensics">Forensics</TabsTrigger>
          <TabsTrigger value="governance">Governance</TabsTrigger>
          <TabsTrigger value="modules">Modules</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Security Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Shield className="h-5 w-5 mr-2 text-blue-600" />
                  Security Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Overall Security</span>
                    <Badge className={getStatusColor('active')}>Active</Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Risk Level</span>
                    <span className={`text-sm font-medium ${getRiskLevelColor(stats?.riskLevel || 'low')}`}>
                      {stats?.riskLevel?.toUpperCase() || 'LOW'}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Last Update</span>
                    <span className="text-sm text-gray-600">{stats?.lastUpdate || 'Never'}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Active Modules */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-green-600" />
                  Active Modules
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {modules.slice(0, 5).map((module) => (
                    <div key={module.id} className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className={`w-2 h-2 rounded-full ${
                          module.health === 'healthy' ? 'bg-green-500' : 
                          module.health === 'degraded' ? 'bg-yellow-500' : 'bg-red-500'
                        }`}></div>
                        <span className="text-sm font-medium">{module.name}</span>
                      </div>
                      <Badge className={getStatusColor(module.status)}>
                        {module.status}
                      </Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-purple-600" />
                Recent Security Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Threat detection system updated</p>
                    <p className="text-xs text-gray-500">2 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New security policy deployed</p>
                    <p className="text-xs text-gray-500">15 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Security scan completed</p>
                    <p className="text-xs text-gray-500">1 hour ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Suspicious activity detected</p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Intelligence Tab */}
        <TabsContent value="intelligence" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Eye className="h-5 w-5 mr-2 text-blue-600" />
                  Threat Intelligence
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">1,247</p>
                    <p className="text-sm text-gray-600">Active IOCs</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>High Confidence</span>
                      <span>892</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Medium Confidence</span>
                      <span>298</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Low Confidence</span>
                      <span>57</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Search className="h-5 w-5 mr-2 text-green-600" />
                  Threat Hunting
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">23</p>
                    <p className="text-sm text-gray-600">Active Hunts</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Findings Today</span>
                      <span>12</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Confirmed Threats</span>
                      <span>3</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>False Positives</span>
                      <span>9</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-purple-600" />
                  Threat Actors
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">156</p>
                    <p className="text-sm text-gray-600">Tracked Actors</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Active</span>
                      <span>89</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Nation State</span>
                      <span>23</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Criminal Groups</span>
                      <span>67</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Forensics Tab */}
        <TabsContent value="forensics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-red-600" />
                  Digital Evidence
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-red-600">342</p>
                    <p className="text-sm text-gray-600">Evidence Items</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Analyzed</span>
                      <span>298</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Pending</span>
                      <span>44</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Archived</span>
                      <span>156</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
                  Incident Response
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-orange-600">18</p>
                    <p className="text-sm text-gray-600">Active Incidents</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Critical</span>
                      <span>2</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>High</span>
                      <span>5</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Medium</span>
                      <span>11</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Governance Tab */}
        <TabsContent value="governance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Policies
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">47</p>
                    <p className="text-sm text-gray-600">Active Policies</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Compliant</span>
                      <span>42</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Non-Compliant</span>
                      <span>5</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                  Compliance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">94%</p>
                    <p className="text-sm text-gray-600">Compliance Rate</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>ISO 27001</span>
                      <span>98%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>SOC 2</span>
                      <span>92%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>GDPR</span>
                      <span>96%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-purple-600" />
                  Training
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-purple-600">89%</p>
                    <p className="text-sm text-gray-600">Completion Rate</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Completed</span>
                      <span>1,247</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>In Progress</span>
                      <span>156</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Overdue</span>
                      <span>23</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Modules Tab */}
        <TabsContent value="modules" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {modules.map((module) => (
              <Card key={module.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium">{module.name}</CardTitle>
                    <Badge className={getStatusColor(module.status)}>
                      {module.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Health:</span>
                      <span className={getHealthColor(module.health)}>
                        {module.health}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Uptime:</span>
                      <span>{module.metrics.uptime}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Performance:</span>
                      <span>{module.metrics.performance}%</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Errors:</span>
                      <span>{module.metrics.errors}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                  Security Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">-15%</p>
                    <p className="text-sm text-gray-600">Threats vs Last Month</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Detection Rate</span>
                      <span className="text-green-600">+8%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Response Time</span>
                      <span className="text-green-600">-12%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>False Positives</span>
                      <span className="text-red-600">+3%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2 text-green-600" />
                  Performance Metrics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">99.9%</p>
                    <p className="text-sm text-gray-600">System Uptime</p>
                  </div>
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Average Response</span>
                      <span>45ms</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Peak Throughput</span>
                      <span>1.2M req/s</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Error Rate</span>
                      <span>0.01%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}
