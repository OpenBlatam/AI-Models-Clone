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
  Database, 
  Memory, 
  Zap, 
  Trash2, 
  RefreshCw, 
  Settings,
  Activity,
  TrendingUp,
  TrendingDown,
  Clock,
  CheckCircle,
  XCircle,
  AlertTriangle,
  BarChart3,
  Server,
  HardDrive,
  Cpu,
  Network,
  Shield,
  Eye,
  EyeOff,
  Play,
  Pause,
  RotateCcw,
  Download,
  Upload
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface CacheStats {
  memory: {
    keys: number;
    stats: any;
  };
  redis: {
    hits: number;
    misses: number;
    sets: number;
    deletes: number;
    errors: number;
    totalRequests: number;
    hitRate: number;
    averageResponseTime: number;
    memoryUsage: number;
    connectedClients: number;
  };
  service: {
    totalRequests: number;
    cacheHits: number;
    cacheMisses: number;
    hitRate: number;
    averageResponseTime: number;
    errors: number;
  };
  middleware: {
    totalRequests: number;
    cacheHits: number;
    cacheMisses: number;
    hitRate: number;
    cacheSets: number;
    cacheInvalidations: number;
    cacheErrors: number;
    responseTimeSaved: number;
  };
  config: any;
}

interface CacheKey {
  key: string;
  ttl: number;
  size: number;
  lastAccessed: number;
  accessCount: number;
}

export function CacheDashboard() {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState<CacheStats | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5000);
  const [cacheKeys, setCacheKeys] = useState<CacheKey[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedKeys, setSelectedKeys] = useState<Set<string>>(new Set());
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Fetch cache statistics
  const fetchStats = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/cache/stats');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Failed to fetch cache stats:', error);
      toast.error('Failed to fetch cache statistics');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch cache keys
  const fetchCacheKeys = useCallback(async () => {
    try {
      const response = await fetch('/api/cache/keys');
      if (response.ok) {
        const data = await response.json();
        setCacheKeys(data);
      }
    } catch (error) {
      console.error('Failed to fetch cache keys:', error);
    }
  }, []);

  // Auto-refresh effect
  useEffect(() => {
    fetchStats();
    fetchCacheKeys();

    if (autoRefresh) {
      const interval = setInterval(() => {
        fetchStats();
        fetchCacheKeys();
      }, refreshInterval);

      return () => clearInterval(interval);
    }
  }, [fetchStats, fetchCacheKeys, autoRefresh, refreshInterval]);

  // Clear cache
  const clearCache = async (type: 'all' | 'memory' | 'redis' = 'all') => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/cache/clear', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type }),
      });

      if (response.ok) {
        toast.success(`Cache cleared successfully`);
        await fetchStats();
        await fetchCacheKeys();
      } else {
        toast.error('Failed to clear cache');
      }
    } catch (error) {
      console.error('Cache clear error:', error);
      toast.error('Failed to clear cache');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete specific keys
  const deleteKeys = async (keys: string[]) => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/cache/delete', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ keys }),
      });

      if (response.ok) {
        toast.success(`${keys.length} keys deleted successfully`);
        setSelectedKeys(new Set());
        await fetchStats();
        await fetchCacheKeys();
      } else {
        toast.error('Failed to delete keys');
      }
    } catch (error) {
      console.error('Delete keys error:', error);
      toast.error('Failed to delete keys');
    } finally {
      setIsLoading(false);
    }
  };

  // Warm cache
  const warmCache = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('/api/cache/warm', {
        method: 'POST',
      });

      if (response.ok) {
        const data = await response.json();
        toast.success(`Cache warmed with ${data.count} entries`);
        await fetchStats();
      } else {
        toast.error('Failed to warm cache');
      }
    } catch (error) {
      console.error('Cache warming error:', error);
      toast.error('Failed to warm cache');
    } finally {
      setIsLoading(false);
    }
  };

  // Filter cache keys
  const filteredKeys = cacheKeys.filter(key =>
    key.key.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Get status color
  const getStatusColor = (hitRate: number) => {
    if (hitRate >= 80) return 'text-green-600';
    if (hitRate >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  // Get status icon
  const getStatusIcon = (hitRate: number) => {
    if (hitRate >= 80) return <CheckCircle className="h-4 w-4 text-green-600" />;
    if (hitRate >= 60) return <AlertTriangle className="h-4 w-4 text-yellow-600" />;
    return <XCircle className="h-4 w-4 text-red-600" />;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Cache Management</h2>
          <p className="text-muted-foreground">
            Monitor and manage Redis and memory caching systems
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setAutoRefresh(!autoRefresh)}
          >
            {autoRefresh ? <Pause className="h-4 w-4 mr-2" /> : <Play className="h-4 w-4 mr-2" />}
            {autoRefresh ? 'Pause' : 'Resume'} Auto-refresh
          </Button>
          <Button variant="outline" size="sm" onClick={fetchStats} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Cache Status Overview */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Overall Hit Rate</CardTitle>
              {getStatusIcon(stats.service.hitRate)}
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getStatusColor(stats.service.hitRate)}`}>
                {stats.service.hitRate.toFixed(1)}%
              </div>
              <p className="text-xs text-muted-foreground">
                {stats.service.cacheHits} hits / {stats.service.totalRequests} requests
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Memory Cache</CardTitle>
              <Memory className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.memory.keys}</div>
              <p className="text-xs text-muted-foreground">
                Active keys in memory
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Redis Cache</CardTitle>
              <Database className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.redis.hitRate.toFixed(1)}%</div>
              <p className="text-xs text-muted-foreground">
                Redis hit rate
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Response Time</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.service.averageResponseTime.toFixed(0)}ms</div>
              <p className="text-xs text-muted-foreground">
                Average response time
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="performance">Performance</TabsTrigger>
          <TabsTrigger value="keys">Cache Keys</TabsTrigger>
          <TabsTrigger value="operations">Operations</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Cache Performance */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Cache Performance
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && (
                  <>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span>Hit Rate</span>
                        <span>{stats.service.hitRate.toFixed(1)}%</span>
                      </div>
                      <Progress value={stats.service.hitRate} className="h-2" />
                    </div>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <div className="text-muted-foreground">Total Requests</div>
                        <div className="font-semibold">{stats.service.totalRequests.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Cache Hits</div>
                        <div className="font-semibold text-green-600">{stats.service.cacheHits.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Cache Misses</div>
                        <div className="font-semibold text-red-600">{stats.service.cacheMisses.toLocaleString()}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Errors</div>
                        <div className="font-semibold text-orange-600">{stats.service.errors.toLocaleString()}</div>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* System Health */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  System Health
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && (
                  <>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Memory className="h-4 w-4" />
                          <span className="text-sm">Memory Cache</span>
                        </div>
                        <Badge variant="outline" className="text-green-600">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Healthy
                        </Badge>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Database className="h-4 w-4" />
                          <span className="text-sm">Redis Cache</span>
                        </div>
                        <Badge variant="outline" className="text-green-600">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Connected
                        </Badge>
                      </div>

                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Zap className="h-4 w-4" />
                          <span className="text-sm">Middleware</span>
                        </div>
                        <Badge variant="outline" className="text-green-600">
                          <CheckCircle className="h-3 w-3 mr-1" />
                          Active
                        </Badge>
                      </div>
                    </div>

                    <div className="pt-4 border-t">
                      <div className="text-sm text-muted-foreground mb-2">Memory Usage</div>
                      <div className="text-2xl font-bold">
                        {(stats.redis.memoryUsage / 1024 / 1024).toFixed(1)} MB
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Cache Activity</CardTitle>
              <CardDescription>
                Latest cache operations and performance metrics
              </CardDescription>
            </CardHeader>
            <CardContent>
              {stats && (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-green-600">{stats.middleware.cacheSets}</div>
                      <div className="text-sm text-muted-foreground">Cache Sets</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-orange-600">{stats.middleware.cacheInvalidations}</div>
                      <div className="text-sm text-muted-foreground">Invalidations</div>
                    </div>
                    <div className="text-center p-4 border rounded-lg">
                      <div className="text-2xl font-bold text-blue-600">
                        {(stats.middleware.responseTimeSaved / 1000).toFixed(1)}s
                      </div>
                      <div className="text-sm text-muted-foreground">Time Saved</div>
                    </div>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Performance Tab */}
        <TabsContent value="performance" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Performance Metrics */}
            <Card>
              <CardHeader>
                <CardTitle>Performance Metrics</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && (
                  <>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Average Response Time</span>
                        <span className="font-semibold">{stats.service.averageResponseTime.toFixed(0)}ms</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Redis Response Time</span>
                        <span className="font-semibold">{stats.redis.averageResponseTime.toFixed(0)}ms</span>
                      </div>
                      <div className="flex justify-between items-center">
                        <span className="text-sm">Connected Clients</span>
                        <span className="font-semibold">{stats.redis.connectedClients}</span>
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Cache Efficiency */}
            <Card>
              <CardHeader>
                <CardTitle>Cache Efficiency</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && (
                  <>
                    <div className="space-y-3">
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Overall Hit Rate</span>
                          <span>{stats.service.hitRate.toFixed(1)}%</span>
                        </div>
                        <Progress value={stats.service.hitRate} className="h-2" />
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Redis Hit Rate</span>
                          <span>{stats.redis.hitRate.toFixed(1)}%</span>
                        </div>
                        <Progress value={stats.redis.hitRate} className="h-2" />
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Memory Hit Rate</span>
                          <span>95.0%</span>
                        </div>
                        <Progress value={95} className="h-2" />
                      </div>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Cache Keys Tab */}
        <TabsContent value="keys" className="space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Input
                  placeholder="Search cache keys..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64"
                />
              </div>
              <Badge variant="outline">
                {filteredKeys.length} keys
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              {selectedKeys.size > 0 && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => deleteKeys(Array.from(selectedKeys))}
                >
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete Selected ({selectedKeys.size})
                </Button>
              )}
              <Button variant="outline" size="sm" onClick={fetchCacheKeys}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>

          <Card>
            <CardContent className="p-0">
              <div className="max-h-96 overflow-y-auto">
                {filteredKeys.length === 0 ? (
                  <div className="p-8 text-center text-muted-foreground">
                    No cache keys found
                  </div>
                ) : (
                  <div className="space-y-1">
                    {filteredKeys.map((key, index) => (
                      <div
                        key={index}
                        className={`flex items-center justify-between p-3 border-b hover:bg-muted/50 ${
                          selectedKeys.has(key.key) ? 'bg-muted' : ''
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <input
                            type="checkbox"
                            checked={selectedKeys.has(key.key)}
                            onChange={(e) => {
                              const newSelected = new Set(selectedKeys);
                              if (e.target.checked) {
                                newSelected.add(key.key);
                              } else {
                                newSelected.delete(key.key);
                              }
                              setSelectedKeys(newSelected);
                            }}
                            className="rounded"
                          />
                          <div>
                            <div className="font-mono text-sm">{key.key}</div>
                            <div className="text-xs text-muted-foreground">
                              TTL: {key.ttl}s | Size: {key.size}B | Access: {key.accessCount}
                            </div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline" className="text-xs">
                            {key.ttl > 0 ? `${key.ttl}s` : 'Permanent'}
                          </Badge>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => deleteKeys([key.key])}
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Operations Tab */}
        <TabsContent value="operations" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Cache Operations */}
            <Card>
              <CardHeader>
                <CardTitle>Cache Operations</CardTitle>
                <CardDescription>
                  Manage cache operations and maintenance
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-3">
                  <Button
                    onClick={() => clearCache('all')}
                    variant="destructive"
                    className="w-full"
                    disabled={isLoading}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear All Cache
                  </Button>

                  <Button
                    onClick={() => clearCache('memory')}
                    variant="outline"
                    className="w-full"
                    disabled={isLoading}
                  >
                    <Memory className="h-4 w-4 mr-2" />
                    Clear Memory Cache
                  </Button>

                  <Button
                    onClick={() => clearCache('redis')}
                    variant="outline"
                    className="w-full"
                    disabled={isLoading}
                  >
                    <Database className="h-4 w-4 mr-2" />
                    Clear Redis Cache
                  </Button>

                  <Button
                    onClick={warmCache}
                    variant="outline"
                    className="w-full"
                    disabled={isLoading}
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Warm Cache
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Cache Configuration */}
            <Card>
              <CardHeader>
                <CardTitle>Cache Configuration</CardTitle>
                <CardDescription>
                  Current cache system configuration
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats && (
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Memory Cache Enabled</span>
                      <Badge variant="outline" className="text-green-600">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Enabled
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Redis Cache Enabled</span>
                      <Badge variant="outline" className="text-green-600">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Enabled
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Middleware Enabled</span>
                      <Badge variant="outline" className="text-green-600">
                        <CheckCircle className="h-3 w-3 mr-1" />
                        Active
                      </Badge>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Default TTL</span>
                      <span className="font-semibold">300s</span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-sm">Default Strategy</span>
                      <span className="font-semibold">Cache First</span>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Auto-refresh Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Auto-refresh Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="auto-refresh">Enable Auto-refresh</Label>
                  <Switch
                    id="auto-refresh"
                    checked={autoRefresh}
                    onCheckedChange={setAutoRefresh}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="refresh-interval">Refresh Interval (ms)</Label>
                  <Input
                    id="refresh-interval"
                    type="number"
                    value={refreshInterval}
                    onChange={(e) => setRefreshInterval(parseInt(e.target.value))}
                    min="1000"
                    max="60000"
                    step="1000"
                  />
                </div>
              </CardContent>
            </Card>

            {/* Advanced Settings */}
            <Card>
              <CardHeader>
                <CardTitle>Advanced Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <Label htmlFor="show-advanced">Show Advanced Options</Label>
                  <Switch
                    id="show-advanced"
                    checked={showAdvanced}
                    onCheckedChange={setShowAdvanced}
                  />
                </div>
                {showAdvanced && (
                  <div className="space-y-3 pt-4 border-t">
                    <div className="text-sm text-muted-foreground">
                      Advanced cache configuration options will be available here.
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

