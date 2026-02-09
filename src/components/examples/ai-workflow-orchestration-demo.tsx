/**
 * @fileoverview AI workflow orchestration demo component
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
  TouchableOpacity,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIWorkflowAutomationDashboard } from '../dashboard/ai-workflow-automation-dashboard';
import { AIWorkflowOrchestrationIntegrationService } from '../../lib/ai/ai-workflow-orchestration-integration';
import {
  AIWorkflow,
  AIWorkflowStep,
  AITask,
  AIRequest,
  AIWorkflowExecution,
  AITaskType,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DemoTask {
  id: string;
  name: string;
  type: AITaskType;
  description: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimatedDuration: number;
}

interface DemoWorkflowStep extends AIWorkflowStep {
  tasks?: DemoTask[];
}

interface DemoWorkflow {
  id: string;
  name: string;
  description: string;
  steps: DemoWorkflowStep[];
  isActive: boolean;
  executionCount: number;
  lastExecuted?: Date;
}

interface DemoMetrics {
  totalWorkflows: number;
  activeWorkflows: number;
  totalExecutions: number;
  averageExecutionTime: number;
  successRate: number;
  resourceUtilization: number;
  automationEffectiveness: number;
  orchestrationEfficiency: number;
}

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_WORKFLOWS: DemoWorkflow[] = [
  {
    id: 'workflow_1',
    name: 'Content Generation Pipeline',
    description: 'Automated content creation with AI-powered writing, editing, and publishing',
    steps: [
      {
        id: 'step_1',
        name: 'Content Planning',
        taskType: AITaskType.TEXT_GENERATION,
        description: 'Generate content outline and structure',
        modelId: 'gpt-4',
        inputMapping: { prompt: 'content_prompt' },
        outputMapping: { outline: 'content_outline' },
        dependencies: [],
        timeout: 30000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 512, cpu: 30 } },
        tasks: [
          {
            id: 'task_1_1',
            name: 'Topic Research',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Research trending topics and keywords',
            priority: 'high',
            estimatedDuration: 30000,
          },
          {
            id: 'task_1_2',
            name: 'Outline Generation',
            type: AITaskType.TEXT_GENERATION,
            description: 'Create content outline using AI',
            priority: 'high',
            estimatedDuration: 15000,
          },
        ],
      },
      {
        id: 'step_2',
        name: 'Content Creation',
        taskType: AITaskType.TEXT_GENERATION,
        description: 'Generate initial content using AI models',
        modelId: 'gpt-4',
        inputMapping: { outline: 'content_outline' },
        outputMapping: { content: 'generated_content' },
        dependencies: ['step_1'],
        timeout: 60000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 1024, cpu: 60 } },
        tasks: [
          {
            id: 'task_2_1',
            name: 'Draft Writing',
            type: AITaskType.TEXT_GENERATION,
            description: 'Write initial content draft',
            priority: 'high',
            estimatedDuration: 60000,
          },
          {
            id: 'task_2_2',
            name: 'Content Enhancement',
            type: AITaskType.TEXT_COMPLETION,
            description: 'Enhance content with additional details',
            priority: 'medium',
            estimatedDuration: 45000,
          },
        ],
      },
      {
        id: 'step_3',
        name: 'Quality Assurance',
        taskType: AITaskType.TEXT_CLASSIFICATION,
        description: 'Review and validate content quality',
        modelId: 'gpt-4',
        inputMapping: { content: 'generated_content' },
        outputMapping: { quality_score: 'content_quality' },
        dependencies: ['step_2'],
        timeout: 30000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'medium', resourceRequirements: { memory: 512, cpu: 40 } },
        tasks: [
          {
            id: 'task_3_1',
            name: 'Grammar Check',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Check grammar and spelling',
            priority: 'medium',
            estimatedDuration: 20000,
          },
          {
            id: 'task_3_2',
            name: 'Content Review',
            type: AITaskType.TEXT_SENTIMENT_ANALYSIS,
            description: 'Review content for accuracy and relevance',
            priority: 'high',
            estimatedDuration: 30000,
          },
        ],
      },
      {
        id: 'step_4',
        name: 'Publishing',
        taskType: AITaskType.TEXT_GENERATION,
        description: 'Publish content to various platforms',
        modelId: 'gpt-4',
        inputMapping: { content: 'generated_content' },
        outputMapping: { published_urls: 'publication_links' },
        dependencies: ['step_3'],
        timeout: 45000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'low', resourceRequirements: { memory: 256, cpu: 20 } },
        tasks: [
          {
            id: 'task_4_1',
            name: 'Format Conversion',
            type: AITaskType.TEXT_GENERATION,
            description: 'Convert content to various formats',
            priority: 'low',
            estimatedDuration: 15000,
          },
          {
            id: 'task_4_2',
            name: 'Platform Publishing',
            type: AITaskType.TEXT_GENERATION,
            description: 'Publish to social media and websites',
            priority: 'low',
            estimatedDuration: 25000,
          },
        ],
      },
    ],
    isActive: true,
    executionCount: 15,
    lastExecuted: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
  },
  {
    id: 'workflow_2',
    name: 'Data Analysis Pipeline',
    description: 'Automated data collection, processing, and analysis with AI insights',
    steps: [
      {
        id: 'step_1',
        name: 'Data Collection',
        taskType: AITaskType.TEXT_CLASSIFICATION,
        description: 'Collect data from various sources',
        modelId: 'gpt-4',
        inputMapping: { sources: 'data_sources' },
        outputMapping: { raw_data: 'collected_data' },
        dependencies: [],
        timeout: 60000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 2048, cpu: 50 } },
        tasks: [
          {
            id: 'task_1_1',
            name: 'API Data Fetch',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Fetch data from external APIs',
            priority: 'high',
            estimatedDuration: 45000,
          },
        ],
      },
      {
        id: 'step_2',
        name: 'Data Processing',
        taskType: AITaskType.TEXT_CLASSIFICATION,
        description: 'Clean and preprocess collected data',
        modelId: 'gpt-4',
        inputMapping: { raw_data: 'collected_data' },
        outputMapping: { processed_data: 'clean_data' },
        dependencies: ['step_1'],
        timeout: 90000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 4096, cpu: 80 } },
        tasks: [
          {
            id: 'task_2_1',
            name: 'Data Cleaning',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Remove duplicates and invalid data',
            priority: 'high',
            estimatedDuration: 60000,
          },
          {
            id: 'task_2_2',
            name: 'Data Transformation',
            type: AITaskType.TEXT_GENERATION,
            description: 'Transform data into required format',
            priority: 'medium',
            estimatedDuration: 90000,
          },
        ],
      },
      {
        id: 'step_3',
        name: 'AI Analysis',
        taskType: AITaskType.TEXT_SENTIMENT_ANALYSIS,
        description: 'Perform AI-powered data analysis',
        modelId: 'gpt-4',
        inputMapping: { processed_data: 'clean_data' },
        outputMapping: { insights: 'analysis_results' },
        dependencies: ['step_2'],
        timeout: 120000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 8192, cpu: 90 } },
        tasks: [
          {
            id: 'task_3_1',
            name: 'Pattern Recognition',
            type: AITaskType.CLUSTERING,
            description: 'Identify patterns and trends',
            priority: 'high',
            estimatedDuration: 120000,
          },
          {
            id: 'task_3_2',
            name: 'Insight Generation',
            type: AITaskType.TEXT_GENERATION,
            description: 'Generate actionable insights',
            priority: 'high',
            estimatedDuration: 80000,
          },
        ],
      },
    ],
    isActive: true,
    executionCount: 8,
    lastExecuted: new Date(Date.now() - 6 * 60 * 60 * 1000), // 6 hours ago
  },
  {
    id: 'workflow_3',
    name: 'Customer Support Automation',
    description: 'Automated customer support with AI-powered ticket routing and resolution',
    steps: [
      {
        id: 'step_1',
        name: 'Ticket Classification',
        taskType: AITaskType.TEXT_CLASSIFICATION,
        description: 'Classify incoming support tickets',
        modelId: 'gpt-4',
        inputMapping: { ticket: 'support_ticket' },
        outputMapping: { category: 'ticket_category' },
        dependencies: [],
        timeout: 15000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'urgent', resourceRequirements: { memory: 512, cpu: 30 } },
        tasks: [
          {
            id: 'task_1_1',
            name: 'Priority Assessment',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Assess ticket priority level',
            priority: 'urgent',
            estimatedDuration: 10000,
          },
        ],
      },
      {
        id: 'step_2',
        name: 'Auto-Resolution',
        taskType: AITaskType.TEXT_GENERATION,
        description: 'Attempt automatic ticket resolution',
        modelId: 'gpt-4',
        inputMapping: { ticket: 'support_ticket', category: 'ticket_category' },
        outputMapping: { response: 'auto_response' },
        dependencies: ['step_1'],
        timeout: 30000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'high', resourceRequirements: { memory: 1024, cpu: 50 } },
        tasks: [
          {
            id: 'task_2_1',
            name: 'Solution Search',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Search knowledge base for solutions',
            priority: 'high',
            estimatedDuration: 20000,
          },
          {
            id: 'task_2_2',
            name: 'Response Generation',
            type: AITaskType.TEXT_GENERATION,
            description: 'Generate automated response',
            priority: 'high',
            estimatedDuration: 15000,
          },
        ],
      },
      {
        id: 'step_3',
        name: 'Escalation',
        taskType: AITaskType.TEXT_CLASSIFICATION,
        description: 'Escalate unresolved tickets to human agents',
        modelId: 'gpt-4',
        inputMapping: { ticket: 'support_ticket', response: 'auto_response' },
        outputMapping: { agent: 'assigned_agent' },
        dependencies: ['step_2'],
        timeout: 20000,
        retryCount: 0,
        maxRetries: 3,
        isRequired: true,
        metadata: { priority: 'medium', resourceRequirements: { memory: 256, cpu: 20 } },
        tasks: [
          {
            id: 'task_3_1',
            name: 'Agent Assignment',
            type: AITaskType.TEXT_CLASSIFICATION,
            description: 'Assign ticket to appropriate agent',
            priority: 'medium',
            estimatedDuration: 10000,
          },
        ],
      },
    ],
    isActive: false,
    executionCount: 23,
    lastExecuted: new Date(Date.now() - 24 * 60 * 60 * 1000), // 1 day ago
  },
];

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * AI Workflow Orchestration Demo Component
 * Comprehensive demonstration of advanced AI workflow automation and orchestration
 */
export function AIWorkflowOrchestrationDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'workflows' | 'automation' | 'orchestration' | 'integration'>('overview');
  const [workflows, setWorkflows] = useState<DemoWorkflow[]>(DEMO_WORKFLOWS);
  const [isLoading, setIsLoading] = useState(false);
  const [executingWorkflow, setExecutingWorkflow] = useState<string | null>(null);
  const [showIntegrationDashboard, setShowIntegrationDashboard] = useState(false);
  const [showAutomationDashboard, setShowAutomationDashboard] = useState(false);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    // Initialize demo data
    initializeDemoData();
  }, []);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  const initializeDemoData = useCallback(async () => {
    setIsLoading(true);
    try {
      // Simulate initialization delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Initialize integration service with demo data
      const integrationService = AIWorkflowOrchestrationIntegrationService.getInstance();
      
      // Update workflows with real-time data
      setWorkflows(prevWorkflows => 
        prevWorkflows.map(workflow => ({
          ...workflow,
          executionCount: Math.floor(Math.random() * 50) + 1,
          lastExecuted: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000),
        }))
      );
      
    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo data');
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

  const handleExecuteWorkflow = useCallback(async (workflowId: string) => {
    setExecutingWorkflow(workflowId);
    
    try {
      const workflow = workflows.find(w => w.id === workflowId);
      if (!workflow) {
        throw new Error('Workflow not found');
      }

      // Create demo AI request
      const demoRequest: AIRequest = {
        id: 'demo_request_1',
        modelId: 'gpt-4',
        userId: 'demo_user',
        timestamp: Date.now(),
        priority: 'medium',
      };

      // Convert DemoWorkflow to AIWorkflow
      const aiWorkflow: AIWorkflow = {
        id: workflow.id,
        name: workflow.name,
        description: workflow.description,
        version: '1.0.0',
        steps: workflow.steps.map(step => ({
          id: step.id,
          name: step.name,
          description: step.description,
          taskType: step.taskType,
          modelId: step.modelId,
          inputMapping: step.inputMapping,
          outputMapping: step.outputMapping,
          dependencies: step.dependencies,
          timeout: step.timeout,
          retryCount: step.retryCount,
          maxRetries: step.maxRetries,
          isRequired: step.isRequired,
          metadata: step.metadata,
        })),
        inputSchema: {},
        outputSchema: {},
        isEnabled: workflow.isActive,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      // Execute workflow with integration service
      const integrationService = AIWorkflowOrchestrationIntegrationService.getInstance();
      const result = await integrationService.executeWorkflowWithIntegration(
        aiWorkflow,
        demoRequest,
        'demo_user'
      );

      // Update workflow execution count
      setWorkflows(prev => 
        prev.map(w => 
          w.id === workflowId 
            ? { ...w, executionCount: w.executionCount + 1, lastExecuted: new Date() }
            : w
        )
      );

      Alert.alert(
        'Success', 
        `Workflow executed successfully!\n\nExecution ID: ${result.executionId}\nDuration: ${result.totalDuration}ms\nRules Applied: ${result.automationRulesApplied.length}\nStrategy: ${result.executionStrategy}`
      );

    } catch (error) {
      Alert.alert('Error', `Failed to execute workflow: ${error}`);
    } finally {
      setExecutingWorkflow(null);
    }
  }, [workflows]);

  const handleToggleWorkflow = useCallback((workflowId: string) => {
    setWorkflows(prev => 
      prev.map(w => 
        w.id === workflowId 
          ? { ...w, isActive: !w.isActive }
          : w
      )
    );
  }, []);

  const handleShowIntegrationDashboard = useCallback(() => {
    setShowIntegrationDashboard(true);
  }, []);

  const handleShowAutomationDashboard = useCallback(() => {
    setShowAutomationDashboard(true);
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
    const metrics: DemoMetrics = {
      totalWorkflows: workflows.length,
      activeWorkflows: workflows.filter(w => w.isActive).length,
      totalExecutions: workflows.reduce((sum, w) => sum + w.executionCount, 0),
      averageExecutionTime: 2500, // Simulated
      successRate: 0.94, // Simulated
      resourceUtilization: 0.72, // Simulated
      automationEffectiveness: 0.87, // Simulated
      orchestrationEfficiency: 0.91, // Simulated
    };

    return (
      <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
        {/* System Overview */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalWorkflows}</Text>
              <Text style={styles.overviewLabel}>Total Workflows</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.activeWorkflows}</Text>
              <Text style={styles.overviewLabel}>Active Workflows</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{metrics.totalExecutions}</Text>
              <Text style={styles.overviewLabel}>Total Executions</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewValue}>{(metrics.successRate * 100).toFixed(1)}%</Text>
              <Text style={styles.overviewLabel}>Success Rate</Text>
            </View>
          </View>
        </View>

        {/* Performance Metrics */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Performance Metrics</Text>
          <View style={styles.metricsGrid}>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Execution Time</Text>
              <Text style={styles.metricValue}>{metrics.averageExecutionTime}ms</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${(metrics.averageExecutionTime / 5000) * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Resource Utilization</Text>
              <Text style={styles.metricValue}>{(metrics.resourceUtilization * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.resourceUtilization * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Automation Effectiveness</Text>
              <Text style={styles.metricValue}>{(metrics.automationEffectiveness * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.automationEffectiveness * 100}%` }]} />
              </View>
            </View>
            <View style={styles.metricCard}>
              <Text style={styles.metricLabel}>Orchestration Efficiency</Text>
              <Text style={styles.metricValue}>{(metrics.orchestrationEfficiency * 100).toFixed(1)}%</Text>
              <View style={styles.metricBar}>
                <View style={[styles.metricBarFill, { width: `${metrics.orchestrationEfficiency * 100}%` }]} />
              </View>
            </View>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="🔗 Integration Dashboard"
              accessibilityLabel="Show integration dashboard"
              onPress={handleShowIntegrationDashboard}
              style={styles.actionButton}
              textStyle={styles.actionButtonText}
              variant="primary"
              size="small"
            />
            <AccessibleButton
              title="🤖 Automation Dashboard"
              accessibilityLabel="Show automation dashboard"
              onPress={handleShowAutomationDashboard}
              style={styles.actionButton}
              textStyle={styles.actionButtonText}
              variant="primary"
              size="small"
            />
            <AccessibleButton
              title={executingWorkflow === 'workflow_1' ? '⏳ Executing...' : '▶️ Execute Sample'}
              accessibilityLabel="Execute sample workflow"
              onPress={() => handleExecuteWorkflow('workflow_1')}
              style={styles.actionButton}
              textStyle={styles.actionButtonText}
              variant="primary"
              size="small"
              isDisabled={executingWorkflow === 'workflow_1'}
            />
          </View>
        </View>

        {/* Recent Activity */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Activity</Text>
          <View style={styles.activityList}>
            {workflows
              .filter(w => w.lastExecuted)
              .sort((a, b) => (b.lastExecuted?.getTime() || 0) - (a.lastExecuted?.getTime() || 0))
              .slice(0, 5)
              .map(workflow => (
                <View key={workflow.id} style={styles.activityItem}>
                  <View style={styles.activityHeader}>
                    <Text style={styles.activityTitle}>{workflow.name}</Text>
                    <Text style={styles.activityTime}>
                      {workflow.lastExecuted?.toLocaleTimeString()}
                    </Text>
                  </View>
                  <Text style={styles.activityDescription}>
                    Executed {workflow.executionCount} times
                  </Text>
                </View>
              ))}
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderWorkflowsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Available Workflows</Text>
        <View style={styles.workflowsList}>
          {workflows.map(workflow => (
            <View key={workflow.id} style={styles.workflowCard}>
              <View style={styles.workflowHeader}>
                <View style={styles.workflowInfo}>
                  <Text style={styles.workflowName}>{workflow.name}</Text>
                  <Text style={styles.workflowDescription}>{workflow.description}</Text>
                </View>
                <View style={styles.workflowControls}>
                  <Switch
                    value={workflow.isActive}
                    onValueChange={() => handleToggleWorkflow(workflow.id)}
                  />
                  <AccessibleButton
                    title={executingWorkflow === workflow.id ? '⏳' : '▶️'}
                    accessibilityLabel={`Execute workflow ${workflow.name}`}
                    onPress={() => handleExecuteWorkflow(workflow.id)}
                    style={[styles.executeButton, executingWorkflow === workflow.id && styles.executingButton]}
                    textStyle={styles.executeButtonText}
                    variant="success"
                    size="small"
                    isDisabled={executingWorkflow === workflow.id}
                  />
                </View>
              </View>
              
              <View style={styles.workflowDetails}>
                <Text style={styles.workflowDetail}>
                  Steps: {workflow.steps.length} | Tasks: {workflow.steps.reduce((sum, step) => sum + (step.tasks?.length || 0), 0)}
                </Text>
                <Text style={styles.workflowDetail}>
                  Executions: {workflow.executionCount} | Last: {workflow.lastExecuted?.toLocaleDateString() || 'Never'}
                </Text>
                <Text style={styles.workflowDetail}>
                  Status: {workflow.isActive ? '🟢 Active' : '🔴 Inactive'}
                </Text>
              </View>

              {/* Workflow Steps Preview */}
              <View style={styles.stepsPreview}>
                <Text style={styles.stepsPreviewTitle}>Workflow Steps:</Text>
                {workflow.steps.slice(0, 3).map(step => (
                  <View key={step.id} style={styles.stepPreview}>
                    <Text style={styles.stepPreviewName}>• {step.name}</Text>
                    <Text style={styles.stepPreviewType}>({step.taskType})</Text>
                  </View>
                ))}
                {workflow.steps.length > 3 && (
                  <Text style={styles.stepsPreviewMore}>... and {workflow.steps.length - 3} more</Text>
                )}
              </View>
            </View>
          ))}
        </View>
      </View>
    </ScrollView>
  );

  const renderAutomationTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Workflow Automation</Text>
        <Text style={styles.sectionDescription}>
          This tab demonstrates the AI workflow automation system. Click the button below to open the comprehensive automation dashboard.
        </Text>
        
        <AccessibleButton
          title="🤖 Open Automation Dashboard"
          accessibilityLabel="Open automation dashboard"
          onPress={handleShowAutomationDashboard}
          style={styles.primaryButton}
          textStyle={styles.primaryButtonText}
          variant="primary"
          size="large"
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Automation Features</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⚡</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Intelligent Rule Engine</Text>
              <Text style={styles.featureDescription}>
                Automatically apply rules based on workflow conditions and execution context
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔄</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Dynamic Workflow Adaptation</Text>
              <Text style={styles.featureDescription}>
                Modify workflow execution based on real-time conditions and performance metrics
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Performance Monitoring</Text>
              <Text style={styles.featureDescription}>
                Track automation effectiveness and identify optimization opportunities
              </Text>
            </View>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  const renderOrchestrationTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Task Orchestration</Text>
        <Text style={styles.sectionDescription}>
          This tab demonstrates the intelligent task orchestration system. The system automatically selects optimal execution strategies and manages resource allocation.
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Orchestration Features</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🎯</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Smart Strategy Selection</Text>
              <Text style={styles.featureDescription}>
                Automatically select the best execution strategy based on task requirements and system load
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⚖️</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Load Balancing</Text>
              <Text style={styles.featureDescription}>
                Distribute tasks across available resources for optimal performance
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📈</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Resource Optimization</Text>
              <Text style={styles.featureDescription}>
                Monitor and optimize resource usage for maximum efficiency
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Execution Strategies</Text>
        <View style={styles.strategiesPreview}>
          <View style={styles.strategyPreview}>
            <Text style={styles.strategyPreviewName}>High Priority Strategy</Text>
            <Text style={styles.strategyPreviewDesc}>Optimized for urgent tasks with resource pre-allocation</Text>
          </View>
          <View style={styles.strategyPreview}>
            <Text style={styles.strategyPreviewName}>Batch Processing Strategy</Text>
            <Text style={styles.strategyPreviewDesc}>Efficiently process multiple tasks in parallel</Text>
          </View>
          <View style={styles.strategyPreview}>
            <Text style={styles.strategyPreviewName}>Resource-Conscious Strategy</Text>
            <Text style={styles.strategyPreviewDesc}>Minimize resource usage for cost optimization</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  const renderIntegrationTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Integration</Text>
        <Text style={styles.sectionDescription}>
          This tab demonstrates the unified integration of automation and orchestration systems. Click the button below to open the comprehensive integration dashboard.
        </Text>
        
        <AccessibleButton
          title="🔗 Open Integration Dashboard"
          accessibilityLabel="Open integration dashboard"
          onPress={handleShowIntegrationDashboard}
          style={styles.primaryButton}
          textStyle={styles.primaryButtonText}
          variant="primary"
          size="large"
        />
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Integration Benefits</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🔄</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Unified Workflow Management</Text>
              <Text style={styles.featureDescription}>
                Manage both automation rules and execution strategies from a single interface
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>📊</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Comprehensive Analytics</Text>
              <Text style={styles.featureDescription}>
                Get insights into both automation effectiveness and orchestration efficiency
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⚡</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Performance Optimization</Text>
              <Text style={styles.featureDescription}>
                Automatically optimize workflows based on integrated performance data
              </Text>
            </View>
          </View>
        </View>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Real-time Monitoring</Text>
        <View style={styles.monitoringPreview}>
          <Text style={styles.monitoringText}>
            The integration dashboard provides real-time monitoring of:
          </Text>
          <View style={styles.monitoringList}>
            <Text style={styles.monitoringItem}>• Active workflow executions</Text>
            <Text style={styles.monitoringItem}>• Automation rule effectiveness</Text>
            <Text style={styles.monitoringItem}>• Resource utilization metrics</Text>
            <Text style={styles.monitoringItem}>• Performance bottlenecks</Text>
            <Text style={styles.monitoringItem}>• Optimization recommendations</Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (showIntegrationDashboard) {
    return (
      <View style={styles.fullScreen}>
        <View style={styles.dashboardHeader}>
          <AccessibleButton
            title="✕ Close"
            accessibilityLabel="Close integration dashboard"
            onPress={() => setShowIntegrationDashboard(false)}
            style={styles.closeButton}
            textStyle={styles.closeButtonText}
            variant="ghost"
            size="small"
          />
          <Text style={styles.dashboardTitle}>AI Workflow Orchestration Integration</Text>
        </View>
        <AIWorkflowAutomationDashboard />
      </View>
    );
  }

  if (showAutomationDashboard) {
    return (
      <View style={styles.fullScreen}>
        <View style={styles.dashboardHeader}>
          <AccessibleButton
            title="✕ Close"
            accessibilityLabel="Close automation dashboard"
            onPress={() => setShowAutomationDashboard(false)}
            style={styles.closeButton}
            textStyle={styles.closeButtonText}
            variant="ghost"
            size="small"
          />
          <Text style={styles.dashboardTitle}>AI Workflow Automation</Text>
        </View>
        <AIWorkflowAutomationDashboard />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Workflow Orchestration Demo</Text>
        <Text style={styles.headerSubtitle}>
          Advanced Workflow Automation & Intelligent Task Orchestration
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('workflows', 'Workflows')}
        {renderTabButton('automation', 'Automation')}
        {renderTabButton('orchestration', 'Orchestration')}
        {renderTabButton('integration', 'Integration')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'workflows' && renderWorkflowsTab()}
        {activeTab === 'automation' && renderAutomationTab()}
        {activeTab === 'orchestration' && renderOrchestrationTab()}
        {activeTab === 'integration' && renderIntegrationTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Initializing Demo...</Text>
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
    backgroundColor: '#007AFF',
    borderRadius: 8,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  primaryButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#007AFF',
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  workflowsList: {
    maxHeight: 600,
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
    marginRight: 16,
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
  executeButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#28a745',
    borderRadius: 6,
    marginLeft: 12,
  },
  executingButton: {
    backgroundColor: '#ffc107',
  },
  executeButtonText: {
    color: '#ffffff',
    fontSize: 16,
  },
  workflowDetails: {
    marginBottom: 12,
  },
  workflowDetail: {
    fontSize: 12,
    color: '#888',
    marginBottom: 4,
  },
  stepsPreview: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  stepsPreviewTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  stepPreview: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  stepPreviewName: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
  },
  stepPreviewType: {
    fontSize: 10,
    color: '#999',
    fontStyle: 'italic',
  },
  stepsPreviewMore: {
    fontSize: 12,
    color: '#999',
    fontStyle: 'italic',
    marginTop: 4,
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
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  featureDescription: {
    fontSize: 12,
    color: '#666',
    lineHeight: 18,
  },
  strategiesPreview: {
    marginTop: 8,
  },
  strategyPreview: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  strategyPreviewName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  strategyPreviewDesc: {
    fontSize: 12,
    color: '#666',
  },
  monitoringPreview: {
    marginTop: 8,
  },
  monitoringText: {
    fontSize: 14,
    color: '#333',
    marginBottom: 12,
  },
  monitoringList: {
    marginLeft: 16,
  },
  monitoringItem: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  activityList: {
    maxHeight: 200,
  },
  activityItem: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 6,
    marginBottom: 8,
  },
  activityHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  activityTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  activityTime: {
    fontSize: 12,
    color: '#888',
  },
  activityDescription: {
    fontSize: 12,
    color: '#666',
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

export default AIWorkflowOrchestrationDemo;
