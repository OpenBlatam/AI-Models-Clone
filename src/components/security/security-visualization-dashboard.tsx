'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  Activity, 
  Shield, 
  AlertTriangle, 
  TrendingUp, 
  TrendingDown,
  Eye,
  Lock,
  Zap,
  Globe,
  Users,
  Clock,
  RefreshCw,
  Download,
  Filter,
  Settings,
  Maximize2,
  Minimize2
} from 'lucide-react';

interface SecurityVisualizationData {
  threatTimeline: Array<{
    date: string;
    threats: number;
    blocked: number;
    severity: 'low' | 'medium' | 'high' | 'critical';
  }>;
  eventDistribution: Array<{
    category: string;
    count: number;
    percentage: number;
    trend: 'up' | 'down' | 'stable';
  }>;
  geographicThreats: Array<{
    country: string;
    threats: number;
    blocked: number;
    risk: 'low' | 'medium' | 'high';
  }>;
  userActivity: Array<{
    user: string;
    events: number;
    lastActivity: string;
    status: 'active' | 'inactive' | 'suspicious';
  }>;
  systemHealth: {
    overall: number;
    components: Array<{
      name: string;
      status: 'healthy' | 'warning' | 'critical';
      uptime: number;
    }>;
  };
  complianceStatus: Array<{
    framework: string;
    score: number;
    status: 'compliant' | 'partial' | 'non-compliant';
    lastAssessment: string;
  }>;
}

export function SecurityVisualizationDashboard() {
  const [data, setData] = useState<SecurityVisualizationData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedTimeRange, setSelectedTimeRange] = useState('24h');
  const [selectedView, setSelectedView] = useState('overview');
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    loadVisualizationData();
    const interval = setInterval(loadVisualizationData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, [selectedTimeRange]);

  const loadVisualizationData = useCallback(async () => {
    try {
      setIsLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData: SecurityVisualizationData = {
        threatTimeline: generateThreatTimeline(),
        eventDistribution: generateEventDistribution(),
        geographicThreats: generateGeographicThreats(),
        userActivity: generateUserActivity(),
        systemHealth: generateSystemHealth(),
        complianceStatus: generateComplianceStatus(),
      };
      
      setData(mockData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load visualization data:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedTimeRange]);

  const generateThreatTimeline = () => {
    return Array.from({ length: 24 }, (_, i) => ({
      date: new Date(Date.now() - (23 - i) * 60 * 60 * 1000).toISOString(),
      threats: Math.floor(Math.random() * 20) + 1,
      blocked: Math.floor(Math.random() * 18) + 1,
      severity: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)] as 'low' | 'medium' | 'high' | 'critical',
    }));
  };

  const generateEventDistribution = () => {
    const categories = ['Authentication', 'Authorization', 'Threat Detection', 'System Events', 'API Calls', 'Data Access'];
    return categories.map(category => ({
      category,
      count: Math.floor(Math.random() * 200) + 50,
      percentage: Math.floor(Math.random() * 30) + 10,
      trend: ['up', 'down', 'stable'][Math.floor(Math.random() * 3)] as 'up' | 'down' | 'stable',
    }));
  };

  const generateGeographicThreats = () => {
    const countries = ['United States', 'China', 'Russia', 'Germany', 'United Kingdom', 'France', 'Japan', 'Brazil'];
    return countries.map(country => ({
      country,
      threats: Math.floor(Math.random() * 100) + 10,
      blocked: Math.floor(Math.random() * 90) + 8,
      risk: ['low', 'medium', 'high'][Math.floor(Math.random() * 3)] as 'low' | 'medium' | 'high',
    }));
  };

  const generateUserActivity = () => {
    const users = ['admin@company.com', 'user1@company.com', 'user2@company.com', 'user3@company.com', 'user4@company.com'];
    return users.map(user => ({
      user,
      events: Math.floor(Math.random() * 100) + 10,
      lastActivity: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toISOString(),
      status: ['active', 'inactive', 'suspicious'][Math.floor(Math.random() * 3)] as 'active' | 'inactive' | 'suspicious',
    }));
  };

  const generateSystemHealth = () => {
    return {
      overall: 95 + Math.random() * 5,
      components: [
        { name: 'Authentication Service', status: 'healthy' as const, uptime: 99.9 },
        { name: 'Threat Detection', status: 'healthy' as const, uptime: 99.8 },
        { name: 'Encryption Service', status: 'warning' as const, uptime: 98.5 },
        { name: 'Monitoring System', status: 'healthy' as const, uptime: 99.7 },
        { name: 'API Gateway', status: 'healthy' as const, uptime: 99.6 },
      ],
    };
  };

  const generateComplianceStatus = () => {
    const frameworks = ['ISO 27001', 'SOC 2', 'GDPR', 'HIPAA', 'PCI-DSS'];
    return frameworks.map(framework => ({
      framework,
      score: Math.floor(Math.random() * 30) + 70,
      status: ['compliant', 'partial', 'non-compliant'][Math.floor(Math.random() * 3)] as 'compliant' | 'partial' | 'non-compliant',
      lastAssessment: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    }));
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

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'up': return <TrendingUp className="h-4 w-4 text-red-600" />;
      case 'down': return <TrendingDown className="h-4 w-4 text-green-600" />;
      default: return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      case 'active': return 'text-green-600 bg-green-100';
      case 'inactive': return 'text-gray-600 bg-gray-100';
      case 'suspicious': return 'text-red-600 bg-red-100';
      case 'compliant': return 'text-green-600 bg-green-100';
      case 'partial': return 'text-yellow-600 bg-yellow-100';
      case 'non-compliant': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading visualization data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`space-y-6 ${isFullscreen ? 'fixed inset-0 z-50 bg-background p-6 overflow-auto' : ''}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Security Visualization Dashboard</h2>
          <p className="text-muted-foreground">
            Advanced security analytics and visualizations
            {lastUpdate && (
              <span className="ml-2 text-xs">
                • Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={loadVisualizationData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline" size="sm" onClick={() => setIsFullscreen(!isFullscreen)}>
            {isFullscreen ? <Minimize2 className="h-4 w-4" /> : <Maximize2 className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Time Range Selector */}
      <div className="flex items-center gap-2">
        <span className="text-sm font-medium">Time Range:</span>
        {['1h', '24h', '7d', '30d'].map(range => (
          <Button
            key={range}
            variant={selectedTimeRange === range ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedTimeRange(range)}
          >
            {range}
          </Button>
        ))}
      </div>

      {/* Main Content */}
      <Tabs value={selectedView} onValueChange={setSelectedView} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="geography">Geography</TabsTrigger>
          <TabsTrigger value="users">Users</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* System Health Overview */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">System Health</CardTitle>
                <Activity className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{data.systemHealth.overall.toFixed(1)}%</div>
                <Progress value={data.systemHealth.overall} className="h-2 mt-2" />
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Threats</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {data.threatTimeline.reduce((sum, item) => sum + item.threats, 0)}
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.threatTimeline.reduce((sum, item) => sum + item.blocked, 0)} blocked
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Users</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {data.userActivity.filter(u => u.status === 'active').length}
                </div>
                <p className="text-xs text-muted-foreground">
                  {data.userActivity.filter(u => u.status === 'suspicious').length} suspicious
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Event Distribution */}
          <Card>
            <CardHeader>
              <CardTitle>Event Distribution</CardTitle>
              <CardDescription>Security events by category</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.eventDistribution.map((event, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-3 h-3 rounded-full bg-blue-500" />
                      <span className="font-medium">{event.category}</span>
                      {getTrendIcon(event.trend)}
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="w-32">
                        <Progress value={event.percentage} className="h-2" />
                      </div>
                      <span className="text-sm font-medium w-16 text-right">{event.count}</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* System Components */}
          <Card>
            <CardHeader>
              <CardTitle>System Components</CardTitle>
              <CardDescription>Health status of security components</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {data.systemHealth.components.map((component, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className={`w-2 h-2 rounded-full ${
                        component.status === 'healthy' ? 'bg-green-500' :
                        component.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                      }`} />
                      <span className="font-medium">{component.name}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge className={getStatusColor(component.status)}>
                        {component.status}
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        {component.uptime.toFixed(1)}% uptime
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threats Tab */}
        <TabsContent value="threats" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Threat Timeline</CardTitle>
              <CardDescription>Threats detected over time</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.threatTimeline.slice(-12).map((threat, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-sm">
                        {new Date(threat.date).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="font-medium">{threat.threats}</div>
                        <div className="text-xs text-muted-foreground">threats</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-green-600">{threat.blocked}</div>
                        <div className="text-xs text-muted-foreground">blocked</div>
                      </div>
                      <Badge className={getSeverityColor(threat.severity)}>
                        {threat.severity}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Geography Tab */}
        <TabsContent value="geography" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Geographic Threat Distribution</CardTitle>
              <CardDescription>Threats by country</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.geographicThreats.map((geo, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Globe className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{geo.country}</span>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="font-medium">{geo.threats}</div>
                        <div className="text-xs text-muted-foreground">threats</div>
                      </div>
                      <div className="text-center">
                        <div className="font-medium text-green-600">{geo.blocked}</div>
                        <div className="text-xs text-muted-foreground">blocked</div>
                      </div>
                      <Badge className={getStatusColor(geo.risk)}>
                        {geo.risk} risk
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>User Activity</CardTitle>
              <CardDescription>User activity and status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.userActivity.map((user, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Users className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{user.user}</div>
                        <div className="text-sm text-muted-foreground">
                          Last activity: {new Date(user.lastActivity).toLocaleString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="font-medium">{user.events}</div>
                        <div className="text-xs text-muted-foreground">events</div>
                      </div>
                      <Badge className={getStatusColor(user.status)}>
                        {user.status}
                      </Badge>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Status</CardTitle>
              <CardDescription>Compliance framework status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {data.complianceStatus.map((compliance, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      <Shield className="h-4 w-4 text-muted-foreground" />
                      <div>
                        <div className="font-medium">{compliance.framework}</div>
                        <div className="text-sm text-muted-foreground">
                          Last assessment: {new Date(compliance.lastAssessment).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-center">
                        <div className="font-medium">{compliance.score}%</div>
                        <div className="text-xs text-muted-foreground">score</div>
                      </div>
                      <Badge className={getStatusColor(compliance.status)}>
                        {compliance.status}
                      </Badge>
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
