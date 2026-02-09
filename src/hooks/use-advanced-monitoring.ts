'use client';

import { useEffect, useCallback, useMemo } from 'react';
import { 
  useMemoryMetrics, 
  useNetworkMetrics, 
  useBuildMetrics, 
  useComponentMetrics,
  useMonitoringEnabled,
  useExamplesStore 
} from '@/lib/stores/examples-store';
import { memoryUtils } from '@/lib/monitoring/memory-monitor';
import { networkUtils } from '@/lib/monitoring/network-optimizer';
import { buildUtils } from '@/lib/monitoring/build-monitor';
import { runtimeUtils } from '@/lib/monitoring/runtime-profiler';

/**
 * Hook for comprehensive performance monitoring
 */
export function useAdvancedMonitoring() {
  const memoryMetrics = useMemoryMetrics();
  const networkMetrics = useNetworkMetrics();
  const buildMetrics = useBuildMetrics();
  const componentMetrics = useComponentMetrics();
  const monitoringEnabled = useMonitoringEnabled();
  
  const { 
    getMemoryReport, 
    getNetworkReport, 
    getBuildReport, 
    getRuntimeReport,
    toggleMonitoring,
    updateMemoryMetrics,
    updateNetworkMetrics,
    updateBuildMetrics,
    updateComponentMetrics
  } = useExamplesStore();

  // Refresh all metrics
  const refreshAllMetrics = useCallback(async () => {
    try {
      const [memoryReport, networkReport, buildReport, runtimeReport] = await Promise.allSettled([
        getMemoryReport(),
        getNetworkReport(),
        getBuildReport(),
        getRuntimeReport()
      ]);

      if (memoryReport.status === 'fulfilled') {
        updateMemoryMetrics(memoryReport.value.metrics);
      }
      
      if (networkReport.status === 'fulfilled') {
        updateNetworkMetrics(networkReport.value.metrics);
      }
      
      if (buildReport.status === 'fulfilled') {
        updateBuildMetrics(buildReport.value.metrics);
      }
      
      if (runtimeReport.status === 'fulfilled') {
        updateComponentMetrics(runtimeReport.value.componentMetrics);
      }
    } catch (error) {
      console.error('Failed to refresh metrics:', error);
    }
  }, [getMemoryReport, getNetworkReport, getBuildReport, getRuntimeReport, updateMemoryMetrics, updateNetworkMetrics, updateBuildMetrics, updateComponentMetrics]);

  // Overall health score
  const overallHealth = useMemo(() => {
    const scores = [];
    
    if (memoryMetrics) {
      const memoryScore = memoryMetrics.memoryPressure === 'critical' ? 0 : 
                         memoryMetrics.memoryPressure === 'high' ? 25 :
                         memoryMetrics.memoryPressure === 'medium' ? 50 : 100;
      scores.push(memoryScore);
    }
    
    if (networkMetrics) {
      const networkScore = networkMetrics.errorRate > 0.1 ? 0 : 
                          networkMetrics.errorRate > 0.05 ? 50 : 100;
      scores.push(networkScore);
    }
    
    if (buildMetrics) {
      const buildScore = buildMetrics.duration > 120000 ? 0 :
                        buildMetrics.duration > 60000 ? 50 : 100;
      scores.push(buildScore);
    }
    
    if (componentMetrics.length > 0) {
      const avgComponentScore = componentMetrics.reduce((sum, comp) => sum + comp.performanceScore, 0) / componentMetrics.length;
      scores.push(avgComponentScore);
    }
    
    return scores.length > 0 ? Math.round(scores.reduce((sum, score) => sum + score, 0) / scores.length) : 100;
  }, [memoryMetrics, networkMetrics, buildMetrics, componentMetrics]);

  // Health grade
  const healthGrade = useMemo(() => {
    if (overallHealth >= 95) return 'A+';
    if (overallHealth >= 90) return 'A';
    if (overallHealth >= 80) return 'B';
    if (overallHealth >= 70) return 'C';
    if (overallHealth >= 60) return 'D';
    return 'F';
  }, [overallHealth]);

  // Auto-refresh when monitoring is enabled
  useEffect(() => {
    if (!monitoringEnabled) return;
    
    const interval = setInterval(refreshAllMetrics, 30000);
    return () => clearInterval(interval);
  }, [monitoringEnabled, refreshAllMetrics]);

  return {
    // Metrics
    memoryMetrics,
    networkMetrics,
    buildMetrics,
    componentMetrics,
    monitoringEnabled,
    
    // Computed values
    overallHealth,
    healthGrade,
    
    // Actions
    refreshAllMetrics,
    toggleMonitoring,
    
    // Individual report getters
    getMemoryReport,
    getNetworkReport,
    getBuildReport,
    getRuntimeReport,
  };
}

/**
 * Hook for memory monitoring
 */
export function useMemoryMonitoring() {
  const memoryMetrics = useMemoryMetrics();
  const monitoringEnabled = useMonitoringEnabled();
  const { getMemoryReport, updateMemoryMetrics, toggleMonitoring } = useExamplesStore();

  const refreshMemoryMetrics = useCallback(async () => {
    try {
      const report = await getMemoryReport();
      updateMemoryMetrics(report.metrics);
    } catch (error) {
      console.error('Failed to refresh memory metrics:', error);
    }
  }, [getMemoryReport, updateMemoryMetrics]);

  const startMemoryMonitoring = useCallback(() => {
    memoryUtils.startMonitoring();
    toggleMonitoring(true);
  }, [toggleMonitoring]);

  const stopMemoryMonitoring = useCallback(() => {
    memoryUtils.stopMonitoring();
    toggleMonitoring(false);
  }, [toggleMonitoring]);

  const forceGC = useCallback(() => {
    memoryUtils.forceGC();
  }, []);

  // Auto-refresh when monitoring is enabled
  useEffect(() => {
    if (!monitoringEnabled) return;
    
    const interval = setInterval(refreshMemoryMetrics, 5000);
    return () => clearInterval(interval);
  }, [monitoringEnabled, refreshMemoryMetrics]);

  return {
    memoryMetrics,
    monitoringEnabled,
    refreshMemoryMetrics,
    startMemoryMonitoring,
    stopMemoryMonitoring,
    forceGC,
  };
}

/**
 * Hook for network monitoring
 */
export function useNetworkMonitoring() {
  const networkMetrics = useNetworkMetrics();
  const { getNetworkReport, updateNetworkMetrics } = useExamplesStore();

  const refreshNetworkMetrics = useCallback(async () => {
    try {
      const report = await getNetworkReport();
      updateNetworkMetrics(report.metrics);
    } catch (error) {
      console.error('Failed to refresh network metrics:', error);
    }
  }, [getNetworkReport, updateNetworkMetrics]);

  const makeOptimizedRequest = useCallback(async <T>(url: string, options?: RequestInit, priority?: 'low' | 'medium' | 'high' | 'critical') => {
    return networkUtils.request<T>(url, options, priority);
  }, []);

  const prefetchResources = useCallback(async (urls: string[]) => {
    return networkUtils.prefetch(urls);
  }, []);

  const clearCache = useCallback(() => {
    networkUtils.clearCache();
  }, []);

  const getCacheStats = useCallback(() => {
    return networkUtils.getCacheStats();
  }, []);

  return {
    networkMetrics,
    refreshNetworkMetrics,
    makeOptimizedRequest,
    prefetchResources,
    clearCache,
    getCacheStats,
  };
}

/**
 * Hook for build monitoring
 */
export function useBuildMonitoring() {
  const buildMetrics = useBuildMetrics();
  const { getBuildReport, updateBuildMetrics } = useExamplesStore();

  const refreshBuildMetrics = useCallback(async () => {
    try {
      const report = await getBuildReport();
      updateBuildMetrics(report.metrics);
    } catch (error) {
      console.error('Failed to refresh build metrics:', error);
    }
  }, [getBuildReport, updateBuildMetrics]);

  const recordBuild = useCallback((metrics: Partial<typeof buildMetrics>) => {
    buildUtils.recordBuild(metrics);
  }, []);

  const getBuildHistory = useCallback(() => {
    return buildUtils.getBuildHistory();
  }, []);

  const getOptimizations = useCallback(() => {
    return buildUtils.getOptimizations();
  }, []);

  const clearBuildHistory = useCallback(() => {
    buildUtils.clearHistory();
  }, []);

  return {
    buildMetrics,
    refreshBuildMetrics,
    recordBuild,
    getBuildHistory,
    getOptimizations,
    clearBuildHistory,
  };
}

/**
 * Hook for component performance monitoring
 */
export function useComponentMonitoring() {
  const componentMetrics = useComponentMetrics();
  const { getRuntimeReport, updateComponentMetrics } = useExamplesStore();

  const refreshComponentMetrics = useCallback(async () => {
    try {
      const report = await getRuntimeReport();
      updateComponentMetrics(report.componentMetrics);
    } catch (error) {
      console.error('Failed to refresh component metrics:', error);
    }
  }, [getRuntimeReport, updateComponentMetrics]);

  const startProfiling = useCallback((componentName: string) => {
    return runtimeUtils.startProfiling(componentName);
  }, []);

  const getComponentMetrics = useCallback((componentName?: string) => {
    return runtimeUtils.getComponentMetrics(componentName);
  }, []);

  const getBottlenecks = useCallback(() => {
    return runtimeUtils.getBottlenecks();
  }, []);

  const clearProfilingData = useCallback(() => {
    runtimeUtils.clearData();
  }, []);

  const stopMonitoring = useCallback(() => {
    runtimeUtils.stopMonitoring();
  }, []);

  return {
    componentMetrics,
    refreshComponentMetrics,
    startProfiling,
    getComponentMetrics,
    getBottlenecks,
    clearProfilingData,
    stopMonitoring,
  };
}

/**
 * Hook for component performance profiling
 */
export function useComponentProfiling(componentName: string) {
  const { startProfiling } = useComponentMonitoring();

  const profileComponent = useCallback(() => {
    return startProfiling(componentName);
  }, [componentName, startProfiling]);

  return {
    profileComponent,
  };
}

/**
 * Hook for performance alerts and warnings
 */
export function usePerformanceAlerts() {
  const { memoryMetrics, networkMetrics, buildMetrics, componentMetrics } = useAdvancedMonitoring();

  const alerts = useMemo(() => {
    const alertsList = [];

    // Memory alerts
    if (memoryMetrics) {
      if (memoryMetrics.memoryPressure === 'critical') {
        alertsList.push({
          type: 'critical',
          category: 'memory',
          message: 'Critical memory pressure detected',
          details: `${Math.round(memoryMetrics.memoryUsage * 100)}% of heap limit used`,
        });
      } else if (memoryMetrics.memoryPressure === 'high') {
        alertsList.push({
          type: 'warning',
          category: 'memory',
          message: 'High memory pressure',
          details: `${Math.round(memoryMetrics.memoryUsage * 100)}% of heap limit used`,
        });
      }

      if (memoryMetrics.memoryLeakScore > 0.3) {
        alertsList.push({
          type: 'warning',
          category: 'memory',
          message: 'Potential memory leak detected',
          details: `Leak score: ${Math.round(memoryMetrics.memoryLeakScore * 100)}%`,
        });
      }
    }

    // Network alerts
    if (networkMetrics) {
      if (networkMetrics.errorRate > 0.1) {
        alertsList.push({
          type: 'critical',
          category: 'network',
          message: 'High network error rate',
          details: `${Math.round(networkMetrics.errorRate * 100)}% of requests failing`,
        });
      } else if (networkMetrics.errorRate > 0.05) {
        alertsList.push({
          type: 'warning',
          category: 'network',
          message: 'Elevated network error rate',
          details: `${Math.round(networkMetrics.errorRate * 100)}% of requests failing`,
        });
      }

      if (networkMetrics.responseTime > 5000) {
        alertsList.push({
          type: 'warning',
          category: 'network',
          message: 'Slow network response times',
          details: `Average response time: ${Math.round(networkMetrics.responseTime)}ms`,
        });
      }
    }

    // Build alerts
    if (buildMetrics) {
      if (buildMetrics.duration > 120000) {
        alertsList.push({
          type: 'critical',
          category: 'build',
          message: 'Very slow build times',
          details: `Build took ${Math.round(buildMetrics.duration / 1000)}s`,
        });
      } else if (buildMetrics.duration > 60000) {
        alertsList.push({
          type: 'warning',
          category: 'build',
          message: 'Slow build times',
          details: `Build took ${Math.round(buildMetrics.duration / 1000)}s`,
        });
      }

      if (buildMetrics.bundleSize > 5 * 1024 * 1024) {
        alertsList.push({
          type: 'warning',
          category: 'build',
          message: 'Large bundle size',
          details: `Bundle size: ${Math.round(buildMetrics.bundleSize / 1024 / 1024)}MB`,
        });
      }
    }

    // Component alerts
    const slowComponents = componentMetrics.filter(comp => comp.performanceScore < 70);
    if (slowComponents.length > 0) {
      alertsList.push({
        type: 'warning',
        category: 'components',
        message: `${slowComponents.length} components with poor performance`,
        details: slowComponents.map(comp => `${comp.componentName} (${comp.performanceScore}/100)`).join(', '),
      });
    }

    return alertsList;
  }, [memoryMetrics, networkMetrics, buildMetrics, componentMetrics]);

  const criticalAlerts = useMemo(() => 
    alerts.filter(alert => alert.type === 'critical'),
    [alerts]
  );

  const warningAlerts = useMemo(() => 
    alerts.filter(alert => alert.type === 'warning'),
    [alerts]
  );

  return {
    alerts,
    criticalAlerts,
    warningAlerts,
    hasAlerts: alerts.length > 0,
    hasCriticalAlerts: criticalAlerts.length > 0,
  };
}





