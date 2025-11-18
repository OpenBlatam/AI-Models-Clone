'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
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
  Monitor
} from 'lucide-react';
import { securityManager } from '@/lib/security';

export function SecurityDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [securityStatus, setSecurityStatus] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(30000); // 30 seconds

  useEffect(() => {
    initializeSecurity();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refreshSecurity();
      }, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const initializeSecurity = async () => {
    try {
      setIsLoading(true);
      await securityManager.initialize();
      const status = securityManager.getSecurityStatus();
      setSecurityStatus(status);
    } catch (error) {
      console.error('Failed to initialize security:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const refreshSecurity = useCallback(async () => {
    try {
      setIsLoading(true);
      const status = securityManager.getSecurityStatus();
      setSecurityStatus(status);
      setLastUpdate(new Date());
      
      // Check for new alerts
      const newAlerts = await fetchSecurityAlerts();
      setAlerts(newAlerts);
    } catch (error) {
      console.error('Failed to refresh security status:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchSecurityAlerts = async () => {
    try {
      const response = await fetch('/api/security/alerts');
      if (response.ok) {
        const data = await response.json();
        return data.alerts || [];
      }
    } catch (error) {
      console.error('Failed to fetch security alerts:', error);
    }
    return [];
  };

  const handleConfigUpdate = async (service: string, config: any) => {
    try {
      await fetch('/api/security', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'update-config',
          service,
          config
        })
      });
      await refreshSecurity();
    } catch (error) {
      console.error('Failed to update configuration:', error);
    }
  };

  if (!securityStatus) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Initializing security services...</p>
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
          <h2 className="text-3xl font-bold tracking-tight">Security Dashboard</h2>
          <p className="text-muted-foreground">
            Comprehensive security monitoring and management
            {lastUpdate && (
              <span className="ml-2 text-xs">
                • Last updated: {lastUpdate.toLocaleTimeString()}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Switch
              checked={autoRefresh}
              onCheckedChange={setAutoRefresh}
              id="auto-refresh"
            />
            <label htmlFor="auto-refresh" className="text-sm">
              Auto-refresh
            </label>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm">Interval:</span>
            <Slider
              value={[refreshInterval / 1000]}
              onValueChange={([value]) => setRefreshInterval(value * 1000)}
              min={5}
              max={300}
              step={5}
              className="w-20"
            />
            <span className="text-xs text-muted-foreground">
              {refreshInterval / 1000}s
            </span>
          </div>
          <Button variant="outline" size="sm" onClick={refreshSecurity} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
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

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-6">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="biometric">Biometric</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="monitoring">Monitoring</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Security Services Status */}
            <Card>
              <CardHeader>
                <CardTitle>Security Services Status</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Fingerprint className="h-4 w-4" />
                    <span className="text-sm">Biometric Authentication</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">
                    {metrics.biometric.isSupported ? 'Supported' : 'Not Supported'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4" />
                    <span className="text-sm">Threat Detection</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Lock className="h-4 w-4" />
                    <span className="text-sm">Zero Trust</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Key className="h-4 w-4" />
                    <span className="text-sm">Encryption</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Eye className="h-4 w-4" />
                    <span className="text-sm">Monitoring</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Workflow className="h-4 w-4" />
                    <span className="text-sm">Orchestration</span>
                  </div>
                  <Badge className="text-green-600 bg-green-100">Active</Badge>
                </div>
              </CardContent>
            </Card>

            {/* Security Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Security Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Detection Rate</span>
                    <span className="text-sm font-medium">98.5%</span>
                  </div>
                  <Progress value={98.5} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">False Positives</span>
                    <span className="text-sm font-medium">2.1%</span>
                  </div>
                  <Progress value={2.1} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Response Time</span>
                    <span className="text-sm font-medium">45ms</span>
                  </div>
                  <Progress value={90} className="h-2" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Uptime</span>
                    <span className="text-sm font-medium">99.9%</span>
                  </div>
                  <Progress value={99.9} className="h-2" />
                </div>
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
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <div>
                      <div className="font-medium">Threat blocked successfully</div>
                      <div className="text-sm text-muted-foreground">
                        SQL injection attempt from 192.168.1.100
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline">2 minutes ago</Badge>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <Fingerprint className="h-4 w-4 text-blue-600" />
                    <div>
                      <div className="font-medium">Biometric authentication successful</div>
                      <div className="text-sm text-muted-foreground">
                        User: john.doe@example.com
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline">5 minutes ago</Badge>
                </div>
                <div className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className="h-4 w-4 text-yellow-600" />
                    <div>
                      <div className="font-medium">Suspicious activity detected</div>
                      <div className="text-sm text-muted-foreground">
                        Multiple failed login attempts
                      </div>
                    </div>
                  </div>
                  <Badge variant="outline">10 minutes ago</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Biometric Tab */}
        <TabsContent value="biometric" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Biometric Authentication</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Fingerprint className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Biometric authentication features are available in the dedicated biometric dashboard.
                </p>
                <Button className="mt-4">
                  Open Biometric Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threats Tab */}
        <TabsContent value="threats" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Threat Detection</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Shield className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Advanced threat detection features are available in the dedicated threat dashboard.
                </p>
                <Button className="mt-4">
                  Open Threat Dashboard
                </Button>
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
                  Real-time security monitoring features are available in the dedicated monitoring dashboard.
                </p>
                <Button className="mt-4">
                  Open Monitoring Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Compliance</CardTitle>
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

        {/* Intelligence Tab */}
        <TabsContent value="intelligence" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Security Intelligence</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-center py-8">
                <Target className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                <p className="text-muted-foreground">
                  Threat intelligence and hunting features are available in the dedicated intelligence dashboard.
                </p>
                <Button className="mt-4">
                  Open Intelligence Dashboard
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}