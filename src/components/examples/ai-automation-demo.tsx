/**
 * @fileoverview AI automation and orchestration demo component
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIAutomationDashboard } from '../dashboard/ai-automation-dashboard';
import { 
  aiAutomationOrchestrator, 
  AIAutomationRule, 
  AIWorkflowOrchestration 
} from '../../lib/ai/ai-automation-orchestrator';

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_AUTOMATION_SCENARIOS = [
  {
    id: 'scenario_1',
    title: 'Auto-Retrain on Performance Degradation',
    description: 'Automatically retrain models when accuracy drops below threshold',
    category: 'Performance Monitoring',
    difficulty: 'intermediate',
    estimatedTime: 5,
    steps: [
      'Monitor model performance metrics',
      'Detect performance degradation',
      'Trigger automatic retraining',
      'Validate improved performance',
      'Deploy updated model if successful',
    ],
    expectedOutcome: 'Automated model maintenance with improved performance',
  },
  {
    id: 'scenario_2',
    title: 'Intelligent Resource Scaling',
    description: 'Automatically scale resources based on system load and demand',
    category: 'Resource Management',
    difficulty: 'advanced',
    estimatedTime: 8,
    steps: [
      'Monitor system resource utilization',
      'Analyze load patterns and trends',
      'Predict resource requirements',
      'Scale resources automatically',
      'Optimize cost and performance',
    ],
    expectedOutcome: 'Optimal resource utilization with cost efficiency',
  },
  {
    id: 'scenario_3',
    title: 'Automated Model Deployment Pipeline',
    description: 'End-to-end automated deployment with validation and rollback',
    category: 'Deployment Automation',
    difficulty: 'advanced',
    estimatedTime: 10,
    steps: [
      'Validate model performance',
      'Run integration tests',
      'Deploy to staging environment',
      'Execute smoke tests',
      'Deploy to production with monitoring',
    ],
    expectedOutcome: 'Reliable, automated deployment pipeline',
  },
  {
    id: 'scenario_4',
    title: 'Smart Alert Management',
    description: 'Intelligent alerting with context-aware notifications',
    category: 'Monitoring & Alerting',
    difficulty: 'intermediate',
    estimatedTime: 6,
    steps: [
      'Configure alert conditions',
      'Set up intelligent filtering',
      'Implement escalation policies',
      'Create context-aware notifications',
      'Monitor alert effectiveness',
    ],
    expectedOutcome: 'Reduced alert fatigue with actionable notifications',
  },
];

const DEMO_WORKFLOWS = [
  {
    id: 'workflow_1',
    name: 'Model Retraining Pipeline',
    description: 'Complete automated model retraining workflow',
    status: 'active' as const,
    triggers: [
      {
        type: 'schedule' as const,
        configuration: { cron: '0 2 * * *' }, // Daily at 2 AM
      },
    ],
    steps: [
      {
        id: 'step_1',
        name: 'Data Validation',
        type: 'data_processing' as const,
        configuration: { validationRules: 'comprehensive' },
        dependencies: [],
        timeout: 300,
        retryCount: 3,
      },
      {
        id: 'step_2',
        name: 'Model Training',
        type: 'model_training' as const,
        configuration: { algorithm: 'neural_network', epochs: 100 },
        dependencies: ['step_1'],
        timeout: 3600,
        retryCount: 2,
      },
      {
        id: 'step_3',
        name: 'Performance Validation',
        type: 'data_processing' as const,
        configuration: { validationType: 'performance' },
        dependencies: ['step_2'],
        timeout: 600,
        retryCount: 2,
      },
      {
        id: 'step_4',
        name: 'Deploy if Improved',
        type: 'model_deployment' as const,
        configuration: { environment: 'production', condition: 'improved' },
        dependencies: ['step_3'],
        timeout: 900,
        retryCount: 1,
      },
    ],
    execution: {
      status: 'idle' as const,
    },
    metadata: { category: 'model_lifecycle' },
    createdAt: Date.now() - 86400000,
    updatedAt: Date.now() - 86400000,
  },
  {
    id: 'workflow_2',
    name: 'System Health Monitoring',
    description: 'Continuous system health monitoring and optimization',
    status: 'active' as const,
    triggers: [
      {
        type: 'schedule' as const,
        configuration: { interval: 300 }, // Every 5 minutes
      },
    ],
    steps: [
      {
        id: 'step_1',
        name: 'Collect Metrics',
        type: 'data_processing' as const,
        configuration: { metrics: ['cpu', 'memory', 'network', 'storage'] },
        dependencies: [],
        timeout: 60,
        retryCount: 3,
      },
      {
        id: 'step_2',
        name: 'Analyze Performance',
        type: 'data_processing' as const,
        configuration: { analysisType: 'trend' },
        dependencies: ['step_1'],
        timeout: 120,
        retryCount: 2,
      },
      {
        id: 'step_3',
        name: 'Optimize if Needed',
        type: 'optimization' as const,
        configuration: { optimizationType: 'resource' },
        dependencies: ['step_2'],
        timeout: 300,
        retryCount: 1,
      },
    ],
    execution: {
      status: 'running' as const,
      startedAt: Date.now() - 180000,
      currentStep: 'step_2',
    },
    metadata: { category: 'system_optimization' },
    createdAt: Date.now() - 172800000,
    updatedAt: Date.now() - 172800000,
  },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export default function AIAutomationDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'scenarios' | 'workflows' | 'dashboard'>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [systemStats, setSystemStats] = useState<any>(null);
  const [showDashboard, setShowDashboard] = useState(false);

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
      // Initialize demo workflows
      DEMO_WORKFLOWS.forEach(workflow => {
        aiAutomationOrchestrator.createWorkflow(workflow);
      });

      // Get system stats
      const stats = aiAutomationOrchestrator.getSystemStats();
      setSystemStats(stats);

      // Set up event listeners
      aiAutomationOrchestrator.on('workflowStarted', handleWorkflowStarted);
      aiAutomationOrchestrator.on('workflowCompleted', handleWorkflowCompleted);
      aiAutomationOrchestrator.on('workflowFailed', handleWorkflowFailed);

    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo');
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

  const handleWorkflowStarted = useCallback((data: any) => {
    Alert.alert('Workflow Started', `Workflow ${data.workflow.name} has started execution`);
  }, []);

  const handleWorkflowCompleted = useCallback((data: any) => {
    Alert.alert('Workflow Completed', `Workflow ${data.workflow.name} has completed successfully`);
  }, []);

  const handleWorkflowFailed = useCallback((data: any) => {
    Alert.alert('Workflow Failed', `Workflow ${data.workflow.name} has failed: ${data.error}`);
  }, []);

  // ============================================================================
  // DEMO ACTIONS
  // ============================================================================

  const handleRunScenario = useCallback(async (scenario: any) => {
    setIsLoading(true);
    try {
      // Simulate scenario execution
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert(
        'Scenario Completed',
        `${scenario.title} completed successfully!\n\nExpected outcome: ${scenario.expectedOutcome}`
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to run scenario');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleExecuteWorkflow = useCallback(async (workflowId: string) => {
    setIsLoading(true);
    try {
      const success = await aiAutomationOrchestrator.executeWorkflow(workflowId);
      if (success) {
        Alert.alert('Success', 'Workflow executed successfully');
      } else {
        Alert.alert('Error', 'Failed to execute workflow');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to execute workflow');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleCreateDemoRule = useCallback(async () => {
    setIsLoading(true);
    try {
      const demoRule: AIAutomationRule = {
        id: `demo_rule_${Date.now()}`,
        name: 'Demo Performance Rule',
        description: 'Automatically optimize models when performance drops',
        enabled: true,
        priority: 80,
        conditions: [
          {
            type: 'metric',
            operator: 'less_than',
            value: 'model_accuracy',
            threshold: 0.85,
            timeWindow: 30,
          },
        ],
        actions: [
          {
            type: 'optimize_model',
            parameters: { modelId: 'auto', optimizationType: 'hyperparameter' },
            delay: 60,
          },
        ],
        metadata: { category: 'demo', createdBy: 'user' },
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      aiAutomationOrchestrator.createAutomationRule(demoRule);
      Alert.alert('Success', 'Demo automation rule created successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to create demo rule');
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

  const renderScenarioCard = (scenario: any): JSX.Element => {
    const getDifficultyColor = (difficulty: string): string => {
      switch (difficulty) {
        case 'beginner': return '#34C759';
        case 'intermediate': return '#FF9500';
        case 'advanced': return '#FF3B30';
        default: return '#8E8E93';
      }
    };

    const getCategoryIcon = (category: string): string => {
      switch (category) {
        case 'Performance Monitoring': return '📊';
        case 'Resource Management': return '⚙️';
        case 'Deployment Automation': return '🚀';
        case 'Monitoring & Alerting': return '🔔';
        default: return '🤖';
      }
    };

    return (
      <TouchableOpacity
        key={scenario.id}
        style={styles.scenarioCard}
        onPress={() => handleRunScenario(scenario)}
        activeOpacity={0.7}
      >
        <View style={styles.scenarioHeader}>
          <View style={styles.scenarioTitleRow}>
            <Text style={styles.scenarioCategoryIcon}>{getCategoryIcon(scenario.category)}</Text>
            <View style={styles.scenarioInfo}>
              <Text style={styles.scenarioTitle}>{scenario.title}</Text>
              <Text style={styles.scenarioCategory}>{scenario.category}</Text>
            </View>
          </View>
          <View style={[styles.difficultyBadge, { backgroundColor: getDifficultyColor(scenario.difficulty) }]}>
            <Text style={styles.difficultyBadgeText}>{scenario.difficulty.toUpperCase()}</Text>
          </View>
        </View>
        
        <Text style={styles.scenarioDescription}>{scenario.description}</Text>
        
        <View style={styles.scenarioDetails}>
          <Text style={styles.scenarioDetail}>⏱️ {scenario.estimatedTime} minutes</Text>
          <Text style={styles.scenarioDetail}>📋 {scenario.steps.length} steps</Text>
        </View>
        
        <Text style={styles.expectedOutcome}>
          <Text style={styles.expectedOutcomeLabel}>Expected Outcome: </Text>
          {scenario.expectedOutcome}
        </Text>
      </TouchableOpacity>
    );
  };

  const renderWorkflowCard = (workflow: any): JSX.Element => {
    const getStatusColor = (status: string): string => {
      switch (status) {
        case 'active': return '#34C759';
        case 'running': return '#007AFF';
        case 'paused': return '#FF9500';
        case 'stopped': return '#8E8E93';
        case 'error': return '#FF3B30';
        default: return '#8E8E93';
      }
    };

    const getExecutionStatusColor = (status: string): string => {
      switch (status) {
        case 'running': return '#007AFF';
        case 'completed': return '#34C759';
        case 'failed': return '#FF3B30';
        case 'paused': return '#FF9500';
        default: return '#8E8E93';
      }
    };

    return (
      <View key={workflow.id} style={styles.workflowCard}>
        <View style={styles.workflowHeader}>
          <View style={styles.workflowInfo}>
            <Text style={styles.workflowName}>{workflow.name}</Text>
            <Text style={styles.workflowDescription}>{workflow.description}</Text>
          </View>
          <View style={styles.workflowControls}>
            <View style={[styles.statusBadge, { backgroundColor: getStatusColor(workflow.status) }]}>
              <Text style={styles.statusBadgeText}>{workflow.status.toUpperCase()}</Text>
            </View>
            <View style={[styles.executionBadge, { backgroundColor: getExecutionStatusColor(workflow.execution.status) }]}>
              <Text style={styles.executionBadgeText}>{workflow.execution.status.toUpperCase()}</Text>
            </View>
          </View>
        </View>
        
        <View style={styles.workflowDetails}>
          <Text style={styles.workflowDetail}>
            Steps: {workflow.steps.length} step{workflow.steps.length !== 1 ? 's' : ''}
          </Text>
          <Text style={styles.workflowDetail}>
            Triggers: {workflow.triggers.length} trigger{workflow.triggers.length !== 1 ? 's' : ''}
          </Text>
          {workflow.execution.currentStep && (
            <Text style={styles.workflowDetail}>
              Current Step: {workflow.execution.currentStep}
            </Text>
          )}
          {workflow.execution.lastExecutedAt && (
            <Text style={styles.workflowDetail}>
              Last Run: {new Date(workflow.execution.lastExecutedAt).toLocaleString()}
            </Text>
          )}
        </View>
        
        <View style={styles.workflowActions}>
          {workflow.status === 'active' && workflow.execution.status === 'idle' && (
            <AccessibleButton
              title="Execute"
              onPress={() => handleExecuteWorkflow(workflow.id)}
              style={styles.workflowActionButton}
              variant="primary"
              size="small"
            />
          )}
          <AccessibleButton
            title="View Details"
            onPress={() => Alert.alert('Workflow Details', `Workflow: ${workflow.name}\nStatus: ${workflow.status}\nSteps: ${workflow.steps.length}`)}
            style={styles.workflowActionButton}
            variant="outline"
            size="small"
          />
        </View>
      </View>
    );
  };

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Automation & Orchestration</Text>
        <Text style={styles.sectionDescription}>
          Intelligent automation system that orchestrates AI models, workflows, and system operations 
          with advanced rule-based automation and intelligent decision making.
        </Text>
        
        {systemStats && (
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.totalRules}</Text>
              <Text style={styles.statLabel}>Automation Rules</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.activeRules}</Text>
              <Text style={styles.statLabel}>Active Rules</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.totalWorkflows}</Text>
              <Text style={styles.statLabel}>Workflows</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.activeWorkflows}</Text>
              <Text style={styles.statLabel}>Active</Text>
            </View>
          </View>
        )}
      </View>

      {/* Key Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Features</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⚡</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Intelligent Automation Rules</Text>
              <Text style={styles.featureDescription}>
                Rule-based automation with conditions, actions, and intelligent triggers
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🚀</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Workflow Orchestration</Text>
              <Text style={styles.featureDescription}>
                Complex workflow orchestration with dependencies and error handling
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Event-Driven Architecture</Text>
              <Text style={styles.featureDescription}>
                Real-time event processing and automated responses
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔧</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>System Integration</Text>
              <Text style={styles.featureDescription}>
                Seamless integration with AI models, analytics, and optimization systems
              </Text>
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
            onPress={() => setShowDashboard(true)}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="⚡ Create Demo Rule"
            onPress={handleCreateDemoRule}
            style={styles.actionButton}
            variant="secondary"
            size="small"
            isDisabled={isLoading}
          />
          <AccessibleButton
            title="🎯 Try Scenarios"
            onPress={() => handleTabChange('scenarios')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Explore different AI automation scenarios and use cases
        </Text>
        
        {DEMO_AUTOMATION_SCENARIOS.map(renderScenarioCard)}
      </View>
    </ScrollView>
  );

  const renderWorkflowsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Workflow Orchestration</Text>
        <Text style={styles.sectionDescription}>
          Manage and execute automated workflows
        </Text>
        
        {DEMO_WORKFLOWS.map(renderWorkflowCard)}
      </View>
    </ScrollView>
  );

  const renderDashboardTab = (): JSX.Element => (
    <View style={styles.tabContent}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Dashboard</Text>
        <Text style={styles.sectionDescription}>
          Access the full-featured automation and orchestration dashboard
        </Text>
        
        <AccessibleButton
          title="🚀 Open Dashboard"
          onPress={() => setShowDashboard(true)}
          style={styles.primaryButton}
          variant="primary"
          size="large"
        />
      </View>
    </View>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (showDashboard) {
    return (
      <View style={styles.dashboardContainer}>
        <View style={styles.dashboardHeader}>
          <AccessibleButton
            title="← Back to Demo"
            onPress={() => setShowDashboard(false)}
            style={styles.backButton}
            variant="ghost"
            size="small"
          />
          <Text style={styles.dashboardTitle}>AI Automation Dashboard</Text>
        </View>
        <AIAutomationDashboard />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Automation & Orchestration Demo</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Automation Rules & Workflow Management
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('scenarios', 'Scenarios')}
        {renderTabButton('workflows', 'Workflows')}
        {renderTabButton('dashboard', 'Dashboard')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
        {activeTab === 'workflows' && renderWorkflowsTab()}
        {activeTab === 'dashboard' && renderDashboardTab()}
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
    marginBottom: 16,
  },
  statsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statItem: {
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
  featuresList: {
    marginTop: 8,
  },
  featureItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 16,
  },
  featureIcon: {
    fontSize: 24,
    marginRight: 12,
    marginTop: 2,
  },
  featureContent: {
    flex: 1,
  },
  featureTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
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
    marginVertical: 4,
  },
  primaryButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 16,
  },
  scenarioCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  scenarioHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  scenarioTitleRow: {
    flexDirection: 'row',
    flex: 1,
  },
  scenarioCategoryIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  scenarioInfo: {
    flex: 1,
  },
  scenarioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  scenarioCategory: {
    fontSize: 12,
    color: '#666',
  },
  difficultyBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  difficultyBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  scenarioDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  scenarioDetails: {
    flexDirection: 'row',
    marginBottom: 12,
  },
  scenarioDetail: {
    fontSize: 12,
    color: '#666',
    marginRight: 16,
  },
  expectedOutcome: {
    fontSize: 12,
    color: '#333',
    lineHeight: 16,
  },
  expectedOutcomeLabel: {
    fontWeight: '600',
  },
  workflowCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
  },
  workflowHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  workflowInfo: {
    flex: 1,
  },
  workflowName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  workflowDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  workflowControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  statusBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  executionBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  executionBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  workflowDetails: {
    marginBottom: 12,
  },
  workflowDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  workflowActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  workflowActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  dashboardContainer: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  dashboardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#007AFF',
    padding: 16,
  },
  backButton: {
    marginRight: 16,
  },
  dashboardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    flex: 1,
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

export default AIAutomationDemo;

