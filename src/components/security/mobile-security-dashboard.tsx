'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
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
  Menu,
  X,
  ChevronRight,
  ChevronDown
} from 'lucide-react';

interface MobileSecurityData {
  status: 'healthy' | 'warning' | 'critical';
  metrics: {
    threats: number;
    blocked: number;
    users: number;
    uptime: number;
  };
  alerts: Array<{
    id: string;
    title: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    time: string;
    description: string;
  }>;
  recentActivity: Array<{
    id: string;
    action: string;
    user: string;
    time: string;
    status: 'success' | 'warning' | 'error';
  }>;
  systemHealth: Array<{
    name: string;
    status: 'healthy' | 'warning' | 'critical';
    uptime: number;
  }>;
}

export function MobileSecurityDashboard() {
  const [data, setData] = useState<MobileSecurityData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  useEffect(() => {
    loadSecurityData();
    const interval = setInterval(loadSecurityData, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadSecurityData = async () => {
    try {
      setIsLoading(true);
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const mockData: MobileSecurityData = {
        status: Math.random() > 0.8 ? 'critical' : Math.random() > 0.6 ? 'warning' : 'healthy',
        metrics: {
          threats: Math.floor(Math.random() * 50) + 10,
          blocked: Math.floor(Math.random() * 45) + 8,
          users: Math.floor(Math.random() * 100) + 50,
          uptime: 95 + Math.random() * 5,
        },
        alerts: [
          {
            id: '1',
            title: 'Suspicious Login Attempt',
            severity: 'high',
            time: '2 minutes ago',
            description: 'Multiple failed login attempts detected from IP 192.168.1.100',
          },
          {
            id: '2',
            title: 'Threat Blocked',
            severity: 'medium',
            time: '5 minutes ago',
            description: 'SQL injection attempt blocked successfully',
          },
          {
            id: '3',
            title: 'System Update Available',
            severity: 'low',
            time: '1 hour ago',
            description: 'Security patch available for installation',
          },
        ],
        recentActivity: [
          {
            id: '1',
            action: 'User Login',
            user: 'admin@company.com',
            time: '1 minute ago',
            status: 'success',
          },
          {
            id: '2',
            action: 'Threat Detection',
            user: 'System',
            time: '3 minutes ago',
            status: 'warning',
          },
          {
            id: '3',
            action: 'Configuration Update',
            user: 'security@company.com',
            time: '10 minutes ago',
            status: 'success',
          },
        ],
        systemHealth: [
          { name: 'Authentication', status: 'healthy', uptime: 99.9 },
          { name: 'Threat Detection', status: 'healthy', uptime: 99.8 },
          { name: 'Encryption', status: 'warning', uptime: 98.5 },
          { name: 'Monitoring', status: 'healthy', uptime: 99.7 },
        ],
      };
      
      setData(mockData);
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to load security data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return 'text-green-600 bg-green-100';
      case 'warning':
        return 'text-yellow-600 bg-yellow-100';
      case 'critical':
      case 'error':
        return 'text-red-600 bg-red-100';
      case 'low':
        return 'text-blue-600 bg-blue-100';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100';
      case 'high':
        return 'text-orange-600 bg-orange-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'warning':
        return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
      case 'critical':
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-600" />;
      default:
        return <Activity className="h-4 w-4 text-gray-600" />;
    }
  };

  if (!data) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading security data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Mobile Header */}
      <div className="sticky top-0 z-50 bg-background border-b p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden"
            >
              {isMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            <div>
              <h1 className="text-lg font-bold">Security Dashboard</h1>
              <p className="text-xs text-muted-foreground">
                {lastUpdate && `Updated ${lastUpdate.toLocaleTimeString()}`}
              </p>
            </div>
          </div>
          <Button variant="outline" size="sm" onClick={loadSecurityData} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="fixed inset-0 z-40 bg-background md:hidden">
          <div className="p-4 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold">Security Menu</h2>
              <Button variant="ghost" size="sm" onClick={() => setIsMenuOpen(false)}>
                <X className="h-5 w-5" />
              </Button>
            </div>
            <div className="space-y-2">
              {[
                { id: 'overview', name: 'Overview', icon: BarChart3 },
                { id: 'threats', name: 'Threats', icon: Shield },
                { id: 'users', name: 'Users', icon: Users },
                { id: 'system', name: 'System', icon: Monitor },
                { id: 'alerts', name: 'Alerts', icon: Bell },
                { id: 'settings', name: 'Settings', icon: Settings },
              ].map((item) => (
                <Button
                  key={item.id}
                  variant="ghost"
                  className="w-full justify-start"
                  onClick={() => {
                    toggleSection(item.id);
                    setIsMenuOpen(false);
                  }}
                >
                  <item.icon className="h-4 w-4 mr-3" />
                  {item.name}
                </Button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="p-4 space-y-4">
        {/* Status Overview */}
        <Card>
          <CardHeader className="pb-3">
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Security Status</CardTitle>
              <Badge className={getStatusColor(data.status)}>
                {data.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{data.metrics.threats}</div>
                <div className="text-xs text-muted-foreground">Threats</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{data.metrics.blocked}</div>
                <div className="text-xs text-muted-foreground">Blocked</div>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{data.metrics.users}</div>
                <div className="text-xs text-muted-foreground">Users</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{data.metrics.uptime.toFixed(1)}%</div>
                <div className="text-xs text-muted-foreground">Uptime</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Alerts Section */}
        <Card>
          <CardHeader 
            className="pb-3 cursor-pointer"
            onClick={() => toggleSection('alerts')}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Security Alerts</CardTitle>
              <div className="flex items-center gap-2">
                <Badge variant="outline">{data.alerts.length}</Badge>
                {expandedSections.has('alerts') ? 
                  <ChevronDown className="h-4 w-4" /> : 
                  <ChevronRight className="h-4 w-4" />
                }
              </div>
            </div>
          </CardHeader>
          {expandedSections.has('alerts') && (
            <CardContent className="space-y-3">
              {data.alerts.map((alert) => (
                <div key={alert.id} className="p-3 border rounded-lg">
                  <div className="flex items-start gap-3">
                    {getStatusIcon(alert.severity)}
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-sm">{alert.title}</div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {alert.description}
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <Badge className={getStatusColor(alert.severity)} size="sm">
                          {alert.severity}
                        </Badge>
                        <span className="text-xs text-muted-foreground">{alert.time}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          )}
        </Card>

        {/* Recent Activity Section */}
        <Card>
          <CardHeader 
            className="pb-3 cursor-pointer"
            onClick={() => toggleSection('activity')}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">Recent Activity</CardTitle>
              {expandedSections.has('activity') ? 
                <ChevronDown className="h-4 w-4" /> : 
                <ChevronRight className="h-4 w-4" />
              }
            </div>
          </CardHeader>
          {expandedSections.has('activity') && (
            <CardContent className="space-y-3">
              {data.recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-center gap-3 p-2">
                  {getStatusIcon(activity.status)}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium">{activity.action}</div>
                    <div className="text-xs text-muted-foreground">{activity.user}</div>
                  </div>
                  <div className="text-xs text-muted-foreground">{activity.time}</div>
                </div>
              ))}
            </CardContent>
          )}
        </Card>

        {/* System Health Section */}
        <Card>
          <CardHeader 
            className="pb-3 cursor-pointer"
            onClick={() => toggleSection('system')}
          >
            <div className="flex items-center justify-between">
              <CardTitle className="text-base">System Health</CardTitle>
              {expandedSections.has('system') ? 
                <ChevronDown className="h-4 w-4" /> : 
                <ChevronRight className="h-4 w-4" />
              }
            </div>
          </CardHeader>
          {expandedSections.has('system') && (
            <CardContent className="space-y-3">
              {data.systemHealth.map((component, index) => (
                <div key={index} className="flex items-center justify-between p-2">
                  <div className="flex items-center gap-3">
                    {getStatusIcon(component.status)}
                    <span className="text-sm font-medium">{component.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="text-xs text-muted-foreground">
                      {component.uptime.toFixed(1)}%
                    </span>
                    <Badge className={getStatusColor(component.status)} size="sm">
                      {component.status}
                    </Badge>
                  </div>
                </div>
              ))}
            </CardContent>
          )}
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              <Button variant="outline" size="sm" className="h-12">
                <Shield className="h-4 w-4 mr-2" />
                Block IP
              </Button>
              <Button variant="outline" size="sm" className="h-12">
                <Users className="h-4 w-4 mr-2" />
                Manage Users
              </Button>
              <Button variant="outline" size="sm" className="h-12">
                <Settings className="h-4 w-4 mr-2" />
                Settings
              </Button>
              <Button variant="outline" size="sm" className="h-12">
                <BarChart3 className="h-4 w-4 mr-2" />
                Reports
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Bottom Navigation - Hidden on desktop */}
      <div className="fixed bottom-0 left-0 right-0 bg-background border-t p-2 md:hidden">
        <div className="grid grid-cols-4 gap-2">
          <Button variant="ghost" size="sm" className="h-12 flex-col">
            <BarChart3 className="h-4 w-4 mb-1" />
            <span className="text-xs">Overview</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-12 flex-col">
            <Shield className="h-4 w-4 mb-1" />
            <span className="text-xs">Threats</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-12 flex-col">
            <Users className="h-4 w-4 mb-1" />
            <span className="text-xs">Users</span>
          </Button>
          <Button variant="ghost" size="sm" className="h-12 flex-col">
            <Settings className="h-4 w-4 mb-1" />
            <span className="text-xs">Settings</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
