/**
 * @fileoverview AI-powered dashboard component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import AIChatInterface from '../ai/ai-chat-interface';
import {
  AIModel,
  AITask,
  AIWorkflowExecution,
  AIEvent,
  AISystemConfig,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DashboardMetric {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
}

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  models: number;
  activeTasks: number;
  activeExecutions: number;
  recentEvents: number;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI-powered dashboard component
 * Provides comprehensive overview of AI system performance and health
 */
export function AIDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const [activeTab, setActiveTab] = useState<'overview' | 'chat' | 'models' | 'monitoring'>('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Initialize AI manager on component mount
  useEffect(() => {
    if (!ai.isInitialized) {
      ai.initialize();
    }
  }, [ai]);

  // Update system health when data changes
  useEffect(() => {
    updateSystemHealth();
  }, [ai.models, ai.activeTasks, ai.activeExecutions, ai.recentEvents]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await ai.refreshData();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh dashboard data');
    } finally {
      setRefreshing(false);
    }
  }, [ai]);

  const handleModelToggle = useCallback(async (modelId: string, isEnabled: boolean) => {
    try {
      await ai.updateModel(modelId, { isEnabled });
    } catch (error) {
      Alert.alert('Error', 'Failed to update model status');
    }
  }, [ai]);

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  const updateSystemHealth = useCallback(() => {
    const activeModels = ai.models.filter(model => model.isEnabled);
    const totalTasks = ai.activeTasks.length;
    const totalExecutions = ai.activeExecutions.length;
    const recentEventsCount = ai.recentEvents.length;

    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    
    if (totalTasks > 50 || totalExecutions > 20) {
      status = 'degraded';
    }
    
    if (totalTasks > 100 || totalExecutions > 50) {
      status = 'unhealthy';
    }

    setSystemHealth({
      status,
      models: activeModels.length,
      activeTasks: totalTasks,
      activeExecutions: totalExecutions,
      recentEvents: recentEventsCount,
    });
  }, [ai.models, ai.activeTasks, ai.activeExecutions, ai.recentEvents]);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '#4CAF50';
      case 'degraded':
        return '#FF9800';
      case 'unhealthy':
        return '#F44336';
      default:
        return '#666';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '🟢';
      case 'degraded':
        return '🟡';
      case 'unhealthy':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const formatTimestamp = (timestamp: number): string => {
    const now = Date.now();
    const diff = now - timestamp;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string): JSX.Element => (
    <AccessibleButton
      accessibilityLabel={`Switch to ${label} tab`}
      onPress={() => handleTabChange(tab)}
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
    >
      <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
        {label}
      </Text>
    </AccessibleButton>
  );

  const renderMetricCard = (metric: DashboardMetric): JSX.Element => (
    <View key={metric.label} style={styles.metricCard}>
      <Text style={styles.metricLabel}>{metric.label}</Text>
      <View style={styles.metricValueContainer}>
        <Text style={[styles.metricValue, { color: metric.color || '#333' }]}>
          {metric.value}
        </Text>
        {metric.unit && <Text style={styles.metricUnit}>{metric.unit}</Text>}
      </View>
      {metric.trend && (
        <Text style={[styles.metricTrend, { color: metric.trend === 'up' ? '#4CAF50' : '#F44336' }]}>
          {metric.trend === 'up' ? '↗' : metric.trend === 'down' ? '↘' : '→'}
        </Text>
      )}
    </View>
  );

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Health Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Health</Text>
        {systemHealth && (
          <View style={[styles.healthCard, { borderColor: getStatusColor(systemHealth.status) }]}>
            <View style={styles.healthHeader}>
              <Text style={styles.healthStatus}>
                {getStatusIcon(systemHealth.status)} {systemHealth.status.toUpperCase()}
              </Text>
              <Text style={styles.healthTimestamp}>
                {formatTimestamp(Date.now())}
              </Text>
            </View>
            <View style={styles.healthMetrics}>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.models}</Text>
                <Text style={styles.healthMetricLabel}>Active Models</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.activeTasks}</Text>
                <Text style={styles.healthMetricLabel}>Active Tasks</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.activeExecutions}</Text>
                <Text style={styles.healthMetricLabel}>Executions</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.recentEvents}</Text>
                <Text style={styles.healthMetricLabel}>Recent Events</Text>
              </View>
            </View>
          </View>
        )}
      </View>

      {/* Key Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Metrics</Text>
        <View style={styles.metricsGrid}>
          {[
            { label: 'Total Models', value: ai.models.length, unit: 'models' },
            { label: 'Enabled Models', value: ai.models.filter(m => m.isEnabled).length, unit: 'models' },
            { label: 'Active Tasks', value: ai.activeTasks.length, unit: 'tasks' },
            { label: 'Workflow Executions', value: ai.activeExecutions.length, unit: 'executions' },
            { label: 'Recent Events', value: ai.recentEvents.length, unit: 'events' },
            { label: 'System Status', value: systemHealth?.status || 'unknown', color: getStatusColor(systemHealth?.status || 'unknown') },
          ].map(renderMetricCard)}
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          {ai.recentEvents.slice(0, 10).map(event => (
            <View key={event.id} style={styles.activityItem}>
              <View style={styles.activityHeader}>
                <Text style={styles.activityType}>{event.type}</Text>
                <Text style={styles.activityTimestamp}>
                  {formatTimestamp(event.timestamp)}
                </Text>
              </View>
              {event.userId && (
                <Text style={styles.activityUser}>User: {event.userId}</Text>
              )}
            </View>
          ))}
          {ai.recentEvents.length === 0 && (
            <Text style={styles.emptyText}>No recent activity</Text>
          )}
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <AccessibleButton
            accessibilityLabel="Refresh dashboard data"
            onPress={handleRefresh}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>🔄 Refresh</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Cleanup system"
            onPress={ai.cleanup}
            style={[styles.actionButton, styles.actionButtonWarning]}
          >
            <Text style={styles.actionButtonText}>🧹 Cleanup</Text>
          </AccessibleButton>
        </View>
      </View>
    </ScrollView>
  );

  const renderModelsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Models</Text>
        <View style={styles.modelsList}>
          {ai.models.map(model => (
            <View key={model.id} style={styles.modelCard}>
              <View style={styles.modelHeader}>
                <Text style={styles.modelName}>{model.name}</Text>
                <View style={styles.modelStatus}>
                  <View style={[
                    styles.statusIndicator,
                    { backgroundColor: model.isEnabled ? '#4CAF50' : '#F44336' }
                  ]} />
                  <Text style={styles.statusText}>
                    {model.isEnabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
              </View>
              <Text style={styles.modelDescription}>{model.description}</Text>
              <View style={styles.modelDetails}>
                <Text style={styles.modelDetail}>Type: {model.config.modelType}</Text>
                <Text style={styles.modelDetail}>Provider: {model.config.provider}</Text>
                <Text style={styles.modelDetail}>Version: {model.config.version}</Text>
                <Text style={styles.modelDetail}>Accuracy: {(model.metrics.accuracy * 100).toFixed(1)}%</Text>
              </View>
              <View style={styles.modelActions}>
                <AccessibleButton
                  accessibilityLabel={`Toggle ${model.name} model`}
                  onPress={() => handleModelToggle(model.id, !model.isEnabled)}
                  style={[styles.smallButton, model.isEnabled ? styles.disableButton : styles.enableButton]}
                >
                  <Text style={styles.smallButtonText}>
                    {model.isEnabled ? 'Disable' : 'Enable'}
                  </Text>
                </AccessibleButton>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* Active Tasks */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Active Tasks</Text>
        <View style={styles.monitoringList}>
          {ai.activeTasks.map(task => (
            <View key={task.id} style={styles.monitoringItem}>
              <View style={styles.monitoringHeader}>
                <Text style={styles.monitoringTitle}>{task.type}</Text>
                <Text style={styles.monitoringStatus}>{task.status}</Text>
              </View>
              <Text style={styles.monitoringSubtitle}>
                Progress: {task.progress}% | Priority: {task.priority}
              </Text>
              <Text style={styles.monitoringTimestamp}>
                Created: {formatTimestamp(task.createdAt)}
              </Text>
            </View>
          ))}
          {ai.activeTasks.length === 0 && (
            <Text style={styles.emptyText}>No active tasks</Text>
          )}
        </View>
      </View>

      {/* Workflow Executions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Workflow Executions</Text>
        <View style={styles.monitoringList}>
          {ai.activeExecutions.map(exec => (
            <View key={exec.id} style={styles.monitoringItem}>
              <View style={styles.monitoringHeader}>
                <Text style={styles.monitoringTitle}>Workflow {exec.workflowId}</Text>
                <Text style={styles.monitoringStatus}>{exec.status}</Text>
              </View>
              <Text style={styles.monitoringSubtitle}>
                Progress: {exec.progress}% | Steps: {exec.stepExecutions.length}
              </Text>
              <Text style={styles.monitoringTimestamp}>
                Started: {exec.startedAt ? formatTimestamp(exec.startedAt) : 'Pending'}
              </Text>
            </View>
          ))}
          {ai.activeExecutions.length === 0 && (
            <Text style={styles.emptyText}>No active executions</Text>
          )}
        </View>
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
        <Text style={styles.headerTitle}>AI Dashboard</Text>
        <Text style={styles.headerSubtitle}>
          Real-time AI System Monitoring
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('chat', 'AI Chat')}
        {renderTabButton('models', 'Models')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'chat' && <AIChatInterface />}
        {activeTab === 'models' && renderModelsTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}
      </View>

      {/* Error Display */}
      {ai.error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>Error: {ai.error}</Text>
        </View>
      )}

      {/* Loading Indicator */}
      {ai.isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Processing...</Text>
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
    fontSize: 14,
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
    marginBottom: 16,
  },
  healthCard: {
    borderWidth: 2,
    borderRadius: 8,
    padding: 16,
    backgroundColor: '#f8f9fa',
  },
  healthHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  healthStatus: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  healthTimestamp: {
    fontSize: 12,
    color: '#666',
  },
  healthMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  healthMetric: {
    alignItems: 'center',
  },
  healthMetricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  healthMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  metricValueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  metricUnit: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  metricTrend: {
    fontSize: 16,
    marginTop: 4,
  },
  activityList: {
    maxHeight: 300,
  },
  activityItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  activityType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  activityTimestamp: {
    fontSize: 12,
    color: '#666',
  },
  activityUser: {
    fontSize: 12,
    color: '#888',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    paddingVertical: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  actionButtonWarning: {
    backgroundColor: '#FF6B6B',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  modelsList: {
    maxHeight: 400,
  },
  modelCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  modelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  modelName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  modelStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#666',
  },
  modelDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  modelDetails: {
    marginBottom: 12,
  },
  modelDetail: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  modelActions: {
    alignItems: 'flex-end',
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  enableButton: {
    backgroundColor: '#4CAF50',
  },
  disableButton: {
    backgroundColor: '#FF9800',
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  monitoringList: {
    maxHeight: 300,
  },
  monitoringItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  monitoringHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  monitoringTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  monitoringStatus: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
  },
  monitoringSubtitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  monitoringTimestamp: {
    fontSize: 11,
    color: '#888',
  },
  errorBanner: {
    backgroundColor: '#F44336',
    padding: 12,
    alignItems: 'center',
  },
  errorText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIDashboard;
 * @fileoverview AI-powered dashboard component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  RefreshControl,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import AIChatInterface from '../ai/ai-chat-interface';
import {
  AIModel,
  AITask,
  AIWorkflowExecution,
  AIEvent,
  AISystemConfig,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DashboardMetric {
  label: string;
  value: string | number;
  unit?: string;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
}

interface SystemHealth {
  status: 'healthy' | 'degraded' | 'unhealthy';
  models: number;
  activeTasks: number;
  activeExecutions: number;
  recentEvents: number;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI-powered dashboard component
 * Provides comprehensive overview of AI system performance and health
 */
export function AIDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const [activeTab, setActiveTab] = useState<'overview' | 'chat' | 'models' | 'monitoring'>('overview');
  const [refreshing, setRefreshing] = useState(false);
  const [systemHealth, setSystemHealth] = useState<SystemHealth | null>(null);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  // Initialize AI manager on component mount
  useEffect(() => {
    if (!ai.isInitialized) {
      ai.initialize();
    }
  }, [ai]);

  // Update system health when data changes
  useEffect(() => {
    updateSystemHealth();
  }, [ai.models, ai.activeTasks, ai.activeExecutions, ai.recentEvents]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    try {
      await ai.refreshData();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh dashboard data');
    } finally {
      setRefreshing(false);
    }
  }, [ai]);

  const handleModelToggle = useCallback(async (modelId: string, isEnabled: boolean) => {
    try {
      await ai.updateModel(modelId, { isEnabled });
    } catch (error) {
      Alert.alert('Error', 'Failed to update model status');
    }
  }, [ai]);

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  const updateSystemHealth = useCallback(() => {
    const activeModels = ai.models.filter(model => model.isEnabled);
    const totalTasks = ai.activeTasks.length;
    const totalExecutions = ai.activeExecutions.length;
    const recentEventsCount = ai.recentEvents.length;

    let status: 'healthy' | 'degraded' | 'unhealthy' = 'healthy';
    
    if (totalTasks > 50 || totalExecutions > 20) {
      status = 'degraded';
    }
    
    if (totalTasks > 100 || totalExecutions > 50) {
      status = 'unhealthy';
    }

    setSystemHealth({
      status,
      models: activeModels.length,
      activeTasks: totalTasks,
      activeExecutions: totalExecutions,
      recentEvents: recentEventsCount,
    });
  }, [ai.models, ai.activeTasks, ai.activeExecutions, ai.recentEvents]);

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '#4CAF50';
      case 'degraded':
        return '#FF9800';
      case 'unhealthy':
        return '#F44336';
      default:
        return '#666';
    }
  };

  const getStatusIcon = (status: string): string => {
    switch (status) {
      case 'healthy':
        return '🟢';
      case 'degraded':
        return '🟡';
      case 'unhealthy':
        return '🔴';
      default:
        return '⚪';
    }
  };

  const formatTimestamp = (timestamp: number): string => {
    const now = Date.now();
    const diff = now - timestamp;
    
    if (diff < 60000) return 'Just now';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return `${Math.floor(diff / 86400000)}d ago`;
  };

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string): JSX.Element => (
    <AccessibleButton
      accessibilityLabel={`Switch to ${label} tab`}
      onPress={() => handleTabChange(tab)}
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
    >
      <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
        {label}
      </Text>
    </AccessibleButton>
  );

  const renderMetricCard = (metric: DashboardMetric): JSX.Element => (
    <View key={metric.label} style={styles.metricCard}>
      <Text style={styles.metricLabel}>{metric.label}</Text>
      <View style={styles.metricValueContainer}>
        <Text style={[styles.metricValue, { color: metric.color || '#333' }]}>
          {metric.value}
        </Text>
        {metric.unit && <Text style={styles.metricUnit}>{metric.unit}</Text>}
      </View>
      {metric.trend && (
        <Text style={[styles.metricTrend, { color: metric.trend === 'up' ? '#4CAF50' : '#F44336' }]}>
          {metric.trend === 'up' ? '↗' : metric.trend === 'down' ? '↘' : '→'}
        </Text>
      )}
    </View>
  );

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Health Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Health</Text>
        {systemHealth && (
          <View style={[styles.healthCard, { borderColor: getStatusColor(systemHealth.status) }]}>
            <View style={styles.healthHeader}>
              <Text style={styles.healthStatus}>
                {getStatusIcon(systemHealth.status)} {systemHealth.status.toUpperCase()}
              </Text>
              <Text style={styles.healthTimestamp}>
                {formatTimestamp(Date.now())}
              </Text>
            </View>
            <View style={styles.healthMetrics}>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.models}</Text>
                <Text style={styles.healthMetricLabel}>Active Models</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.activeTasks}</Text>
                <Text style={styles.healthMetricLabel}>Active Tasks</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.activeExecutions}</Text>
                <Text style={styles.healthMetricLabel}>Executions</Text>
              </View>
              <View style={styles.healthMetric}>
                <Text style={styles.healthMetricValue}>{systemHealth.recentEvents}</Text>
                <Text style={styles.healthMetricLabel}>Recent Events</Text>
              </View>
            </View>
          </View>
        )}
      </View>

      {/* Key Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Metrics</Text>
        <View style={styles.metricsGrid}>
          {[
            { label: 'Total Models', value: ai.models.length, unit: 'models' },
            { label: 'Enabled Models', value: ai.models.filter(m => m.isEnabled).length, unit: 'models' },
            { label: 'Active Tasks', value: ai.activeTasks.length, unit: 'tasks' },
            { label: 'Workflow Executions', value: ai.activeExecutions.length, unit: 'executions' },
            { label: 'Recent Events', value: ai.recentEvents.length, unit: 'events' },
            { label: 'System Status', value: systemHealth?.status || 'unknown', color: getStatusColor(systemHealth?.status || 'unknown') },
          ].map(renderMetricCard)}
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          {ai.recentEvents.slice(0, 10).map(event => (
            <View key={event.id} style={styles.activityItem}>
              <View style={styles.activityHeader}>
                <Text style={styles.activityType}>{event.type}</Text>
                <Text style={styles.activityTimestamp}>
                  {formatTimestamp(event.timestamp)}
                </Text>
              </View>
              {event.userId && (
                <Text style={styles.activityUser}>User: {event.userId}</Text>
              )}
            </View>
          ))}
          {ai.recentEvents.length === 0 && (
            <Text style={styles.emptyText}>No recent activity</Text>
          )}
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <AccessibleButton
            accessibilityLabel="Refresh dashboard data"
            onPress={handleRefresh}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>🔄 Refresh</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Cleanup system"
            onPress={ai.cleanup}
            style={[styles.actionButton, styles.actionButtonWarning]}
          >
            <Text style={styles.actionButtonText}>🧹 Cleanup</Text>
          </AccessibleButton>
        </View>
      </View>
    </ScrollView>
  );

  const renderModelsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Models</Text>
        <View style={styles.modelsList}>
          {ai.models.map(model => (
            <View key={model.id} style={styles.modelCard}>
              <View style={styles.modelHeader}>
                <Text style={styles.modelName}>{model.name}</Text>
                <View style={styles.modelStatus}>
                  <View style={[
                    styles.statusIndicator,
                    { backgroundColor: model.isEnabled ? '#4CAF50' : '#F44336' }
                  ]} />
                  <Text style={styles.statusText}>
                    {model.isEnabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
              </View>
              <Text style={styles.modelDescription}>{model.description}</Text>
              <View style={styles.modelDetails}>
                <Text style={styles.modelDetail}>Type: {model.config.modelType}</Text>
                <Text style={styles.modelDetail}>Provider: {model.config.provider}</Text>
                <Text style={styles.modelDetail}>Version: {model.config.version}</Text>
                <Text style={styles.modelDetail}>Accuracy: {(model.metrics.accuracy * 100).toFixed(1)}%</Text>
              </View>
              <View style={styles.modelActions}>
                <AccessibleButton
                  accessibilityLabel={`Toggle ${model.name} model`}
                  onPress={() => handleModelToggle(model.id, !model.isEnabled)}
                  style={[styles.smallButton, model.isEnabled ? styles.disableButton : styles.enableButton]}
                >
                  <Text style={styles.smallButtonText}>
                    {model.isEnabled ? 'Disable' : 'Enable'}
                  </Text>
                </AccessibleButton>
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* Active Tasks */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Active Tasks</Text>
        <View style={styles.monitoringList}>
          {ai.activeTasks.map(task => (
            <View key={task.id} style={styles.monitoringItem}>
              <View style={styles.monitoringHeader}>
                <Text style={styles.monitoringTitle}>{task.type}</Text>
                <Text style={styles.monitoringStatus}>{task.status}</Text>
              </View>
              <Text style={styles.monitoringSubtitle}>
                Progress: {task.progress}% | Priority: {task.priority}
              </Text>
              <Text style={styles.monitoringTimestamp}>
                Created: {formatTimestamp(task.createdAt)}
              </Text>
            </View>
          ))}
          {ai.activeTasks.length === 0 && (
            <Text style={styles.emptyText}>No active tasks</Text>
          )}
        </View>
      </View>

      {/* Workflow Executions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Workflow Executions</Text>
        <View style={styles.monitoringList}>
          {ai.activeExecutions.map(exec => (
            <View key={exec.id} style={styles.monitoringItem}>
              <View style={styles.monitoringHeader}>
                <Text style={styles.monitoringTitle}>Workflow {exec.workflowId}</Text>
                <Text style={styles.monitoringStatus}>{exec.status}</Text>
              </View>
              <Text style={styles.monitoringSubtitle}>
                Progress: {exec.progress}% | Steps: {exec.stepExecutions.length}
              </Text>
              <Text style={styles.monitoringTimestamp}>
                Started: {exec.startedAt ? formatTimestamp(exec.startedAt) : 'Pending'}
              </Text>
            </View>
          ))}
          {ai.activeExecutions.length === 0 && (
            <Text style={styles.emptyText}>No active executions</Text>
          )}
        </View>
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
        <Text style={styles.headerTitle}>AI Dashboard</Text>
        <Text style={styles.headerSubtitle}>
          Real-time AI System Monitoring
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('chat', 'AI Chat')}
        {renderTabButton('models', 'Models')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'chat' && <AIChatInterface />}
        {activeTab === 'models' && renderModelsTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}
      </View>

      {/* Error Display */}
      {ai.error && (
        <View style={styles.errorBanner}>
          <Text style={styles.errorText}>Error: {ai.error}</Text>
        </View>
      )}

      {/* Loading Indicator */}
      {ai.isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Processing...</Text>
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
    fontSize: 14,
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
    marginBottom: 16,
  },
  healthCard: {
    borderWidth: 2,
    borderRadius: 8,
    padding: 16,
    backgroundColor: '#f8f9fa',
  },
  healthHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  healthStatus: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
  },
  healthTimestamp: {
    fontSize: 12,
    color: '#666',
  },
  healthMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  healthMetric: {
    alignItems: 'center',
  },
  healthMetricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  healthMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  metricCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    fontWeight: '500',
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  metricValueContainer: {
    flexDirection: 'row',
    alignItems: 'baseline',
  },
  metricValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  metricUnit: {
    fontSize: 12,
    color: '#666',
    marginLeft: 4,
  },
  metricTrend: {
    fontSize: 16,
    marginTop: 4,
  },
  activityList: {
    maxHeight: 300,
  },
  activityItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  activityType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  activityTimestamp: {
    fontSize: 12,
    color: '#666',
  },
  activityUser: {
    fontSize: 12,
    color: '#888',
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    paddingVertical: 20,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  actionButtonWarning: {
    backgroundColor: '#FF6B6B',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  modelsList: {
    maxHeight: 400,
  },
  modelCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  modelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  modelName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  modelStatus: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 6,
  },
  statusText: {
    fontSize: 12,
    color: '#666',
  },
  modelDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  modelDetails: {
    marginBottom: 12,
  },
  modelDetail: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  modelActions: {
    alignItems: 'flex-end',
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
  },
  enableButton: {
    backgroundColor: '#4CAF50',
  },
  disableButton: {
    backgroundColor: '#FF9800',
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  monitoringList: {
    maxHeight: 300,
  },
  monitoringItem: {
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  monitoringHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  monitoringTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  monitoringStatus: {
    fontSize: 12,
    color: '#666',
    textTransform: 'capitalize',
  },
  monitoringSubtitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  monitoringTimestamp: {
    fontSize: 11,
    color: '#888',
  },
  errorBanner: {
    backgroundColor: '#F44336',
    padding: 12,
    alignItems: 'center',
  },
  errorText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '500',
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIDashboard;


