'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Shield, 
  Lock, 
  Eye, 
  AlertTriangle, 
  CheckCircle, 
  Activity,
  TrendingUp,
  Users,
  Settings,
  RefreshCw,
  Zap,
  Database,
  Network,
  Bell,
  BarChart3,
  BookOpen,
  Workflow,
  Target,
  Fingerprint,
  Key,
  FileText,
  Globe,
  Smartphone,
  Monitor,
  Play,
  Pause,
  Square,
  Download,
  Upload,
  Filter,
  Search,
  Plus,
  Edit,
  Trash2,
  ExternalLink,
  Clock,
  AlertCircle,
  Info,
  X
} from 'lucide-react';
import { securityManager } from '@/lib/security';

export function ComprehensiveSecurityDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [securityStatus, setSecurityStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [integrations, setIntegrations] = useState<any[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [automationRules, setAutomationRules] = useState<any[]>([]);
  const [executions, setExecutions] = useState<any[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000);

  useEffect(() => {
    initializeDashboard();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refreshDashboard();
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const initializeDashboard = async () => {
    try {
      setIsLoading(true);
      await securityManager.initialize();
      await loadDashboardData();
    } catch (error) {
      console.error('Failed to initialize dashboard:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadDashboardData = async () => {
    try {
      // Load security status
      const status = securityManager.getSecurityStatus();
      setSecurityStatus(status);

      // Load alerts
      const alertsResponse = await fetch('/api/security/alerts');
      if (alertsResponse.ok) {
        const alertsData = await alertsResponse.json();
        setAlerts(alertsData.alerts || []);
      }

      // Load integrations
      const integrationsResponse = await fetch('/api/security/integrations');
      if (integrationsResponse.ok) {
        const integrationsData = await integrationsResponse.json();
        setIntegrations(integrationsData.integrations || []);
      }

      // Load reports
      const reportsResponse = await fetch('/api/security/reports');
      if (reportsResponse.ok) {
        const reportsData = await reportsResponse.json();
        setReports(reportsData.reports || []);
      }

      // Load automation rules
      const automationResponse = await fetch('/api/security/automation');
      if (automationResponse.ok) {
        const automationData = await automationResponse.json();
        setAutomationRules(automationData.rules || []);
        setExecutions(automationData.executions || []);
      }

      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    }
  };

  const refreshDashboard = useCallback(async () => {
    await loadDashboardData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
      case 'completed':
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'warning':
      case 'partial':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
      case 'error':
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'inactive':
      case 'pending':
        return 'text-gray-600 bg-gray-100';
      default:
        return 'text-blue-600 bg-blue-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
      case 'healthy':
      case 'completed':
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning':
      case 'partial':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'critical':
      case 'error':
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  if (!securityStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing security dashboard...</p>
        </div>
      </div>
    );
  }

  const metrics = securityStatus.metrics;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Comprehensive Security Dashboard</h2>
          <p className="text-muted-foreground">
            Complete security monitoring, automation, and management
            {lastUpdate && (
              <span className="ml-2 text-xs">
                • Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={refreshDashboard} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Security Alerts */}
      {alerts.length > 0 && (
        <Alert className="border-orange-200 bg-orange-50">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>{alerts.length} active security alert{alerts.length > 1 ? 's' : ''}</strong>
            <span className="ml-2">
              {alerts.slice(0, 2).map((alert, index) => (
                <span key={index}>
                  {alert.message}
                  {index < Math.min(alerts.length, 2) - 1 && ', '}
                </span>
              ))}
              {alerts.length > 2 && ` and ${alerts.length - 2} more...`}
            </span>
          </AlertDescription>
        </Alert>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-8">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="automation">Automation</TabsTrigger>
          <TabsTrigger value="integrations">Integrations</TabsTrigger>
          <TabsTrigger value="reports">Reports</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          {/* Security Status Overview */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Threat Detection</CardTitle>
                <Shield className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.threatDetection.totalThreats}</div>
                <p className="text-xs text-muted-foreground">
                  {metrics.threatDetection.blockedIPs} IPs blocked
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Zero Trust</CardTitle>
                <Lock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.zeroTrust.averageTrustScore}%</div>
                <p className="text-xs text-muted-foreground">
                  {metrics.zeroTrust.activeSessions} active sessions
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Security Alerts</CardTitle>
                <Bell className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.monitoring.activeAlerts}</div>
                <p className="text-xs text-muted-foreground">
                  {metrics.monitoring.totalIncidents} total incidents
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Compliance</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metrics.compliance.frameworks}</div>
                <p className="text-xs text-muted-foreground">
                  {metrics.compliance.activePolicies} active policies
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Security Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {executions.slice(0, 5).map((execution, index) => (
                  <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex items-center gap-3">
                      {getStatusIcon(execution.status)}
                      <div>
                        <div className="font-medium">Automation Rule Executed</div>
                        <div className="text-sm text-muted-foreground">
                          Rule ID: {execution.ruleId}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Badge className={getStatusColor(execution.status)}>
                        {execution.status}
                      </Badge>
                      <span className="text-xs text-muted-foreground">
                        {new Date(execution.startedAt).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Monitoring Tab */}
        <TabsContent value="monitoring" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Monitoring</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Eye className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Advanced monitoring features are available in the dedicated monitoring dashboard.
                </p>
                <Button className="mt-4">
                  Open Monitoring Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threats Tab */}
        <TabsContent value="threats" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Threat Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Advanced threat detection and management features are available in the dedicated threat dashboard.
                </p>
                <Button className="mt-4">
                  Open Threat Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Automation Tab */}
        <TabsContent value="automation" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Automation Rules</h3>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {automationRules.map((rule, index) => (
              <Card key={index}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{rule.name}</CardTitle>
                    <Badge className={getStatusColor(rule.enabled ? 'active' : 'inactive')}>
                      {rule.enabled ? 'Active' : 'Inactive'}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">{rule.description}</p>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Priority: {rule.priority}</span>
                    <span>Executions: {rule.executionCount}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Edit className="h-3 w-3 mr-1" />
                      Edit
                    </Button>
                    <Button variant="outline" size="sm">
                      <Play className="h-3 w-3 mr-1" />
                      Run
                    </Button>
                    <Button variant="outline" size="sm">
                      <Trash2 className="h-3 w-3" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Integrations Tab */}
        <TabsContent value="integrations" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">External Integrations</h3>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Add Integration
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {integrations.map((integration, index) => (
              <Card key={index}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{integration.name}</CardTitle>
                    <Badge className={getStatusColor(integration.status)}>
                      {integration.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Provider: {integration.provider}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Type: {integration.type}
                  </p>
                  {integration.lastSync && (
                    <p className="text-xs text-muted-foreground">
                      Last sync: {new Date(integration.lastSync).toLocaleString()}
                    </p>
                  )}
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Settings className="h-3 w-3 mr-1" />
                      Configure
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Test
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Reports Tab */}
        <TabsContent value="reports" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Security Reports</h3>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
          
          <div className="space-y-4">
            {reports.map((report, index) => (
              <Card key={index}>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-sm">{report.title}</CardTitle>
                    <Badge className={getStatusColor(report.status)}>
                      {report.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Type: {report.type} • Generated: {new Date(report.generatedAt).toLocaleString()}
                  </p>
                  <div className="flex items-center gap-2">
                    <Button variant="outline" size="sm">
                      <Eye className="h-3 w-3 mr-1" />
                      View
                    </Button>
                    <Button variant="outline" size="sm">
                      <Download className="h-3 w-3 mr-1" />
                      Download
                    </Button>
                    <Button variant="outline" size="sm">
                      <ExternalLink className="h-3 w-3 mr-1" />
                      Share
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Compliance Management</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <BookOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Compliance management features are available in the dedicated governance dashboard.
                </p>
                <Button className="mt-4">
                  Open Governance Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Settings</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Settings className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Security configuration and settings management.
                </p>
                <Button className="mt-4">
                  Open Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
