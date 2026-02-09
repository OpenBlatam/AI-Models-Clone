/**
 * @fileoverview Performance Monitoring Demo Component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { PerformanceDashboard } from '../dashboard/performance-dashboard';
import { performanceMonitor } from '../../lib/performance/performance-monitor';

// ============================================================================
// MAIN DEMO COMPONENT
// ============================================================================

export function PerformanceDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'demo' | 'dashboard' | 'scenarios'>('demo');
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [demoDataLoaded, setDemoDataLoaded] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    initializeDemo();
  }, []);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  const initializeDemo = useCallback(async () => {
    setIsLoading(true);
    try {
      await loadDemoData();
      setDemoDataLoaded(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadDemoData = useCallback(async () => {
    // Generate demo metrics
    const demoMetrics = [
      { type: 'render' as const, name: 'component_render_time', value: 12.5, unit: 'ms', metadata: { component: 'Dashboard' } },
      { type: 'render' as const, name: 'component_render_time', value: 18.2, unit: 'ms', metadata: { component: 'UserList' } },
      { type: 'network' as const, name: 'network_request_duration', value: 850, unit: 'ms', metadata: { url: '/api/users' } },
      { type: 'network' as const, name: 'network_request_duration', value: 1200, unit: 'ms', metadata: { url: '/api/analytics' } },
      { type: 'memory' as const, name: 'memory_usage', value: 150, unit: 'MB', metadata: { component: 'ImageGallery' } },
      { type: 'memory' as const, name: 'memory_usage', value: 85, unit: 'MB', metadata: { component: 'System' } },
      { type: 'battery' as const, name: 'battery_level', value: 75, unit: '%', metadata: {} },
      { type: 'storage' as const, name: 'storage_used', value: 650, unit: 'MB', metadata: {} },
    ];

    // Record demo metrics
    demoMetrics.forEach(metric => {
      performanceMonitor.recordMetric(metric);
    });

    // Generate demo alerts
    const demoAlerts = [
      {
        metricId: 'demo_metric_1',
        type: 'threshold' as const,
        severity: 'high' as const,
        title: 'High Render Time Alert',
        message: 'Component render time exceeded threshold (16ms)',
        threshold: { max: 16, operator: 'gt' },
        currentValue: 18.2,
        metadata: { component: 'UserList' },
      },
      {
        metricId: 'demo_metric_2',
        type: 'threshold' as const,
        severity: 'medium' as const,
        title: 'Slow Network Request',
        message: 'Network request duration is high (1200ms)',
        threshold: { max: 1000, operator: 'gt' },
        currentValue: 1200,
        metadata: { url: '/api/analytics' },
      },
    ];

    // Create demo alerts
    demoAlerts.forEach(alert => {
      performanceMonitor.createAlert(alert);
    });

    // Generate demo optimizations
    const demoOptimizations = [
      {
        type: 'component' as const,
        target: 'UserList',
        strategy: 'memoization' as const,
        description: 'UserList component render time is high. Consider using React.memo.',
        impact: 'high' as const,
        effort: 'medium' as const,
        priority: 1,
        applied: false,
        metadata: { component: 'UserList' },
      },
      {
        type: 'network' as const,
        target: '/api/analytics',
        strategy: 'caching' as const,
        description: 'Analytics API request is slow. Consider implementing caching.',
        impact: 'medium' as const,
        effort: 'low' as const,
        priority: 2,
        applied: false,
        metadata: { url: '/api/analytics' },
      },
    ];

    // Suggest demo optimizations
    demoOptimizations.forEach(optimization => {
      performanceMonitor.suggestOptimization({
        type: optimization.type,
        name: optimization.type === 'component' ? 'component_render_time' : 'network_request_duration',
        value: optimization.type === 'component' ? 18.2 : 1200,
        unit: optimization.type === 'component' ? 'ms' : 'ms',
        metadata: optimization.metadata,
      });
    });

    // Generate demo report
    const endTime = Date.now();
    const startTime = endTime - (24 * 60 * 60 * 1000); // 1 day ago
    performanceMonitor.generateReport('daily', startTime, endTime);
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await loadDemoData();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh demo data');
    } finally {
      setIsRefreshing(false);
    }
  }, [loadDemoData]);

  const handleSimulateMetric = useCallback(() => {
    const metricTypes = ['render', 'network', 'memory', 'battery', 'storage'];
    const randomType = metricTypes[Math.floor(Math.random() * metricTypes.length)];
    
    let metric;
    switch (randomType) {
      case 'render':
        metric = {
          type: 'render' as const,
          name: 'component_render_time',
          value: Math.random() * 30 + 5, // 5-35ms
          unit: 'ms',
          metadata: { component: 'DemoComponent' },
        };
        break;
      case 'network':
        metric = {
          type: 'network' as const,
          name: 'network_request_duration',
          value: Math.random() * 2000 + 100, // 100-2100ms
          unit: 'ms',
          metadata: { url: '/api/demo' },
        };
        break;
      case 'memory':
        metric = {
          type: 'memory' as const,
          name: 'memory_usage',
          value: Math.random() * 300 + 50, // 50-350MB
          unit: 'MB',
          metadata: { component: 'DemoComponent' },
        };
        break;
      case 'battery':
        metric = {
          type: 'battery' as const,
          name: 'battery_level',
          value: Math.random() * 100, // 0-100%
          unit: '%',
          metadata: {},
        };
        break;
      case 'storage':
        metric = {
          type: 'storage' as const,
          name: 'storage_used',
          value: Math.random() * 1500 + 100, // 100-1600MB
          unit: 'MB',
          metadata: {},
        };
        break;
    }

    if (metric) {
      performanceMonitor.recordMetric(metric);
      Alert.alert('Success', `Simulated ${randomType} metric recorded`);
    }
  }, []);

  const handleSimulateAlert = useCallback(() => {
    const alertTypes = [
      {
        type: 'threshold' as const,
        severity: 'high' as const,
        title: 'Performance Threshold Exceeded',
        message: 'A performance metric has exceeded its threshold value',
        threshold: { max: 1000, operator: 'gt' },
        currentValue: 1200,
        metadata: { metric: 'demo' },
      },
      {
        type: 'anomaly' as const,
        severity: 'medium' as const,
        title: 'Performance Anomaly Detected',
        message: 'An unusual performance pattern has been detected',
        threshold: { max: 500, operator: 'gt' },
        currentValue: 750,
        metadata: { metric: 'demo' },
      },
    ];

    const randomAlert = alertTypes[Math.floor(Math.random() * alertTypes.length)];
    performanceMonitor.createAlert(randomAlert);
    Alert.alert('Success', 'Simulated alert created');
  }, []);

  const handleGenerateReport = useCallback(() => {
    const periods = ['hourly', 'daily', 'weekly'] as const;
    const randomPeriod = periods[Math.floor(Math.random() * periods.length)];
    
    const endTime = Date.now();
    let startTime;
    switch (randomPeriod) {
      case 'hourly':
        startTime = endTime - (60 * 60 * 1000);
        break;
      case 'daily':
        startTime = endTime - (24 * 60 * 60 * 1000);
        break;
      case 'weekly':
        startTime = endTime - (7 * 24 * 60 * 60 * 1000);
        break;
    }

    const report = performanceMonitor.generateReport(randomPeriod, startTime, endTime);
    Alert.alert('Success', `${randomPeriod} report generated with ${report.summary.totalMetrics} metrics`);
  }, []);

  const handleViewSystemStats = useCallback(() => {
    const stats = performanceMonitor.getSystemStats();
    Alert.alert(
      'System Statistics',
      `Total Metrics: ${stats.totalMetrics}\nTotal Alerts: ${stats.totalAlerts}\nActive Alerts: ${stats.activeAlerts}\nTotal Optimizations: ${stats.totalOptimizations}\nApplied Optimizations: ${stats.appliedOptimizations}\nTotal Reports: ${stats.totalReports}`
    );
  }, []);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string, icon: string): JSX.Element => (
    <AccessibleButton
      title={`${icon} ${label}`}
      accessibilityLabel={`Switch to ${label} tab`}
      onPress={() => handleTabChange(tab)}
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      textStyle={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}
      variant="ghost"
      size="small"
    />
  );

  const renderDemoTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Demo Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Performance Monitoring Demo</Text>
        <Text style={styles.sectionDescription}>
          This demo showcases a comprehensive performance monitoring system with real-time metrics collection, alerting, optimization suggestions, and reporting capabilities.
        </Text>
        <View style={styles.featureList}>
          <Text style={styles.featureItem}>• Real-time performance metrics collection</Text>
          <Text style={styles.featureItem}>• Intelligent alerting with threshold management</Text>
          <Text style={styles.featureItem}>• Automated optimization suggestions</Text>
          <Text style={styles.featureItem}>• Comprehensive performance reporting</Text>
          <Text style={styles.featureItem}>• System-wide performance monitoring</Text>
          <Text style={styles.featureItem}>• Performance insights and recommendations</Text>
        </View>
      </View>

      {/* Demo Data Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📈 Demo Data Status</Text>
        <View style={styles.statusGrid}>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>8</Text>
            <Text style={styles.statusLabel}>Demo Metrics</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>2</Text>
            <Text style={styles.statusLabel}>Demo Alerts</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>2</Text>
            <Text style={styles.statusLabel}>Demo Optimizations</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>1</Text>
            <Text style={styles.statusLabel}>Demo Report</Text>
          </View>
        </View>
        <Text style={styles.statusDescription}>
          Demo data has been loaded into the performance monitoring system. You can now explore the dashboard and test various scenarios.
        </Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Quick Actions</Text>
        <View style={styles.actionGrid}>
          <AccessibleButton
            title="📊 Simulate Metric"
            onPress={handleSimulateMetric}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="🚨 Simulate Alert"
            onPress={handleSimulateAlert}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="📋 Generate Report"
            onPress={handleGenerateReport}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="📈 View System Stats"
            onPress={handleViewSystemStats}
            style={styles.actionButton}
            variant="outline"
            size="small"
          />
          <AccessibleButton
            title="🔄 Refresh Demo Data"
            onPress={handleRefresh}
            style={styles.actionButton}
            variant="outline"
            size="small"
          />
        </View>
      </View>

      {/* Demo Scenarios */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Demo Scenarios</Text>
        <View style={styles.scenarioList}>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Real-time Performance Monitoring</Text>
            <Text style={styles.scenarioDescription}>
              Monitor component render times, network requests, memory usage, battery level, and storage usage in real-time.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Intelligent Alerting System</Text>
            <Text style={styles.scenarioDescription}>
              Automatic alerts when performance metrics exceed thresholds, with severity levels and resolution tracking.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Performance Optimization</Text>
            <Text style={styles.scenarioDescription}>
              AI-powered optimization suggestions based on performance patterns, with impact and effort analysis.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Comprehensive Reporting</Text>
            <Text style={styles.scenarioDescription}>
              Generate detailed performance reports with insights, trends, and recommendations for improvement.
            </Text>
          </View>
        </View>
      </View>

      {/* Navigation */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🧭 Navigation</Text>
        <View style={styles.navigationButtons}>
          <AccessibleButton
            title="📊 Open Dashboard"
            onPress={() => handleTabChange('dashboard')}
            style={styles.navigationButton}
            variant="primary"
            size="medium"
          />
          <AccessibleButton
            title="🔄 Refresh Demo Data"
            onPress={handleRefresh}
            style={styles.navigationButton}
            variant="secondary"
            size="medium"
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderDashboardTab = (): JSX.Element => {
    if (!demoDataLoaded) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading dashboard...</Text>
        </View>
      );
    }

    return <PerformanceDashboard />;
  };

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Scenario Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Performance Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Explore different performance monitoring scenarios and use cases:
        </Text>
      </View>

      {/* Scenario 1: Real-time Monitoring */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Real-time Performance Monitoring</Text>
        <Text style={styles.scenarioDescription}>
          Continuous monitoring of application performance with real-time metrics collection and visualization.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Component render time tracking</Text>
          <Text style={styles.scenarioFeature}>• Network request monitoring</Text>
          <Text style={styles.scenarioFeature}>• Memory usage tracking</Text>
          <Text style={styles.scenarioFeature}>• Battery level monitoring</Text>
          <Text style={styles.scenarioFeature}>• Storage usage tracking</Text>
        </View>
        <AccessibleButton
          title="Explore Real-time Monitoring"
          onPress={() => Alert.alert('Scenario', 'Real-time monitoring scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 2: Alert Management */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🚨 Performance Alert Management</Text>
        <Text style={styles.scenarioDescription}>
          Intelligent alerting system with threshold management, severity levels, and automated resolution tracking.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Threshold-based alerting</Text>
          <Text style={styles.scenarioFeature}>• Severity level classification</Text>
          <Text style={styles.scenarioFeature}>• Alert resolution tracking</Text>
          <Text style={styles.scenarioFeature}>• Custom alert rules</Text>
        </View>
        <AccessibleButton
          title="Explore Alert Management"
          onPress={() => Alert.alert('Scenario', 'Alert management scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 3: Performance Optimization */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Performance Optimization</Text>
        <Text style={styles.scenarioDescription}>
          AI-powered performance optimization with automated suggestions and impact analysis.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Automated optimization suggestions</Text>
          <Text style={styles.scenarioFeature}>• Impact and effort analysis</Text>
          <Text style={styles.scenarioFeature}>• Performance improvement tracking</Text>
          <Text style={styles.scenarioFeature}>• Optimization strategy recommendations</Text>
        </View>
        <AccessibleButton
          title="Explore Performance Optimization"
          onPress={() => Alert.alert('Scenario', 'Performance optimization scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 4: Performance Reporting */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📋 Performance Reporting</Text>
        <Text style={styles.scenarioDescription}>
          Comprehensive performance reporting with insights, trends, and actionable recommendations.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Automated report generation</Text>
          <Text style={styles.scenarioFeature}>• Performance insights and trends</Text>
          <Text style={styles.scenarioFeature}>• Actionable recommendations</Text>
          <Text style={styles.scenarioFeature}>• Historical performance analysis</Text>
        </View>
        <AccessibleButton
          title="Explore Performance Reporting"
          onPress={() => Alert.alert('Scenario', 'Performance reporting scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Performance Monitoring Demo</Text>
        <Text style={styles.headerSubtitle}>
          Comprehensive Performance Monitoring & Optimization System
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('demo', 'Demo', '🚀')}
        {renderTabButton('dashboard', 'Dashboard', '📊')}
        {renderTabButton('scenarios', 'Scenarios', '🎯')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'demo' && renderDemoTab()}
        {activeTab === 'dashboard' && renderDashboardTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Initializing demo...</Text>
        </View>
      )}
    </SafeAreaView>
  );
}

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    backgroundColor: '#007AFF',
    padding: 20,
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  headerSubtitle: {
    fontSize: 16,
    color: '#ffffff',
    opacity: 0.9,
    textAlign: 'center',
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  tabButton: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabButtonActive: {
    borderBottomColor: '#007AFF',
  },
  tabButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  tabButtonTextActive: {
    color: '#007AFF',
  },
  contentContainer: {
    flex: 1,
  },
  tabContent: {
    flex: 1,
    padding: 16,
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    marginBottom: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  featureList: {
    marginTop: 8,
  },
  featureItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statusItem: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statusValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statusLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  statusDescription: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    paddingVertical: 12,
    marginBottom: 8,
  },
  scenarioList: {
    marginTop: 8,
  },
  scenarioItem: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  scenarioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  scenarioDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 18,
  },
  scenarioFeatures: {
    marginTop: 8,
  },
  scenarioFeature: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  scenarioButton: {
    marginTop: 12,
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  navigationButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 16,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});

export default PerformanceDemo;
