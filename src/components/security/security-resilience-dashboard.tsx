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
  RefreshCw, 
  AlertTriangle, 
  CheckCircle, 
  Clock, 
  Database,
  Server,
  Cloud,
  HardDrive,
  Network,
  Zap,
  Target,
  Activity,
  BarChart3,
  Settings,
  Play,
  Pause,
  Stop,
  TestTube,
  FileText,
  Users,
  Globe,
  Lock,
  TrendingUp,
  AlertCircle,
  Info
} from 'lucide-react';

interface ResilienceStats {
  totalResilience: number;
  totalDisasterRecovery: number;
  totalPlans: number;
  totalRunbooks: number;
  activeTests: number;
  averageRTO: number;
  averageRPO: number;
  averageSLA: number;
}

interface ResilienceItem {
  id: string;
  name: string;
  type: string;
  status: string;
  priority: string;
  rto: number;
  rpo: number;
  sla: number;
  lastTest?: string;
  nextTest?: string;
}

interface DisasterRecoveryItem {
  id: string;
  name: string;
  type: string;
  status: string;
  priority: string;
  rto: number;
  rpo: number;
  sla: number;
  primarySite: string;
  secondarySite: string;
  lastTest?: string;
  nextTest?: string;
}

export default function SecurityResilienceDashboard() {
  const [stats, setStats] = useState<ResilienceStats | null>(null);
  const [resilience, setResilience] = useState<ResilienceItem[]>([]);
  const [disasterRecovery, setDisasterRecovery] = useState<DisasterRecoveryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    loadResilienceData();
    
    if (autoRefresh) {
      const interval = setInterval(loadResilienceData, 30000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const loadResilienceData = async () => {
    try {
      setLoading(true);
      
      const [statsRes, resilienceRes, drRes] = await Promise.all([
        fetch('/api/security/resilience/stats'),
        fetch('/api/security/resilience/list'),
        fetch('/api/security/disaster-recovery/list')
      ]);

      const [statsData, resilienceData, drData] = await Promise.all([
        statsRes.json(),
        resilienceRes.json(),
        drRes.json()
      ]);

      setStats(statsData);
      setResilience(resilienceData);
      setDisasterRecovery(drData);
    } catch (error) {
      console.error('Error loading resilience data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'testing': return 'bg-blue-100 text-blue-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'failed': return 'bg-red-100 text-red-800';
      case 'maintenance': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'medium': return 'text-yellow-600';
      case 'low': return 'text-green-600';
      default: return 'text-gray-600';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'backup': return <HardDrive className="h-4 w-4" />;
      case 'replication': return <Database className="h-4 w-4" />;
      case 'failover': return <RefreshCw className="h-4 w-4" />;
      case 'recovery': return <Zap className="h-4 w-4" />;
      case 'continuity': return <Activity className="h-4 w-4" />;
      case 'redundancy': return <Server className="h-4 w-4" />;
      case 'hot_standby': return <Cloud className="h-4 w-4" />;
      case 'warm_standby': return <Server className="h-4 w-4" />;
      case 'cold_standby': return <HardDrive className="h-4 w-4" />;
      case 'backup_restore': return <RefreshCw className="h-4 w-4" />;
      case 'cloud_failover': return <Cloud className="h-4 w-4" />;
      case 'multi_region': return <Globe className="h-4 w-4" />;
      default: return <Shield className="h-4 w-4" />;
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
          <h1 className="text-3xl font-bold text-gray-900">Security Resilience & Disaster Recovery</h1>
          <p className="text-gray-600">Comprehensive resilience monitoring, testing, and disaster recovery management</p>
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
          <Button variant="outline" size="sm" onClick={loadResilienceData}>
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
                  <p className="text-sm font-medium text-gray-600">Resilience Configs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalResilience}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Cloud className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">DR Configs</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalDisasterRecovery}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <TestTube className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Active Tests</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.activeTests}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Target className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Avg SLA</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.averageSLA.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* RTO/RPO Summary */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-sm">
                <Clock className="h-4 w-4 mr-2 text-blue-600" />
                Average RTO
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-blue-600">{stats.averageRTO.toFixed(1)} min</p>
              <p className="text-xs text-gray-500">Recovery Time Objective</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-sm">
                <Database className="h-4 w-4 mr-2 text-green-600" />
                Average RPO
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-green-600">{stats.averageRPO.toFixed(1)} min</p>
              <p className="text-xs text-gray-500">Recovery Point Objective</p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center text-sm">
                <CheckCircle className="h-4 w-4 mr-2 text-purple-600" />
                SLA Compliance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-purple-600">{stats.averageSLA.toFixed(1)}%</p>
              <p className="text-xs text-gray-500">Service Level Agreement</p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="resilience">Resilience</TabsTrigger>
          <TabsTrigger value="disaster-recovery">Disaster Recovery</TabsTrigger>
          <TabsTrigger value="testing">Testing</TabsTrigger>
          <TabsTrigger value="plans">Plans & Runbooks</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Resilience Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Activity className="h-5 w-5 mr-2 text-blue-600" />
                  Resilience Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Active Configurations</span>
                    <Badge className="bg-green-100 text-green-800">
                      {resilience.filter(r => r.status === 'active').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Testing</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {resilience.filter(r => r.status === 'testing').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Failed</span>
                    <Badge className="bg-red-100 text-red-800">
                      {resilience.filter(r => r.status === 'failed').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Maintenance</span>
                    <Badge className="bg-yellow-100 text-yellow-800">
                      {resilience.filter(r => r.status === 'maintenance').length}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Disaster Recovery Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Cloud className="h-5 w-5 mr-2 text-green-600" />
                  Disaster Recovery Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Active Configurations</span>
                    <Badge className="bg-green-100 text-green-800">
                      {disasterRecovery.filter(d => d.status === 'active').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Testing</span>
                    <Badge className="bg-blue-100 text-blue-800">
                      {disasterRecovery.filter(d => d.status === 'testing').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Failed</span>
                    <Badge className="bg-red-100 text-red-800">
                      {disasterRecovery.filter(d => d.status === 'failed').length}
                    </Badge>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium">Maintenance</span>
                    <Badge className="bg-yellow-100 text-yellow-800">
                      {disasterRecovery.filter(d => d.status === 'maintenance').length}
                    </Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-purple-600" />
                Recent Resilience Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Database backup test completed successfully</p>
                    <p className="text-xs text-gray-500">5 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">DR failover test initiated</p>
                    <p className="text-xs text-gray-500">15 minutes ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Resilience configuration updated</p>
                    <p className="text-xs text-gray-500">1 hour ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">DR test failed - investigating</p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Resilience Tab */}
        <TabsContent value="resilience" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Resilience Configurations</h3>
            <Button size="sm">
              <Shield className="h-4 w-4 mr-2" />
              New Configuration
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {resilience.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(item.type)}
                      <CardTitle className="text-sm font-medium">{item.name}</CardTitle>
                    </div>
                    <Badge className={getStatusColor(item.status)}>
                      {item.status}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs capitalize">{item.type.replace('_', ' ')}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Priority:</span>
                      <span className={getPriorityColor(item.priority)}>{item.priority}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">RTO:</span>
                      <span>{item.rto} min</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">RPO:</span>
                      <span>{item.rpo} min</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">SLA:</span>
                      <span>{item.sla}%</span>
                    </div>
                    {item.lastTest && (
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Last Test:</span>
                        <span>{new Date(item.lastTest).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Disaster Recovery Tab */}
        <TabsContent value="disaster-recovery" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Disaster Recovery Configurations</h3>
            <Button size="sm">
              <Cloud className="h-4 w-4 mr-2" />
              New DR Configuration
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {disasterRecovery.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      {getTypeIcon(item.type)}
                      <CardTitle className="text-sm font-medium">{item.name}</CardTitle>
                    </div>
                    <Badge className={getStatusColor(item.status)}>
                      {item.status}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs capitalize">{item.type.replace('_', ' ')}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Priority:</span>
                      <span className={getPriorityColor(item.priority)}>{item.priority}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Primary Site:</span>
                      <span>{item.primarySite}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Secondary Site:</span>
                      <span>{item.secondarySite}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">RTO:</span>
                      <span>{item.rto} min</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">RPO:</span>
                      <span>{item.rpo} min</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">SLA:</span>
                      <span>{item.sla}%</span>
                    </div>
                    {item.lastTest && (
                      <div className="flex justify-between text-xs">
                        <span className="text-gray-500">Last Test:</span>
                        <span>{new Date(item.lastTest).toLocaleDateString()}</span>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Testing Tab */}
        <TabsContent value="testing" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TestTube className="h-5 w-5 mr-2 text-blue-600" />
                  Resilience Testing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">
                      {resilience.filter(r => r.status === 'testing').length}
                    </p>
                    <p className="text-sm text-gray-600">Active Tests</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Tests Today</span>
                      <span>12</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Successful</span>
                      <span className="text-green-600">10</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Failed</span>
                      <span className="text-red-600">2</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Success Rate</span>
                      <span className="text-green-600">83.3%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Cloud className="h-5 w-5 mr-2 text-green-600" />
                  DR Testing
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">
                      {disasterRecovery.filter(d => d.status === 'testing').length}
                    </p>
                    <p className="text-sm text-gray-600">Active DR Tests</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Tests This Month</span>
                      <span>8</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Successful</span>
                      <span className="text-green-600">7</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Failed</span>
                      <span className="text-red-600">1</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Success Rate</span>
                      <span className="text-green-600">87.5%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Test Schedule */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Clock className="h-5 w-5 mr-2 text-purple-600" />
                Upcoming Tests
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Database backup test</p>
                    <p className="text-xs text-gray-500">Tomorrow, 2:00 AM</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">DR failover test</p>
                    <p className="text-xs text-gray-500">Next Friday, 10:00 AM</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Resilience configuration test</p>
                    <p className="text-xs text-gray-500">Next Monday, 3:00 PM</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Plans & Runbooks Tab */}
        <TabsContent value="plans" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Disaster Recovery Plans
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-blue-600">{stats?.totalPlans || 0}</p>
                    <p className="text-sm text-gray-600">Total Plans</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Active</span>
                      <span>8</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Draft</span>
                      <span>3</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Under Review</span>
                      <span>2</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Deprecated</span>
                      <span>1</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="h-5 w-5 mr-2 text-green-600" />
                  Runbooks
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">{stats?.totalRunbooks || 0}</p>
                    <p className="text-sm text-gray-600">Total Runbooks</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Active</span>
                      <span>15</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Draft</span>
                      <span>5</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Under Review</span>
                      <span>3</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Deprecated</span>
                      <span>2</span>
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
