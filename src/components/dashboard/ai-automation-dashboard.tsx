/**
 * @fileoverview AI automation and orchestration dashboard
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
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { 
  aiAutomationOrchestrator, 
  AIAutomationRule, 
  AIWorkflowOrchestration,
  AIAutomationEvent 
} from '../../lib/ai/ai-automation-orchestrator';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface RuleCardProps {
  rule: AIAutomationRule;
  onToggle: (rule: AIAutomationRule) => void;
  onEdit: (rule: AIAutomationRule) => void;
  onDelete: (rule: AIAutomationRule) => void;
}

interface WorkflowCardProps {
  workflow: AIWorkflowOrchestration;
  onExecute: (workflow: AIWorkflowOrchestration) => void;
  onPause: (workflow: AIWorkflowOrchestration) => void;
  onViewDetails: (workflow: AIWorkflowOrchestration) => void;
}

interface EventCardProps {
  event: AIAutomationEvent;
  onViewDetails: (event: AIAutomationEvent) => void;
}

// ============================================================================
// RULE CARD COMPONENT
// ============================================================================

const RuleCard: React.FC<RuleCardProps> = ({ rule, onToggle, onEdit, onDelete }) => {
  const getPriorityColor = (priority: number): string => {
    if (priority >= 90) return '#FF3B30';
    if (priority >= 70) return '#FF9500';
    if (priority >= 50) return '#FFCC00';
    return '#34C759';
  };

  const getStatusColor = (enabled: boolean): string => {
    return enabled ? '#34C759' : '#8E8E93';
  };

  return (
    <View style={styles.ruleCard}>
      <View style={styles.ruleHeader}>
        <View style={styles.ruleInfo}>
          <Text style={styles.ruleName}>{rule.name}</Text>
          <Text style={styles.ruleDescription}>{rule.description}</Text>
        </View>
        <View style={styles.ruleControls}>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(rule.priority) }]}>
            <Text style={styles.priorityBadgeText}>P{rule.priority}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(rule.enabled) }]}>
            <Text style={styles.statusBadgeText}>{rule.enabled ? 'ON' : 'OFF'}</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.ruleDetails}>
        <Text style={styles.ruleDetail}>
          Conditions: {rule.conditions.length} condition{rule.conditions.length !== 1 ? 's' : ''}
        </Text>
        <Text style={styles.ruleDetail}>
          Actions: {rule.actions.length} action{rule.actions.length !== 1 ? 's' : ''}
        </Text>
        <Text style={styles.ruleDetail}>
          Created: {new Date(rule.createdAt).toLocaleDateString()}
        </Text>
      </View>
      
      <View style={styles.ruleActions}>
        <AccessibleButton
          title={rule.enabled ? "Disable" : "Enable"}
          onPress={() => onToggle(rule)}
          style={styles.ruleActionButton}
          variant={rule.enabled ? "danger" : "primary"}
          size="small"
        />
        <AccessibleButton
          title="Edit"
          onPress={() => onEdit(rule)}
          style={styles.ruleActionButton}
          variant="secondary"
          size="small"
        />
        <AccessibleButton
          title="Delete"
          onPress={() => onDelete(rule)}
          style={styles.ruleActionButton}
          variant="ghost"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// WORKFLOW CARD COMPONENT
// ============================================================================

const WorkflowCard: React.FC<WorkflowCardProps> = ({ workflow, onExecute, onPause, onViewDetails }) => {
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
    <View style={styles.workflowCard}>
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
            onPress={() => onExecute(workflow)}
            style={styles.workflowActionButton}
            variant="primary"
            size="small"
          />
        )}
        {workflow.execution.status === 'running' && (
          <AccessibleButton
            title="Pause"
            onPress={() => onPause(workflow)}
            style={styles.workflowActionButton}
            variant="secondary"
            size="small"
          />
        )}
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(workflow)}
          style={styles.workflowActionButton}
          variant="outline"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// EVENT CARD COMPONENT
// ============================================================================

const EventCard: React.FC<EventCardProps> = ({ event, onViewDetails }) => {
  const getEventTypeColor = (type: string): string => {
    switch (type) {
      case 'rule_triggered': return '#007AFF';
      case 'workflow_started': return '#34C759';
      case 'workflow_completed': return '#34C759';
      case 'workflow_failed': return '#FF3B30';
      case 'action_executed': return '#FF9500';
      case 'system_alert': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  const getEventIcon = (type: string): string => {
    switch (type) {
      case 'rule_triggered': return '⚡';
      case 'workflow_started': return '🚀';
      case 'workflow_completed': return '✅';
      case 'workflow_failed': return '❌';
      case 'action_executed': return '🔧';
      case 'system_alert': return '⚠️';
      default: return '📋';
    }
  };

  return (
    <TouchableOpacity
      style={styles.eventCard}
      onPress={() => onViewDetails(event)}
      activeOpacity={0.7}
    >
      <View style={styles.eventHeader}>
        <View style={styles.eventInfo}>
          <Text style={styles.eventIcon}>{getEventIcon(event.type)}</Text>
          <View style={styles.eventDetails}>
            <Text style={styles.eventType}>{event.type.replace('_', ' ').toUpperCase()}</Text>
            <Text style={styles.eventSource}>Source: {event.source}</Text>
          </View>
        </View>
        <View style={[styles.eventTypeBadge, { backgroundColor: getEventTypeColor(event.type) }]}>
          <Text style={styles.eventTypeBadgeText}>{event.processed ? 'PROCESSED' : 'PENDING'}</Text>
        </View>
      </View>
      
      <Text style={styles.eventTimestamp}>
        {new Date(event.timestamp).toLocaleString()}
      </Text>
    </TouchableOpacity>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

export function AIAutomationDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'workflows' | 'events'>('overview');
  const [rules, setRules] = useState<AIAutomationRule[]>([]);
  const [workflows, setWorkflows] = useState<AIWorkflowOrchestration[]>([]);
  const [events, setEvents] = useState<AIAutomationEvent[]>([]);
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
      aiAutomationOrchestrator.on('automationRuleCreated', () => refreshData());
      aiAutomationOrchestrator.on('automationRuleUpdated', () => refreshData());
      aiAutomationOrchestrator.on('workflowStarted', () => refreshData());
      aiAutomationOrchestrator.on('workflowCompleted', () => refreshData());
      aiAutomationOrchestrator.on('workflowFailed', () => refreshData());

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
      const rulesData = aiAutomationOrchestrator.getAutomationRules();
      const workflowsData = aiAutomationOrchestrator.getWorkflows();
      
      setRules(rulesData);
      setWorkflows(workflowsData);
      
      // Simulate events (in real implementation, these would come from the orchestrator)
      const simulatedEvents: AIAutomationEvent[] = [
        {
          id: 'event_1',
          type: 'rule_triggered',
          source: 'auto_retrain_on_performance_degradation',
          data: { modelId: 'sentiment_analyzer', accuracy: 0.75 },
          timestamp: Date.now() - 1000,
          processed: true,
        },
        {
          id: 'event_2',
          type: 'workflow_started',
          source: 'model_retraining_workflow',
          data: { workflowId: 'workflow_1' },
          timestamp: Date.now() - 2000,
          processed: true,
        },
        {
          id: 'event_3',
          type: 'action_executed',
          source: 'auto_deploy_on_improvement',
          data: { action: 'deploy_model', modelId: 'demand_forecaster' },
          timestamp: Date.now() - 3000,
          processed: false,
        },
      ];
      
      setEvents(simulatedEvents);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleToggleRule = useCallback((rule: AIAutomationRule) => {
    const success = aiAutomationOrchestrator.updateAutomationRule(rule.id, { enabled: !rule.enabled });
    if (success) {
      Alert.alert('Success', `Rule ${rule.enabled ? 'disabled' : 'enabled'} successfully`);
      refreshData();
    } else {
      Alert.alert('Error', 'Failed to update rule');
    }
  }, [refreshData]);

  const handleEditRule = useCallback((rule: AIAutomationRule) => {
    Alert.alert('Edit Rule', `Edit functionality for rule: ${rule.name}`);
  }, []);

  const handleDeleteRule = useCallback((rule: AIAutomationRule) => {
    Alert.alert(
      'Delete Rule',
      `Are you sure you want to delete the rule "${rule.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Delete',
          style: 'destructive',
          onPress: () => {
            const success = aiAutomationOrchestrator.deleteAutomationRule(rule.id);
            if (success) {
              Alert.alert('Success', 'Rule deleted successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to delete rule');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleExecuteWorkflow = useCallback(async (workflow: AIWorkflowOrchestration) => {
    setIsLoading(true);
    try {
      const success = await aiAutomationOrchestrator.executeWorkflow(workflow.id);
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

  const handlePauseWorkflow = useCallback((workflow: AIWorkflowOrchestration) => {
    Alert.alert('Pause Workflow', `Pause functionality for workflow: ${workflow.name}`);
  }, []);

  const handleViewWorkflowDetails = useCallback((workflow: AIWorkflowOrchestration) => {
    Alert.alert(
      'Workflow Details',
      `${workflow.name}\n\nDescription: ${workflow.description}\nStatus: ${workflow.status}\nSteps: ${workflow.steps.length}\nTriggers: ${workflow.triggers.length}`
    );
  }, []);

  const handleViewEventDetails = useCallback((event: AIAutomationEvent) => {
    Alert.alert(
      'Event Details',
      `Type: ${event.type}\nSource: ${event.source}\nTimestamp: ${new Date(event.timestamp).toLocaleString()}\nProcessed: ${event.processed ? 'Yes' : 'No'}\nData: ${JSON.stringify(event.data, null, 2)}`
    );
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
    const stats = aiAutomationOrchestrator.getSystemStats();
    const recentEvents = events.slice(0, 5);
    const activeRules = rules.filter(rule => rule.enabled);
    const runningWorkflows = workflows.filter(workflow => workflow.execution.status === 'running');

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
          <Text style={styles.sectionTitle}>Automation Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalRules}</Text>
              <Text style={styles.statLabel}>Total Rules</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeRules}</Text>
              <Text style={styles.statLabel}>Active Rules</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalWorkflows}</Text>
              <Text style={styles.statLabel}>Workflows</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeWorkflows}</Text>
              <Text style={styles.statLabel}>Active</Text>
            </View>
          </View>
        </View>

        {/* Active Rules */}
        {activeRules.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Active Automation Rules</Text>
            {activeRules.slice(0, 3).map(rule => (
              <RuleCard
                key={rule.id}
                rule={rule}
                onToggle={handleToggleRule}
                onEdit={handleEditRule}
                onDelete={handleDeleteRule}
              />
            ))}
          </View>
        )}

        {/* Running Workflows */}
        {runningWorkflows.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Running Workflows</Text>
            {runningWorkflows.map(workflow => (
              <WorkflowCard
                key={workflow.id}
                workflow={workflow}
                onExecute={handleExecuteWorkflow}
                onPause={handlePauseWorkflow}
                onViewDetails={handleViewWorkflowDetails}
              />
            ))}
          </View>
        )}

        {/* Recent Events */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Events</Text>
          {recentEvents.length > 0 ? (
            recentEvents.map(event => (
              <EventCard
                key={event.id}
                event={event}
                onViewDetails={handleViewEventDetails}
              />
            ))
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>No recent events</Text>
            </View>
          )}
        </View>

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
              title="⚡ View Rules"
              onPress={() => handleTabChange('rules')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="🚀 View Workflows"
              onPress={() => handleTabChange('workflows')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderRulesTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Rules</Text>
        {rules.length > 0 ? (
          rules.map(rule => (
            <RuleCard
              key={rule.id}
              rule={rule}
              onToggle={handleToggleRule}
              onEdit={handleEditRule}
              onDelete={handleDeleteRule}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No automation rules configured</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderWorkflowsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Workflow Orchestration</Text>
        {workflows.length > 0 ? (
          workflows.map(workflow => (
            <WorkflowCard
              key={workflow.id}
              workflow={workflow}
              onExecute={handleExecuteWorkflow}
              onPause={handlePauseWorkflow}
              onViewDetails={handleViewWorkflowDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No workflows configured</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderEventsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Events</Text>
        {events.length > 0 ? (
          events.map(event => (
            <EventCard
              key={event.id}
              event={event}
              onViewDetails={handleViewEventDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No events available</Text>
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
        <Text style={styles.headerTitle}>AI Automation & Orchestration</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Automation Rules & Workflow Management
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('rules', 'Rules')}
        {renderTabButton('workflows', 'Workflows')}
        {renderTabButton('events', 'Events')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'rules' && renderRulesTab()}
        {activeTab === 'workflows' && renderWorkflowsTab()}
        {activeTab === 'events' && renderEventsTab()}
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
  ruleCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  ruleHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  ruleInfo: {
    flex: 1,
  },
  ruleName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  ruleDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  ruleControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  priorityBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  ruleDetails: {
    marginBottom: 12,
  },
  ruleDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  ruleActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  ruleActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  workflowCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
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
  executionBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginLeft: 8,
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
  eventCard: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  eventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  eventInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  eventIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  eventDetails: {
    flex: 1,
  },
  eventType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  eventSource: {
    fontSize: 12,
    color: '#666',
  },
  eventTypeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  eventTypeBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  eventTimestamp: {
    fontSize: 12,
    color: '#666',
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

export default AIAutomationDashboard;

