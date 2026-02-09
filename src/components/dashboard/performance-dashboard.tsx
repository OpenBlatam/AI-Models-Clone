/**
 * @fileoverview Performance Monitoring Dashboard
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
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { 
  performanceMonitor,
  PerformanceMetric,
  PerformanceAlert,
  PerformanceOptimization,
  PerformanceReport
} from '../../lib/performance/performance-monitor';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface MetricCardProps {
  metric: PerformanceMetric;
  onViewDetails: (metric: PerformanceMetric) => void;
}

interface AlertCardProps {
  alert: PerformanceAlert;
  onResolve: (alert: PerformanceAlert) => void;
  onViewDetails: (alert: PerformanceAlert) => void;
}

interface OptimizationCardProps {
  optimization: PerformanceOptimization;
  onApply: (optimization: PerformanceOptimization) => void;
  onViewDetails: (optimization: PerformanceOptimization) => void;
}

interface ReportCardProps {
  report: PerformanceReport;
  onViewDetails: (report: PerformanceReport) => void;
}

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

const MetricCard: React.FC<MetricCardProps> = ({ metric, onViewDetails }) => {
  const getMetricColor = (type: string, value: number): string => {
    switch (type) {
      case 'render':
        return value > 16 ? '#FF3B30' : value > 8 ? '#FF9500' : '#34C759';
      case 'network':
        return value > 1000 ? '#FF3B30' : value > 500 ? '#FF9500' : '#34C759';
      case 'memory':
        return value > 200 ? '#FF3B30' : value > 100 ? '#FF9500' : '#34C759';
      case 'battery':
        return value < 20 ? '#FF3B30' : value < 50 ? '#FF9500' : '#34C759';
      case 'storage':
        return value > 1000 ? '#FF3B30' : value > 500 ? '#FF9500' : '#34C759';
      default:
        return '#007AFF';
    }
  };

  const getMetricIcon = (type: string): string => {
    switch (type) {
      case 'render': return '⚡';
      case 'network': return '🌐';
      case 'memory': return '💾';
      case 'cpu': return '🖥️';
      case 'battery': return '🔋';
      case 'storage': return '💿';
      default: return '📊';
    }
  };

  return (
    <View style={styles.metricCard}>
      <View style={styles.metricHeader}>
        <View style={styles.metricInfo}>
          <Text style={styles.metricIcon}>{getMetricIcon(metric.type)}</Text>
          <View style={styles.metricDetails}>
            <Text style={styles.metricName}>{metric.name}</Text>
            <Text style={styles.metricType}>{metric.type.toUpperCase()}</Text>
          </View>
        </View>
        <View style={styles.metricValueContainer}>
          <Text style={[styles.metricValue, { color: getMetricColor(metric.type, metric.value) }]}>
            {metric.value.toFixed(2)}
          </Text>
          <Text style={styles.metricUnit}>{metric.unit}</Text>
        </View>
      </View>
      
      <View style={styles.metricMetadata}>
        <Text style={styles.metadataText}>
          Component: {metric.metadata.component || 'System'}
        </Text>
        <Text style={styles.metadataText}>
          Time: {new Date(metric.timestamp).toLocaleTimeString()}
        </Text>
      </View>
      
      <AccessibleButton
        title="View Details"
        onPress={() => onViewDetails(metric)}
        style={styles.metricButton}
        variant="outline"
        size="small"
      />
    </View>
  );
};

// ============================================================================
// ALERT CARD COMPONENT
// ============================================================================

const AlertCard: React.FC<AlertCardProps> = ({ alert, onResolve, onViewDetails }) => {
  const getSeverityColor = (severity: string): string => {
    switch (severity) {
      case 'critical': return '#FF3B30';
      case 'high': return '#FF9500';
      case 'medium': return '#FFCC00';
      case 'low': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getSeverityIcon = (severity: string): string => {
    switch (severity) {
      case 'critical': return '🚨';
      case 'high': return '⚠️';
      case 'medium': return '⚡';
      case 'low': return 'ℹ️';
      default: return '📊';
    }
  };

  return (
    <View style={styles.alertCard}>
      <View style={styles.alertHeader}>
        <View style={styles.alertInfo}>
          <Text style={styles.alertIcon}>{getSeverityIcon(alert.severity)}</Text>
          <View style={styles.alertDetails}>
            <Text style={styles.alertTitle}>{alert.title}</Text>
            <Text style={styles.alertType}>{alert.type.toUpperCase()}</Text>
          </View>
        </View>
        <View style={[styles.severityBadge, { backgroundColor: getSeverityColor(alert.severity) }]}>
          <Text style={styles.severityBadgeText}>{alert.severity.toUpperCase()}</Text>
        </View>
      </View>
      
      <Text style={styles.alertMessage}>{alert.message}</Text>
      
      <View style={styles.alertDetails}>
        <Text style={styles.alertDetail}>
          Current Value: {alert.currentValue.toFixed(2)}
        </Text>
        <Text style={styles.alertDetail}>
          Time: {new Date(alert.timestamp).toLocaleTimeString()}
        </Text>
        <Text style={styles.alertDetail}>
          Status: {alert.resolved ? 'Resolved' : 'Active'}
        </Text>
      </View>
      
      <View style={styles.alertActions}>
        <AccessibleButton
          title="View Details"
          onPress={() => onViewDetails(alert)}
          style={styles.alertActionButton}
          variant="outline"
          size="small"
        />
        {!alert.resolved && (
          <AccessibleButton
            title="Resolve"
            onPress={() => onResolve(alert)}
            style={styles.alertActionButton}
            variant="primary"
            size="small"
          />
        )}
      </View>
    </View>
  );
};

// ============================================================================
// OPTIMIZATION CARD COMPONENT
// ============================================================================

const OptimizationCard: React.FC<OptimizationCardProps> = ({ optimization, onApply, onViewDetails }) => {
  const getImpactColor = (impact: string): string => {
    switch (impact) {
      case 'high': return '#34C759';
      case 'medium': return '#FF9500';
      case 'low': return '#8E8E93';
      default: return '#007AFF';
    }
  };

  const getEffortColor = (effort: string): string => {
    switch (effort) {
      case 'low': return '#34C759';
      case 'medium': return '#FF9500';
      case 'high': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.optimizationCard}>
      <View style={styles.optimizationHeader}>
        <View style={styles.optimizationInfo}>
          <Text style={styles.optimizationTitle}>{optimization.description}</Text>
          <Text style={styles.optimizationTarget}>Target: {optimization.target}</Text>
        </View>
        <View style={styles.optimizationBadges}>
          <View style={[styles.impactBadge, { backgroundColor: getImpactColor(optimization.impact) }]}>
            <Text style={styles.impactBadgeText}>{optimization.impact.toUpperCase()}</Text>
          </View>
          <View style={[styles.effortBadge, { backgroundColor: getEffortColor(optimization.effort) }]}>
            <Text style={styles.effortBadgeText}>{optimization.effort.toUpperCase()}</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.optimizationDetails}>
        <Text style={styles.optimizationDetail}>
          Strategy: {optimization.strategy.replace('_', ' ').toUpperCase()}
        </Text>
        <Text style={styles.optimizationDetail}>
          Priority: {optimization.priority}
        </Text>
        <Text style={styles.optimizationDetail}>
          Status: {optimization.applied ? 'Applied' : 'Pending'}
        </Text>
        {optimization.applied && optimization.results && (
          <Text style={styles.optimizationDetail}>
            Improvement: {optimization.results.improvement.toFixed(2)}%
          </Text>
        )}
      </View>
      
      <View style={styles.optimizationActions}>
        <AccessibleButton
          title="View Details"
          onPress={() => onViewDetails(optimization)}
          style={styles.optimizationActionButton}
          variant="outline"
          size="small"
        />
        {!optimization.applied && (
          <AccessibleButton
            title="Apply"
            onPress={() => onApply(optimization)}
            style={styles.optimizationActionButton}
            variant="primary"
            size="small"
          />
        )}
      </View>
    </View>
  );
};

// ============================================================================
// REPORT CARD COMPONENT
// ============================================================================

const ReportCard: React.FC<ReportCardProps> = ({ report, onViewDetails }) => {
  return (
    <View style={styles.reportCard}>
      <View style={styles.reportHeader}>
        <View style={styles.reportInfo}>
          <Text style={styles.reportTitle}>
            {report.period.toUpperCase()} Performance Report
          </Text>
          <Text style={styles.reportPeriod}>
            {new Date(report.startTime).toLocaleDateString()} - {new Date(report.endTime).toLocaleDateString()}
          </Text>
        </View>
        <View style={styles.reportStats}>
          <Text style={styles.reportStat}>{report.summary.totalMetrics} Metrics</Text>
          <Text style={styles.reportStat}>{report.summary.alertCount} Alerts</Text>
        </View>
      </View>
      
      <View style={styles.reportSummary}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Critical Alerts</Text>
          <Text style={[styles.summaryValue, { color: '#FF3B30' }]}>
            {report.summary.criticalAlerts}
          </Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryLabel}>Insights</Text>
          <Text style={[styles.summaryValue, { color: '#007AFF' }]}>
            {report.insights.length}
          </Text>
        </View>
      </View>
      
      <AccessibleButton
        title="View Full Report"
        onPress={() => onViewDetails(report)}
        style={styles.reportButton}
        variant="primary"
        size="small"
      />
    </View>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

export function PerformanceDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'metrics' | 'alerts' | 'optimizations' | 'reports'>('overview');
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [alerts, setAlerts] = useState<PerformanceAlert[]>([]);
  const [optimizations, setOptimizations] = useState<PerformanceOptimization[]>([]);
  const [reports, setReports] = useState<PerformanceReport[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    initializeDashboard();
  }, []);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  const initializeDashboard = useCallback(async () => {
    setIsLoading(true);
    try {
      await refreshData();
      
      // Set up event listeners
      performanceMonitor.on('metricRecorded', () => refreshData());
      performanceMonitor.on('alertCreated', () => refreshData());
      performanceMonitor.on('optimizationSuggested', () => refreshData());
      performanceMonitor.on('reportGenerated', () => refreshData());

    } catch (error) {
      Alert.alert('Error', 'Failed to initialize dashboard');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    await refreshData();
    setIsRefreshing(false);
  }, []);

  const refreshData = useCallback(async () => {
    try {
      const metricsData = performanceMonitor.getMetrics();
      const alertsData = performanceMonitor.getAlerts();
      const optimizationsData = performanceMonitor.getOptimizations();
      const reportsData = performanceMonitor.getReports();
      
      setMetrics(metricsData);
      setAlerts(alertsData);
      setOptimizations(optimizationsData);
      setReports(reportsData);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewMetricDetails = useCallback((metric: PerformanceMetric) => {
    Alert.alert(
      metric.name,
      `Type: ${metric.type}\nValue: ${metric.value.toFixed(2)} ${metric.unit}\nComponent: ${metric.metadata.component || 'System'}\nTime: ${new Date(metric.timestamp).toLocaleString()}`
    );
  }, []);

  const handleResolveAlert = useCallback((alert: PerformanceAlert) => {
    Alert.alert(
      'Resolve Alert',
      `Are you sure you want to resolve this alert?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Resolve',
          onPress: () => {
            const success = performanceMonitor.resolveAlert(alert.id);
            if (success) {
              Alert.alert('Success', 'Alert resolved successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to resolve alert');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleViewAlertDetails = useCallback((alert: PerformanceAlert) => {
    Alert.alert(
      alert.title,
      `Message: ${alert.message}\nSeverity: ${alert.severity}\nType: ${alert.type}\nCurrent Value: ${alert.currentValue.toFixed(2)}\nTime: ${new Date(alert.timestamp).toLocaleString()}\nStatus: ${alert.resolved ? 'Resolved' : 'Active'}`
    );
  }, []);

  const handleApplyOptimization = useCallback((optimization: PerformanceOptimization) => {
    Alert.alert(
      'Apply Optimization',
      `Are you sure you want to apply this optimization?\n\n${optimization.description}`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Apply',
          onPress: () => {
            const success = performanceMonitor.applyOptimization(optimization.id);
            if (success) {
              Alert.alert('Success', 'Optimization applied successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to apply optimization');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleViewOptimizationDetails = useCallback((optimization: PerformanceOptimization) => {
    Alert.alert(
      'Optimization Details',
      `Description: ${optimization.description}\nTarget: ${optimization.target}\nStrategy: ${optimization.strategy}\nImpact: ${optimization.impact}\nEffort: ${optimization.effort}\nPriority: ${optimization.priority}\nStatus: ${optimization.applied ? 'Applied' : 'Pending'}`
    );
  }, []);

  const handleViewReportDetails = useCallback((report: PerformanceReport) => {
    const insightsText = report.insights.map(insight => 
      `• ${insight.title}: ${insight.description}`
    ).join('\n\n');
    
    Alert.alert(
      'Performance Report',
      `Period: ${report.period}\nTotal Metrics: ${report.summary.totalMetrics}\nAlerts: ${report.summary.alertCount}\nCritical Alerts: ${report.summary.criticalAlerts}\nInsights: ${report.insights.length}\n\nInsights:\n${insightsText || 'No insights available'}`
    );
  }, []);

  const handleGenerateReport = useCallback(() => {
    Alert.alert(
      'Generate Report',
      'Select report period:',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Hourly', onPress: () => {
          const endTime = Date.now();
          const startTime = endTime - (60 * 60 * 1000); // 1 hour ago
          const report = performanceMonitor.generateReport('hourly', startTime, endTime);
          Alert.alert('Success', 'Hourly report generated successfully');
          refreshData();
        }},
        { text: 'Daily', onPress: () => {
          const endTime = Date.now();
          const startTime = endTime - (24 * 60 * 60 * 1000); // 1 day ago
          const report = performanceMonitor.generateReport('daily', startTime, endTime);
          Alert.alert('Success', 'Daily report generated successfully');
          refreshData();
        }},
        { text: 'Weekly', onPress: () => {
          const endTime = Date.now();
          const startTime = endTime - (7 * 24 * 60 * 60 * 1000); // 1 week ago
          const report = performanceMonitor.generateReport('weekly', startTime, endTime);
          Alert.alert('Success', 'Weekly report generated successfully');
          refreshData();
        }},
      ]
    );
  }, [refreshData]);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string): JSX.Element => (
    <AccessibleButton
      title={label}
      accessibilityLabel={`Switch to ${label} tab`}
      onPress={() => handleTabChange(tab)}
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      textStyle={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}
      variant="ghost"
      size="small"
    />
  );

  const renderOverviewTab = (): JSX.Element => {
    const stats = performanceMonitor.getSystemStats();
    const recentMetrics = metrics.slice(0, 5);
    const activeAlerts = alerts.filter(alert => !alert.resolved).slice(0, 3);
    const pendingOptimizations = optimizations.filter(opt => !opt.applied).slice(0, 3);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {/* System Stats */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalMetrics}</Text>
              <Text style={styles.statLabel}>Total Metrics</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeAlerts}</Text>
              <Text style={styles.statLabel}>Active Alerts</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalOptimizations}</Text>
              <Text style={styles.statLabel}>Optimizations</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.appliedOptimizations}</Text>
              <Text style={styles.statLabel}>Applied</Text>
            </View>
          </View>
        </View>

        {/* Recent Metrics */}
        {recentMetrics.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Metrics</Text>
            {recentMetrics.map(metric => (
              <MetricCard
                key={metric.id}
                metric={metric}
                onViewDetails={handleViewMetricDetails}
              />
            ))}
          </View>
        )}

        {/* Active Alerts */}
        {activeAlerts.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Alerts</Text>
            {activeAlerts.map(alert => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onResolve={handleResolveAlert}
                onViewDetails={handleViewAlertDetails}
              />
            ))}
          </View>
        )}

        {/* Pending Optimizations */}
        {pendingOptimizations.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Pending Optimizations</Text>
            {pendingOptimizations.map(optimization => (
              <OptimizationCard
                key={optimization.id}
                optimization={optimization}
                onApply={handleApplyOptimization}
                onViewDetails={handleViewOptimizationDetails}
              />
            ))}
          </View>
        )}

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="🔄 Refresh Data"
              onPress={handleRefresh}
              style={styles.actionButton}
              variant="primary"
              size="small"
            />
            <AccessibleButton
              title="📊 Generate Report"
              onPress={handleGenerateReport}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="📈 View Metrics"
              onPress={() => handleTabChange('metrics')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderMetricsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Metrics</Text>
        {metrics.length > 0 ? (
          metrics.map(metric => (
            <MetricCard
              key={metric.id}
              metric={metric}
              onViewDetails={handleViewMetricDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No metrics available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderAlertsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Alerts</Text>
        {alerts.length > 0 ? (
          alerts.map(alert => (
            <AlertCard
              key={alert.id}
              alert={alert}
              onResolve={handleResolveAlert}
              onViewDetails={handleViewAlertDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No alerts available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderOptimizationsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Optimizations</Text>
        {optimizations.length > 0 ? (
          optimizations.map(optimization => (
            <OptimizationCard
              key={optimization.id}
              optimization={optimization}
              onApply={handleApplyOptimization}
              onViewDetails={handleViewOptimizationDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No optimizations available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderReportsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Reports</Text>
        {reports.length > 0 ? (
          reports.map(report => (
            <ReportCard
              key={report.id}
              report={report}
              onViewDetails={handleViewReportDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No reports available</Text>
          </View>
        )}
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
        <Text style={styles.headerTitle}>Performance Monitor</Text>
        <Text style={styles.headerSubtitle}>
          Real-time Performance Monitoring & Optimization
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('metrics', 'Metrics')}
        {renderTabButton('alerts', 'Alerts')}
        {renderTabButton('optimizations', 'Optimizations')}
        {renderTabButton('reports', 'Reports')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'metrics' && renderMetricsTab()}
        {activeTab === 'alerts' && renderAlertsTab()}
        {activeTab === 'optimizations' && renderOptimizationsTab()}
        {activeTab === 'reports' && renderReportsTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading...</Text>
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
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  metricCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  metricHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  metricInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  metricIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  metricDetails: {
    flex: 1,
  },
  metricName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  metricType: {
    fontSize: 12,
    color: '#666',
  },
  metricValueContainer: {
    alignItems: 'flex-end',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 2,
  },
  metricUnit: {
    fontSize: 12,
    color: '#666',
  },
  metricMetadata: {
    marginBottom: 12,
  },
  metadataText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  metricButton: {
    width: '100%',
  },
  alertCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  alertHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  alertInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  alertIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  alertDetails: {
    flex: 1,
  },
  alertTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  alertType: {
    fontSize: 12,
    color: '#666',
  },
  severityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  severityBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  alertMessage: {
    fontSize: 14,
    color: '#333',
    marginBottom: 12,
    lineHeight: 20,
  },
  alertDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  alertActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  alertActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  optimizationCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  optimizationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  optimizationInfo: {
    flex: 1,
  },
  optimizationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  optimizationTarget: {
    fontSize: 12,
    color: '#666',
  },
  optimizationBadges: {
    flexDirection: 'row',
  },
  impactBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  impactBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  effortBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  effortBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  optimizationDetails: {
    marginBottom: 12,
  },
  optimizationDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  optimizationActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  optimizationActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  reportCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  reportHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  reportInfo: {
    flex: 1,
  },
  reportTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  reportPeriod: {
    fontSize: 12,
    color: '#666',
  },
  reportStats: {
    alignItems: 'flex-end',
  },
  reportStat: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  reportSummary: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  reportButton: {
    width: '100%',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginHorizontal: 4,
    marginVertical: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
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
  loadingText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    marginTop: 16,
  },
});

export default PerformanceDashboard;
