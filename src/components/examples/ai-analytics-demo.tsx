/**
 * @fileoverview AI analytics and insights demo component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIInsightsDashboard } from '../dashboard/ai-insights-dashboard';
import { aiAnalyticsEngine, AIAnalyticsDataPoint, AIAnalyticsInsight } from '../../lib/ai/ai-analytics-engine';
import { AIWorkflowExecution, AIEvent, AIEventType } from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DemoMetrics {
  totalDataPoints: number;
  totalInsights: number;
  criticalInsights: number;
  averageConfidence: number;
  systemHealth: number;
  userEngagement: number;
  workflowEfficiency: number;
  errorRate: number;
}

interface DemoScenario {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  isActive: boolean;
  dataPoints: AIAnalyticsDataPoint[];
}

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'scenario_1',
    name: 'Performance Monitoring',
    description: 'Monitor system performance metrics and response times',
    category: 'performance',
    icon: '⚡',
    isActive: true,
    dataPoints: [
      {
        id: 'perf_1',
        timestamp: Date.now() - 300000,
        userId: 'user_1',
        category: 'performance',
        metric: 'response_time',
        value: 245,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
      {
        id: 'perf_2',
        timestamp: Date.now() - 240000,
        userId: 'user_2',
        category: 'performance',
        metric: 'response_time',
        value: 189,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
      {
        id: 'perf_3',
        timestamp: Date.now() - 180000,
        userId: 'user_1',
        category: 'performance',
        metric: 'response_time',
        value: 312,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
    ],
  },
  {
    id: 'scenario_2',
    name: 'User Behavior Analysis',
    description: 'Analyze user interaction patterns and engagement',
    category: 'usage',
    icon: '👥',
    isActive: true,
    dataPoints: [
      {
        id: 'usage_1',
        timestamp: Date.now() - 600000,
        userId: 'user_1',
        category: 'usage',
        metric: 'session_duration',
        value: 1800,
        metadata: { feature: 'ai_chat', action: 'session_start' },
        tags: ['user_behavior', 'session'],
      },
      {
        id: 'usage_2',
        timestamp: Date.now() - 540000,
        userId: 'user_2',
        category: 'usage',
        metric: 'feature_usage',
        value: 1,
        metadata: { feature: 'workflow_automation', action: 'create_workflow' },
        tags: ['user_behavior', 'feature_usage'],
      },
      {
        id: 'usage_3',
        timestamp: Date.now() - 480000,
        userId: 'user_3',
        category: 'usage',
        metric: 'api_calls',
        value: 15,
        metadata: { endpoint: '/api/ai/chat', method: 'POST' },
        tags: ['user_behavior', 'api_usage'],
      },
    ],
  },
  {
    id: 'scenario_3',
    name: 'Workflow Analytics',
    description: 'Track workflow execution and success rates',
    category: 'workflow',
    icon: '🔄',
    isActive: true,
    dataPoints: [
      {
        id: 'workflow_1',
        timestamp: Date.now() - 900000,
        userId: 'user_1',
        category: 'workflow',
        metric: 'execution_duration',
        value: 45000,
        metadata: { workflowId: 'content_generation', status: 'completed' },
        tags: ['workflow', 'execution'],
      },
      {
        id: 'workflow_2',
        timestamp: Date.now() - 840000,
        userId: 'user_2',
        category: 'workflow',
        metric: 'step_count',
        value: 4,
        metadata: { workflowId: 'data_analysis', status: 'completed' },
        tags: ['workflow', 'steps'],
      },
      {
        id: 'workflow_3',
        timestamp: Date.now() - 780000,
        userId: 'user_1',
        category: 'workflow',
        metric: 'success_rate',
        value: 0.95,
        metadata: { workflowId: 'customer_support', status: 'completed' },
        tags: ['workflow', 'success'],
      },
    ],
  },
  {
    id: 'scenario_4',
    name: 'Error Tracking',
    description: 'Monitor system errors and failure patterns',
    category: 'error',
    icon: '🚨',
    isActive: true,
    dataPoints: [
      {
        id: 'error_1',
        timestamp: Date.now() - 1200000,
        userId: 'system',
        category: 'error',
        metric: 'error_count',
        value: 1,
        metadata: { errorType: 'timeout', component: 'ai_processor' },
        tags: ['error', 'timeout'],
      },
      {
        id: 'error_2',
        timestamp: Date.now() - 1140000,
        userId: 'system',
        category: 'error',
        metric: 'error_count',
        value: 1,
        metadata: { errorType: 'validation', component: 'api_gateway' },
        tags: ['error', 'validation'],
      },
    ],
  },
];

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI Analytics Demo Component
 * Comprehensive demonstration of AI analytics and insights capabilities
 */
export function AIAnalyticsDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'scenarios' | 'insights' | 'dashboard'>('overview');
  const [scenarios, setScenarios] = useState<DemoScenario[]>(DEMO_SCENARIOS);
  const [insights, setInsights] = useState<AIAnalyticsInsight[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

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
      // Add initial demo data points
      scenarios.forEach(scenario => {
        if (scenario.isActive) {
          aiAnalyticsEngine.addDataPoints(scenario.dataPoints);
        }
      });

      // Generate initial insights
      const initialInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(initialInsights);

      // Set up event listeners
      aiAnalyticsEngine.on('insightGenerated', (insight: AIAnalyticsInsight) => {
        setInsights(prev => [insight, ...prev.filter(i => i.id !== insight.id)]);
      });

    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo');
    } finally {
      setIsLoading(false);
    }
  }, [scenarios]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleToggleScenario = useCallback((scenarioId: string) => {
    setScenarios(prev => 
      prev.map(scenario => 
        scenario.id === scenarioId 
          ? { ...scenario, isActive: !scenario.isActive }
          : scenario
      )
    );
  }, []);

  const handleSimulateData = useCallback(async () => {
    setIsSimulating(true);
    try {
      // Simulate new data points
      const newDataPoints: AIAnalyticsDataPoint[] = [];
      
      scenarios.forEach(scenario => {
        if (scenario.isActive) {
          // Generate 3-5 new data points per scenario
          const count = Math.floor(Math.random() * 3) + 3;
          for (let i = 0; i < count; i++) {
            const baseDataPoint = scenario.dataPoints[0];
            const newDataPoint: AIAnalyticsDataPoint = {
              ...baseDataPoint,
              id: `${scenario.id}_sim_${Date.now()}_${i}`,
              timestamp: Date.now() - (Math.random() * 300000), // Last 5 minutes
              value: baseDataPoint.value + (Math.random() - 0.5) * baseDataPoint.value * 0.3, // ±30% variation
              metadata: {
                ...baseDataPoint.metadata,
                simulated: true,
                simulationId: `sim_${Date.now()}`,
              },
            };
            newDataPoints.push(newDataPoint);
          }
        }
      });

      // Add data points to analytics engine
      aiAnalyticsEngine.addDataPoints(newDataPoints);

      // Generate new insights
      const newInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);

      Alert.alert('Success', `Simulated ${newDataPoints.length} new data points and generated ${newInsights.length} insights`);

    } catch (error) {
      Alert.alert('Error', 'Failed to simulate data');
    } finally {
      setIsSimulating(false);
    }
  }, [scenarios]);

  const handleGenerateInsights = useCallback(async () => {
    setIsLoading(true);
    try {
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);
      Alert.alert('Success', `Generated ${newInsights.length} new insights`);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate insights');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleShowDashboard = useCallback(() => {
    setShowDashboard(true);
  }, []);

  const handleSimulateWorkflowExecution = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate a workflow execution
      const mockExecution: AIWorkflowExecution = {
        id: `execution_${Date.now()}`,
        workflowId: 'demo_workflow',
        userId: 'demo_user',
        status: 'completed',
        input: { prompt: 'Generate demo content' },
        output: { result: 'Demo content generated successfully' },
        stepExecutions: [
          {
            id: 'step_1',
            stepId: 'content_planning',
            executionId: `execution_${Date.now()}`,
            status: 'completed',
            input: { prompt: 'Generate demo content' },
            output: { outline: 'Demo content outline' },
            startedAt: Date.now() - 30000,
            completedAt: Date.now() - 20000,
          },
          {
            id: 'step_2',
            stepId: 'content_generation',
            executionId: `execution_${Date.now()}`,
            status: 'completed',
            input: { outline: 'Demo content outline' },
            output: { content: 'Demo content generated' },
            startedAt: Date.now() - 20000,
            completedAt: Date.now() - 10000,
          },
        ],
        progress: 100,
        createdAt: Date.now() - 30000,
        startedAt: Date.now() - 30000,
        completedAt: Date.now(),
      };

      // Process workflow execution
      aiAnalyticsEngine.processWorkflowExecution(mockExecution);

      Alert.alert('Success', 'Simulated workflow execution and processed analytics data');

    } catch (error) {
      Alert.alert('Error', 'Failed to simulate workflow execution');
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    const stats = aiAnalyticsEngine.getSystemStats();
    const metrics: DemoMetrics = {
      totalDataPoints: stats.totalDataPoints,
      totalInsights: stats.totalInsights,
      criticalInsights: insights.filter(i => i.impact === 'critical' || i.impact === 'high').length,
      averageConfidence: insights.length > 0 ? insights.reduce((sum, i) => sum + i.confidence, 0) / insights.length : 0,
      systemHealth: 0.95, // Simulated
      userEngagement: 0.87, // Simulated
      workflowEfficiency: 0.92, // Simulated
      errorRate: 0.02, // Simulated
    };

    return (
      <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
        {/* System Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalDataPoints}</Text>
              <Text style={styles.overviewLabel}>Data Points</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalInsights}</Text>
              <Text style={styles.overviewLabel}>Insights</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.criticalInsights}</Text>
              <Text style={styles.overviewLabel}>Critical</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{(metrics.averageConfidence * 100).toFixed(0)}%</Text>
              <Text style={styles.overviewLabel}>Avg Confidence</Text>
            </View>
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Metrics</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>System Health</Text>
              <Text style={styles.metricValue}>{(metrics.systemHealth * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.systemHealth * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>User Engagement</Text>
              <Text style={styles.metricValue}>{(metrics.userEngagement * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.userEngagement * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Workflow Efficiency</Text>
              <Text style={styles.metricValue}>{(metrics.workflowEfficiency * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.workflowEfficiency * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Error Rate</Text>
              <Text style={styles.metricValue}>{(metrics.errorRate * 100).toFixed(2)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${(1 - metrics.errorRate) * 100}%` }]} />
              </View>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="📊 Open Dashboard"
              onPress={handleShowDashboard}
              style={styles.actionButton}
              variant="primary"
              size="small"
            />
            <AccessibleButton
              title="🔄 Simulate Data"
              onPress={handleSimulateData}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isSimulating}
            />
            <AccessibleButton
              title="💡 Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isLoading}
            />
            <AccessibleButton
              title="⚡ Simulate Workflow"
              onPress={handleSimulateWorkflowExecution}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isLoading}
            />
          </View>
        </View>

        {/* Recent Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Insights</Text>
          {insights.length > 0 ? (
            insights.slice(0, 3).map(insight => (
              <View key={insight.id} style={styles.insightPreview}>
                <View style={styles.insightPreviewHeader}>
                  <Text style={styles.insightPreviewTitle}>{insight.title}</Text>
                  <View style={[styles.impactBadge, { backgroundColor: insight.impact === 'high' ? '#FF3B30' : '#34C759' }]}>
                    <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
                  </View>
                </View>
                <Text style={styles.insightPreviewDescription}>{insight.description}</Text>
                <Text style={styles.insightPreviewConfidence}>
                  Confidence: {(insight.confidence * 100).toFixed(0)}%
                </Text>
              </View>
            ))
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>No insights available</Text>
              <AccessibleButton
                title="Generate Insights"
                onPress={handleGenerateInsights}
                style={styles.generateButton}
                variant="primary"
                size="medium"
              />
            </View>
          )}
        </View>
      </ScrollView>
    );
  };

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Analytics Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Configure and manage different analytics scenarios to simulate real-world data patterns.
        </Text>
        
        {scenarios.map(scenario => (
          <View key={scenario.id} style={styles.scenarioCard}>
            <View style={styles.scenarioHeader}>
              <View style={styles.scenarioInfo}>
                <Text style={styles.scenarioIcon}>{scenario.icon}</Text>
                <View style={styles.scenarioDetails}>
                  <Text style={styles.scenarioName}>{scenario.name}</Text>
                  <Text style={styles.scenarioDescription}>{scenario.description}</Text>
                </View>
              </View>
              <View style={styles.scenarioControls}>
                <Text style={styles.scenarioStatus}>
                  {scenario.isActive ? '🟢 Active' : '🔴 Inactive'}
                </Text>
                <AccessibleButton
                  title={scenario.isActive ? 'Disable' : 'Enable'}
                  onPress={() => handleToggleScenario(scenario.id)}
                  style={styles.scenarioToggle}
                  variant={scenario.isActive ? 'danger' : 'success'}
                  size="small"
                />
              </View>
            </View>
            
            <View style={styles.scenarioStats}>
              <Text style={styles.scenarioStat}>
                Data Points: {scenario.dataPoints.length}
              </Text>
              <Text style={styles.scenarioStat}>
                Category: {scenario.category}
              </Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderInsightsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI-Generated Insights</Text>
        <Text style={styles.sectionDescription}>
          Intelligent insights generated from analytics data using AI algorithms.
        </Text>
        
        {insights.length > 0 ? (
          insights.map(insight => (
            <View key={insight.id} style={styles.insightCard}>
              <View style={styles.insightHeader}>
                <Text style={styles.insightTitle}>{insight.title}</Text>
                <View style={[styles.impactBadge, { backgroundColor: insight.impact === 'high' ? '#FF3B30' : '#34C759' }]}>
                  <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
                </View>
              </View>
              
              <Text style={styles.insightDescription}>{insight.description}</Text>
              
              <View style={styles.insightData}>
                <Text style={styles.insightDataLabel}>Current Value: {insight.data.current.toFixed(2)}</Text>
                {insight.data.previous && (
                  <Text style={styles.insightDataLabel}>Previous: {insight.data.previous.toFixed(2)}</Text>
                )}
                {insight.data.trend && (
                  <Text style={styles.insightDataLabel}>Trend: {insight.data.trend}</Text>
                )}
              </View>
              
              <View style={styles.confidenceBar}>
                <Text style={styles.confidenceLabel}>Confidence: {(insight.confidence * 100).toFixed(0)}%</Text>
                <View style={styles.confidenceBarBackground}>
                  <View style={[styles.confidenceBarFill, { width: `${insight.confidence * 100}%` }]} />
                </View>
              </View>
              
              {insight.recommendations.length > 0 && (
                <View style={styles.recommendations}>
                  <Text style={styles.recommendationsTitle}>Recommendations:</Text>
                  {insight.recommendations.slice(0, 2).map((rec, index) => (
                    <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
                  ))}
                </View>
              )}
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No insights available</Text>
            <AccessibleButton
              title="Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.generateButton}
              variant="primary"
              size="medium"
            />
          </View>
        )}
      </View>
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (showDashboard) {
    return (
      <View style={styles.fullScreen}>
        <View style={styles.dashboardHeader}>
          <AccessibleButton
            title="✕ Close"
            accessibilityLabel="Close analytics dashboard"
            onPress={() => setShowDashboard(false)}
            style={styles.closeButton}
            textStyle={styles.closeButtonText}
            variant="ghost"
            size="small"
          />
          <Text style={styles.dashboardTitle}>AI Analytics Dashboard</Text>
        </View>
        <AIInsightsDashboard />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Analytics Demo</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Analytics & Predictive Insights
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('scenarios', 'Scenarios')}
        {renderTabButton('insights', 'Insights')}
        {renderTabButton('dashboard', 'Dashboard')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
        {activeTab === 'insights' && renderInsightsTab()}
        {activeTab === 'dashboard' && (
          <View style={styles.tabContent}>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Analytics Dashboard</Text>
              <Text style={styles.sectionDescription}>
                Access the comprehensive AI analytics dashboard with real-time insights and monitoring.
              </Text>
              
              <AccessibleButton
                title="📊 Open Analytics Dashboard"
                onPress={handleShowDashboard}
                style={styles.primaryButton}
                variant="primary"
                size="large"
              />
            </View>
          </View>
        )}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
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

const { width } = Dimensions.get('window');

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
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  overviewCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  overviewValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
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
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  metricBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
  },
  metricBarFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 120,
  },
  primaryButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  generateButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    marginTop: 16,
  },
  insightPreview: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  insightPreviewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightPreviewTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  impactBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  impactBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  insightPreviewDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  insightPreviewConfidence: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  scenarioCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  scenarioHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  scenarioInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  scenarioIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  scenarioDetails: {
    flex: 1,
  },
  scenarioName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  scenarioDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  scenarioControls: {
    alignItems: 'flex-end',
  },
  scenarioStatus: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  scenarioToggle: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  scenarioStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  scenarioStat: {
    fontSize: 12,
    color: '#666',
  },
  insightCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  insightDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  insightData: {
    marginBottom: 12,
  },
  insightDataLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  confidenceBar: {
    marginBottom: 12,
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  confidenceBarBackground: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
  },
  confidenceBarFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  recommendations: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  recommendationsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  recommendationItem: {
    fontSize: 12,
    color: '#666',
    lineHeight: 16,
    marginBottom: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
    textAlign: 'center',
  },
  fullScreen: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  dashboardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    padding: 16,
  },
  closeButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 6,
    marginRight: 16,
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  dashboardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
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

export default AIAnalyticsDemo;
 * @fileoverview AI analytics and insights demo component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIInsightsDashboard } from '../dashboard/ai-insights-dashboard';
import { aiAnalyticsEngine, AIAnalyticsDataPoint, AIAnalyticsInsight } from '../../lib/ai/ai-analytics-engine';
import { AIWorkflowExecution, AIEvent, AIEventType } from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DemoMetrics {
  totalDataPoints: number;
  totalInsights: number;
  criticalInsights: number;
  averageConfidence: number;
  systemHealth: number;
  userEngagement: number;
  workflowEfficiency: number;
  errorRate: number;
}

interface DemoScenario {
  id: string;
  name: string;
  description: string;
  category: string;
  icon: string;
  isActive: boolean;
  dataPoints: AIAnalyticsDataPoint[];
}

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_SCENARIOS: DemoScenario[] = [
  {
    id: 'scenario_1',
    name: 'Performance Monitoring',
    description: 'Monitor system performance metrics and response times',
    category: 'performance',
    icon: '⚡',
    isActive: true,
    dataPoints: [
      {
        id: 'perf_1',
        timestamp: Date.now() - 300000,
        userId: 'user_1',
        category: 'performance',
        metric: 'response_time',
        value: 245,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
      {
        id: 'perf_2',
        timestamp: Date.now() - 240000,
        userId: 'user_2',
        category: 'performance',
        metric: 'response_time',
        value: 189,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
      {
        id: 'perf_3',
        timestamp: Date.now() - 180000,
        userId: 'user_1',
        category: 'performance',
        metric: 'response_time',
        value: 312,
        metadata: { endpoint: '/api/ai/process', method: 'POST' },
        tags: ['api', 'response_time'],
      },
    ],
  },
  {
    id: 'scenario_2',
    name: 'User Behavior Analysis',
    description: 'Analyze user interaction patterns and engagement',
    category: 'usage',
    icon: '👥',
    isActive: true,
    dataPoints: [
      {
        id: 'usage_1',
        timestamp: Date.now() - 600000,
        userId: 'user_1',
        category: 'usage',
        metric: 'session_duration',
        value: 1800,
        metadata: { feature: 'ai_chat', action: 'session_start' },
        tags: ['user_behavior', 'session'],
      },
      {
        id: 'usage_2',
        timestamp: Date.now() - 540000,
        userId: 'user_2',
        category: 'usage',
        metric: 'feature_usage',
        value: 1,
        metadata: { feature: 'workflow_automation', action: 'create_workflow' },
        tags: ['user_behavior', 'feature_usage'],
      },
      {
        id: 'usage_3',
        timestamp: Date.now() - 480000,
        userId: 'user_3',
        category: 'usage',
        metric: 'api_calls',
        value: 15,
        metadata: { endpoint: '/api/ai/chat', method: 'POST' },
        tags: ['user_behavior', 'api_usage'],
      },
    ],
  },
  {
    id: 'scenario_3',
    name: 'Workflow Analytics',
    description: 'Track workflow execution and success rates',
    category: 'workflow',
    icon: '🔄',
    isActive: true,
    dataPoints: [
      {
        id: 'workflow_1',
        timestamp: Date.now() - 900000,
        userId: 'user_1',
        category: 'workflow',
        metric: 'execution_duration',
        value: 45000,
        metadata: { workflowId: 'content_generation', status: 'completed' },
        tags: ['workflow', 'execution'],
      },
      {
        id: 'workflow_2',
        timestamp: Date.now() - 840000,
        userId: 'user_2',
        category: 'workflow',
        metric: 'step_count',
        value: 4,
        metadata: { workflowId: 'data_analysis', status: 'completed' },
        tags: ['workflow', 'steps'],
      },
      {
        id: 'workflow_3',
        timestamp: Date.now() - 780000,
        userId: 'user_1',
        category: 'workflow',
        metric: 'success_rate',
        value: 0.95,
        metadata: { workflowId: 'customer_support', status: 'completed' },
        tags: ['workflow', 'success'],
      },
    ],
  },
  {
    id: 'scenario_4',
    name: 'Error Tracking',
    description: 'Monitor system errors and failure patterns',
    category: 'error',
    icon: '🚨',
    isActive: true,
    dataPoints: [
      {
        id: 'error_1',
        timestamp: Date.now() - 1200000,
        userId: 'system',
        category: 'error',
        metric: 'error_count',
        value: 1,
        metadata: { errorType: 'timeout', component: 'ai_processor' },
        tags: ['error', 'timeout'],
      },
      {
        id: 'error_2',
        timestamp: Date.now() - 1140000,
        userId: 'system',
        category: 'error',
        metric: 'error_count',
        value: 1,
        metadata: { errorType: 'validation', component: 'api_gateway' },
        tags: ['error', 'validation'],
      },
    ],
  },
];

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI Analytics Demo Component
 * Comprehensive demonstration of AI analytics and insights capabilities
 */
export function AIAnalyticsDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'scenarios' | 'insights' | 'dashboard'>('overview');
  const [scenarios, setScenarios] = useState<DemoScenario[]>(DEMO_SCENARIOS);
  const [insights, setInsights] = useState<AIAnalyticsInsight[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDashboard, setShowDashboard] = useState(false);
  const [isSimulating, setIsSimulating] = useState(false);

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
      // Add initial demo data points
      scenarios.forEach(scenario => {
        if (scenario.isActive) {
          aiAnalyticsEngine.addDataPoints(scenario.dataPoints);
        }
      });

      // Generate initial insights
      const initialInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(initialInsights);

      // Set up event listeners
      aiAnalyticsEngine.on('insightGenerated', (insight: AIAnalyticsInsight) => {
        setInsights(prev => [insight, ...prev.filter(i => i.id !== insight.id)]);
      });

    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo');
    } finally {
      setIsLoading(false);
    }
  }, [scenarios]);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleToggleScenario = useCallback((scenarioId: string) => {
    setScenarios(prev => 
      prev.map(scenario => 
        scenario.id === scenarioId 
          ? { ...scenario, isActive: !scenario.isActive }
          : scenario
      )
    );
  }, []);

  const handleSimulateData = useCallback(async () => {
    setIsSimulating(true);
    try {
      // Simulate new data points
      const newDataPoints: AIAnalyticsDataPoint[] = [];
      
      scenarios.forEach(scenario => {
        if (scenario.isActive) {
          // Generate 3-5 new data points per scenario
          const count = Math.floor(Math.random() * 3) + 3;
          for (let i = 0; i < count; i++) {
            const baseDataPoint = scenario.dataPoints[0];
            const newDataPoint: AIAnalyticsDataPoint = {
              ...baseDataPoint,
              id: `${scenario.id}_sim_${Date.now()}_${i}`,
              timestamp: Date.now() - (Math.random() * 300000), // Last 5 minutes
              value: baseDataPoint.value + (Math.random() - 0.5) * baseDataPoint.value * 0.3, // ±30% variation
              metadata: {
                ...baseDataPoint.metadata,
                simulated: true,
                simulationId: `sim_${Date.now()}`,
              },
            };
            newDataPoints.push(newDataPoint);
          }
        }
      });

      // Add data points to analytics engine
      aiAnalyticsEngine.addDataPoints(newDataPoints);

      // Generate new insights
      const newInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);

      Alert.alert('Success', `Simulated ${newDataPoints.length} new data points and generated ${newInsights.length} insights`);

    } catch (error) {
      Alert.alert('Error', 'Failed to simulate data');
    } finally {
      setIsSimulating(false);
    }
  }, [scenarios]);

  const handleGenerateInsights = useCallback(async () => {
    setIsLoading(true);
    try {
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);
      Alert.alert('Success', `Generated ${newInsights.length} new insights`);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate insights');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleShowDashboard = useCallback(() => {
    setShowDashboard(true);
  }, []);

  const handleSimulateWorkflowExecution = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate a workflow execution
      const mockExecution: AIWorkflowExecution = {
        id: `execution_${Date.now()}`,
        workflowId: 'demo_workflow',
        userId: 'demo_user',
        status: 'completed',
        input: { prompt: 'Generate demo content' },
        output: { result: 'Demo content generated successfully' },
        stepExecutions: [
          {
            id: 'step_1',
            stepId: 'content_planning',
            executionId: `execution_${Date.now()}`,
            status: 'completed',
            input: { prompt: 'Generate demo content' },
            output: { outline: 'Demo content outline' },
            startedAt: Date.now() - 30000,
            completedAt: Date.now() - 20000,
          },
          {
            id: 'step_2',
            stepId: 'content_generation',
            executionId: `execution_${Date.now()}`,
            status: 'completed',
            input: { outline: 'Demo content outline' },
            output: { content: 'Demo content generated' },
            startedAt: Date.now() - 20000,
            completedAt: Date.now() - 10000,
          },
        ],
        progress: 100,
        createdAt: Date.now() - 30000,
        startedAt: Date.now() - 30000,
        completedAt: Date.now(),
      };

      // Process workflow execution
      aiAnalyticsEngine.processWorkflowExecution(mockExecution);

      Alert.alert('Success', 'Simulated workflow execution and processed analytics data');

    } catch (error) {
      Alert.alert('Error', 'Failed to simulate workflow execution');
    } finally {
      setIsLoading(false);
    }
  }, []);

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
    const stats = aiAnalyticsEngine.getSystemStats();
    const metrics: DemoMetrics = {
      totalDataPoints: stats.totalDataPoints,
      totalInsights: stats.totalInsights,
      criticalInsights: insights.filter(i => i.impact === 'critical' || i.impact === 'high').length,
      averageConfidence: insights.length > 0 ? insights.reduce((sum, i) => sum + i.confidence, 0) / insights.length : 0,
      systemHealth: 0.95, // Simulated
      userEngagement: 0.87, // Simulated
      workflowEfficiency: 0.92, // Simulated
      errorRate: 0.02, // Simulated
    };

    return (
      <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
        {/* System Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalDataPoints}</Text>
              <Text style={styles.overviewLabel}>Data Points</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalInsights}</Text>
              <Text style={styles.overviewLabel}>Insights</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.criticalInsights}</Text>
              <Text style={styles.overviewLabel}>Critical</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{(metrics.averageConfidence * 100).toFixed(0)}%</Text>
              <Text style={styles.overviewLabel}>Avg Confidence</Text>
            </View>
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Metrics</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>System Health</Text>
              <Text style={styles.metricValue}>{(metrics.systemHealth * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.systemHealth * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>User Engagement</Text>
              <Text style={styles.metricValue}>{(metrics.userEngagement * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.userEngagement * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Workflow Efficiency</Text>
              <Text style={styles.metricValue}>{(metrics.workflowEfficiency * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.workflowEfficiency * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Error Rate</Text>
              <Text style={styles.metricValue}>{(metrics.errorRate * 100).toFixed(2)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${(1 - metrics.errorRate) * 100}%` }]} />
              </View>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="📊 Open Dashboard"
              onPress={handleShowDashboard}
              style={styles.actionButton}
              variant="primary"
              size="small"
            />
            <AccessibleButton
              title="🔄 Simulate Data"
              onPress={handleSimulateData}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isSimulating}
            />
            <AccessibleButton
              title="💡 Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isLoading}
            />
            <AccessibleButton
              title="⚡ Simulate Workflow"
              onPress={handleSimulateWorkflowExecution}
              style={styles.actionButton}
              variant="secondary"
              size="small"
              isDisabled={isLoading}
            />
          </View>
        </View>

        {/* Recent Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Insights</Text>
          {insights.length > 0 ? (
            insights.slice(0, 3).map(insight => (
              <View key={insight.id} style={styles.insightPreview}>
                <View style={styles.insightPreviewHeader}>
                  <Text style={styles.insightPreviewTitle}>{insight.title}</Text>
                  <View style={[styles.impactBadge, { backgroundColor: insight.impact === 'high' ? '#FF3B30' : '#34C759' }]}>
                    <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
                  </View>
                </View>
                <Text style={styles.insightPreviewDescription}>{insight.description}</Text>
                <Text style={styles.insightPreviewConfidence}>
                  Confidence: {(insight.confidence * 100).toFixed(0)}%
                </Text>
              </View>
            ))
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>No insights available</Text>
              <AccessibleButton
                title="Generate Insights"
                onPress={handleGenerateInsights}
                style={styles.generateButton}
                variant="primary"
                size="medium"
              />
            </View>
          )}
        </View>
      </ScrollView>
    );
  };

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Analytics Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Configure and manage different analytics scenarios to simulate real-world data patterns.
        </Text>
        
        {scenarios.map(scenario => (
          <View key={scenario.id} style={styles.scenarioCard}>
            <View style={styles.scenarioHeader}>
              <View style={styles.scenarioInfo}>
                <Text style={styles.scenarioIcon}>{scenario.icon}</Text>
                <View style={styles.scenarioDetails}>
                  <Text style={styles.scenarioName}>{scenario.name}</Text>
                  <Text style={styles.scenarioDescription}>{scenario.description}</Text>
                </View>
              </View>
              <View style={styles.scenarioControls}>
                <Text style={styles.scenarioStatus}>
                  {scenario.isActive ? '🟢 Active' : '🔴 Inactive'}
                </Text>
                <AccessibleButton
                  title={scenario.isActive ? 'Disable' : 'Enable'}
                  onPress={() => handleToggleScenario(scenario.id)}
                  style={styles.scenarioToggle}
                  variant={scenario.isActive ? 'danger' : 'success'}
                  size="small"
                />
              </View>
            </View>
            
            <View style={styles.scenarioStats}>
              <Text style={styles.scenarioStat}>
                Data Points: {scenario.dataPoints.length}
              </Text>
              <Text style={styles.scenarioStat}>
                Category: {scenario.category}
              </Text>
            </View>
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderInsightsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI-Generated Insights</Text>
        <Text style={styles.sectionDescription}>
          Intelligent insights generated from analytics data using AI algorithms.
        </Text>
        
        {insights.length > 0 ? (
          insights.map(insight => (
            <View key={insight.id} style={styles.insightCard}>
              <View style={styles.insightHeader}>
                <Text style={styles.insightTitle}>{insight.title}</Text>
                <View style={[styles.impactBadge, { backgroundColor: insight.impact === 'high' ? '#FF3B30' : '#34C759' }]}>
                  <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
                </View>
              </View>
              
              <Text style={styles.insightDescription}>{insight.description}</Text>
              
              <View style={styles.insightData}>
                <Text style={styles.insightDataLabel}>Current Value: {insight.data.current.toFixed(2)}</Text>
                {insight.data.previous && (
                  <Text style={styles.insightDataLabel}>Previous: {insight.data.previous.toFixed(2)}</Text>
                )}
                {insight.data.trend && (
                  <Text style={styles.insightDataLabel}>Trend: {insight.data.trend}</Text>
                )}
              </View>
              
              <View style={styles.confidenceBar}>
                <Text style={styles.confidenceLabel}>Confidence: {(insight.confidence * 100).toFixed(0)}%</Text>
                <View style={styles.confidenceBarBackground}>
                  <View style={[styles.confidenceBarFill, { width: `${insight.confidence * 100}%` }]} />
                </View>
              </View>
              
              {insight.recommendations.length > 0 && (
                <View style={styles.recommendations}>
                  <Text style={styles.recommendationsTitle}>Recommendations:</Text>
                  {insight.recommendations.slice(0, 2).map((rec, index) => (
                    <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
                  ))}
                </View>
              )}
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No insights available</Text>
            <AccessibleButton
              title="Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.generateButton}
              variant="primary"
              size="medium"
            />
          </View>
        )}
      </View>
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (showDashboard) {
    return (
      <View style={styles.fullScreen}>
        <View style={styles.dashboardHeader}>
          <AccessibleButton
            title="✕ Close"
            accessibilityLabel="Close analytics dashboard"
            onPress={() => setShowDashboard(false)}
            style={styles.closeButton}
            textStyle={styles.closeButtonText}
            variant="ghost"
            size="small"
          />
          <Text style={styles.dashboardTitle}>AI Analytics Dashboard</Text>
        </View>
        <AIInsightsDashboard />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Analytics Demo</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Analytics & Predictive Insights
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('scenarios', 'Scenarios')}
        {renderTabButton('insights', 'Insights')}
        {renderTabButton('dashboard', 'Dashboard')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
        {activeTab === 'insights' && renderInsightsTab()}
        {activeTab === 'dashboard' && (
          <View style={styles.tabContent}>
            <View style={styles.section}>
              <Text style={styles.sectionTitle}>Analytics Dashboard</Text>
              <Text style={styles.sectionDescription}>
                Access the comprehensive AI analytics dashboard with real-time insights and monitoring.
              </Text>
              
              <AccessibleButton
                title="📊 Open Analytics Dashboard"
                onPress={handleShowDashboard}
                style={styles.primaryButton}
                variant="primary"
                size="large"
              />
            </View>
          </View>
        )}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
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

const { width } = Dimensions.get('window');

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
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  overviewCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  overviewValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  overviewLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
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
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
  },
  metricBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
  },
  metricBarFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 120,
  },
  primaryButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 8,
  },
  generateButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    marginTop: 16,
  },
  insightPreview: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  insightPreviewHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightPreviewTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  impactBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  impactBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  insightPreviewDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  insightPreviewConfidence: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '600',
  },
  scenarioCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  scenarioHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  scenarioInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  scenarioIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  scenarioDetails: {
    flex: 1,
  },
  scenarioName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  scenarioDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  scenarioControls: {
    alignItems: 'flex-end',
  },
  scenarioStatus: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
  },
  scenarioToggle: {
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  scenarioStats: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  scenarioStat: {
    fontSize: 12,
    color: '#666',
  },
  insightCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  insightTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  insightDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  insightData: {
    marginBottom: 12,
  },
  insightDataLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  confidenceBar: {
    marginBottom: 12,
  },
  confidenceLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  confidenceBarBackground: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
  },
  confidenceBarFill: {
    height: '100%',
    backgroundColor: '#007AFF',
    borderRadius: 2,
  },
  recommendations: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  recommendationsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  recommendationItem: {
    fontSize: 12,
    color: '#666',
    lineHeight: 16,
    marginBottom: 4,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  emptyStateText: {
    fontSize: 16,
    color: '#666',
    marginBottom: 16,
    textAlign: 'center',
  },
  fullScreen: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  dashboardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    padding: 16,
  },
  closeButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    borderRadius: 6,
    marginRight: 16,
  },
  closeButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  dashboardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
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

export default AIAnalyticsDemo;


