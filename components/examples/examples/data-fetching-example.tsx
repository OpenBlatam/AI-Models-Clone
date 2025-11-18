'use client';

import React, { useState, useCallback, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useDataFetching } from '@/hooks/use-data-fetching';
import { z } from 'zod';
import { toast } from 'react-hot-toast';
import { RefreshCw, Trash2, Activity, Database, AlertCircle, CheckCircle } from 'lucide-react';

// Schema definition for better type safety
const postSchema = z.object({
  id: z.number(),
  title: z.string(),
  body: z.string(),
  userId: z.number(),
});

type Post = z.infer<typeof postSchema>;

// Constants for better maintainability
const API_ENDPOINT = 'https://jsonplaceholder.typicode.com/posts?_limit=5';
const CACHE_TIME = 10 * 60 * 1000; // 10 minutes
const RETRY_COUNT = 3;
const RETRY_DELAY = 1000;

interface FetchStats {
  totalRequests: number;
  successfulRequests: number;
  failedRequests: number;
  averageResponseTime: number;
}

export default function DataFetchingExample() {
  // Data fetching hook
  const {
    data: posts,
    loading,
    error,
    refetch,
    clearCache,
  } = useDataFetching(
    API_ENDPOINT,
    z.array(postSchema),
    {
      immediate: false,
      cacheTime: CACHE_TIME,
      retryCount: RETRY_COUNT,
      retryDelay: RETRY_DELAY,
      onSuccess: (data) => {
        toast.success(`Loaded ${data.length} posts successfully!`);
      },
      onError: (error) => {
        toast.error(`Failed to load posts: ${error.message}`);
      },
    }
  );

  // Local state for UI feedback
  const [isProcessing, setIsProcessing] = useState(false);
  const [fetchStats, setFetchStats] = useState<FetchStats>({
    totalRequests: 0,
    successfulRequests: 0,
    failedRequests: 0,
    averageResponseTime: 0,
  });

  // Memoized computed values
  const hasData = useMemo(() => posts && posts.length > 0, [posts]);
  const hasError = useMemo(() => error !== null, [error]);
  const isReady = useMemo(() => !loading && !hasError, [loading, hasError]);

  const cacheStatus = useMemo(() => {
    if (loading) return 'fetching';
    if (hasError) return 'error';
    if (hasData) return 'cached';
    return 'empty';
  }, [loading, hasError, hasData]);

  // Optimized handlers with useCallback
  const handleRefetch = useCallback(async () => {
    try {
      setIsProcessing(true);
      const startTime = Date.now();
      
      await refetch();
      
      const responseTime = Date.now() - startTime;
      setFetchStats(prev => ({
        totalRequests: prev.totalRequests + 1,
        successfulRequests: prev.successfulRequests + 1,
        failedRequests: prev.failedRequests,
        averageResponseTime: (prev.averageResponseTime + responseTime) / 2,
      }));
    } catch (error) {
      setFetchStats(prev => ({
        totalRequests: prev.totalRequests + 1,
        successfulRequests: prev.successfulRequests,
        failedRequests: prev.failedRequests + 1,
        averageResponseTime: prev.averageResponseTime,
      }));
      toast.error('Failed to refetch data');
    } finally {
      setIsProcessing(false);
    }
  }, [refetch]);

  const handleClearCache = useCallback(async () => {
    try {
      setIsProcessing(true);
      clearCache();
      toast.success('Cache cleared successfully!');
    } catch (error) {
      toast.error('Failed to clear cache');
      console.error('Cache clear error:', error);
    } finally {
      setIsProcessing(false);
    }
  }, [clearCache]);

  // Early return for invalid states
  if (posts === undefined && !loading && !error) {
    return (
      <div className="text-center py-8">
        <p className="text-destructive">Failed to initialize data fetching</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Data Controls Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database className="h-5 w-5" />
              Data Controls
            </CardTitle>
            <CardDescription>
              Control data fetching behavior and cache management
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Control Buttons */}
            <div className="flex gap-2">
              <Button 
                onClick={handleRefetch} 
                disabled={loading || isProcessing}
                className="flex-1"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
                {loading ? 'Fetching...' : 'Fetch Data'}
              </Button>
              <Button 
                variant="outline" 
                onClick={handleClearCache} 
                disabled={loading || isProcessing}
              >
                <Trash2 className="h-4 w-4 mr-2" />
                Clear Cache
              </Button>
            </div>

            {/* Status Indicators */}
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Badge variant={loading ? 'default' : 'secondary'}>
                  {loading ? 'Loading' : 'Ready'}
                </Badge>
                {hasError && (
                  <Badge variant="destructive">
                    Error
                  </Badge>
                )}
                <Badge variant={cacheStatus === 'cached' ? 'success' : 'secondary'}>
                  {cacheStatus === 'cached' ? 'Cached' : 'Not Cached'}
                </Badge>
              </div>
            </div>

            {/* Fetch Statistics */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Fetch Statistics:</h4>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Total Requests</p>
                  <p className="text-muted-foreground">{fetchStats.totalRequests}</p>
                </div>
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Success Rate</p>
                  <p className="text-muted-foreground">
                    {fetchStats.totalRequests > 0 
                      ? Math.round((fetchStats.successfulRequests / fetchStats.totalRequests) * 100)
                      : 0}%
                  </p>
                </div>
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Avg Response</p>
                  <p className="text-muted-foreground">{Math.round(fetchStats.averageResponseTime)}ms</p>
                </div>
                <div className="bg-muted p-2 rounded">
                  <p className="font-medium">Cache Time</p>
                  <p className="text-muted-foreground">{CACHE_TIME / 1000}s</p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Status Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-lg">Status</CardTitle>
            <CardDescription>
              Current data fetching state and configuration
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Loading State */}
            {loading && (
              <div className="flex items-center gap-2 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <RefreshCw className="h-4 w-4 animate-spin text-blue-600" />
                <span className="text-sm text-blue-800">Loading posts...</span>
              </div>
            )}
            
            {/* Error State */}
            {hasError && (
              <div className="space-y-2 p-3 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <Badge variant="destructive">Error</Badge>
                </div>
                <p className="text-sm text-red-800">{error?.message}</p>
                <div className="text-xs text-red-700">
                  <p>• Retry count: {RETRY_COUNT}</p>
                  <p>• Retry delay: {RETRY_DELAY}ms</p>
                </div>
              </div>
            )}
            
            {/* Success State */}
            {hasData && (
              <div className="space-y-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <Badge variant="success">Success</Badge>
                </div>
                <p className="text-sm text-green-800">
                  Loaded {posts.length} posts successfully
                </p>
                <div className="text-xs text-green-700">
                  <p>• Data is cached for {CACHE_TIME / 1000} seconds</p>
                  <p>• Ready for immediate access</p>
                </div>
              </div>
            )}

            {/* Configuration Info */}
            <div className="space-y-2">
              <h4 className="font-medium text-sm">Configuration:</h4>
              <div className="text-xs text-muted-foreground space-y-1">
                <p>• API Endpoint: <code className="bg-muted px-1 rounded">{API_ENDPOINT}</code></p>
                <p>• Cache Time: {CACHE_TIME / 1000} seconds</p>
                <p>• Retry Count: {RETRY_COUNT}</p>
                <p>• Retry Delay: {RETRY_DELAY}ms</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Posts Display */}
      {hasData && (
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center gap-2">
              <Database className="h-5 w-5" />
              Posts Data
            </CardTitle>
            <CardDescription>
              Fetched data from the API with caching and retry logic
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {posts.map((post) => (
                <div key={post.id} className="p-3 border rounded-lg hover:bg-muted/50 transition-colors">
                  <h4 className="font-medium">{post.title}</h4>
                  <p className="text-sm text-muted-foreground line-clamp-2">{post.body}</p>
                  <div className="flex items-center gap-2 mt-2">
                    <Badge variant="outline" size="sm">
                      ID: {post.id}
                    </Badge>
                    <Badge variant="outline" size="sm">
                      User: {post.userId}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Performance Tips */}
      <div className="text-sm text-muted-foreground space-y-2">
        <p>💡 This demonstrates caching, retry logic, and error handling!</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Caching Benefits</p>
            <ul className="space-y-1">
              <li>• Faster subsequent loads</li>
              <li>• Reduced API calls</li>
              <li>• Better user experience</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Retry Logic</p>
            <ul className="space-y-1">
              <li>• Automatic error recovery</li>
              <li>• Configurable retry count</li>
              <li>• Exponential backoff</li>
            </ul>
          </div>
          <div className="bg-muted p-3 rounded-lg">
            <p className="font-medium mb-1">Error Handling</p>
            <ul className="space-y-1">
              <li>• Graceful degradation</li>
              <li>• User-friendly messages</li>
              <li>• Detailed error logging</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}





