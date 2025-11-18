/**
 * @fileoverview Comprehensive AI system demo component
 * @author Blaze AI Team
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import AIChatInterface from '../ai/ai-chat-interface';
import {
  AIModel,
  AISystemConfig,
  AIUserPreferences,
  AITask,
  AIWorkflowExecution,
  AIEvent,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DemoSection {
  id: string;
  title: string;
  isExpanded: boolean;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * Comprehensive AI system demo component
 * Showcases all AI features including chat, model management, and configuration
 */
export function AISystemDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const [activeTab, setActiveTab] = useState<'chat' | 'management' | 'monitoring'>('chat');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [newModelForm, setNewModelForm] = useState({
    name: '',
    description: '',
    modelType: 'language_model' as const,
    provider: 'custom' as const,
    version: '1.0',
  });
  const [systemConfigForm, setSystemConfigForm] = useState({
    maxConcurrentRequests: '10',
    requestTimeout: '30000',
    retryAttempts: '3',
  });

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  const handleAddModel = useCallback(async () => {
    if (!newModelForm.name.trim() || !newModelForm.description.trim()) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      const modelId = await ai.addModel({
        name: newModelForm.name,
        description: newModelForm.description,
        config: {
          modelId: newModelForm.name.toLowerCase().replace(/\s+/g, '-'),
          modelType: newModelForm.modelType,
          provider: newModelForm.provider,
          version: newModelForm.version,
        },
        status: 'ready',
        metrics: {
          accuracy: 0.9,
          precision: 0.88,
          recall: 0.87,
          f1Score: 0.88,
          latency: 1500,
          throughput: 80,
          memoryUsage: 256,
          cpuUsage: 20,
          lastUpdated: Date.now(),
        },
        isEnabled: true,
      });

      Alert.alert('Success', `Model added with ID: ${modelId}`);
      setNewModelForm({
        name: '',
        description: '',
        modelType: 'language_model',
        provider: 'custom',
        version: '1.0',
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to add model');
    }
  }, [newModelForm, ai]);

  const handleUpdateSystemConfig = useCallback(async () => {
    try {
      const config: Partial<AISystemConfig> = {
        maxConcurrentRequests: parseInt(systemConfigForm.maxConcurrentRequests, 10),
        requestTimeout: parseInt(systemConfigForm.requestTimeout, 10),
        retryAttempts: parseInt(systemConfigForm.retryAttempts, 10),
      };

      await ai.updateSystemConfig(config);
      Alert.alert('Success', 'System configuration updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to update system configuration');
    }
  }, [systemConfigForm, ai]);

  const handleCleanup = useCallback(async () => {
    try {
      await ai.cleanup();
      Alert.alert('Success', 'Cleanup completed');
    } catch (error) {
      Alert.alert('Error', 'Failed to cleanup');
    }
  }, [ai]);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string): JSX.Element => (
    <TouchableOpacity
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      onPress={() => handleTabChange(tab)}
    >
      <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  const renderSectionHeader = (sectionId: string, title: string): JSX.Element => (
    <TouchableOpacity
      style={styles.sectionHeader}
      onPress={() => toggleSection(sectionId)}
    >
      <Text style={styles.sectionTitle}>{title}</Text>
      <Text style={styles.expandIcon}>
        {expandedSections.has(sectionId) ? '▼' : '▶'}
      </Text>
    </TouchableOpacity>
  );

  const renderOverviewSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('overview', 'System Overview')}
      {expandedSections.has('overview') && (
        <View style={styles.sectionContent}>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Status</Text>
              <Text style={styles.overviewCardValue}>
                {ai.isInitialized ? '🟢 Active' : '🔴 Inactive'}
              </Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Models</Text>
              <Text style={styles.overviewCardValue}>{ai.models.length}</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Active Tasks</Text>
              <Text style={styles.overviewCardValue}>{ai.activeTasks.length}</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Executions</Text>
              <Text style={styles.overviewCardValue}>{ai.activeExecutions.length}</Text>
            </View>
          </View>

          <View style={styles.overviewActions}>
            <AccessibleButton
              accessibilityLabel="Initialize AI system"
              onPress={() => ai.initialize()}
              disabled={ai.isInitialized}
              style={[styles.actionButton, ai.isInitialized && styles.actionButtonDisabled]}
            >
              <Text style={styles.actionButtonText}>
                {ai.isInitialized ? 'Initialized' : 'Initialize'}
              </Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Refresh data"
              onPress={ai.refreshData}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Refresh</Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Cleanup system"
              onPress={handleCleanup}
              style={[styles.actionButton, styles.actionButtonWarning]}
            >
              <Text style={styles.actionButtonText}>Cleanup</Text>
            </AccessibleButton>
          </View>
        </View>
      )}
    </View>
  );

  const renderModelManagementSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('models', 'Model Management')}
      {expandedSections.has('models') && (
        <View style={styles.sectionContent}>
          <View style={styles.addModelForm}>
            <Text style={styles.formTitle}>Add New Model</Text>
            <TextInput
              style={styles.textInput}
              placeholder="Model name"
              value={newModelForm.name}
              onChangeText={(text) => setNewModelForm(prev => ({ ...prev, name: text }))}
            />
            <TextInput
              style={styles.textInput}
              placeholder="Description"
              value={newModelForm.description}
              onChangeText={(text) => setNewModelForm(prev => ({ ...prev, description: text }))}
              multiline
            />
            <AccessibleButton
              accessibilityLabel="Add model"
              onPress={handleAddModel}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Add Model</Text>
            </AccessibleButton>
          </View>

          <View style={styles.modelsList}>
            <Text style={styles.listTitle}>Available Models</Text>
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
                </View>
                <View style={styles.modelActions}>
                  <AccessibleButton
                    accessibilityLabel={`Toggle ${model.name} model`}
                    onPress={() => ai.updateModel(model.id, { isEnabled: !model.isEnabled })}
                    style={[styles.smallButton, model.isEnabled ? styles.disableButton : styles.enableButton]}
                  >
                    <Text style={styles.smallButtonText}>
                      {model.isEnabled ? 'Disable' : 'Enable'}
                    </Text>
                  </AccessibleButton>
                  <AccessibleButton
                    accessibilityLabel={`Remove ${model.name} model`}
                    onPress={() => ai.removeModel(model.id)}
                    style={[styles.smallButton, styles.removeButton]}
                  >
                    <Text style={styles.smallButtonText}>Remove</Text>
                  </AccessibleButton>
                </View>
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );

  const renderSystemConfigSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('config', 'System Configuration')}
      {expandedSections.has('config') && (
        <View style={styles.sectionContent}>
          <View style={styles.configForm}>
            <Text style={styles.formTitle}>System Settings</Text>
            
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Max Concurrent Requests:</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.maxConcurrentRequests}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, maxConcurrentRequests: text }))}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Request Timeout (ms):</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.requestTimeout}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, requestTimeout: text }))}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Retry Attempts:</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.retryAttempts}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, retryAttempts: text }))}
                keyboardType="numeric"
              />
            </View>

            <AccessibleButton
              accessibilityLabel="Update system configuration"
              onPress={handleUpdateSystemConfig}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Update Config</Text>
            </AccessibleButton>
          </View>

          {ai.systemConfig && (
            <View style={styles.currentConfig}>
              <Text style={styles.configTitle}>Current Configuration</Text>
              <View style={styles.configGrid}>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Default Model</Text>
                  <Text style={styles.configItemValue}>{ai.systemConfig.defaultModel}</Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Max Requests/Min</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.rateLimiting.maxRequestsPerMinute}
                  </Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Caching</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.caching.enabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Monitoring</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.monitoring.enabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
              </View>
            </View>
          )}
        </View>
      )}
    </View>
  );

  const renderMonitoringSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('monitoring', 'System Monitoring')}
      {expandedSections.has('monitoring') && (
        <View style={styles.sectionContent}>
          <View style={styles.monitoringGrid}>
            <View style={styles.monitoringCard}>
              <Text style={styles.monitoringCardTitle}>Active Tasks</Text>
              <ScrollView style={styles.monitoringList}>
                {ai.activeTasks.map(task => (
                  <View key={task.id} style={styles.monitoringItem}>
                    <Text style={styles.monitoringItemTitle}>{task.type}</Text>
                    <Text style={styles.monitoringItemSubtitle}>
                      Progress: {task.progress}% | Status: {task.status}
                    </Text>
                  </View>
                ))}
                {ai.activeTasks.length === 0 && (
                  <Text style={styles.emptyListText}>No active tasks</Text>
                )}
              </ScrollView>
            </View>

            <View style={styles.monitoringCard}>
              <Text style={styles.monitoringCardTitle}>Recent Events</Text>
              <ScrollView style={styles.monitoringList}>
                {ai.recentEvents.slice(0, 10).map(event => (
                  <View key={event.id} style={styles.monitoringItem}>
                    <Text style={styles.monitoringItemTitle}>{event.type}</Text>
                    <Text style={styles.monitoringItemSubtitle}>
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </Text>
                  </View>
                ))}
                {ai.recentEvents.length === 0 && (
                  <Text style={styles.emptyListText}>No recent events</Text>
                )}
              </ScrollView>
            </View>
          </View>
        </View>
      )}
    </View>
  );

  const renderManagementTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {renderOverviewSection()}
      {renderModelManagementSection()}
      {renderSystemConfigSection()}
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {renderMonitoringSection()}
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Blaze AI System Demo</Text>
        <Text style={styles.headerSubtitle}>
          Advanced Machine Learning Integration
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('chat', 'AI Chat')}
        {renderTabButton('management', 'Management')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'chat' && <AIChatInterface />}
        {activeTab === 'management' && renderManagementTab()}
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
    fontSize: 16,
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
    overflow: 'hidden',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  expandIcon: {
    fontSize: 16,
    color: '#666',
  },
  sectionContent: {
    padding: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  overviewCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  overviewCardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  overviewCardValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  overviewActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  actionButtonDisabled: {
    backgroundColor: '#ccc',
  },
  actionButtonWarning: {
    backgroundColor: '#FF6B6B',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  addModelForm: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  formTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
    backgroundColor: '#ffffff',
  },
  modelsList: {
    marginTop: 20,
  },
  listTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
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
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginLeft: 8,
  },
  enableButton: {
    backgroundColor: '#4CAF50',
  },
  disableButton: {
    backgroundColor: '#FF9800',
  },
  removeButton: {
    backgroundColor: '#F44336',
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  configForm: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  configRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  configLabel: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  configInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 8,
    fontSize: 14,
    width: 100,
    backgroundColor: '#ffffff',
    textAlign: 'center',
  },
  currentConfig: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
  },
  configTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  configGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  configItem: {
    width: '48%',
    marginBottom: 12,
  },
  configItemLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  configItemValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  monitoringGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  monitoringCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    overflow: 'hidden',
  },
  monitoringCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    padding: 16,
    backgroundColor: '#e9ecef',
    borderBottomWidth: 1,
    borderBottomColor: '#dee2e6',
  },
  monitoringList: {
    maxHeight: 200,
    padding: 16,
  },
  monitoringItem: {
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  monitoringItemTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  monitoringItemSubtitle: {
    fontSize: 12,
    color: '#666',
  },
  emptyListText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
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
  },
});

// ============================================================================
// EXPORTS
// ============================================================================

export default AISystemDemo;
 * @fileoverview Comprehensive AI system demo component
 * @author Blaze AI Team
 */

import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  Switch,
  TextInput,
  TouchableOpacity,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAI } from '../../hooks/ai/use-ai';
import { AccessibleButton } from '../accessibility/accessible-button';
import AIChatInterface from '../ai/ai-chat-interface';
import {
  AIModel,
  AISystemConfig,
  AIUserPreferences,
  AITask,
  AIWorkflowExecution,
  AIEvent,
} from '../../lib/ai/ai-types';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface DemoSection {
  id: string;
  title: string;
  isExpanded: boolean;
}

// ============================================================================
// COMPONENT IMPLEMENTATION
// ============================================================================

/**
 * Comprehensive AI system demo component
 * Showcases all AI features including chat, model management, and configuration
 */
export function AISystemDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const ai = useAI();
  const [activeTab, setActiveTab] = useState<'chat' | 'management' | 'monitoring'>('chat');
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  const [newModelForm, setNewModelForm] = useState({
    name: '',
    description: '',
    modelType: 'language_model' as const,
    provider: 'custom' as const,
    version: '1.0',
  });
  const [systemConfigForm, setSystemConfigForm] = useState({
    maxConcurrentRequests: '10',
    requestTimeout: '30000',
    retryAttempts: '3',
  });

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const toggleSection = useCallback((sectionId: string) => {
    setExpandedSections(prev => {
      const newSet = new Set(prev);
      if (newSet.has(sectionId)) {
        newSet.delete(sectionId);
      } else {
        newSet.add(sectionId);
      }
      return newSet;
    });
  }, []);

  const handleAddModel = useCallback(async () => {
    if (!newModelForm.name.trim() || !newModelForm.description.trim()) {
      Alert.alert('Error', 'Please fill in all required fields');
      return;
    }

    try {
      const modelId = await ai.addModel({
        name: newModelForm.name,
        description: newModelForm.description,
        config: {
          modelId: newModelForm.name.toLowerCase().replace(/\s+/g, '-'),
          modelType: newModelForm.modelType,
          provider: newModelForm.provider,
          version: newModelForm.version,
        },
        status: 'ready',
        metrics: {
          accuracy: 0.9,
          precision: 0.88,
          recall: 0.87,
          f1Score: 0.88,
          latency: 1500,
          throughput: 80,
          memoryUsage: 256,
          cpuUsage: 20,
          lastUpdated: Date.now(),
        },
        isEnabled: true,
      });

      Alert.alert('Success', `Model added with ID: ${modelId}`);
      setNewModelForm({
        name: '',
        description: '',
        modelType: 'language_model',
        provider: 'custom',
        version: '1.0',
      });
    } catch (error) {
      Alert.alert('Error', 'Failed to add model');
    }
  }, [newModelForm, ai]);

  const handleUpdateSystemConfig = useCallback(async () => {
    try {
      const config: Partial<AISystemConfig> = {
        maxConcurrentRequests: parseInt(systemConfigForm.maxConcurrentRequests, 10),
        requestTimeout: parseInt(systemConfigForm.requestTimeout, 10),
        retryAttempts: parseInt(systemConfigForm.retryAttempts, 10),
      };

      await ai.updateSystemConfig(config);
      Alert.alert('Success', 'System configuration updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to update system configuration');
    }
  }, [systemConfigForm, ai]);

  const handleCleanup = useCallback(async () => {
    try {
      await ai.cleanup();
      Alert.alert('Success', 'Cleanup completed');
    } catch (error) {
      Alert.alert('Error', 'Failed to cleanup');
    }
  }, [ai]);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string): JSX.Element => (
    <TouchableOpacity
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      onPress={() => handleTabChange(tab)}
    >
      <Text style={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}>
        {label}
      </Text>
    </TouchableOpacity>
  );

  const renderSectionHeader = (sectionId: string, title: string): JSX.Element => (
    <TouchableOpacity
      style={styles.sectionHeader}
      onPress={() => toggleSection(sectionId)}
    >
      <Text style={styles.sectionTitle}>{title}</Text>
      <Text style={styles.expandIcon}>
        {expandedSections.has(sectionId) ? '▼' : '▶'}
      </Text>
    </TouchableOpacity>
  );

  const renderOverviewSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('overview', 'System Overview')}
      {expandedSections.has('overview') && (
        <View style={styles.sectionContent}>
          <View style={styles.overviewGrid}>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Status</Text>
              <Text style={styles.overviewCardValue}>
                {ai.isInitialized ? '🟢 Active' : '🔴 Inactive'}
              </Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Models</Text>
              <Text style={styles.overviewCardValue}>{ai.models.length}</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Active Tasks</Text>
              <Text style={styles.overviewCardValue}>{ai.activeTasks.length}</Text>
            </View>
            <View style={styles.overviewCard}>
              <Text style={styles.overviewCardTitle}>Executions</Text>
              <Text style={styles.overviewCardValue}>{ai.activeExecutions.length}</Text>
            </View>
          </View>

          <View style={styles.overviewActions}>
            <AccessibleButton
              accessibilityLabel="Initialize AI system"
              onPress={() => ai.initialize()}
              disabled={ai.isInitialized}
              style={[styles.actionButton, ai.isInitialized && styles.actionButtonDisabled]}
            >
              <Text style={styles.actionButtonText}>
                {ai.isInitialized ? 'Initialized' : 'Initialize'}
              </Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Refresh data"
              onPress={ai.refreshData}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Refresh</Text>
            </AccessibleButton>

            <AccessibleButton
              accessibilityLabel="Cleanup system"
              onPress={handleCleanup}
              style={[styles.actionButton, styles.actionButtonWarning]}
            >
              <Text style={styles.actionButtonText}>Cleanup</Text>
            </AccessibleButton>
          </View>
        </View>
      )}
    </View>
  );

  const renderModelManagementSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('models', 'Model Management')}
      {expandedSections.has('models') && (
        <View style={styles.sectionContent}>
          <View style={styles.addModelForm}>
            <Text style={styles.formTitle}>Add New Model</Text>
            <TextInput
              style={styles.textInput}
              placeholder="Model name"
              value={newModelForm.name}
              onChangeText={(text) => setNewModelForm(prev => ({ ...prev, name: text }))}
            />
            <TextInput
              style={styles.textInput}
              placeholder="Description"
              value={newModelForm.description}
              onChangeText={(text) => setNewModelForm(prev => ({ ...prev, description: text }))}
              multiline
            />
            <AccessibleButton
              accessibilityLabel="Add model"
              onPress={handleAddModel}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Add Model</Text>
            </AccessibleButton>
          </View>

          <View style={styles.modelsList}>
            <Text style={styles.listTitle}>Available Models</Text>
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
                </View>
                <View style={styles.modelActions}>
                  <AccessibleButton
                    accessibilityLabel={`Toggle ${model.name} model`}
                    onPress={() => ai.updateModel(model.id, { isEnabled: !model.isEnabled })}
                    style={[styles.smallButton, model.isEnabled ? styles.disableButton : styles.enableButton]}
                  >
                    <Text style={styles.smallButtonText}>
                      {model.isEnabled ? 'Disable' : 'Enable'}
                    </Text>
                  </AccessibleButton>
                  <AccessibleButton
                    accessibilityLabel={`Remove ${model.name} model`}
                    onPress={() => ai.removeModel(model.id)}
                    style={[styles.smallButton, styles.removeButton]}
                  >
                    <Text style={styles.smallButtonText}>Remove</Text>
                  </AccessibleButton>
                </View>
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );

  const renderSystemConfigSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('config', 'System Configuration')}
      {expandedSections.has('config') && (
        <View style={styles.sectionContent}>
          <View style={styles.configForm}>
            <Text style={styles.formTitle}>System Settings</Text>
            
            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Max Concurrent Requests:</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.maxConcurrentRequests}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, maxConcurrentRequests: text }))}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Request Timeout (ms):</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.requestTimeout}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, requestTimeout: text }))}
                keyboardType="numeric"
              />
            </View>

            <View style={styles.configRow}>
              <Text style={styles.configLabel}>Retry Attempts:</Text>
              <TextInput
                style={styles.configInput}
                value={systemConfigForm.retryAttempts}
                onChangeText={(text) => setSystemConfigForm(prev => ({ ...prev, retryAttempts: text }))}
                keyboardType="numeric"
              />
            </View>

            <AccessibleButton
              accessibilityLabel="Update system configuration"
              onPress={handleUpdateSystemConfig}
              style={styles.actionButton}
            >
              <Text style={styles.actionButtonText}>Update Config</Text>
            </AccessibleButton>
          </View>

          {ai.systemConfig && (
            <View style={styles.currentConfig}>
              <Text style={styles.configTitle}>Current Configuration</Text>
              <View style={styles.configGrid}>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Default Model</Text>
                  <Text style={styles.configItemValue}>{ai.systemConfig.defaultModel}</Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Max Requests/Min</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.rateLimiting.maxRequestsPerMinute}
                  </Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Caching</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.caching.enabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
                <View style={styles.configItem}>
                  <Text style={styles.configItemLabel}>Monitoring</Text>
                  <Text style={styles.configItemValue}>
                    {ai.systemConfig.monitoring.enabled ? 'Enabled' : 'Disabled'}
                  </Text>
                </View>
              </View>
            </View>
          )}
        </View>
      )}
    </View>
  );

  const renderMonitoringSection = (): JSX.Element => (
    <View style={styles.section}>
      {renderSectionHeader('monitoring', 'System Monitoring')}
      {expandedSections.has('monitoring') && (
        <View style={styles.sectionContent}>
          <View style={styles.monitoringGrid}>
            <View style={styles.monitoringCard}>
              <Text style={styles.monitoringCardTitle}>Active Tasks</Text>
              <ScrollView style={styles.monitoringList}>
                {ai.activeTasks.map(task => (
                  <View key={task.id} style={styles.monitoringItem}>
                    <Text style={styles.monitoringItemTitle}>{task.type}</Text>
                    <Text style={styles.monitoringItemSubtitle}>
                      Progress: {task.progress}% | Status: {task.status}
                    </Text>
                  </View>
                ))}
                {ai.activeTasks.length === 0 && (
                  <Text style={styles.emptyListText}>No active tasks</Text>
                )}
              </ScrollView>
            </View>

            <View style={styles.monitoringCard}>
              <Text style={styles.monitoringCardTitle}>Recent Events</Text>
              <ScrollView style={styles.monitoringList}>
                {ai.recentEvents.slice(0, 10).map(event => (
                  <View key={event.id} style={styles.monitoringItem}>
                    <Text style={styles.monitoringItemTitle}>{event.type}</Text>
                    <Text style={styles.monitoringItemSubtitle}>
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </Text>
                  </View>
                ))}
                {ai.recentEvents.length === 0 && (
                  <Text style={styles.emptyListText}>No recent events</Text>
                )}
              </ScrollView>
            </View>
          </View>
        </View>
      )}
    </View>
  );

  const renderManagementTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {renderOverviewSection()}
      {renderModelManagementSection()}
      {renderSystemConfigSection()}
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {renderMonitoringSection()}
    </ScrollView>
  );

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Blaze AI System Demo</Text>
        <Text style={styles.headerSubtitle}>
          Advanced Machine Learning Integration
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('chat', 'AI Chat')}
        {renderTabButton('management', 'Management')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'chat' && <AIChatInterface />}
        {activeTab === 'management' && renderManagementTab()}
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
    fontSize: 16,
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
    overflow: 'hidden',
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  expandIcon: {
    fontSize: 16,
    color: '#666',
  },
  sectionContent: {
    padding: 16,
  },
  overviewGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 20,
  },
  overviewCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  overviewCardTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginBottom: 8,
  },
  overviewCardValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
  },
  overviewActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    backgroundColor: '#007AFF',
    borderRadius: 8,
    minWidth: 100,
    alignItems: 'center',
  },
  actionButtonDisabled: {
    backgroundColor: '#ccc',
  },
  actionButtonWarning: {
    backgroundColor: '#FF6B6B',
  },
  actionButtonText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
  addModelForm: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  formTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 12,
    fontSize: 14,
    marginBottom: 12,
    backgroundColor: '#ffffff',
  },
  modelsList: {
    marginTop: 20,
  },
  listTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
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
    flexDirection: 'row',
    justifyContent: 'flex-end',
  },
  smallButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 6,
    marginLeft: 8,
  },
  enableButton: {
    backgroundColor: '#4CAF50',
  },
  disableButton: {
    backgroundColor: '#FF9800',
  },
  removeButton: {
    backgroundColor: '#F44336',
  },
  smallButtonText: {
    color: '#ffffff',
    fontSize: 12,
    fontWeight: '500',
  },
  configForm: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 20,
  },
  configRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  configLabel: {
    flex: 1,
    fontSize: 14,
    color: '#333',
    fontWeight: '500',
  },
  configInput: {
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 6,
    padding: 8,
    fontSize: 14,
    width: 100,
    backgroundColor: '#ffffff',
    textAlign: 'center',
  },
  currentConfig: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
  },
  configTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  configGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  configItem: {
    width: '48%',
    marginBottom: 12,
  },
  configItemLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  configItemValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
  },
  monitoringGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  monitoringCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
    overflow: 'hidden',
  },
  monitoringCardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    padding: 16,
    backgroundColor: '#e9ecef',
    borderBottomWidth: 1,
    borderBottomColor: '#dee2e6',
  },
  monitoringList: {
    maxHeight: 200,
    padding: 16,
  },
  monitoringItem: {
    marginBottom: 12,
    paddingBottom: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  monitoringItemTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    marginBottom: 4,
  },
  monitoringItemSubtitle: {
    fontSize: 12,
    color: '#666',
  },
  emptyListText: {
    fontSize: 14,
    color: '#999',
    textAlign: 'center',
    fontStyle: 'italic',
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
  },
});

// ============================================================================
// EXPORTS
// ============================================================================

export default AISystemDemo;


