'use client';

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Shield, 
  Brain, 
  Search, 
  FileText, 
  Zap, 
  Lock, 
  Network, 
  Smartphone,
  Cloud,
  Database,
  Globe,
  Cpu,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';

interface SecurityStats {
  intelligence: {
    total_intelligence: number;
    active_intelligence: number;
    threat_hunts: { total: number; active: number; findings: number };
  };
  forensics: {
    total_incidents: number;
    active_incidents: number;
    total_evidence: number;
  };
  resilience: {
    total_resilience: number;
    active_resilience: number;
    average_availability: number;
  };
  ai: {
    total_models: number;
    active_models: number;
    average_accuracy: number;
  };
  quantum: {
    total_keys: number;
    active_keys: number;
    algorithms_used: Record<string, number>;
  };
  blockchain: {
    total_nodes: number;
    active_nodes: number;
    audited_contracts: number;
  };
  iot: {
    total_devices: number;
    online_devices: number;
    critical_events: number;
  };
  cloud: {
    total_providers: number;
    active_providers: number;
    total_services: number;
  };
  devsecops: {
    total_pipelines: number;
    active_pipelines: number;
    total_scans: number;
  };
  edge: {
    total_nodes: number;
    online_nodes: number;
    critical_events: number;
  };
  mobile: {
    total_devices: number;
    active_devices: number;
    critical_events: number;
  };
  api: {
    total_configs: number;
    total_events: number;
    critical_events: number;
  };
  database: {
    total_configs: number;
    total_events: number;
    critical_events: number;
  };
  network: {
    total_configs: number;
    total_events: number;
    critical_events: number;
  };
}

export default function AdvancedSecurityDashboard() {
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSecurityStats();
    const interval = setInterval(fetchSecurityStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchSecurityStats = async () => {
    try {
      setLoading(true);
      const responses = await Promise.all([
        fetch('/api/security/intelligence?action=stats'),
        fetch('/api/security/forensics?action=stats'),
        fetch('/api/security/resilience?action=stats'),
        fetch('/api/security/ai?action=stats'),
        fetch('/api/security/quantum?action=stats'),
        fetch('/api/security/blockchain?action=stats'),
        fetch('/api/security/iot?action=stats'),
        fetch('/api/security/cloud?action=stats'),
        fetch('/api/security/devsecops?action=stats'),
        fetch('/api/security/edge?action=stats'),
        fetch('/api/security/mobile?action=stats'),
        fetch('/api/security/api?action=stats'),
        fetch('/api/security/database?action=stats'),
        fetch('/api/security/network?action=stats'),
      ]);

      const data = await Promise.all(responses.map(r => r.json()));
      
      setStats({
        intelligence: data[0].data,
        forensics: data[1].data,
        resilience: data[2].data,
        ai: data[3].data,
        quantum: data[4].data,
        blockchain: data[5].data,
        iot: data[6].data,
        cloud: data[7].data,
        devsecops: data[8].data,
        edge: data[9].data,
        mobile: data[10].data,
        api: data[11].data,
        database: data[12].data,
        network: data[13].data,
      });
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch security statistics');
      console.error('Error fetching security stats:', err);
    } finally {
      setLoading(false);
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
      <Alert className="mb-4">
        <AlertTriangle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!stats) return null;

  const StatCard = ({ 
    title, 
    value, 
    icon: Icon, 
    color = "blue",
    subtitle,
    trend
  }: {
    title: string;
    value: number | string;
    icon: React.ComponentType<any>;
    color?: string;
    subtitle?: string;
    trend?: 'up' | 'down' | 'neutral';
  }) => (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className={`h-4 w-4 text-${color}-600`} />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
        {trend && (
          <div className={`text-xs ${trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-600'}`}>
            {trend === 'up' ? '↗' : trend === 'down' ? '↘' : '→'} {trend}
          </div>
        )}
      </CardContent>
    </Card>
  );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Advanced Security Dashboard</h1>
          <p className="text-muted-foreground">
            Comprehensive security monitoring and management across all domains
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <CheckCircle className="h-4 w-4 text-green-600" />
          <span className="text-sm text-green-600">All systems operational</span>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="intelligence">Intelligence</TabsTrigger>
          <TabsTrigger value="forensics">Forensics</TabsTrigger>
          <TabsTrigger value="resilience">Resilience</TabsTrigger>
          <TabsTrigger value="ai">AI Security</TabsTrigger>
          <TabsTrigger value="quantum">Quantum</TabsTrigger>
          <TabsTrigger value="blockchain">Blockchain</TabsTrigger>
          <TabsTrigger value="iot">IoT</TabsTrigger>
          <TabsTrigger value="cloud">Cloud</TabsTrigger>
          <TabsTrigger value="devsecops">DevSecOps</TabsTrigger>
          <TabsTrigger value="edge">Edge</TabsTrigger>
          <TabsTrigger value="mobile">Mobile</TabsTrigger>
          <TabsTrigger value="api">API</TabsTrigger>
          <TabsTrigger value="database">Database</TabsTrigger>
          <TabsTrigger value="network">Network</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Security Modules"
              value="14"
              icon={Shield}
              color="blue"
              subtitle="All security domains covered"
            />
            <StatCard
              title="Active Threats"
              value={stats.intelligence.active_intelligence}
              icon={AlertTriangle}
              color="red"
              subtitle="Currently monitored"
            />
            <StatCard
              title="Security Incidents"
              value={stats.forensics.active_incidents}
              icon={FileText}
              color="orange"
              subtitle="Under investigation"
            />
            <StatCard
              title="System Availability"
              value={`${stats.resilience.average_availability.toFixed(1)}%`}
              icon={CheckCircle}
              color="green"
              subtitle="Overall uptime"
            />
          </div>

          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Brain className="h-5 w-5" />
                  <span>AI Security Models</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Active Models</span>
                    <span>{stats.ai.active_models}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Average Accuracy</span>
                    <span>{stats.ai.average_accuracy.toFixed(1)}%</span>
                  </div>
                  <Progress value={stats.ai.average_accuracy} className="w-full" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Network className="h-5 w-5" />
                  <span>IoT Devices</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Total Devices</span>
                    <span>{stats.iot.total_devices}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Online</span>
                    <span>{stats.iot.online_devices}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Critical Events</span>
                    <span className="text-red-600">{stats.iot.critical_events}</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Cloud className="h-5 w-5" />
                  <span>Cloud Security</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span>Providers</span>
                    <span>{stats.cloud.total_providers}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Services</span>
                    <span>{stats.cloud.total_services}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Active</span>
                    <span>{stats.cloud.active_providers}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="intelligence" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Intelligence"
              value={stats.intelligence.total_intelligence}
              icon={Search}
              color="blue"
            />
            <StatCard
              title="Active Intelligence"
              value={stats.intelligence.active_intelligence}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Threat Hunts"
              value={stats.intelligence.threat_hunts.total}
              icon={FileText}
              color="purple"
            />
            <StatCard
              title="Findings"
              value={stats.intelligence.threat_hunts.findings}
              icon={CheckCircle}
              color="green"
            />
          </div>
        </TabsContent>

        <TabsContent value="forensics" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Incidents"
              value={stats.forensics.total_incidents}
              icon={FileText}
              color="blue"
            />
            <StatCard
              title="Active Incidents"
              value={stats.forensics.active_incidents}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Total Evidence"
              value={stats.forensics.total_evidence}
              icon={Shield}
              color="green"
            />
            <StatCard
              title="Analyses"
              value={stats.forensics.total_analyses}
              icon={Brain}
              color="purple"
            />
          </div>
        </TabsContent>

        <TabsContent value="resilience" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Resilience"
              value={stats.resilience.total_resilience}
              icon={Zap}
              color="blue"
            />
            <StatCard
              title="Active Resilience"
              value={stats.resilience.active_resilience}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Average Availability"
              value={`${stats.resilience.average_availability.toFixed(1)}%`}
              icon={Clock}
              color="green"
            />
            <StatCard
              title="Disaster Recovery"
              value={stats.resilience.total_disaster_recovery}
              icon={Shield}
              color="purple"
            />
          </div>
        </TabsContent>

        <TabsContent value="ai" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Models"
              value={stats.ai.total_models}
              icon={Brain}
              color="blue"
            />
            <StatCard
              title="Active Models"
              value={stats.ai.active_models}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Predictions"
              value={stats.ai.total_predictions}
              icon={Zap}
              color="purple"
            />
            <StatCard
              title="Average Accuracy"
              value={`${stats.ai.average_accuracy.toFixed(1)}%`}
              icon={Brain}
              color="green"
            />
          </div>
        </TabsContent>

        <TabsContent value="quantum" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Keys"
              value={stats.quantum.total_keys}
              icon={Lock}
              color="blue"
            />
            <StatCard
              title="Active Keys"
              value={stats.quantum.active_keys}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Signatures"
              value={stats.quantum.total_signatures}
              icon={Shield}
              color="purple"
            />
            <StatCard
              title="Verified"
              value={stats.quantum.verified_signatures}
              icon={CheckCircle}
              color="green"
            />
          </div>
        </TabsContent>

        <TabsContent value="blockchain" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Nodes"
              value={stats.blockchain.total_nodes}
              icon={Network}
              color="blue"
            />
            <StatCard
              title="Active Nodes"
              value={stats.blockchain.active_nodes}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Transactions"
              value={stats.blockchain.total_transactions}
              icon={Zap}
              color="purple"
            />
            <StatCard
              title="Audited Contracts"
              value={stats.blockchain.audited_contracts}
              icon={Shield}
              color="green"
            />
          </div>
        </TabsContent>

        <TabsContent value="iot" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Devices"
              value={stats.iot.total_devices}
              icon={Cpu}
              color="blue"
            />
            <StatCard
              title="Online Devices"
              value={stats.iot.online_devices}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Total Events"
              value={stats.iot.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.iot.critical_events}
              icon={XCircle}
              color="red"
            />
          </div>
        </TabsContent>

        <TabsContent value="cloud" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Providers"
              value={stats.cloud.total_providers}
              icon={Cloud}
              color="blue"
            />
            <StatCard
              title="Active Providers"
              value={stats.cloud.active_providers}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Total Services"
              value={stats.cloud.total_services}
              icon={Zap}
              color="purple"
            />
            <StatCard
              title="Critical Events"
              value={stats.cloud.critical_events}
              icon={XCircle}
              color="red"
            />
          </div>
        </TabsContent>

        <TabsContent value="devsecops" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Pipelines"
              value={stats.devsecops.total_pipelines}
              icon={Zap}
              color="blue"
            />
            <StatCard
              title="Active Pipelines"
              value={stats.devsecops.active_pipelines}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Total Tools"
              value={stats.devsecops.total_tools}
              icon={Shield}
              color="purple"
            />
            <StatCard
              title="Total Scans"
              value={stats.devsecops.total_scans}
              icon={Search}
              color="orange"
            />
          </div>
        </TabsContent>

        <TabsContent value="edge" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Nodes"
              value={stats.edge.total_nodes}
              icon={Network}
              color="blue"
            />
            <StatCard
              title="Online Nodes"
              value={stats.edge.online_nodes}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Total Events"
              value={stats.edge.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.edge.critical_events}
              icon={XCircle}
              color="red"
            />
          </div>
        </TabsContent>

        <TabsContent value="mobile" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Devices"
              value={stats.mobile.total_devices}
              icon={Smartphone}
              color="blue"
            />
            <StatCard
              title="Active Devices"
              value={stats.mobile.active_devices}
              icon={CheckCircle}
              color="green"
            />
            <StatCard
              title="Total Events"
              value={stats.mobile.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.mobile.critical_events}
              icon={XCircle}
              color="red"
            />
          </div>
        </TabsContent>

        <TabsContent value="api" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Configs"
              value={stats.api.total_configs}
              icon={Globe}
              color="blue"
            />
            <StatCard
              title="Total Events"
              value={stats.api.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.api.critical_events}
              icon={XCircle}
              color="red"
            />
            <StatCard
              title="Total Rules"
              value={stats.api.total_rules}
              icon={Shield}
              color="purple"
            />
          </div>
        </TabsContent>

        <TabsContent value="database" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Configs"
              value={stats.database.total_configs}
              icon={Database}
              color="blue"
            />
            <StatCard
              title="Total Events"
              value={stats.database.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.database.critical_events}
              icon={XCircle}
              color="red"
            />
            <StatCard
              title="Databases by Type"
              value={Object.keys(stats.database.databases_by_type).length}
              icon={Database}
              color="green"
            />
          </div>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <StatCard
              title="Total Configs"
              value={stats.network.total_configs}
              icon={Network}
              color="blue"
            />
            <StatCard
              title="Total Events"
              value={stats.network.total_events}
              icon={AlertTriangle}
              color="orange"
            />
            <StatCard
              title="Critical Events"
              value={stats.network.critical_events}
              icon={XCircle}
              color="red"
            />
            <StatCard
              title="Networks by Type"
              value={Object.keys(stats.network.networks_by_type).length}
              icon={Network}
              color="green"
            />
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}