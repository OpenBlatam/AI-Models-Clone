import React, { useState, useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { OptimizedTranslatedText } from '../i18n-components/OptimizedTranslatedText';
import { appOptimizer, getOptimizationMetrics } from '../../utils/optimization/AppOptimizer';
import { componentOptimizer, generateComponentReport } from '../../utils/optimization/ComponentOptimizer';
import { bundleOptimizer, generateBundleReport } from '../../utils/optimization/BundleOptimizer';
import { performanceMonitor } from '../../utils/performance/PerformanceMonitor';
import { cacheManager } from '../../utils/caching/CacheManager';
import { analytics } from '../../utils/analytics/AnalyticsService';
import { securityManager } from '../../utils/security/SecurityManager';

interface OptimizationDashboardProps {
  onOptimize?: () => void;
  onConfigure?: () => void;
  style?: any;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  unit?: string;
  status: 'excellent' | 'good' | 'warning' | 'critical';
  description?: string;
}

const MetricCard: React.FC<MetricCardProps> = ({ title, value, unit, status, description }) => {
  const getStatusColor = () => {
    switch (status) {
      case 'excellent': return '#4CAF50';
      case 'good': return '#8BC34A';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'excellent': return 'Excellent';
      case 'good': return 'Good';
      case 'warning': return 'Warning';
      case 'critical': return 'Critical';
      default: return 'Unknown';
    }
  };

  return (
    <View style={[styles.metricCard, { borderLeftColor: getStatusColor() }]}>
      <View style={styles.metricHeader}>
        <Text style={styles.metricTitle}>{title}</Text>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor() }]}>
          <Text style={styles.statusText}>{getStatusText()}</Text>
        </View>
      </View>
      <View style={styles.metricValue}>
        <Text style={styles.valueText}>{value}</Text>
        {unit && <Text style={styles.unitText}>{unit}</Text>}
      </View>
      {description && (
        <Text style={styles.descriptionText}>{description}</Text>
      )}
    </View>
  );
};

export const OptimizationDashboard: React.FC<OptimizationDashboardProps> = ({
  onOptimize,
  onConfigure,
  style,
}) => {
  const [metrics, setMetrics] = useState<any>({});
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      const appMetrics = getOptimizationMetrics();
      const cacheStats = cacheManager.getStats();
      const performanceReport = performanceMonitor.getReport();
      const securityMetrics = securityManager.getSecurityMetrics();

      setMetrics({
        app: appMetrics,
        cache: cacheStats,
        performance: performanceReport,
        security: securityMetrics,
      });
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  // Auto-refresh metrics
  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Run comprehensive optimization
  const handleOptimize = async () => {
    if (isOptimizing) return;

    setIsOptimizing(true);
    try {
      Alert.alert(
        'Optimization Started',
        'Running comprehensive app optimization...',
        [{ text: 'OK' }]
      );

      // Run all optimizations
      await Promise.all([
        appOptimizer.optimizeApp(),
        bundleOptimizer.optimizeBundle(),
      ]);

      // Refresh metrics
      await fetchMetrics();

      // Track optimization
      analytics.trackEvent('optimization_completed', {
        timestamp: Date.now(),
        metrics: metrics,
      });

      Alert.alert(
        'Optimization Complete',
        'App optimization completed successfully!',
        [{ text: 'OK' }]
      );

      onOptimize?.();
    } catch (error) {
      console.error('Optimization failed:', error);
      Alert.alert(
        'Optimization Failed',
        'Failed to complete optimization. Please try again.',
        [{ text: 'OK' }]
      );
    } finally {
      setIsOptimizing(false);
    }
  };

  // Generate optimization score
  const optimizationScore = useMemo(() => {
    if (!metrics.app) return 0;
    
    const scores = [
      Math.max(0, 100 - (metrics.app.bundleSize / (1024 * 1024)) * 10),
      Math.max(0, 100 - (metrics.app.memoryUsage / (1024 * 1024)) * 2),
      metrics.app.cacheHitRate * 100,
      Math.max(0, 100 - metrics.app.renderTime),
      Math.max(0, 100 - metrics.app.startupTime),
    ];
    
    return scores.reduce((sum, score) => sum + score, 0) / scores.length;
  }, [metrics.app]);

  // Get status for metrics
  const getStatus = (value: number, thresholds: { excellent: number; good: number; warning: number }) => {
    if (value <= thresholds.excellent) return 'excellent';
    if (value <= thresholds.good) return 'good';
    if (value <= thresholds.warning) return 'warning';
    return 'critical';
  };

  return (
    <ScrollView style={[styles.container, style]} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <OptimizedTranslatedText
          translationKey="optimization.dashboard.title"
          style={styles.title}
        />
        <Text style={styles.subtitle}>
          Last updated: {lastUpdate.toLocaleTimeString()}
        </Text>
      </View>

      {/* Overall Score */}
      <View style={styles.scoreSection}>
        <Text style={styles.scoreTitle}>Overall Optimization Score</Text>
        <View style={styles.scoreContainer}>
          <Text style={[styles.scoreValue, { color: getStatus(optimizationScore, { excellent: 90, good: 75, warning: 60 }).color }]}>
            {optimizationScore.toFixed(1)}%
          </Text>
        </View>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={[styles.optimizeButton, isOptimizing && styles.disabledButton]}
          onPress={handleOptimize}
          disabled={isOptimizing}
        >
          <OptimizedTranslatedText
            translationKey={isOptimizing ? "optimization.optimizing" : "optimization.run"}
            style={styles.buttonText}
          />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.configureButton}
          onPress={onConfigure}
        >
          <OptimizedTranslatedText
            translationKey="optimization.configure"
            style={styles.configureButtonText}
          />
        </TouchableOpacity>
      </View>

      {/* Performance Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Metrics</Text>
        
        <MetricCard
          title="Bundle Size"
          value={metrics.app?.bundleSize ? (metrics.app.bundleSize / (1024 * 1024)).toFixed(2) : '0'}
          unit="MB"
          status={getStatus(metrics.app?.bundleSize || 0, { excellent: 5 * 1024 * 1024, good: 10 * 1024 * 1024, warning: 15 * 1024 * 1024 })}
          description="Total application bundle size"
        />

        <MetricCard
          title="Memory Usage"
          value={metrics.app?.memoryUsage ? (metrics.app.memoryUsage / (1024 * 1024)).toFixed(2) : '0'}
          unit="MB"
          status={getStatus(metrics.app?.memoryUsage || 0, { excellent: 50 * 1024 * 1024, good: 100 * 1024 * 1024, warning: 150 * 1024 * 1024 })}
          description="Current memory consumption"
        />

        <MetricCard
          title="Render Time"
          value={metrics.app?.renderTime ? metrics.app.renderTime.toFixed(2) : '0'}
          unit="ms"
          status={getStatus(metrics.app?.renderTime || 0, { excellent: 16, good: 33, warning: 50 })}
          description="Average component render time"
        />

        <MetricCard
          title="Startup Time"
          value={metrics.app?.startupTime ? metrics.app.startupTime.toFixed(2) : '0'}
          unit="ms"
          status={getStatus(metrics.app?.startupTime || 0, { excellent: 1000, good: 2000, warning: 3000 })}
          description="Application startup time"
        />
      </View>

      {/* Cache Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Cache Performance</Text>
        
        <MetricCard
          title="Cache Hit Rate"
          value={metrics.cache?.hitRate ? (metrics.cache.hitRate * 100).toFixed(1) : '0'}
          unit="%"
          status={getStatus((metrics.cache?.hitRate || 0) * 100, { excellent: 90, good: 75, warning: 60 })}
          description="Percentage of cache hits"
        />

        <MetricCard
          title="Cache Size"
          value={metrics.cache?.totalSize ? (metrics.cache.totalSize / 1024).toFixed(2) : '0'}
          unit="KB"
          status={getStatus(metrics.cache?.totalSize || 0, { excellent: 1024 * 1024, good: 5 * 1024 * 1024, warning: 10 * 1024 * 1024 })}
          description="Total cache size"
        />
      </View>

      {/* Network Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Network Performance</Text>
        
        <MetricCard
          title="Network Requests"
          value={metrics.app?.networkRequests || 0}
          unit="requests"
          status={getStatus(metrics.app?.networkRequests || 0, { excellent: 10, good: 25, warning: 50 })}
          description="Total network requests"
        />
      </View>

      {/* Security Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Security Status</Text>
        
        <MetricCard
          title="Failed Login Attempts"
          value={metrics.security?.failedLoginAttempts || 0}
          unit="attempts"
          status={getStatus(metrics.security?.failedLoginAttempts || 0, { excellent: 0, good: 5, warning: 10 })}
          description="Recent failed login attempts"
        />

        <MetricCard
          title="Active Sessions"
          value={metrics.security?.activeSessions || 0}
          unit="sessions"
          status={getStatus(metrics.security?.activeSessions || 0, { excellent: 1, good: 5, warning: 10 })}
          description="Currently active user sessions"
        />
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        
        <View style={styles.quickActions}>
          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => cacheManager.clear()}
          >
            <Text style={styles.quickActionText}>Clear Cache</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => performanceMonitor.clearMetrics()}
          >
            <Text style={styles.quickActionText}>Reset Metrics</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.quickActionButton}
            onPress={() => analytics.forceFlush()}
          >
            <Text style={styles.quickActionText}>Flush Analytics</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  subtitle: {
    fontSize: 14,
    color: '#666',
  },
  scoreSection: {
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  scoreTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 10,
  },
  scoreContainer: {
    alignItems: 'center',
    padding: 20,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
  },
  actionButtons: {
    flexDirection: 'row',
    padding: 20,
    backgroundColor: '#fff',
    marginBottom: 10,
  },
  optimizeButton: {
    flex: 1,
    backgroundColor: '#007AFF',
    padding: 15,
    borderRadius: 8,
    marginRight: 10,
    alignItems: 'center',
  },
  disabledButton: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  configureButton: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#007AFF',
    alignItems: 'center',
  },
  configureButtonText: {
    color: '#007AFF',
    fontSize: 16,
    fontWeight: '600',
  },
  section: {
    backgroundColor: '#fff',
    marginBottom: 10,
    padding: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 15,
  },
  metricCard: {
    backgroundColor: '#f8f9fa',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    borderLeftWidth: 4,
  },
  metricHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  metricTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 12,
    color: '#fff',
    fontWeight: '600',
  },
  metricValue: {
    flexDirection: 'row',
    alignItems: 'baseline',
    marginBottom: 5,
  },
  valueText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  unitText: {
    fontSize: 14,
    color: '#666',
    marginLeft: 5,
  },
  descriptionText: {
    fontSize: 12,
    color: '#666',
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  quickActionButton: {
    flex: 1,
    backgroundColor: '#f0f0f0',
    padding: 12,
    borderRadius: 6,
    marginHorizontal: 5,
    alignItems: 'center',
  },
  quickActionText: {
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
}); 