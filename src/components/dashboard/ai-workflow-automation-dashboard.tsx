/**
 * @fileoverview AI workflow automation dashboard component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import {
  AIWorkflowAutomationRule,
  AIWorkflowCondition,
  AIWorkflowAction,
  aiWorkflowAutomationManager,
} from '../../lib/ai/ai-workflow-automation';
import {
  AITaskExecutionStrategy,
  aiTaskOrchestratorManager,
} from '../../lib/ai/ai-task-orchestrator';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface AutomationRuleForm {
  name: string;
  description: string;
  priority: number;
  isEnabled: boolean;
  conditions: AIWorkflowCondition[];
  actions: AIWorkflowAction[];
}

interface ExecutionStrategyForm {
  name: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  concurrency: number;
  timeout: number;
  maxRetries: number;
  backoffMultiplier: number;
  initialDelay: number;
  loadBalancingStrategy: 'round_robin' | 'least_loaded' | 'fastest_response' | 'weighted';
  maxMemory: number;
  maxCpu: number;
  isEnabled: boolean;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI workflow automation dashboard component
 * Provides comprehensive monitoring and management of AI automation systems
 */
export function AIWorkflowAutomationDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'strategies' | 'monitoring'>('overview');
  const [automationRules, setAutomationRules] = useState<AIWorkflowAutomationRule[]>([]);
  const [executionStrategies, setExecutionStrategies] = useState<AITaskExecutionStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showRuleForm, setShowRuleForm] = useState(false);
  const [showStrategyForm, setShowStrategyForm] = useState(false);
  const [selectedRule, setSelectedRule] = useState<AIWorkflowAutomationRule | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<AITaskExecutionStrategy | null>(null);

  // Form states
  const [ruleForm, setRuleForm] = useState<AutomationRuleForm>({
    name: '',
    description: '',
    priority: 50,
    isEnabled: true,
    conditions: [],
    actions: [],
  });

  const [strategyForm, setStrategyForm] = useState<ExecutionStrategyForm>({
    name: '',
    description: '',
    priority: 'medium',
    concurrency: 10,
    timeout: 30000,
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000,
    loadBalancingStrategy: 'round_robin',
    maxMemory: 2048,
    maxCpu: 60,
    isEnabled: true,
  });

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    loadData();
  }, []);

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [rules, strategies] = await Promise.all([
        Promise.resolve(aiWorkflowAutomationManager.getAutomationRules()),
        Promise.resolve(aiTaskOrchestratorManager.getExecutionStrategies()),
      ]);
      
      setAutomationRules(rules);
      setExecutionStrategies(strategies);
    } catch (error) {
      Alert.alert('Error', 'Failed to load automation data');
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

  const handleCreateRule = useCallback(async () => {
    try {
      if (!ruleForm.name || !ruleForm.description) {
        Alert.alert('Error', 'Name and description are required');
        return;
      }

      const ruleId = await aiWorkflowAutomationManager.addAutomationRule({
        name: ruleForm.name,
        description: ruleForm.description,
        priority: ruleForm.priority,
        isEnabled: ruleForm.isEnabled,
        conditions: ruleForm.conditions,
        actions: ruleForm.actions,
      });

      Alert.alert('Success', `Automation rule created: ${ruleId}`);
      setShowRuleForm(false);
      resetRuleForm();
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to create automation rule');
    }
  }, [ruleForm]);

  const handleCreateStrategy = useCallback(async () => {
    try {
      if (!strategyForm.name || !strategyForm.description) {
        Alert.alert('Error', 'Name and description are required');
        return;
      }

      const strategyId = await aiTaskOrchestratorManager.addExecutionStrategy({
        name: strategyForm.name,
        description: strategyForm.description,
        priority: strategyForm.priority,
        concurrency: strategyForm.concurrency,
        timeout: strategyForm.timeout,
        retryPolicy: {
          maxRetries: strategyForm.maxRetries,
          backoffMultiplier: strategyForm.backoffMultiplier,
          initialDelay: strategyForm.initialDelay,
        },
        loadBalancing: {
          strategy: strategyForm.loadBalancingStrategy,
        },
        resourceConstraints: {
          maxMemory: strategyForm.maxMemory,
          maxCpu: strategyForm.maxCpu,
        },
        isEnabled: strategyForm.isEnabled,
      });

      Alert.alert('Success', `Execution strategy created: ${strategyId}`);
      setShowStrategyForm(false);
      resetStrategyForm();
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to create execution strategy');
    }
  }, [strategyForm]);

  const handleToggleRule = useCallback(async (ruleId: string, isEnabled: boolean) => {
    try {
      await aiWorkflowAutomationManager.updateAutomationRule(ruleId, { isEnabled });
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to update automation rule');
    }
  }, [loadData]);

  const handleToggleStrategy = useCallback(async (strategyId: string, isEnabled: boolean) => {
    try {
      await aiTaskOrchestratorManager.updateExecutionStrategy(strategyId, { isEnabled });
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to update execution strategy');
    }
  }, [loadData]);

  const handleDeleteRule = useCallback(async (ruleId: string) => {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this automation rule?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await aiWorkflowAutomationManager.removeAutomationRule(ruleId);
              loadData();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete automation rule');
            }
          },
        },
      ]
    );
  }, [loadData]);

  const handleDeleteStrategy = useCallback(async (strategyId: string) => {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this execution strategy?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              // Note: This would need to be implemented in the orchestrator
              Alert.alert('Info', 'Strategy deletion not yet implemented');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete execution strategy');
            }
          },
        },
      ]
    );
  }, [loadData]);

  // ============================================================================
  // FORM MANAGEMENT
  // ============================================================================

  const resetRuleForm = useCallback(() => {
    setRuleForm({
      name: '',
      description: '',
      priority: 50,
      isEnabled: true,
      conditions: [],
      actions: [],
    });
  }, []);

  const resetStrategyForm = useCallback(() => {
    setStrategyForm({
      name: '',
      description: '',
      priority: 'medium',
      concurrency: 10,
      timeout: 30000,
      maxRetries: 3,
      backoffMultiplier: 2,
      initialDelay: 1000,
      loadBalancingStrategy: 'round_robin',
      maxMemory: 2048,
      maxCpu: 60,
      isEnabled: true,
    });
  }, []);

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

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Overview</Text>
        <View style={styles.overviewGrid}>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{automationRules.length}</Text>
            <Text style={styles.overviewLabel}>Automation Rules</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{executionStrategies.length}</Text>
            <Text style={styles.overviewLabel}>Execution Strategies</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>
              {automationRules.filter(rule => rule.isEnabled).length}
            </Text>
            <Text style={styles.overviewLabel}>Active Rules</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>
              {executionStrategies.filter(strategy => strategy.isEnabled).length}
            </Text>
            <Text style={styles.overviewLabel}>Active Strategies</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <AccessibleButton
            accessibilityLabel="Create new automation rule"
            onPress={() => setShowRuleForm(true)}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>➕ New Rule</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create new execution strategy"
            onPress={() => setShowStrategyForm(true)}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>⚙️ New Strategy</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Refresh data"
            onPress={loadData}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>🔄 Refresh</Text>
          </AccessibleButton>
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          <Text style={styles.emptyText}>No recent activity to display</Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderRulesTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Automation Rules</Text>
          <AccessibleButton
            accessibilityLabel="Create new automation rule"
            onPress={() => setShowRuleForm(true)}
            style={styles.smallButton}
          >
            <Text style={styles.smallButtonText}>➕ New</Text>
          </AccessibleButton>
        </View>

        <View style={styles.rulesList}>
          {automationRules.map(rule => (
            <View key={rule.id} style={styles.ruleCard}>
              <View style={styles.ruleHeader}>
                <Text style={styles.ruleName}>{rule.name}</Text>
                <View style={styles.ruleControls}>
                  <Switch
                    value={rule.isEnabled}
                    onValueChange={(value) => handleToggleRule(rule.id, value)}
                  />
                  <AccessibleButton
                    accessibilityLabel={`Delete rule ${rule.name}`}
                    onPress={() => handleDeleteRule(rule.id)}
                    style={[styles.iconButton, styles.deleteButton]}
                  >
                    <Text style={styles.iconButtonText}>🗑️</Text>
                  </AccessibleButton>
                </View>
              </View>
              <Text style={styles.ruleDescription}>{rule.description}</Text>
              <View style={styles.ruleDetails}>
                <Text style={styles.ruleDetail}>Priority: {rule.priority}</Text>
                <Text style={styles.ruleDetail}>Conditions: {rule.conditions.length}</Text>
                <Text style={styles.ruleDetail}>Actions: {rule.actions.length}</Text>
              </View>
            </View>
          ))}
          {automationRules.length === 0 && (
            <Text style={styles.emptyText}>No automation rules configured</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderStrategiesTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Execution Strategies</Text>
          <AccessibleButton
            accessibilityLabel="Create new execution strategy"
            onPress={() => setShowStrategyForm(true)}
            style={styles.smallButton}
          >
            <Text style={styles.smallButtonText}>➕ New</Text>
          </AccessibleButton>
        </View>

        <View style={styles.strategiesList}>
          {executionStrategies.map(strategy => (
            <View key={strategy.id} style={styles.strategyCard}>
              <View style={styles.strategyHeader}>
                <Text style={styles.strategyName}>{strategy.name}</Text>
                <View style={styles.strategyControls}>
                  <Switch
                    value={strategy.isEnabled}
                    onValueChange={(value) => handleToggleStrategy(strategy.id, value)}
                  />
                  <AccessibleButton
                    accessibilityLabel={`Delete strategy ${strategy.name}`}
                    onPress={() => handleDeleteStrategy(strategy.id)}
                    style={[styles.iconButton, styles.deleteButton]}
                  >
                    <Text style={styles.iconButtonText}>🗑️</Text>
                  </AccessibleButton>
                </View>
              </View>
              <Text style={styles.strategyDescription}>{strategy.description}</Text>
              <View style={styles.strategyDetails}>
                <Text style={styles.strategyDetail}>Priority: {strategy.priority}</Text>
                <Text style={styles.strategyDetail}>Concurrency: {strategy.concurrency}</Text>
                <Text style={styles.strategyDetail}>Timeout: {strategy.timeout}ms</Text>
                <Text style={styles.strategyDetail}>Max Retries: {strategy.retryPolicy.maxRetries}</Text>
                <Text style={styles.strategyDetail}>Load Balancing: {strategy.loadBalancing.strategy}</Text>
              </View>
            </View>
          ))}
          {executionStrategies.length === 0 && (
            <Text style={styles.emptyText}>No execution strategies configured</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* Automation Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().totalRules}
            </Text>
            <Text style={styles.statLabel}>Total Rules</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().enabledRules}
            </Text>
            <Text style={styles.statLabel}>Enabled Rules</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().activeExecutions}
            </Text>
            <Text style={styles.statLabel}>Active Executions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().totalExecutions}
            </Text>
            <Text style={styles.statLabel}>Total Executions</Text>
          </View>
        </View>
      </View>

      {/* Orchestrator Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Orchestrator Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().totalStrategies}
            </Text>
            <Text style={styles.statLabel}>Total Strategies</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().activeExecutions}
            </Text>
            <Text style={styles.statLabel}>Active Executions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().queuedTasks}
            </Text>
            <Text style={styles.statLabel}>Queued Tasks</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().totalMetrics}
            </Text>
            <Text style={styles.statLabel}>Total Metrics</Text>
          </View>
        </View>
      </View>

      {/* Load Balancing Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Load Balancing Metrics</Text>
        <View style={styles.metricsList}>
          {aiTaskOrchestratorManager.getLoadBalancingMetrics().map(metric => (
            <View key={metric.modelId} style={styles.metricCard}>
              <Text style={styles.metricTitle}>Model: {metric.modelId}</Text>
              <View style={styles.metricDetails}>
                <Text style={styles.metricDetail}>Active Tasks: {metric.activeTasks}</Text>
                <Text style={styles.metricDetail}>Avg Response: {metric.averageResponseTime.toFixed(0)}ms</Text>
                <Text style={styles.metricDetail}>Success Rate: {(metric.successRate * 100).toFixed(1)}%</Text>
                <Text style={styles.metricDetail}>Memory: {metric.resourceUtilization.memory.toFixed(1)}%</Text>
                <Text style={styles.metricDetail}>CPU: {metric.resourceUtilization.cpu.toFixed(1)}%</Text>
              </View>
            </View>
          ))}
          {aiTaskOrchestratorManager.getLoadBalancingMetrics().length === 0 && (
            <Text style={styles.emptyText}>No load balancing metrics available</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderRuleForm = (): JSX.Element => (
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>Create Automation Rule</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Rule Name"
          value={ruleForm.name}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, name: text }))}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Description"
          value={ruleForm.description}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, description: text }))}
          multiline
        />
        
        <TextInput
          style={styles.input}
          placeholder="Priority (1-100)"
          value={ruleForm.priority.toString()}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, priority: parseInt(text) || 50 }))}
          keyboardType="numeric"
        />
        
        <View style={styles.switchContainer}>
          <Text>Enabled</Text>
          <Switch
            value={ruleForm.isEnabled}
            onValueChange={(value) => setRuleForm(prev => ({ ...prev, isEnabled: value }))}
          />
        </View>

        <View style={styles.modalButtons}>
          <AccessibleButton
            accessibilityLabel="Cancel rule creation"
            onPress={() => {
              setShowRuleForm(false);
              resetRuleForm();
            }}
            style={[styles.modalButton, styles.cancelButton]}
          >
            <Text style={styles.modalButtonText}>Cancel</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create automation rule"
            onPress={handleCreateRule}
            style={[styles.modalButton, styles.confirmButton]}
          >
            <Text style={styles.modalButtonText}>Create</Text>
          </AccessibleButton>
        </View>
      </View>
    </View>
  );

  const renderStrategyForm = (): JSX.Element => (
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>Create Execution Strategy</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Strategy Name"
          value={strategyForm.name}
          onChangeText={(text) => setStrategyForm(prev => ({ ...prev, name: text }))}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Description"
          value={strategyForm.description}
          onChangeText={(text) => setStrategyForm(prev => ({ ...prev, description: text }))}
          multiline
        />
        
        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Priority</Text>
            <View style={styles.priorityButtons}>
              {(['low', 'medium', 'high', 'urgent'] as const).map(priority => (
                <TouchableOpacity
                  key={priority}
                  style={[
                    styles.priorityButton,
                    strategyForm.priority === priority && styles.priorityButtonActive
                  ]}
                  onPress={() => setStrategyForm(prev => ({ ...prev, priority }))}
                >
                  <Text style={[
                    styles.priorityButtonText,
                    strategyForm.priority === priority && styles.priorityButtonTextActive
                  ]}>
                    {priority}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Concurrency</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.concurrency.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, concurrency: parseInt(text) || 10 }))}
              keyboardType="numeric"
            />
          </View>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Timeout (ms)</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.timeout.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, timeout: parseInt(text) || 30000 }))}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Max Retries</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.maxRetries.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, maxRetries: parseInt(text) || 3 }))}
              keyboardType="numeric"
            />
          </View>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Backoff Multiplier</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.backoffMultiplier.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, backoffMultiplier: parseFloat(text) || 2 }))}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.switchContainer}>
          <Text>Enabled</Text>
          <Switch
            value={strategyForm.isEnabled}
            onValueChange={(value) => setStrategyForm(prev => ({ ...prev, isEnabled: value }))}
          />
        </View>

        <View style={styles.modalButtons}>
          <AccessibleButton
            accessibilityLabel="Cancel strategy creation"
            onPress={() => {
              setShowStrategyForm(false);
              resetStrategyForm();
            }}
            style={[styles.modalButton, styles.cancelButton]}
          >
            <Text style={styles.modalButtonText}>Cancel</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create execution strategy"
            onPress={handleCreateStrategy}
            style={[styles.modalButton, styles.confirmButton]}
          >
            <Text style={styles.modalButtonText}>Create</Text>
          </AccessibleButton>
        </View>
      </View>
    </View>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Workflow Automation</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Task Orchestration & Decision Making
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('rules', 'Rules')}
        {renderTabButton('strategies', 'Strategies')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'rules' && renderRulesTab()}
        {activeTab === 'strategies' && renderStrategiesTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      )}

      {/* Modals */}
      {showRuleForm && renderRuleForm()}
      {showStrategyForm && renderStrategyForm()}
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
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
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
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  rulesList: {
    maxHeight: 400,
  },
  ruleCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  ruleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  ruleName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  ruleControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ruleDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  ruleDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  ruleDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
  },
  strategiesList: {
    maxHeight: 400,
  },
  strategyCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  strategyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  strategyName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  strategyControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  strategyDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  strategyDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  strategyDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  metricsList: {
    maxHeight: 300,
  },
  metricCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  metricTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  metricDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  metricDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    paddingVertical: 20,
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#007AFF',
    borderRadius: 6,
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  iconButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginLeft: 8,
  },
  deleteButton: {
    backgroundColor: '#FF6B6B',
  },
  iconButtonText: {
    color: '#ffffff',
    fontSize: 12,
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    margin: 20,
    maxWidth: 400,
    width: '100%',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    flex: 1,
    marginRight: 8,
  },
  formRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  formField: {
    flex: 1,
  },
  formLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  priorityButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  priorityButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  priorityButtonActive: {
    backgroundColor: '#007AFF',
  },
  priorityButtonText: {
    fontSize: 12,
    color: '#666',
  },
  priorityButtonTextActive: {
    color: '#ffffff',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  cancelButton: {
    backgroundColor: '#666',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
  },
  modalButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIWorkflowAutomationDashboard;
 * @fileoverview AI workflow automation dashboard component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
  TextInput,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import {
  AIWorkflowAutomationRule,
  AIWorkflowCondition,
  AIWorkflowAction,
  aiWorkflowAutomationManager,
} from '../../lib/ai/ai-workflow-automation';
import {
  AITaskExecutionStrategy,
  aiTaskOrchestratorManager,
} from '../../lib/ai/ai-task-orchestrator';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface AutomationRuleForm {
  name: string;
  description: string;
  priority: number;
  isEnabled: boolean;
  conditions: AIWorkflowCondition[];
  actions: AIWorkflowAction[];
}

interface ExecutionStrategyForm {
  name: string;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  concurrency: number;
  timeout: number;
  maxRetries: number;
  backoffMultiplier: number;
  initialDelay: number;
  loadBalancingStrategy: 'round_robin' | 'least_loaded' | 'fastest_response' | 'weighted';
  maxMemory: number;
  maxCpu: number;
  isEnabled: boolean;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI workflow automation dashboard component
 * Provides comprehensive monitoring and management of AI automation systems
 */
export function AIWorkflowAutomationDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'strategies' | 'monitoring'>('overview');
  const [automationRules, setAutomationRules] = useState<AIWorkflowAutomationRule[]>([]);
  const [executionStrategies, setExecutionStrategies] = useState<AITaskExecutionStrategy[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showRuleForm, setShowRuleForm] = useState(false);
  const [showStrategyForm, setShowStrategyForm] = useState(false);
  const [selectedRule, setSelectedRule] = useState<AIWorkflowAutomationRule | null>(null);
  const [selectedStrategy, setSelectedStrategy] = useState<AITaskExecutionStrategy | null>(null);

  // Form states
  const [ruleForm, setRuleForm] = useState<AutomationRuleForm>({
    name: '',
    description: '',
    priority: 50,
    isEnabled: true,
    conditions: [],
    actions: [],
  });

  const [strategyForm, setStrategyForm] = useState<ExecutionStrategyForm>({
    name: '',
    description: '',
    priority: 'medium',
    concurrency: 10,
    timeout: 30000,
    maxRetries: 3,
    backoffMultiplier: 2,
    initialDelay: 1000,
    loadBalancingStrategy: 'round_robin',
    maxMemory: 2048,
    maxCpu: 60,
    isEnabled: true,
  });

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    loadData();
  }, []);

  // ============================================================================
  // DATA LOADING
  // ============================================================================

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [rules, strategies] = await Promise.all([
        Promise.resolve(aiWorkflowAutomationManager.getAutomationRules()),
        Promise.resolve(aiTaskOrchestratorManager.getExecutionStrategies()),
      ]);
      
      setAutomationRules(rules);
      setExecutionStrategies(strategies);
    } catch (error) {
      Alert.alert('Error', 'Failed to load automation data');
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

  const handleCreateRule = useCallback(async () => {
    try {
      if (!ruleForm.name || !ruleForm.description) {
        Alert.alert('Error', 'Name and description are required');
        return;
      }

      const ruleId = await aiWorkflowAutomationManager.addAutomationRule({
        name: ruleForm.name,
        description: ruleForm.description,
        priority: ruleForm.priority,
        isEnabled: ruleForm.isEnabled,
        conditions: ruleForm.conditions,
        actions: ruleForm.actions,
      });

      Alert.alert('Success', `Automation rule created: ${ruleId}`);
      setShowRuleForm(false);
      resetRuleForm();
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to create automation rule');
    }
  }, [ruleForm]);

  const handleCreateStrategy = useCallback(async () => {
    try {
      if (!strategyForm.name || !strategyForm.description) {
        Alert.alert('Error', 'Name and description are required');
        return;
      }

      const strategyId = await aiTaskOrchestratorManager.addExecutionStrategy({
        name: strategyForm.name,
        description: strategyForm.description,
        priority: strategyForm.priority,
        concurrency: strategyForm.concurrency,
        timeout: strategyForm.timeout,
        retryPolicy: {
          maxRetries: strategyForm.maxRetries,
          backoffMultiplier: strategyForm.backoffMultiplier,
          initialDelay: strategyForm.initialDelay,
        },
        loadBalancing: {
          strategy: strategyForm.loadBalancingStrategy,
        },
        resourceConstraints: {
          maxMemory: strategyForm.maxMemory,
          maxCpu: strategyForm.maxCpu,
        },
        isEnabled: strategyForm.isEnabled,
      });

      Alert.alert('Success', `Execution strategy created: ${strategyId}`);
      setShowStrategyForm(false);
      resetStrategyForm();
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to create execution strategy');
    }
  }, [strategyForm]);

  const handleToggleRule = useCallback(async (ruleId: string, isEnabled: boolean) => {
    try {
      await aiWorkflowAutomationManager.updateAutomationRule(ruleId, { isEnabled });
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to update automation rule');
    }
  }, [loadData]);

  const handleToggleStrategy = useCallback(async (strategyId: string, isEnabled: boolean) => {
    try {
      await aiTaskOrchestratorManager.updateExecutionStrategy(strategyId, { isEnabled });
      loadData();
    } catch (error) {
      Alert.alert('Error', 'Failed to update execution strategy');
    }
  }, [loadData]);

  const handleDeleteRule = useCallback(async (ruleId: string) => {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this automation rule?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              await aiWorkflowAutomationManager.removeAutomationRule(ruleId);
              loadData();
            } catch (error) {
              Alert.alert('Error', 'Failed to delete automation rule');
            }
          },
        },
      ]
    );
  }, [loadData]);

  const handleDeleteStrategy = useCallback(async (strategyId: string) => {
    Alert.alert(
      'Confirm Delete',
      'Are you sure you want to delete this execution strategy?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: async () => {
            try {
              // Note: This would need to be implemented in the orchestrator
              Alert.alert('Info', 'Strategy deletion not yet implemented');
            } catch (error) {
              Alert.alert('Error', 'Failed to delete execution strategy');
            }
          },
        },
      ]
    );
  }, [loadData]);

  // ============================================================================
  // FORM MANAGEMENT
  // ============================================================================

  const resetRuleForm = useCallback(() => {
    setRuleForm({
      name: '',
      description: '',
      priority: 50,
      isEnabled: true,
      conditions: [],
      actions: [],
    });
  }, []);

  const resetStrategyForm = useCallback(() => {
    setStrategyForm({
      name: '',
      description: '',
      priority: 'medium',
      concurrency: 10,
      timeout: 30000,
      maxRetries: 3,
      backoffMultiplier: 2,
      initialDelay: 1000,
      loadBalancingStrategy: 'round_robin',
      maxMemory: 2048,
      maxCpu: 60,
      isEnabled: true,
    });
  }, []);

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

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Overview</Text>
        <View style={styles.overviewGrid}>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{automationRules.length}</Text>
            <Text style={styles.overviewLabel}>Automation Rules</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>{executionStrategies.length}</Text>
            <Text style={styles.overviewLabel}>Execution Strategies</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>
              {automationRules.filter(rule => rule.isEnabled).length}
            </Text>
            <Text style={styles.overviewLabel}>Active Rules</Text>
          </View>
          <View style={styles.overviewCard}>
            <Text style={styles.overviewValue}>
              {executionStrategies.filter(strategy => strategy.isEnabled).length}
            </Text>
            <Text style={styles.overviewLabel}>Active Strategies</Text>
          </View>
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Quick Actions</Text>
        <View style={styles.actionButtons}>
          <AccessibleButton
            accessibilityLabel="Create new automation rule"
            onPress={() => setShowRuleForm(true)}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>➕ New Rule</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create new execution strategy"
            onPress={() => setShowStrategyForm(true)}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>⚙️ New Strategy</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Refresh data"
            onPress={loadData}
            style={styles.actionButton}
          >
            <Text style={styles.actionButtonText}>🔄 Refresh</Text>
          </AccessibleButton>
        </View>
      </View>

      {/* Recent Activity */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recent Activity</Text>
        <View style={styles.activityList}>
          <Text style={styles.emptyText}>No recent activity to display</Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderRulesTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Automation Rules</Text>
          <AccessibleButton
            accessibilityLabel="Create new automation rule"
            onPress={() => setShowRuleForm(true)}
            style={styles.smallButton}
          >
            <Text style={styles.smallButtonText}>➕ New</Text>
          </AccessibleButton>
        </View>

        <View style={styles.rulesList}>
          {automationRules.map(rule => (
            <View key={rule.id} style={styles.ruleCard}>
              <View style={styles.ruleHeader}>
                <Text style={styles.ruleName}>{rule.name}</Text>
                <View style={styles.ruleControls}>
                  <Switch
                    value={rule.isEnabled}
                    onValueChange={(value) => handleToggleRule(rule.id, value)}
                  />
                  <AccessibleButton
                    accessibilityLabel={`Delete rule ${rule.name}`}
                    onPress={() => handleDeleteRule(rule.id)}
                    style={[styles.iconButton, styles.deleteButton]}
                  >
                    <Text style={styles.iconButtonText}>🗑️</Text>
                  </AccessibleButton>
                </View>
              </View>
              <Text style={styles.ruleDescription}>{rule.description}</Text>
              <View style={styles.ruleDetails}>
                <Text style={styles.ruleDetail}>Priority: {rule.priority}</Text>
                <Text style={styles.ruleDetail}>Conditions: {rule.conditions.length}</Text>
                <Text style={styles.ruleDetail}>Actions: {rule.actions.length}</Text>
              </View>
            </View>
          ))}
          {automationRules.length === 0 && (
            <Text style={styles.emptyText}>No automation rules configured</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderStrategiesTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Execution Strategies</Text>
          <AccessibleButton
            accessibilityLabel="Create new execution strategy"
            onPress={() => setShowStrategyForm(true)}
            style={styles.smallButton}
          >
            <Text style={styles.smallButtonText}>➕ New</Text>
          </AccessibleButton>
        </View>

        <View style={styles.strategiesList}>
          {executionStrategies.map(strategy => (
            <View key={strategy.id} style={styles.strategyCard}>
              <View style={styles.strategyHeader}>
                <Text style={styles.strategyName}>{strategy.name}</Text>
                <View style={styles.strategyControls}>
                  <Switch
                    value={strategy.isEnabled}
                    onValueChange={(value) => handleToggleStrategy(strategy.id, value)}
                  />
                  <AccessibleButton
                    accessibilityLabel={`Delete strategy ${strategy.name}`}
                    onPress={() => handleDeleteStrategy(strategy.id)}
                    style={[styles.iconButton, styles.deleteButton]}
                  >
                    <Text style={styles.iconButtonText}>🗑️</Text>
                  </AccessibleButton>
                </View>
              </View>
              <Text style={styles.strategyDescription}>{strategy.description}</Text>
              <View style={styles.strategyDetails}>
                <Text style={styles.strategyDetail}>Priority: {strategy.priority}</Text>
                <Text style={styles.strategyDetail}>Concurrency: {strategy.concurrency}</Text>
                <Text style={styles.strategyDetail}>Timeout: {strategy.timeout}ms</Text>
                <Text style={styles.strategyDetail}>Max Retries: {strategy.retryPolicy.maxRetries}</Text>
                <Text style={styles.strategyDetail}>Load Balancing: {strategy.loadBalancing.strategy}</Text>
              </View>
            </View>
          ))}
          {executionStrategies.length === 0 && (
            <Text style={styles.emptyText}>No execution strategies configured</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* Automation Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().totalRules}
            </Text>
            <Text style={styles.statLabel}>Total Rules</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().enabledRules}
            </Text>
            <Text style={styles.statLabel}>Enabled Rules</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().activeExecutions}
            </Text>
            <Text style={styles.statLabel}>Active Executions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiWorkflowAutomationManager.getAutomationStats().totalExecutions}
            </Text>
            <Text style={styles.statLabel}>Total Executions</Text>
          </View>
        </View>
      </View>

      {/* Orchestrator Statistics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Orchestrator Statistics</Text>
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().totalStrategies}
            </Text>
            <Text style={styles.statLabel}>Total Strategies</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().activeExecutions}
            </Text>
            <Text style={styles.statLabel}>Active Executions</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().queuedTasks}
            </Text>
            <Text style={styles.statLabel}>Queued Tasks</Text>
          </View>
          <View style={styles.statCard}>
            <Text style={styles.statValue}>
              {aiTaskOrchestratorManager.getOrchestratorStats().totalMetrics}
            </Text>
            <Text style={styles.statLabel}>Total Metrics</Text>
          </View>
        </View>
      </View>

      {/* Load Balancing Metrics */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Load Balancing Metrics</Text>
        <View style={styles.metricsList}>
          {aiTaskOrchestratorManager.getLoadBalancingMetrics().map(metric => (
            <View key={metric.modelId} style={styles.metricCard}>
              <Text style={styles.metricTitle}>Model: {metric.modelId}</Text>
              <View style={styles.metricDetails}>
                <Text style={styles.metricDetail}>Active Tasks: {metric.activeTasks}</Text>
                <Text style={styles.metricDetail}>Avg Response: {metric.averageResponseTime.toFixed(0)}ms</Text>
                <Text style={styles.metricDetail}>Success Rate: {(metric.successRate * 100).toFixed(1)}%</Text>
                <Text style={styles.metricDetail}>Memory: {metric.resourceUtilization.memory.toFixed(1)}%</Text>
                <Text style={styles.metricDetail}>CPU: {metric.resourceUtilization.cpu.toFixed(1)}%</Text>
              </View>
            </View>
          ))}
          {aiTaskOrchestratorManager.getLoadBalancingMetrics().length === 0 && (
            <Text style={styles.emptyText}>No load balancing metrics available</Text>
          )}
        </View>
      </View>
    </ScrollView>
  );

  const renderRuleForm = (): JSX.Element => (
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>Create Automation Rule</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Rule Name"
          value={ruleForm.name}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, name: text }))}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Description"
          value={ruleForm.description}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, description: text }))}
          multiline
        />
        
        <TextInput
          style={styles.input}
          placeholder="Priority (1-100)"
          value={ruleForm.priority.toString()}
          onChangeText={(text) => setRuleForm(prev => ({ ...prev, priority: parseInt(text) || 50 }))}
          keyboardType="numeric"
        />
        
        <View style={styles.switchContainer}>
          <Text>Enabled</Text>
          <Switch
            value={ruleForm.isEnabled}
            onValueChange={(value) => setRuleForm(prev => ({ ...prev, isEnabled: value }))}
          />
        </View>

        <View style={styles.modalButtons}>
          <AccessibleButton
            accessibilityLabel="Cancel rule creation"
            onPress={() => {
              setShowRuleForm(false);
              resetRuleForm();
            }}
            style={[styles.modalButton, styles.cancelButton]}
          >
            <Text style={styles.modalButtonText}>Cancel</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create automation rule"
            onPress={handleCreateRule}
            style={[styles.modalButton, styles.confirmButton]}
          >
            <Text style={styles.modalButtonText}>Create</Text>
          </AccessibleButton>
        </View>
      </View>
    </View>
  );

  const renderStrategyForm = (): JSX.Element => (
    <View style={styles.modalOverlay}>
      <View style={styles.modalContent}>
        <Text style={styles.modalTitle}>Create Execution Strategy</Text>
        
        <TextInput
          style={styles.input}
          placeholder="Strategy Name"
          value={strategyForm.name}
          onChangeText={(text) => setStrategyForm(prev => ({ ...prev, name: text }))}
        />
        
        <TextInput
          style={styles.input}
          placeholder="Description"
          value={strategyForm.description}
          onChangeText={(text) => setStrategyForm(prev => ({ ...prev, description: text }))}
          multiline
        />
        
        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Priority</Text>
            <View style={styles.priorityButtons}>
              {(['low', 'medium', 'high', 'urgent'] as const).map(priority => (
                <TouchableOpacity
                  key={priority}
                  style={[
                    styles.priorityButton,
                    strategyForm.priority === priority && styles.priorityButtonActive
                  ]}
                  onPress={() => setStrategyForm(prev => ({ ...prev, priority }))}
                >
                  <Text style={[
                    styles.priorityButtonText,
                    strategyForm.priority === priority && styles.priorityButtonTextActive
                  ]}>
                    {priority}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Concurrency</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.concurrency.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, concurrency: parseInt(text) || 10 }))}
              keyboardType="numeric"
            />
          </View>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Timeout (ms)</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.timeout.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, timeout: parseInt(text) || 30000 }))}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.formRow}>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Max Retries</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.maxRetries.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, maxRetries: parseInt(text) || 3 }))}
              keyboardType="numeric"
            />
          </View>
          <View style={styles.formField}>
            <Text style={styles.formLabel}>Backoff Multiplier</Text>
            <TextInput
              style={styles.numberInput}
              value={strategyForm.backoffMultiplier.toString()}
              onChangeText={(text) => setStrategyForm(prev => ({ ...prev, backoffMultiplier: parseFloat(text) || 2 }))}
              keyboardType="numeric"
            />
          </View>
        </View>

        <View style={styles.switchContainer}>
          <Text>Enabled</Text>
          <Switch
            value={strategyForm.isEnabled}
            onValueChange={(value) => setStrategyForm(prev => ({ ...prev, isEnabled: value }))}
          />
        </View>

        <View style={styles.modalButtons}>
          <AccessibleButton
            accessibilityLabel="Cancel strategy creation"
            onPress={() => {
              setShowStrategyForm(false);
              resetStrategyForm();
            }}
            style={[styles.modalButton, styles.cancelButton]}
          >
            <Text style={styles.modalButtonText}>Cancel</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Create execution strategy"
            onPress={handleCreateStrategy}
            style={[styles.modalButton, styles.confirmButton]}
          >
            <Text style={styles.modalButtonText}>Create</Text>
          </AccessibleButton>
        </View>
      </View>
    </View>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Workflow Automation</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Task Orchestration & Decision Making
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('rules', 'Rules')}
        {renderTabButton('strategies', 'Strategies')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'rules' && renderRulesTab()}
        {activeTab === 'strategies' && renderStrategiesTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading...</Text>
        </View>
      )}

      {/* Modals */}
      {showRuleForm && renderRuleForm()}
      {showStrategyForm && renderStrategyForm()}
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
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
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
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
  },
  actionButton: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  rulesList: {
    maxHeight: 400,
  },
  ruleCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  ruleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  ruleName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  ruleControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  ruleDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  ruleDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  ruleDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
  },
  strategiesList: {
    maxHeight: 400,
  },
  strategyCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  strategyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  strategyName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  strategyControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  strategyDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
    lineHeight: 20,
  },
  strategyDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  strategyDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
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
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  metricsList: {
    maxHeight: 300,
  },
  metricCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  metricTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  metricDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  metricDetail: {
    fontSize: 12,
    color: '#888',
    marginRight: 16,
    marginBottom: 4,
  },
  emptyText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
    paddingVertical: 20,
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#007AFF',
    borderRadius: 6,
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  iconButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    marginLeft: 8,
  },
  deleteButton: {
    backgroundColor: '#FF6B6B',
  },
  iconButtonText: {
    color: '#ffffff',
    fontSize: 12,
  },
  modalOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  modalContent: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    margin: 20,
    maxWidth: 400,
    width: '100%',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 20,
    textAlign: 'center',
  },
  input: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
    fontSize: 16,
  },
  numberInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    flex: 1,
    marginRight: 8,
  },
  formRow: {
    flexDirection: 'row',
    marginBottom: 16,
  },
  formField: {
    flex: 1,
  },
  formLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 8,
  },
  priorityButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  priorityButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#f0f0f0',
    borderRadius: 6,
    marginRight: 8,
    marginBottom: 8,
  },
  priorityButtonActive: {
    backgroundColor: '#007AFF',
  },
  priorityButtonText: {
    fontSize: 12,
    color: '#666',
  },
  priorityButtonTextActive: {
    color: '#ffffff',
  },
  switchContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20,
  },
  modalButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  modalButton: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  cancelButton: {
    backgroundColor: '#666',
  },
  confirmButton: {
    backgroundColor: '#007AFF',
  },
  modalButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIWorkflowAutomationDashboard;


