'use client';

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useDataFetching } from '@/hooks/use-data-fetching';
import { z } from 'zod';
import { toast } from 'react-hot-toast';
import { RefreshCw, Trash2, Activity, Database, AlertCircle, CheckCircle, Info, AlertTriangle, BarChart3, Clock, Zap } from 'lucide-react';
import { usePerformanceMonitor, useHookStatusMonitor, useExamplesStore } from '@/lib/stores/examples-store';

const postSchema = z.object({
  id: z.number(),
  title: z.string(),
  body: z.string(),
  userId: z.number()
});

type Post = z.infer<typeof postSchema>;

const API_ENDPOINT = 'https://jsonplaceholder.typicode.com/posts';
const CACHE_TIME = 5 * 60 * 1000; // 5 minutes
const RETRY_COUNT = 3;
const RETRY_DELAY = 1000;

interface FetchStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
  lastRequestTime: number;
}

export default function DataFetchingExample() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [fetchStats, setFetchStats] = useState<FetchStats>({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
    lastRequestTime: 0
  });

  // Performance monitoring
  const { updatePerformanceMetrics } = usePerformanceMonitor();
  const { updateHookStatus } = useHookStatusMonitor('dataFetching');

  // Data fetching hook
  const {
    data,
    isLoading,
    error,
    refetch,
    clearCache,
    isCached,
    lastFetched
  } = useDataFetching<Post[]>({
    url: API_ENDPOINT,
    schema: z.array(postSchema),
    options: {
      cacheTime: CACHE_TIME,
      retry: RETRY_COUNT,
      retryDelay: RETRY_DELAY
    }
  });

  // Error handling
  const [hasError, setHasError] = useState(false);

  // Memoized computed values
  const hasData = useMemo(() => data && data.length > 0, [data]);
  const hasErrorState = useMemo(() => !!error, [error]);
  const isReady = useMemo(() => !isLoading && !error && hasData, [isLoading, error, hasData]);
  const cacheStatus = useMemo(() => ({
    isCached: isCached,
    lastFetched: lastFetched,
    cacheAge: lastFetched ? Date.now() - lastFetched : 0
  }), [isCached, lastFetched]);

  // Update hook status in store
  useEffect(() => {
    try {
      updateHookStatus({
        isActive: isLoading || hasData,
        lastUsed: Date.now(),
        usageCount: (prev) => prev + 1
      });
    } catch (error) {
      console.error('Failed to update hook status:', error);
      setHasError(true);
    }
  }, [isLoading, hasData, updateHookStatus]);

  // Log errors to store
  useEffect(() => {
    if (hasError) {
      const { logError } = useExamplesStore.getState();
      logError({
        message: 'Data fetching error',
        stack: 'Error in data fetching example component',
        severity: 'warning'
      });
    }
  }, [hasError]);

  // Handle refetch with error handling and stats
  const handleRefetch = useCallback(async () => {
    try {
      setIsProcessing(true);
      const startTime = Date.now();
      
      await refetch();
      
      const responseTime = Date.now() - startTime;
      setFetchStats(prev => {
        const newTotal = prev.totalRequests + 1;
        const newSuccessful = prev.successfulRequests + 1;
        const newAvgTime = ((prev.averageResponseTime * prev.totalRequests) + responseTime) / newTotal;
        
        return {
          totalRequests: newTotal,
          successfulRequests: newSuccessful,
          failedRequests: prev.failedRequests,
          averageResponseTime: Math.round(newAvgTime),
          lastRequestTime: Date.now()
        };
      });
      
      toast.success('Data refreshed successfully');
    } catch (error) {
      console.error('Refetch error:', error);
      setHasError(true);
      setFetchStats(prev => ({
        ...prev,
        totalRequests: prev.totalRequests + 1,
        failedRequests: prev.failedRequests + 1,
        lastRequestTime: Date.now()
      }));
      toast.error('Failed to refresh data');
    } finally {
      setIsProcessing(false);
    }
  }, [refetch]);

  // Handle cache clearing with error handling
  const handleClearCache = useCallback(async () => {
    try {
      setIsProcessing(true);
      await clearCache();
      toast.success('Cache cleared successfully');
    } catch (error) {
      console.error('Cache clear error:', error);
      setHasError(true);
      toast.error('Failed to clear cache');
    } finally {
      setIsProcessing(false);
    }
  }, [clearCache]);

  // Early return for initialization failures
  if (hasError) {
    return (
      <Card className="border-destructive">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="h-5 w-5" />
            Error Loading Component
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            There was an error initializing the data fetching example. Please refresh the page.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Data Fetching Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Data Fetching Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <Button 
              onClick={handleRefetch}
              disabled={isProcessing || isLoading}
              className="min-w-[120px]"
              data-testid="fetch-data-button"
              aria-label="Fetch data from API"
            >
              {isProcessing || isLoading ? (
                <>
                  <Activity className="mr-2 h-4 w-4 animate-spin" />
                  Fetching...
                </>
              ) : (
                <>
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Fetch Data
                </>
              )}
            </Button>
            <Button 
              variant="outline" 
              onClick={handleClearCache}
              disabled={isProcessing || !isCached}
              data-testid="clear-cache-button"
              aria-label="Clear cached data"
            >
              <Trash2 className="mr-2 h-4 w-4" />
              Clear Cache
            </Button>
          </div>

          {/* Status Indicators */}
          <div className="flex flex-wrap gap-2">
            <Badge variant={isLoading ? 'default' : 'secondary'}>
              {isLoading ? 'Loading' : 'Ready'}
            </Badge>
            {hasErrorState && (
              <Badge variant="destructive">
                Error
              </Badge>
            )}
            <Badge variant={isCached ? 'default' : 'outline'}>
              {isCached ? 'Cached' : 'Not Cached'}
            </Badge>
          </div>
        </CardContent>
      </Card>

      {/* Fetch Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Fetch Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Total Requests</label>
              <div className="text-2xl font-bold">{fetchStats.totalRequests}</div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Success Rate</label>
              <div className="text-2xl font-bold text-green-600">
                {fetchStats.totalRequests > 0 
                  ? Math.round((fetchStats.successfulRequests / fetchStats.totalRequests) * 100)
                  : 0}%
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Avg Response</label>
              <div className="text-2xl font-bold text-blue-600">
                {fetchStats.averageResponseTime}ms
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Cache Time</label>
              <div className="text-2xl font-bold text-purple-600">
                {Math.round(CACHE_TIME / 1000)}s
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Status Information */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Status</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Loading State:</span>
                <Badge variant={isLoading ? 'default' : 'secondary'}>
                  {isLoading ? 'Active' : 'Inactive'}
                </Badge>
                {isLoading && <Activity className="h-4 w-4 animate-spin" />}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Error State:</span>
                <Badge variant={hasErrorState ? 'destructive' : 'default'}>
                  {hasErrorState ? 'Error' : 'No Errors'}
                </Badge>
                {hasErrorState && <AlertCircle className="h-4 w-4" />}
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Data State:</span>
                <Badge variant={hasData ? 'default' : 'secondary'}>
                  {hasData ? 'Has Data' : 'No Data'}
                </Badge>
                {hasData && <CheckCircle className="h-4 w-4" />}
              </div>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Cache Status:</span>
                <Badge variant={cacheStatus.isCached ? 'default' : 'outline'}>
                  {cacheStatus.isCached ? 'Cached' : 'Not Cached'}
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Last Fetched:</span>
                <Badge variant="outline">
                  {cacheStatus.lastFetched 
                    ? new Date(cacheStatus.lastFetched).toLocaleTimeString()
                    : 'Never'
                  }
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium">Cache Age:</span>
                <Badge variant="outline">
                  {cacheStatus.cacheAge > 0 
                    ? `${Math.round(cacheStatus.cacheAge / 1000)}s ago`
                    : 'N/A'
                  }
                </Badge>
              </div>
            </div>
          </div>

          {/* Error Display */}
          {hasErrorState && (
            <div className="p-4 bg-destructive/10 border border-destructive/20 rounded-lg">
              <div className="flex items-center gap-2 text-destructive">
                <AlertCircle className="h-5 w-5" />
                <span className="font-medium">Error Details</span>
              </div>
              <p className="text-sm text-destructive mt-1">
                {error?.message || 'An unknown error occurred'}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Configuration Info */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Configuration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">API Endpoint</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {API_ENDPOINT}
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Cache Time</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {CACHE_TIME / 1000}s
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Retry Count</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {RETRY_COUNT} attempts
              </div>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Retry Delay</label>
              <div className="text-sm text-muted-foreground font-mono bg-muted px-2 py-1 rounded">
                {RETRY_DELAY}ms
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Posts Data */}
      {hasData && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Posts Data</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {data?.slice(0, 5).map((post) => (
                <div 
                  key={post.id} 
                  className="p-3 border rounded-lg hover:bg-muted/50 transition-colors"
                >
                  <h4 className="font-medium text-sm line-clamp-2">{post.title}</h4>
                  <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                    {post.body}
                  </p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" className="text-xs">
                      ID: {post.id}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      User: {post.userId}
                    </Badge>
                  </div>
                </div>
              ))}
              {data && data.length > 5 && (
                <p className="text-sm text-muted-foreground text-center">
                  Showing 5 of {data.length} posts
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Tips */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Info className="h-5 w-5" />
            Performance Tips
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2">
            <h4 className="font-medium">Caching Benefits</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Reduces API calls and improves performance</li>
              <li>• Better user experience with faster data access</li>
              <li>• Reduces server load and bandwidth usage</li>
              <li>• Configurable cache time for different data types</li>
            </ul>
          </div>
          <div className="space-y-2">
            <h4 className="font-medium">Retry Logic</h4>
            <ul className="text-sm text-muted-foreground space-y-1">
              <li>• Automatic retry on network failures</li>
              <li>• Configurable retry count and delay</li>
              <li>• Exponential backoff for better reliability</li>
              <li>• User-friendly error handling and feedback</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}





