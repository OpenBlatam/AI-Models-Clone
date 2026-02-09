'use client';

import React, { useEffect, useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Database, Search, MessageSquare, BarChart3, AlertTriangle, RefreshCw } from 'lucide-react';
import { useHookStatus, usePerformanceMetrics, useErrorCount, useExamplesStore } from '@/lib/stores/examples-store';
import { toast } from 'react-hot-toast';

interface HooksStatusProps {
  localStorageCount?: number;
  debounceActive?: boolean;
  formValid?: boolean;
  dataFetching?: boolean;
}

export function HooksStatus({ 
  localStorageCount = 0, 
  debounceActive = false, 
  formValid = false, 
  dataFetching = false 
}: HooksStatusProps) {
  // Store state
  const storeHookStatus = useHookStatus();
  const performanceMetrics = usePerformanceMetrics();
  const errorCount = useErrorCount();
  const { resetStore, logError } = useExamplesStore();

  // Use props or fallback to store values
  const currentStatus = useMemo(() => ({
    localStorageCount: localStorageCount || storeHookStatus.localStorageCount,
    debounceActive: debounceActive || storeHookStatus.debounceActive,
    formValid: formValid || storeHookStatus.formValid,
    dataFetching: dataFetching || storeHookStatus.dataFetching,
  }), [localStorageCount, debounceActive, formValid, dataFetching, storeHookStatus]);

  // Performance indicators
  const performanceStatus = useMemo(() => {
    const isSlow = performanceMetrics.renderTime > 16;
    const isHighMemory = performanceMetrics.memoryUsage > 100; // 100MB threshold
    
    return {
      isSlow,
      isHighMemory,
      performanceClass: isSlow || isHighMemory ? 'text-amber-600' : 'text-green-600',
    };
  }, [performanceMetrics]);

  // Handle store reset
  const handleReset = () => {
    try {
      resetStore();
      toast.success('Store reset successfully!');
    } catch (error) {
      logError({
        message: 'Failed to reset store',
        component: 'HooksStatus',
        severity: 'medium',
      });
      toast.error('Failed to reset store');
    }
  };

  // Handle performance warning
  const handlePerformanceWarning = () => {
    toast.error(`Performance issue detected! Render time: ${performanceMetrics.renderTime.toFixed(2)}ms`);
  };

  return (
    <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-blue-900">
            <Activity className="h-5 w-5" />
            <CardTitle>Hooks Status Monitor</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            {errorCount > 0 && (
              <Badge variant="destructive" size="sm" className="flex items-center gap-1">
                <AlertTriangle className="h-3 w-3" />
                {errorCount} Errors
              </Badge>
            )}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="text-blue-700 hover:text-blue-900"
            >
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
        <CardDescription className="text-blue-700">
          Real-time status of all custom hooks in action
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Hooks Status Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="flex flex-col items-center text-center">
            <Database className="h-6 w-6 text-blue-600 mb-2" />
            <Badge variant={currentStatus.localStorageCount > 0 ? 'success' : 'secondary'} size="sm">
              {currentStatus.localStorageCount} items
            </Badge>
            <p className="text-xs text-blue-700 mt-1">Local Storage</p>
          </div>
          
          <div className="flex flex-col items-center text-center">
            <Search className="h-6 w-6 text-green-600 mb-2" />
            <Badge variant={currentStatus.debounceActive ? 'default' : 'secondary'} size="sm">
              {currentStatus.debounceActive ? 'Active' : 'Idle'}
            </Badge>
            <p className="text-xs text-green-700 mt-1">Debounce</p>
          </div>
          
          <div className="flex flex-col items-center text-center">
            <MessageSquare className="h-6 w-6 text-purple-600 mb-2" />
            <Badge variant={currentStatus.formValid ? 'success' : 'warning'} size="sm">
              {currentStatus.formValid ? 'Valid' : 'Invalid'}
            </Badge>
            <p className="text-xs text-purple-700 mt-1">Form Validation</p>
          </div>
          
          <div className="flex flex-col items-center text-center">
            <Activity className="h-6 w-6 text-orange-600 mb-2" />
            <Badge variant={currentStatus.dataFetching ? 'default' : 'secondary'} size="sm">
              {currentStatus.dataFetching ? 'Fetching' : 'Ready'}
            </Badge>
            <p className="text-xs text-orange-700 mt-1">Data Fetching</p>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="border-t border-blue-200 pt-4">
          <div className="flex items-center justify-between mb-3">
            <h4 className="text-sm font-medium text-blue-900 flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Performance Metrics
            </h4>
            {performanceStatus.isSlow && (
              <Button
                variant="ghost"
                size="sm"
                onClick={handlePerformanceWarning}
                className="text-amber-600 hover:text-amber-700"
              >
                <AlertTriangle className="h-4 w-4" />
              </Button>
            )}
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="text-center">
              <p className="font-medium text-blue-700">Render Time</p>
              <p className={`font-mono ${performanceStatus.performanceClass}`}>
                {performanceMetrics.renderTime.toFixed(2)}ms
              </p>
            </div>
            <div className="text-center">
              <p className="font-medium text-blue-700">Memory</p>
              <p className={`font-mono ${performanceStatus.performanceClass}`}>
                {performanceMetrics.memoryUsage.toFixed(1)}MB
              </p>
            </div>
            <div className="text-center">
              <p className="font-medium text-blue-700">Interactions</p>
              <p className="text-blue-600 font-mono">
                {performanceMetrics.interactionCount}
              </p>
            </div>
            <div className="text-center">
              <p className="font-medium text-blue-700">Last Update</p>
              <p className="text-blue-600 font-mono">
                {performanceMetrics.lastInteraction.toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>

        {/* Status Footer */}
        <div className="border-t border-blue-200 pt-3">
          <div className="flex items-center justify-between text-xs text-blue-600">
            <span>Last updated: {storeHookStatus.lastUpdated.toLocaleTimeString()}</span>
            <span>Store: {storeHookStatus === currentStatus ? 'Synced' : 'Out of sync'}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
