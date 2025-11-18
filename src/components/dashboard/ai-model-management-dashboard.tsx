/**
 * @fileoverview AI model management dashboard component
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
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { 
  aiModelManager, 
  AIModelVersion, 
  AIModelRecommendation, 
  AIModelPerformanceMetrics,
  AIModelOptimizationResult 
} from '../../lib/ai/ai-model-manager';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface ModelCardProps {
  model: any;
  latestVersion?: AIModelVersion;
  onViewDetails: (model: any) => void;
  onDeploy: (model: any) => void;
  onTrain: (model: any) => void;
}

interface VersionCardProps {
  version: AIModelVersion;
  onDeploy: (version: AIModelVersion) => void;
  onViewMetrics: (version: AIModelVersion) => void;
}

interface RecommendationCardProps {
  recommendation: AIModelRecommendation;
  onViewDetails: (recommendation: AIModelRecommendation) => void;
  onDismiss: (recommendation: AIModelRecommendation) => void;
}

// ============================================================================
// MODEL CARD COMPONENT
// ============================================================================

const ModelCard: React.FC<ModelCardProps> = ({ model, latestVersion, onViewDetails, onDeploy, onTrain }) => {
  const getStatusColor = (status?: string): string => {
    switch (status) {
      case 'deployed': return '#34C759';
      case 'trained': return '#007AFF';
      case 'training': return '#FF9500';
      case 'failed': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  const getStatusIcon = (status?: string): string => {
    switch (status) {
      case 'deployed': return '🚀';
      case 'trained': return '✅';
      case 'training': return '⏳';
      case 'failed': return '❌';
      default: return '📊';
    }
  };

  return (
    <TouchableOpacity
      style={styles.modelCard}
      onPress={() => onViewDetails(model)}
      activeOpacity={0.7}
    >
      <View style={styles.modelHeader}>
        <View style={styles.modelInfo}>
          <Text style={styles.modelName}>{model.name}</Text>
          <Text style={styles.modelDescription}>{model.description}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(latestVersion?.status) }]}>
          <Text style={styles.statusIcon}>{getStatusIcon(latestVersion?.status)}</Text>
          <Text style={styles.statusText}>{latestVersion?.status || 'No Version'}</Text>
        </View>
      </View>
      
      {latestVersion && (
        <View style={styles.modelMetrics}>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>Accuracy</Text>
            <Text style={styles.metricValue}>{(latestVersion.accuracy * 100).toFixed(1)}%</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>F1 Score</Text>
            <Text style={styles.metricValue}>{(latestVersion.f1Score * 100).toFixed(1)}%</Text>
          </View>
          <View style={styles.metricItem}>
            <Text style={styles.metricLabel}>Training Time</Text>
            <Text style={styles.metricValue}>{(latestVersion.trainingDuration / 1000).toFixed(1)}s</Text>
          </View>
        </View>
      )}
      
      <View style={styles.modelActions}>
        <AccessibleButton
          title="Train"
          onPress={() => onTrain(model)}
          style={styles.actionButton}
          variant="secondary"
          size="small"
        />
        {latestVersion?.status === 'trained' && (
          <AccessibleButton
            title="Deploy"
            onPress={() => onDeploy(model)}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
        )}
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(model)}
          style={styles.actionButton}
          variant="outline"
          size="small"
        />
      </View>
    </TouchableOpacity>
  );
};

// ============================================================================
// VERSION CARD COMPONENT
// ============================================================================

const VersionCard: React.FC<VersionCardProps> = ({ version, onDeploy, onViewMetrics }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'deployed': return '#34C759';
      case 'trained': return '#007AFF';
      case 'training': return '#FF9500';
      case 'failed': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.versionCard}>
      <View style={styles.versionHeader}>
        <Text style={styles.versionTitle}>Version {version.version}</Text>
        <View style={[styles.versionStatus, { backgroundColor: getStatusColor(version.status) }]}>
          <Text style={styles.versionStatusText}>{version.status.toUpperCase()}</Text>
        </View>
      </View>
      
      <Text style={styles.versionDescription}>{version.description}</Text>
      
      <View style={styles.versionMetrics}>
        <View style={styles.versionMetric}>
          <Text style={styles.versionMetricLabel}>Accuracy</Text>
          <Text style={styles.versionMetricValue}>{(version.accuracy * 100).toFixed(1)}%</Text>
        </View>
        <View style={styles.versionMetric}>
          <Text style={styles.versionMetricLabel}>Precision</Text>
          <Text style={styles.versionMetricValue}>{(version.precision * 100).toFixed(1)}%</Text>
        </View>
        <View style={styles.versionMetric}>
          <Text style={styles.versionMetricLabel}>Recall</Text>
          <Text style={styles.versionMetricValue}>{(version.recall * 100).toFixed(1)}%</Text>
        </View>
        <View style={styles.versionMetric}>
          <Text style={styles.versionMetricLabel}>F1 Score</Text>
          <Text style={styles.versionMetricValue}>{(version.f1Score * 100).toFixed(1)}%</Text>
        </View>
      </View>
      
      <View style={styles.versionActions}>
        {version.status === 'trained' && (
          <AccessibleButton
            title="Deploy"
            onPress={() => onDeploy(version)}
            style={styles.versionActionButton}
            variant="primary"
            size="small"
          />
        )}
        <AccessibleButton
          title="Metrics"
          onPress={() => onViewMetrics(version)}
          style={styles.versionActionButton}
          variant="outline"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// RECOMMENDATION CARD COMPONENT
// ============================================================================

const RecommendationCard: React.FC<RecommendationCardProps> = ({ recommendation, onViewDetails, onDismiss }) => {
  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical': return '#FF3B30';
      case 'high': return '#FF9500';
      case 'medium': return '#FFCC00';
      case 'low': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'training': return '🎯';
      case 'deployment': return '🚀';
      case 'optimization': return '⚡';
      case 'retirement': return '🔄';
      case 'scaling': return '📈';
      default: return '💡';
    }
  };

  return (
    <View style={styles.recommendationCard}>
      <View style={styles.recommendationHeader}>
        <View style={styles.recommendationInfo}>
          <Text style={styles.recommendationTypeIcon}>{getTypeIcon(recommendation.type)}</Text>
          <Text style={styles.recommendationTitle}>{recommendation.title}</Text>
        </View>
        <View style={styles.recommendationControls}>
          <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(recommendation.priority) }]}>
            <Text style={styles.priorityBadgeText}>{recommendation.priority.toUpperCase()}</Text>
          </View>
          <AccessibleButton
            title="✕"
            onPress={() => onDismiss(recommendation)}
            style={styles.dismissButton}
            variant="ghost"
            size="small"
          />
        </View>
      </View>
      
      <Text style={styles.recommendationDescription}>{recommendation.description}</Text>
      
      <View style={styles.recommendationMetrics}>
        <View style={styles.recommendationMetric}>
          <Text style={styles.recommendationMetricLabel}>Impact</Text>
          <Text style={styles.recommendationMetricValue}>{recommendation.impact}</Text>
        </View>
        <View style={styles.recommendationMetric}>
          <Text style={styles.recommendationMetricLabel}>Effort</Text>
          <Text style={styles.recommendationMetricValue}>{recommendation.effort}</Text>
        </View>
        <View style={styles.recommendationMetric}>
          <Text style={styles.recommendationMetricLabel}>ROI</Text>
          <Text style={styles.recommendationMetricValue}>{recommendation.roi.toFixed(1)}x</Text>
        </View>
        <View style={styles.recommendationMetric}>
          <Text style={styles.recommendationMetricLabel}>Confidence</Text>
          <Text style={styles.recommendationMetricValue}>{(recommendation.confidence * 100).toFixed(0)}%</Text>
        </View>
      </View>
      
      {recommendation.recommendations.length > 0 && (
        <View style={styles.recommendationList}>
          <Text style={styles.recommendationListTitle}>Recommendations:</Text>
          {recommendation.recommendations.slice(0, 2).map((rec, index) => (
            <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
          ))}
          {recommendation.recommendations.length > 2 && (
            <Text style={styles.moreRecommendations}>
              +{recommendation.recommendations.length - 2} more recommendations
            </Text>
          )}
        </View>
      )}
      
      <View style={styles.recommendationActions}>
        <AccessibleButton
          title="View Details"
          onPress={() => onViewDetails(recommendation)}
          style={styles.recommendationActionButton}
          variant="primary"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

/**
 * AI Model Management Dashboard Component
 * Comprehensive dashboard for managing AI/ML models, training, deployment, and optimization
 */
export function AIModelManagementDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'models' | 'versions' | 'recommendations' | 'performance'>('overview');
  const [models, setModels] = useState<any[]>([]);
  const [versions, setVersions] = useState<AIModelVersion[]>([]);
  const [recommendations, setRecommendations] = useState<AIModelRecommendation[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState<AIModelPerformanceMetrics[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedModel, setSelectedModel] = useState<any | null>(null);

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
      // Load initial data
      await refreshData();
      
      // Set up event listeners
      aiModelManager.on('modelCreated', () => refreshData());
      aiModelManager.on('modelUpdated', () => refreshData());
      aiModelManager.on('modelVersionCreated', () => refreshData());
      aiModelManager.on('trainingCompleted', () => refreshData());
      aiModelManager.on('modelDeployed', () => refreshData());
      aiModelManager.on('recommendationGenerated', () => refreshData());

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
      const modelsData = aiModelManager.getModels();
      const recommendationsData = aiModelManager.getRecommendations();
      const performanceData = aiModelManager.getPerformanceMetrics();
      
      setModels(modelsData);
      setRecommendations(recommendationsData);
      setPerformanceMetrics(performanceData);
      
      // Get versions for all models
      const allVersions: AIModelVersion[] = [];
      modelsData.forEach(model => {
        const modelVersions = aiModelManager.getModelVersions(model.id);
        allVersions.push(...modelVersions);
      });
      setVersions(allVersions);
      
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewModelDetails = useCallback((model: any) => {
    setSelectedModel(model);
    Alert.alert(
      model.name,
      `${model.description}\n\nType: ${model.type}\nAlgorithm: ${model.algorithm}\nStatus: ${model.status}`,
      [{ text: 'OK', onPress: () => setSelectedModel(null) }]
    );
  }, []);

  const handleDeployModel = useCallback(async (model: any) => {
    setIsLoading(true);
    try {
      const latestVersion = aiModelManager.getLatestModelVersion(model.id);
      if (!latestVersion) {
        Alert.alert('Error', 'No trained version available for deployment');
        return;
      }

      const success = await aiModelManager.deployModelVersion(latestVersion.id, 'production');
      if (success) {
        Alert.alert('Success', 'Model deployed successfully');
        await refreshData();
      } else {
        Alert.alert('Error', 'Failed to deploy model');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to deploy model');
    } finally {
      setIsLoading(false);
    }
  }, [refreshData]);

  const handleTrainModel = useCallback(async (model: any) => {
    setIsLoading(true);
    try {
      // Create training configuration
      const config = {
        id: `config_${model.id}_${Date.now()}`,
        modelId: model.id,
        algorithm: model.algorithm,
        hyperparameters: {
          learningRate: 0.001,
          batchSize: 32,
          epochs: 100,
        },
        trainingData: {
          source: 'analytics_data',
          size: 1000,
          features: ['feature1', 'feature2', 'feature3'],
          target: 'target',
        },
        validation: {
          split: 0.2,
          crossValidation: true,
          folds: 5,
        },
        optimization: {
          objective: 'accuracy',
          metrics: ['accuracy', 'precision', 'recall', 'f1'],
          earlyStopping: true,
          patience: 10,
        },
        resources: {
          maxMemory: 2048,
          maxCpu: 2,
          timeout: 3600000,
        },
        isActive: true,
        createdAt: Date.now(),
        updatedAt: Date.now(),
      };

      aiModelManager.createTrainingConfig(config);
      const versionId = await aiModelManager.startTraining(model.id, config.id);
      
      Alert.alert('Success', `Training started for model ${model.name}\nVersion ID: ${versionId}`);
      await refreshData();
    } catch (error) {
      Alert.alert('Error', 'Failed to start training');
    } finally {
      setIsLoading(false);
    }
  }, [refreshData]);

  const handleDeployVersion = useCallback(async (version: AIModelVersion) => {
    setIsLoading(true);
    try {
      const success = await aiModelManager.deployModelVersion(version.id, 'production');
      if (success) {
        Alert.alert('Success', 'Model version deployed successfully');
        await refreshData();
      } else {
        Alert.alert('Error', 'Failed to deploy model version');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to deploy model version');
    } finally {
      setIsLoading(false);
    }
  }, [refreshData]);

  const handleViewVersionMetrics = useCallback((version: AIModelVersion) => {
    Alert.alert(
      `Version ${version.version} Metrics`,
      `Accuracy: ${(version.accuracy * 100).toFixed(1)}%\nPrecision: ${(version.precision * 100).toFixed(1)}%\nRecall: ${(version.recall * 100).toFixed(1)}%\nF1 Score: ${(version.f1Score * 100).toFixed(1)}%\nTraining Duration: ${(version.trainingDuration / 1000).toFixed(1)}s`,
      [{ text: 'OK' }]
    );
  }, []);

  const handleViewRecommendationDetails = useCallback((recommendation: AIModelRecommendation) => {
    Alert.alert(
      recommendation.title,
      `${recommendation.description}\n\nPriority: ${recommendation.priority}\nImpact: ${recommendation.impact}\nEffort: ${recommendation.effort}\nROI: ${recommendation.roi.toFixed(1)}x\n\nRecommendations:\n${recommendation.recommendations.map(rec => `• ${rec}`).join('\n')}`,
      [{ text: 'OK' }]
    );
  }, []);

  const handleDismissRecommendation = useCallback((recommendation: AIModelRecommendation) => {
    // In a real implementation, this would mark the recommendation as dismissed
    Alert.alert('Dismissed', 'Recommendation dismissed');
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
    const stats = aiModelManager.getSystemStats();
    const recentVersions = versions.slice(0, 3);
    const criticalRecommendations = recommendations.filter(r => r.priority === 'critical' || r.priority === 'high');

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
          <Text style={styles.sectionTitle}>System Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalModels}</Text>
              <Text style={styles.statLabel}>Total Models</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.deployedModels}</Text>
              <Text style={styles.statLabel}>Deployed</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.trainingModels}</Text>
              <Text style={styles.statLabel}>Training</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{(stats.averageAccuracy * 100).toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Avg Accuracy</Text>
            </View>
          </View>
        </View>

        {/* Critical Recommendations */}
        {criticalRecommendations.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Critical Recommendations</Text>
            {criticalRecommendations.slice(0, 2).map(recommendation => (
              <RecommendationCard
                key={recommendation.id}
                recommendation={recommendation}
                onViewDetails={handleViewRecommendationDetails}
                onDismiss={handleDismissRecommendation}
              />
            ))}
          </View>
        )}

        {/* Recent Versions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Model Versions</Text>
          {recentVersions.length > 0 ? (
            recentVersions.map(version => (
              <VersionCard
                key={version.id}
                version={version}
                onDeploy={handleDeployVersion}
                onViewMetrics={handleViewVersionMetrics}
              />
            ))
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyStateText}>No model versions available</Text>
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
              title="📊 View Models"
              onPress={() => handleTabChange('models')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="💡 Recommendations"
              onPress={() => handleTabChange('recommendations')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderModelsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Models</Text>
        {models.length > 0 ? (
          models.map(model => {
            const latestVersion = aiModelManager.getLatestModelVersion(model.id);
            return (
              <ModelCard
                key={model.id}
                model={model}
                latestVersion={latestVersion}
                onViewDetails={handleViewModelDetails}
                onDeploy={handleDeployModel}
                onTrain={handleTrainModel}
              />
            );
          })
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No models available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderVersionsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Model Versions</Text>
        {versions.length > 0 ? (
          versions.map(version => (
            <VersionCard
              key={version.id}
              version={version}
              onDeploy={handleDeployVersion}
              onViewMetrics={handleViewVersionMetrics}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No model versions available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderRecommendationsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Recommendations</Text>
        {recommendations.length > 0 ? (
          recommendations.map(recommendation => (
            <RecommendationCard
              key={recommendation.id}
              recommendation={recommendation}
              onViewDetails={handleViewRecommendationDetails}
              onDismiss={handleDismissRecommendation}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No recommendations available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderPerformanceTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Performance Metrics</Text>
        {performanceMetrics.length > 0 ? (
          performanceMetrics.slice(0, 10).map((metrics, index) => (
            <View key={index} style={styles.performanceCard}>
              <View style={styles.performanceHeader}>
                <Text style={styles.performanceTitle}>Model {metrics.modelId}</Text>
                <Text style={styles.performancePeriod}>{metrics.period}</Text>
              </View>
              
              <View style={styles.performanceMetrics}>
                <View style={styles.performanceMetric}>
                  <Text style={styles.performanceMetricLabel}>Predictions</Text>
                  <Text style={styles.performanceMetricValue}>{metrics.metrics.totalPredictions}</Text>
                </View>
                <View style={styles.performanceMetric}>
                  <Text style={styles.performanceMetricLabel}>Accuracy</Text>
                  <Text style={styles.performanceMetricValue}>{(metrics.metrics.averageAccuracy * 100).toFixed(1)}%</Text>
                </View>
                <View style={styles.performanceMetric}>
                  <Text style={styles.performanceMetricLabel}>Latency</Text>
                  <Text style={styles.performanceMetricValue}>{metrics.metrics.averageLatency.toFixed(1)}ms</Text>
                </View>
                <View style={styles.performanceMetric}>
                  <Text style={styles.performanceMetricLabel}>Throughput</Text>
                  <Text style={styles.performanceMetricValue}>{metrics.metrics.throughput.toFixed(1)}/s</Text>
                </View>
              </View>
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No performance metrics available</Text>
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
        <Text style={styles.headerTitle}>AI Model Management</Text>
        <Text style={styles.headerSubtitle}>
          Advanced Model Training, Deployment & Optimization
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('models', 'Models')}
        {renderTabButton('versions', 'Versions')}
        {renderTabButton('recommendations', 'Recommendations')}
        {renderTabButton('performance', 'Performance')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'models' && renderModelsTab()}
        {activeTab === 'versions' && renderVersionsTab()}
        {activeTab === 'recommendations' && renderRecommendationsTab()}
        {activeTab === 'performance' && renderPerformanceTab()}
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
  modelCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  modelHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  modelInfo: {
    flex: 1,
  },
  modelName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  modelDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  statusBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusIcon: {
    fontSize: 12,
    marginRight: 4,
  },
  statusText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  modelMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  metricItem: {
    alignItems: 'center',
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  modelActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  actionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  versionCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  versionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  versionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  versionStatus: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  versionStatusText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  versionDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 12,
  },
  versionMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  versionMetric: {
    alignItems: 'center',
  },
  versionMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  versionMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  versionActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  versionActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  recommendationCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  recommendationInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  recommendationTypeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  recommendationTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  recommendationControls: {
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
  dismissButton: {
    paddingHorizontal: 8,
    paddingVertical: 4,
  },
  recommendationDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  recommendationMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  recommendationMetric: {
    alignItems: 'center',
  },
  recommendationMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  recommendationMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  recommendationList: {
    marginBottom: 12,
  },
  recommendationListTitle: {
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
  moreRecommendations: {
    fontSize: 12,
    color: '#007AFF',
    fontStyle: 'italic',
  },
  recommendationActions: {
    flexDirection: 'row',
    justifyContent: 'center',
  },
  recommendationActionButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
  },
  performanceCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  performanceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  performanceTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  performancePeriod: {
    fontSize: 12,
    color: '#666',
  },
  performanceMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  performanceMetric: {
    alignItems: 'center',
  },
  performanceMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  performanceMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  actionButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    flexWrap: 'wrap',
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIModelManagementDashboard;