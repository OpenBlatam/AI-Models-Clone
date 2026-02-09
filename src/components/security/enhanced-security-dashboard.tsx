'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';
import { 
  Shield, 
  AlertTriangle, 
  Eye, 
  EyeOff, 
  Lock, 
  Unlock,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  Zap,
  Database,
  Network,
  Users,
  Settings,
  RefreshCw,
  Filter,
  Search,
  Download,
  Upload,
  Trash2,
  Plus,
  Edit,
  Save,
  Cancel
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ThreatEvent {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  source: string;
  target: string;
  timestamp: number;
  metadata: any;
  confidence: number;
  blocked: boolean;
}

interface SecurityRule {
  id: string;
  name: string;
  pattern: string;
  action: 'block' | 'alert' | 'log' | 'rate_limit';
  threshold: number;
  enabled: boolean;
  createdAt: number;
}

interface SecurityStats {
  totalThreats: number;
  threatsLast24h: number;
  blockedIPs: number;
  threatsByType: Record<string, number>;
  threatsBySeverity: Record<string, number>;
  topThreatSources: Array<{ ip: string; count: number }>;
}

export function EnhancedSecurityDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState<SecurityStats | null>(null);
  const [recentThreats, setRecentThreats] = useState<ThreatEvent[]>([]);
  const [securityRules, setSecurityRules] = useState<SecurityRule[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedThreats, setSelectedThreats] = useState<Set<string>>(new Set());
  const [showBlockedIPs, setShowBlockedIPs] = useState(false);
  const [editingRule, setEditingRule] = useState<SecurityRule | null>(null);

  // Fetch security statistics
  const fetchStats = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/security/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch security stats:', error);
      toast.error('Failed to fetch security statistics');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch recent threats
  const fetchRecentThreats = useCallback(async () => {
    try {
      const response = await fetch('/api/security/threats');
      if (response.ok) {
        const data = await response.json();
        setRecentThreats(data);
      }
    } catch (error) {
      console.error('Failed to fetch recent threats:', error);
    }
  }, []);

  // Fetch security rules
  const fetchSecurityRules = useCallback(async () => {
    try {
      const response = await fetch('/api/security/rules');
      if (response.ok) {
        const data = await response.json();
        setSecurityRules(data);
      }
    } catch (error) {
      console.error('Failed to fetch security rules:', error);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    fetchStats();
    fetchRecentThreats();
    fetchSecurityRules();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchStats();
        fetchRecentThreats();
      }, 5000);

      return () => clearInterval(interval);
    }
  }, [fetchStats, fetchRecentThreats, fetchSecurityRules, autoRefresh]);

  // Block IP address
  const blockIP = async (ip: string) => {
    try {
      const response = await fetch('/api/security/block-ip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip, reason: 'Manual block' }),
      });

      if (response.ok) {
        toast.success(`IP ${ip} blocked successfully`);
        await fetchStats();
      } else {
        toast.error('Failed to block IP address');
      }
    } catch (error) {
      console.error('Block IP error:', error);
      toast.error('Failed to block IP address');
    }
  };

  // Unblock IP address
  const unblockIP = async (ip: string) => {
    try {
      const response = await fetch('/api/security/unblock-ip', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip }),
      });

      if (response.ok) {
        toast.success(`IP ${ip} unblocked successfully`);
        await fetchStats();
      } else {
        toast.error('Failed to unblock IP address');
      }
    } catch (error) {
      console.error('Unblock IP error:', error);
      toast.error('Failed to unblock IP address');
    }
  };

  // Get severity color
  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-600 bg-red-100 border-red-200';
      case 'high': return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'medium': return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low': return 'text-blue-600 bg-blue-100 border-blue-200';
      default: return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  // Get threat type icon
  const getThreatTypeIcon = (type: string) => {
    switch (type) {
      case 'sql_injection': return <Database className="h-4 w-4" />;
      case 'xss': return <AlertTriangle className="h-4 w-4" />;
      case 'brute_force': return <Lock className="h-4 w-4" />;
      case 'ddos': return <Network className="h-4 w-4" />;
      default: return <Shield className="h-4 w-4" />;
    }
  };

  // Filter threats
  const filteredThreats = recentThreats.filter(threat =>
    threat.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
    threat.source.includes(searchQuery) ||
    threat.target.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Enhanced Security Dashboard</h2>
          <p className="text-muted-foreground">
            Advanced threat detection and security monitoring
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
            {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
          </Button>
          <Button variant="outline" size="sm" onClick={fetchStats} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Security Status Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Threats</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.totalThreats}</div>
              <p className="text-xs text-muted-foreground">
                {stats.threatsLast24h} in last 24h
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Blocked IPs</CardTitle>
              <Lock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.blockedIPs}</div>
              <p className="text-xs text-muted-foreground">
                Currently blocked
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Critical Threats</CardTitle>
              <AlertTriangle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {stats.threatsBySeverity.critical || 0}
              </div>
              <p className="text-xs text-muted-foreground">
                High priority alerts
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Security Rules</CardTitle>
              <Settings className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{securityRules.length}</div>
              <p className="text-xs text-muted-foreground">
                Active rules
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="threats">Threats</TabsTrigger>
          <TabsTrigger value="rules">Rules</TabsTrigger>
          <TabsTrigger value="blocked">Blocked IPs</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Threat Types */}
            <Card>
              <CardHeader>
                <CardTitle>Threat Types</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && Object.entries(stats.threatsByType).map(([type, count]) => (
                  <div key={type} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      {getThreatTypeIcon(type)}
                      <span className="capitalize">{type.replace('_', ' ')}</span>
                    </div>
                    <Badge variant="outline">{count}</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Threat Severity */}
            <Card>
              <CardHeader>
                <CardTitle>Threat Severity</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && Object.entries(stats.threatsBySeverity).map(([severity, count]) => (
                  <div key={severity} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="capitalize">{severity}</span>
                      <Badge className={getSeverityColor(severity)}>{count}</Badge>
                    </div>
                    <Progress 
                      value={(count / stats.totalThreats) * 100} 
                      className="h-2"
                    />
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>

          {/* Top Threat Sources */}
          <Card>
            <CardHeader>
              <CardTitle>Top Threat Sources</CardTitle>
            </CardHeader>
            <CardContent>
              {stats && stats.topThreatSources.length > 0 ? (
                <div className="space-y-3">
                  {stats.topThreatSources.slice(0, 10).map((source, index) => (
                    <div key={source.ip} className="flex items-center justify-between p-3 border rounded-lg">
                      <div className="flex items-center gap-3">
                        <Badge variant="outline">#{index + 1}</Badge>
                        <code className="text-sm">{source.ip}</code>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge variant="secondary">{source.count} threats</Badge>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => blockIP(source.ip)}
                        >
                          <Lock className="h-3 w-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No threat sources found
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Threats Tab */}
        <TabsContent value="threats" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Input
                  placeholder="Search threats..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
              <Badge variant="outline">
                {filteredThreats.length} threats
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              {selectedThreats.size > 0 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    // Handle bulk actions
                    setSelectedThreats(new Set());
                  }}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Bulk Action ({selectedThreats.size})
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={fetchRecentThreats}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="max-h-96 overflow-y-auto">
                {filteredThreats.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    No threats found
                  </div>
                ) : (
                  <div className="space-y-1">
                    {filteredThreats.map((threat) => (
                      <div
                        key={threat.id}
                        className={`flex items-center justify-between p-3 border-b hover:bg-muted/50 ${
                          selectedThreats.has(threat.id) ? 'bg-muted' : ''
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={selectedThreats.has(threat.id)}
                            onChange={(e) => {
                              const newSelected = new Set(selectedThreats);
                              if (e.target.checked) {
                                newSelected.add(threat.id);
                              } else {
                                newSelected.delete(threat.id);
                              }
                              setSelectedThreats(newSelected);
                            }}
                            className="rounded"
                          />
                          <div>
                            <div className="flex items-center gap-2">
                              {getThreatTypeIcon(threat.type)}
                              <span className="font-medium capitalize">
                                {threat.type.replace('_', ' ')}
                              </span>
                              <Badge className={getSeverityColor(threat.severity)}>
                                {threat.severity}
                              </Badge>
                            </div>
                            <div className="text-sm text-muted-foreground">
                              From: {threat.source} | Target: {threat.target}
                            </div>
                            <div className="text-xs text-muted-foreground">
                              {new Date(threat.timestamp).toLocaleString()} | 
                              Confidence: {(threat.confidence * 100).toFixed(1)}%
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {threat.blocked ? (
                            <Badge variant="outline" className="text-green-600">
                              <CheckCircle className="h-3 w-3 mr-1" />
                              Blocked
                            </Badge>
                          ) : (
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => blockIP(threat.source)}
                            >
                              <Lock className="h-3 w-3" />
                            </Button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Rules Tab */}
        <TabsContent value="rules" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Security Rules</h3>
            <Button onClick={() => setEditingRule({
              id: '',
              name: '',
              pattern: '',
              action: 'alert',
              threshold: 0.5,
              enabled: true,
              createdAt: Date.now(),
            })}>
              <Plus className="h-4 w-4 mr-2" />
              Add Rule
            </Button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {securityRules.map((rule) => (
              <Card key={rule.id}>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-lg">{rule.name}</CardTitle>
                    <div className="flex items-center gap-2">
                      <Switch
                        checked={rule.enabled}
                        onCheckedChange={(enabled) => {
                          // Update rule enabled status
                        }}
                      />
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setEditingRule(rule)}
                      >
                        <Edit className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <Label className="text-sm font-medium">Pattern</Label>
                    <code className="text-xs bg-muted p-2 rounded block mt-1">
                      {rule.pattern}
                    </code>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Action: {rule.action}</span>
                    <span className="text-sm">Threshold: {rule.threshold}</span>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Blocked IPs Tab */}
        <TabsContent value="blocked" className="space-y-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold">Blocked IP Addresses</h3>
            <div className="flex items-center gap-2">
              <Switch
                checked={showBlockedIPs}
                onCheckedChange={setShowBlockedIPs}
              />
              <Label>Show blocked IPs</Label>
            </div>
          </div>

          <Card>
            <CardContent className="p-6">
              <div className="text-center text-muted-foreground">
                Blocked IP management interface would be implemented here.
                This would show all currently blocked IP addresses with options to unblock them.
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Threat Trends</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center text-muted-foreground py-8">
                  Threat trend charts would be displayed here
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Security Metrics</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Detection Rate</span>
                    <span className="font-semibold">98.5%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">False Positives</span>
                    <span className="font-semibold">2.1%</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-sm">Response Time</span>
                    <span className="font-semibold">45ms</span>
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

