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
  FileText, 
  CheckCircle, 
  AlertTriangle, 
  Clock, 
  Users, 
  TrendingUp, 
  BarChart3,
  Settings,
  BookOpen,
  Target,
  AlertCircle,
  Calendar,
  UserCheck,
  FileCheck,
  Award,
  Activity
} from 'lucide-react';

interface SecurityGovernanceStats {
  totalGovernance: number;
  totalFrameworks: number;
  totalPolicies: number;
  totalAssessments: number;
  complianceRate: number;
  riskLevel: string;
  upcomingReviews: number;
  overdueItems: number;
}

interface SecurityGovernance {
  id: string;
  name: string;
  description: string;
  type: string;
  category: string;
  status: string;
  version: string;
  effectiveDate: string;
  reviewDate: string;
  owner: string;
  stakeholders: string[];
  tags: string[];
  metrics: {
    views: number;
    downloads: number;
    acknowledgments: number;
    violations: number;
    effectiveness: number;
    compliance: number;
  };
}

interface SecurityFramework {
  id: string;
  name: string;
  version: string;
  description: string;
  type: string;
  category: string;
  status: string;
  controls: number;
  compliance: {
    overall: number;
    byCategory: Record<string, number>;
    byPriority: Record<string, number>;
  };
}

interface SecurityPolicy {
  id: string;
  name: string;
  description: string;
  type: string;
  category: string;
  status: string;
  version: string;
  effectiveDate: string;
  reviewDate: string;
  owner: string;
  metrics: {
    awareness: number;
    compliance: number;
    violations: number;
    exceptions: number;
    effectiveness: number;
  };
}

export default function SecurityGovernanceDashboard() {
  const [stats, setStats] = useState<SecurityGovernanceStats | null>(null);
  const [governance, setGovernance] = useState<SecurityGovernance[]>([]);
  const [frameworks, setFrameworks] = useState<SecurityFramework[]>([]);
  const [policies, setPolicies] = useState<SecurityPolicy[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadGovernanceData();
  }, []);

  const loadGovernanceData = async () => {
    try {
      setLoading(true);
      
      // Simulate API calls
      const [statsRes, governanceRes, frameworksRes, policiesRes] = await Promise.all([
        fetch('/api/security/governance/stats'),
        fetch('/api/security/governance/list'),
        fetch('/api/security/frameworks/list'),
        fetch('/api/security/policies/list')
      ]);

      const [statsData, governanceData, frameworksData, policiesData] = await Promise.all([
        statsRes.json(),
        governanceRes.json(),
        frameworksRes.json(),
        policiesRes.json()
      ]);

      setStats(statsData);
      setGovernance(governanceData);
      setFrameworks(frameworksData);
      setPolicies(policiesData);
    } catch (error) {
      console.error('Error loading governance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'approved': return 'bg-blue-100 text-blue-800';
      case 'review': return 'bg-yellow-100 text-yellow-800';
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'deprecated': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
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
          <h1 className="text-3xl font-bold text-gray-900">Security Governance</h1>
          <p className="text-gray-600">Comprehensive security governance, compliance, and policy management</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" size="sm">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button size="sm">
            <FileText className="h-4 w-4 mr-2" />
            New Policy
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
                  <p className="text-sm font-medium text-gray-600">Total Governance</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalGovernance}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <BookOpen className="h-8 w-8 text-green-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Frameworks</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalFrameworks}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <FileText className="h-8 w-8 text-purple-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Policies</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.totalPolicies}</p>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center">
                <Target className="h-8 w-8 text-orange-600" />
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Compliance Rate</p>
                  <p className="text-2xl font-bold text-gray-900">{stats.complianceRate.toFixed(1)}%</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Alerts */}
      {stats && (stats.upcomingReviews > 0 || stats.overdueItems > 0) && (
        <div className="space-y-2">
          {stats.upcomingReviews > 0 && (
            <Alert>
              <Clock className="h-4 w-4" />
              <AlertDescription>
                {stats.upcomingReviews} governance items require review in the next 30 days.
              </AlertDescription>
            </Alert>
          )}
          {stats.overdueItems > 0 && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {stats.overdueItems} governance items are overdue for review.
              </AlertDescription>
            </Alert>
          )}
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="governance">Governance</TabsTrigger>
          <TabsTrigger value="frameworks">Frameworks</TabsTrigger>
          <TabsTrigger value="policies">Policies</TabsTrigger>
          <TabsTrigger value="compliance">Compliance</TabsTrigger>
          <TabsTrigger value="training">Training</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Compliance Overview */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <CheckCircle className="h-5 w-5 mr-2 text-green-600" />
                  Compliance Overview
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Overall Compliance</span>
                    <span className="text-sm text-gray-600">{stats?.complianceRate.toFixed(1)}%</span>
                  </div>
                  <Progress value={stats?.complianceRate || 0} className="h-2" />
                  
                  <div className="grid grid-cols-2 gap-4 mt-4">
                    <div className="text-center">
                      <p className="text-2xl font-bold text-green-600">{stats?.totalAssessments || 0}</p>
                      <p className="text-sm text-gray-600">Assessments</p>
                    </div>
                    <div className="text-center">
                      <p className="text-2xl font-bold text-blue-600">{stats?.upcomingReviews || 0}</p>
                      <p className="text-sm text-gray-600">Upcoming Reviews</p>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Risk Assessment */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <AlertTriangle className="h-5 w-5 mr-2 text-orange-600" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">Risk Level</span>
                    <Badge className={getRiskLevelColor(stats?.riskLevel || 'medium')}>
                      {stats?.riskLevel?.toUpperCase() || 'MEDIUM'}
                    </Badge>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Operational Risk</span>
                      <span>Medium</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Compliance Risk</span>
                      <span>Low</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Financial Risk</span>
                      <span>Low</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Activity className="h-5 w-5 mr-2 text-blue-600" />
                Recent Activity
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Information Security Policy updated</p>
                    <p className="text-xs text-gray-500">2 hours ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">ISO 27001 assessment completed</p>
                    <p className="text-xs text-gray-500">1 day ago</p>
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-yellow-500 rounded-full"></div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Access Control Policy review scheduled</p>
                    <p className="text-xs text-gray-500">3 days ago</p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Governance Tab */}
        <TabsContent value="governance" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Governance Documents</h3>
            <Button size="sm">
              <FileText className="h-4 w-4 mr-2" />
              New Document
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {governance.map((item) => (
              <Card key={item.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm font-medium">{item.name}</CardTitle>
                    <Badge className={getStatusColor(item.status)}>
                      {item.status}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">{item.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Type:</span>
                      <span>{item.type}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Version:</span>
                      <span>{item.version}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Owner:</span>
                      <span>{item.owner}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Review Date:</span>
                      <span>{new Date(item.reviewDate).toLocaleDateString()}</span>
                    </div>
                    <div className="pt-2">
                      <div className="flex justify-between text-xs mb-1">
                        <span>Effectiveness</span>
                        <span>{item.metrics.effectiveness}%</span>
                      </div>
                      <Progress value={item.metrics.effectiveness} className="h-1" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Frameworks Tab */}
        <TabsContent value="frameworks" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Security Frameworks</h3>
            <Button size="sm">
              <BookOpen className="h-4 w-4 mr-2" />
              Add Framework
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {frameworks.map((framework) => (
              <Card key={framework.id} className="hover:shadow-md transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base">{framework.name}</CardTitle>
                    <Badge className={getStatusColor(framework.status)}>
                      {framework.status}
                    </Badge>
                  </div>
                  <CardDescription>{framework.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Version:</span>
                      <span>{framework.version}</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span className="text-gray-500">Controls:</span>
                      <span>{framework.controls}</span>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Overall Compliance</span>
                        <span>{framework.compliance.overall}%</span>
                      </div>
                      <Progress value={framework.compliance.overall} className="h-2" />
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      {Object.entries(framework.compliance.byCategory).map(([category, score]) => (
                        <div key={category} className="flex justify-between">
                          <span className="text-gray-500">{category}:</span>
                          <span>{score.toFixed(0)}%</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Policies Tab */}
        <TabsContent value="policies" className="space-y-4">
          <div className="flex justify-between items-center">
            <h3 className="text-lg font-semibold">Security Policies</h3>
            <Button size="sm">
              <FileText className="h-4 w-4 mr-2" />
              New Policy
            </Button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {policies.map((policy) => (
              <Card key={policy.id} className="hover:shadow-md transition-shadow">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-sm font-medium">{policy.name}</CardTitle>
                    <Badge className={getStatusColor(policy.status)}>
                      {policy.status}
                    </Badge>
                  </div>
                  <CardDescription className="text-xs">{policy.description}</CardDescription>
                </CardHeader>
                <CardContent className="pt-0">
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Type:</span>
                      <span>{policy.type}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Version:</span>
                      <span>{policy.version}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-gray-500">Owner:</span>
                      <span>{policy.owner}</span>
                    </div>
                    <div className="pt-2 space-y-1">
                      <div className="flex justify-between text-xs">
                        <span>Awareness</span>
                        <span>{policy.metrics.awareness}%</span>
                      </div>
                      <Progress value={policy.metrics.awareness} className="h-1" />
                      <div className="flex justify-between text-xs">
                        <span>Compliance</span>
                        <span>{policy.metrics.compliance}%</span>
                      </div>
                      <Progress value={policy.metrics.compliance} className="h-1" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Compliance Tab */}
        <TabsContent value="compliance" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Award className="h-5 w-5 mr-2 text-green-600" />
                  Compliance Status
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-3xl font-bold text-green-600">{stats?.complianceRate.toFixed(1)}%</p>
                    <p className="text-sm text-gray-600">Overall Compliance</p>
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">ISO 27001</span>
                      <Badge className="bg-green-100 text-green-800">Compliant</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">SOC 2</span>
                      <Badge className="bg-yellow-100 text-yellow-800">In Progress</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">GDPR</span>
                      <Badge className="bg-green-100 text-green-800">Compliant</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">PCI DSS</span>
                      <Badge className="bg-red-100 text-red-800">Non-Compliant</Badge>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2 text-blue-600" />
                  Compliance Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">+5.2%</p>
                    <p className="text-sm text-gray-600">vs Last Month</p>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Q1 2024</span>
                      <span>78.5%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Q2 2024</span>
                      <span>82.1%</span>
                    </div>
                    <div className="flex justify-between text-sm">
                      <span>Q3 2024</span>
                      <span>85.3%</span>
                    </div>
                    <div className="flex justify-between text-sm font-medium">
                      <span>Q4 2024</span>
                      <span>87.8%</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Training Tab */}
        <TabsContent value="training" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <UserCheck className="h-5 w-5 mr-2 text-purple-600" />
                  Training Progress
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-center">
                    <div>
                      <p className="text-2xl font-bold text-green-600">120</p>
                      <p className="text-sm text-gray-600">Completed</p>
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-blue-600">30</p>
                      <p className="text-sm text-gray-600">In Progress</p>
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Security Awareness</span>
                      <span>95%</span>
                    </div>
                    <Progress value={95} className="h-2" />
                    
                    <div className="flex justify-between text-sm">
                      <span>Policy Training</span>
                      <span>87%</span>
                    </div>
                    <Progress value={87} className="h-2" />
                    
                    <div className="flex justify-between text-sm">
                      <span>Compliance Training</span>
                      <span>92%</span>
                    </div>
                    <Progress value={92} className="h-2" />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="h-5 w-5 mr-2 text-orange-600" />
                  Upcoming Training
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">GDPR Compliance Training</p>
                      <p className="text-xs text-gray-500">Next Monday, 10:00 AM</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Security Awareness Workshop</p>
                      <p className="text-xs text-gray-500">Next Wednesday, 2:00 PM</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
                    <div className="flex-1">
                      <p className="text-sm font-medium">Incident Response Training</p>
                      <p className="text-xs text-gray-500">Next Friday, 9:00 AM</p>
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