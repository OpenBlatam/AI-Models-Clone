/**
 * @fileoverview AI model management demo component
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
import { AIModelManagementDashboard } from '../dashboard/ai-model-management-dashboard';
import { 
  aiModelManager, 
  AIModelVersion, 
  AIModelRecommendation, 
  AIModelTrainingConfig,
  AIModelOptimizationResult 
} from '../../lib/ai/ai-model-manager';

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_MODELS = [
  {
    id: 'sentiment_analyzer',
    name: 'Sentiment Analysis Model',
    description: 'Advanced neural network for analyzing sentiment in customer feedback',
    type: 'classification',
    algorithm: 'neural_network',
    status: 'active',
    createdAt: Date.now() - 7 * 24 * 60 * 60 * 1000,
  },
  {
    id: 'demand_forecaster',
    name: 'Demand Forecasting Model',
    description: 'LSTM-based model for predicting product demand patterns',
    type: 'regression',
    algorithm: 'lstm',
    status: 'active',
    createdAt: Date.now() - 14 * 24 * 60 * 60 * 1000,
  },
  {
    id: 'anomaly_detector',
    name: 'Anomaly Detection Model',
    description: 'Isolation Forest model for detecting system anomalies',
    type: 'anomaly_detection',
    algorithm: 'isolation_forest',
    status: 'active',
    createdAt: Date.now() - 21 * 24 * 60 * 60 * 1000,
  },
  {
    id: 'recommendation_engine',
    name: 'Recommendation Engine',
    description: 'Collaborative filtering model for product recommendations',
    type: 'recommendation',
    algorithm: 'neural_network',
    status: 'active',
    createdAt: Date.now() - 10 * 24 * 60 * 60 * 1000,
  },
  {
    id: 'image_classifier',
    name: 'Image Classification Model',
    description: 'CNN model for classifying product images',
    type: 'classification',
    algorithm: 'neural_network',
    status: 'active',
    createdAt: Date.now() - 5 * 24 * 60 * 60 * 1000,
  },
];

const DEMO_TRAINING_SCENARIOS = [
  {
    id: 'scenario_1',
    title: 'Hyperparameter Optimization',
    description: 'Automatically find optimal hyperparameters for better model performance',
    type: 'optimization',
    steps: [
      'Analyze current model performance',
      'Define hyperparameter search space',
      'Run automated optimization',
      'Compare results and select best configuration',
    ],
    expectedImprovement: '15-25% accuracy improvement',
    estimatedTime: '2-4 hours',
  },
  {
    id: 'scenario_2',
    title: 'Model Retraining Pipeline',
    description: 'Set up automated retraining when model performance degrades',
    type: 'training',
    steps: [
      'Monitor model performance metrics',
      'Detect performance degradation',
      'Trigger automatic retraining',
      'Deploy improved model version',
    ],
    expectedImprovement: 'Maintain optimal performance',
    estimatedTime: '1-2 hours',
  },
  {
    id: 'scenario_3',
    title: 'Ensemble Model Creation',
    description: 'Combine multiple models for improved accuracy and robustness',
    type: 'ensemble',
    steps: [
      'Train multiple model variants',
      'Evaluate individual model performance',
      'Create ensemble combination',
      'Optimize ensemble weights',
    ],
    expectedImprovement: '10-20% accuracy improvement',
    estimatedTime: '3-6 hours',
  },
  {
    id: 'scenario_4',
    title: 'Feature Engineering Pipeline',
    description: 'Automatically generate and select optimal features',
    type: 'feature_engineering',
    steps: [
      'Analyze feature importance',
      'Generate new features',
      'Select optimal feature subset',
      'Retrain model with new features',
    ],
    expectedImprovement: '8-15% accuracy improvement',
    estimatedTime: '1-3 hours',
  },
];

// ============================================================================
// MAIN COMPONENT
// ============================================================================

/**
 * AI Model Management Demo Component
 * Interactive demonstration of AI model management capabilities
 */
export default function AIModelManagementDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'scenarios' | 'training' | 'dashboard'>('overview');
  const [isLoading, setIsLoading] = useState(false);
  const [trainingProgress, setTrainingProgress] = useState<{ [key: string]: number }>({});
  const [systemStats, setSystemStats] = useState<any>(null);
  const [recommendations, setRecommendations] = useState<AIModelRecommendation[]>([]);
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
      // Initialize demo models
      DEMO_MODELS.forEach(model => {
        aiModelManager.createModel(model);
      });

      // Create some demo versions
      await createDemoVersions();

      // Generate initial recommendations
      const systemRecommendations = aiModelManager.generateSystemRecommendations();
      setRecommendations(systemRecommendations);

      // Get system stats
      const stats = aiModelManager.getSystemStats();
      setSystemStats(stats);

      // Set up event listeners
      aiModelManager.on('trainingCompleted', handleTrainingCompleted);
      aiModelManager.on('modelDeployed', handleModelDeployed);
      aiModelManager.on('recommendationGenerated', handleRecommendationGenerated);

    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ============================================================================
  // DEMO DATA CREATION
  // ============================================================================

  const createDemoVersions = useCallback(async () => {
    const models = aiModelManager.getModels();
    
    for (const model of models) {
      // Create a trained version
      const version: AIModelVersion = {
        id: `version_${model.id}_trained`,
        modelId: model.id,
        version: 'v1.0.0',
        description: `Initial trained version of ${model.name}`,
        status: 'trained',
        accuracy: 0.85 + Math.random() * 0.1,
        precision: 0.82 + Math.random() * 0.1,
        recall: 0.80 + Math.random() * 0.1,
        f1Score: 0.81 + Math.random() * 0.1,
        trainingDataSize: 1000 + Math.floor(Math.random() * 5000),
        trainingDuration: 30000 + Math.floor(Math.random() * 120000),
        hyperparameters: {
          learningRate: 0.001,
          batchSize: 32,
          epochs: 100,
        },
        metadata: {
          algorithm: model.algorithm,
          createdBy: 'demo_user',
        },
        createdAt: Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000),
      };

      aiModelManager.createModelVersion(version);

      // Randomly deploy some models
      if (Math.random() > 0.5) {
        await aiModelManager.deployModelVersion(version.id, 'production');
      }
    }
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleTrainingCompleted = useCallback((data: any) => {
    Alert.alert(
      'Training Completed',
      `Model ${data.version.modelId} training completed with ${(data.metrics.accuracy * 100).toFixed(1)}% accuracy`
    );
    setTrainingProgress(prev => ({ ...prev, [data.version.modelId]: 100 }));
  }, []);

  const handleModelDeployed = useCallback((data: any) => {
    Alert.alert(
      'Model Deployed',
      `Model ${data.version.modelId} version ${data.version.version} deployed successfully`
    );
  }, []);

  const handleRecommendationGenerated = useCallback((recommendation: AIModelRecommendation) => {
    setRecommendations(prev => [recommendation, ...prev]);
  }, []);

  // ============================================================================
  // DEMO ACTIONS
  // ============================================================================

  const handleStartTraining = useCallback(async (modelId: string) => {
    setIsLoading(true);
    try {
      // Create training configuration
      const config: AIModelTrainingConfig = {
        id: `config_${modelId}_${Date.now()}`,
        modelId: modelId,
        algorithm: 'neural_network',
        hyperparameters: {
          learningRate: 0.001,
          batchSize: 32,
          epochs: 100,
          dropout: 0.2,
        },
        trainingData: {
          source: 'demo_dataset',
          size: 2000,
          features: ['feature1', 'feature2', 'feature3', 'feature4'],
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
      const versionId = await aiModelManager.startTraining(modelId, config.id);
      
      // Start progress simulation
      simulateTrainingProgress(modelId);
      
      Alert.alert(
        'Training Started',
        `Training started for model ${modelId}\nVersion ID: ${versionId}`
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to start training');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const simulateTrainingProgress = useCallback((modelId: string) => {
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 10;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      setTrainingProgress(prev => ({ ...prev, [modelId]: progress }));
    }, 1000);
  }, []);

  const handleOptimizeModel = useCallback(async (modelId: string, optimizationType: string) => {
    setIsLoading(true);
    try {
      const result = await aiModelManager.optimizeModel(modelId, optimizationType);
      
      Alert.alert(
        'Optimization Completed',
        `Model ${modelId} optimized with ${optimizationType}\nAccuracy improved by ${(result.improvement.accuracy * 100).toFixed(1)}%`
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to optimize model');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleDeployModel = useCallback(async (modelId: string) => {
    setIsLoading(true);
    try {
      const latestVersion = aiModelManager.getLatestModelVersion(modelId);
      if (!latestVersion) {
        Alert.alert('Error', 'No trained version available for deployment');
        return;
      }

      const success = await aiModelManager.deployModelVersion(latestVersion.id, 'production');
      if (success) {
        Alert.alert('Success', 'Model deployed successfully');
      } else {
        Alert.alert('Error', 'Failed to deploy model');
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to deploy model');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleRunScenario = useCallback(async (scenario: any) => {
    setIsLoading(true);
    try {
      // Simulate scenario execution
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      Alert.alert(
        'Scenario Completed',
        `${scenario.title} completed successfully!\n\nExpected improvement: ${scenario.expectedImprovement}\nTime taken: ${scenario.estimatedTime}`
      );
    } catch (error) {
      Alert.alert('Error', 'Failed to run scenario');
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

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      {/* System Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>AI Model Management System</Text>
        <Text style={styles.sectionDescription}>
          Advanced AI/ML model lifecycle management with automated training, deployment, 
          optimization, and intelligent recommendations.
        </Text>
        
        {systemStats && (
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.totalModels}</Text>
              <Text style={styles.statLabel}>Total Models</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.deployedModels}</Text>
              <Text style={styles.statLabel}>Deployed</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{systemStats.trainingModels}</Text>
              <Text style={styles.statLabel}>Training</Text>
            </View>
            <View style={styles.statItem}>
              <Text style={styles.statValue}>{(systemStats.averageAccuracy * 100).toFixed(1)}%</Text>
              <Text style={styles.statLabel}>Avg Accuracy</Text>
            </View>
          </View>
        )}
      </View>

      {/* Key Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Key Features</Text>
        <View style={styles.featuresList}>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🎯</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Automated Training</Text>
              <Text style={styles.featureDescription}>
                Intelligent model training with hyperparameter optimization
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>🚀</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Smart Deployment</Text>
              <Text style={styles.featureDescription}>
                Automated deployment with monitoring and scaling
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>⚡</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>Model Optimization</Text>
              <Text style={styles.featureDescription}>
                Continuous optimization for better performance
              </Text>
            </View>
          </View>
          <View style={styles.featureItem}>
            <Text style={styles.featureIcon}>💡</Text>
            <View style={styles.featureContent}>
              <Text style={styles.featureTitle}>AI Recommendations</Text>
              <Text style={styles.featureDescription}>
                Intelligent recommendations for model improvements
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
            title="🎯 Training Scenarios"
            onPress={() => handleTabChange('scenarios')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="⚡ Model Training"
            onPress={() => handleTabChange('training')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
        </View>
      </View>

      {/* Recent Recommendations */}
      {recommendations.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Recommendations</Text>
          {recommendations.slice(0, 2).map(recommendation => (
            <View key={recommendation.id} style={styles.recommendationCard}>
              <View style={styles.recommendationHeader}>
                <Text style={styles.recommendationTitle}>{recommendation.title}</Text>
                <View style={[styles.priorityBadge, { backgroundColor: getPriorityColor(recommendation.priority) }]}>
                  <Text style={styles.priorityBadgeText}>{recommendation.priority.toUpperCase()}</Text>
                </View>
              </View>
              <Text style={styles.recommendationDescription}>{recommendation.description}</Text>
              <Text style={styles.recommendationImpact}>
                Impact: {recommendation.impact} | ROI: {recommendation.roi.toFixed(1)}x
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Training Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Explore different AI model training and optimization scenarios
        </Text>
        
        {DEMO_TRAINING_SCENARIOS.map(scenario => (
          <View key={scenario.id} style={styles.scenarioCard}>
            <View style={styles.scenarioHeader}>
              <Text style={styles.scenarioTitle}>{scenario.title}</Text>
              <View style={[styles.scenarioTypeBadge, { backgroundColor: getScenarioTypeColor(scenario.type) }]}>
                <Text style={styles.scenarioTypeText}>{scenario.type.toUpperCase()}</Text>
              </View>
            </View>
            
            <Text style={styles.scenarioDescription}>{scenario.description}</Text>
            
            <View style={styles.scenarioSteps}>
              <Text style={styles.scenarioStepsTitle}>Steps:</Text>
              {scenario.steps.map((step, index) => (
                <Text key={index} style={styles.scenarioStep}>
                  {index + 1}. {step}
                </Text>
              ))}
            </View>
            
            <View style={styles.scenarioMetrics}>
              <View style={styles.scenarioMetric}>
                <Text style={styles.scenarioMetricLabel}>Expected Improvement</Text>
                <Text style={styles.scenarioMetricValue}>{scenario.expectedImprovement}</Text>
              </View>
              <View style={styles.scenarioMetric}>
                <Text style={styles.scenarioMetricLabel}>Estimated Time</Text>
                <Text style={styles.scenarioMetricValue}>{scenario.estimatedTime}</Text>
              </View>
            </View>
            
            <AccessibleButton
              title="Run Scenario"
              onPress={() => handleRunScenario(scenario)}
              style={styles.scenarioButton}
              variant="primary"
              size="small"
            />
          </View>
        ))}
      </View>
    </ScrollView>
  );

  const renderTrainingTab = (): JSX.Element => {
    const models = aiModelManager.getModels();
    
    return (
      <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Model Training</Text>
          <Text style={styles.sectionDescription}>
            Train and optimize your AI models with advanced techniques
          </Text>
          
          {models.map(model => {
            const latestVersion = aiModelManager.getLatestModelVersion(model.id);
            const progress = trainingProgress[model.id] || 0;
            
            return (
              <View key={model.id} style={styles.modelCard}>
                <View style={styles.modelHeader}>
                  <View style={styles.modelInfo}>
                    <Text style={styles.modelName}>{model.name}</Text>
                    <Text style={styles.modelDescription}>{model.description}</Text>
                    <Text style={styles.modelAlgorithm}>Algorithm: {model.algorithm}</Text>
                  </View>
                  <View style={styles.modelStatus}>
                    <Text style={styles.modelStatusText}>
                      {latestVersion ? latestVersion.status : 'No Version'}
                    </Text>
                    {latestVersion && (
                      <Text style={styles.modelAccuracy}>
                        Accuracy: {(latestVersion.accuracy * 100).toFixed(1)}%
                      </Text>
                    )}
                  </View>
                </View>
                
                {progress > 0 && progress < 100 && (
                  <View style={styles.progressContainer}>
                    <Text style={styles.progressText}>Training Progress: {progress.toFixed(0)}%</Text>
                    <View style={styles.progressBar}>
                      <View style={[styles.progressFill, { width: `${progress}%` }]} />
                    </View>
                  </View>
                )}
                
                <View style={styles.modelActions}>
                  <AccessibleButton
                    title="Train"
                    onPress={() => handleStartTraining(model.id)}
                    style={styles.modelActionButton}
                    variant="primary"
                    size="small"
                  />
                  <AccessibleButton
                    title="Optimize"
                    onPress={() => handleOptimizeModel(model.id, 'hyperparameter')}
                    style={styles.modelActionButton}
                    variant="secondary"
                    size="small"
                  />
                  {latestVersion?.status === 'trained' && (
                    <AccessibleButton
                      title="Deploy"
                      onPress={() => handleDeployModel(model.id)}
                      style={styles.modelActionButton}
                      variant="outline"
                      size="small"
                    />
                  )}
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>
    );
  };

  // ============================================================================
  // UTILITY FUNCTIONS
  // ============================================================================

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'critical': return '#FF3B30';
      case 'high': return '#FF9500';
      case 'medium': return '#FFCC00';
      case 'low': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getScenarioTypeColor = (type: string): string => {
    switch (type) {
      case 'optimization': return '#007AFF';
      case 'training': return '#34C759';
      case 'ensemble': return '#FF9500';
      case 'feature_engineering': return '#AF52DE';
      default: return '#8E8E93';
    }
  };

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
          <Text style={styles.dashboardTitle}>AI Model Management Dashboard</Text>
        </View>
        <AIModelManagementDashboard />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>AI Model Management Demo</Text>
        <Text style={styles.headerSubtitle}>
          Advanced AI/ML Model Training, Deployment & Optimization
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('scenarios', 'Scenarios')}
        {renderTabButton('training', 'Training')}
        {renderTabButton('dashboard', 'Dashboard')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
        {activeTab === 'training' && renderTrainingTab()}
        {activeTab === 'dashboard' && (
          <View style={styles.dashboardTab}>
            <Text style={styles.dashboardTabTitle}>Full Dashboard</Text>
            <Text style={styles.dashboardTabDescription}>
              Access the complete AI Model Management Dashboard with all features
            </Text>
            <AccessibleButton
              title="Open Dashboard"
              onPress={() => setShowDashboard(true)}
              style={styles.dashboardButton}
              variant="primary"
              size="large"
            />
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
  recommendationCard: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  recommendationHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  recommendationTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  priorityBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  priorityBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  recommendationDescription: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  recommendationImpact: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '500',
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
    alignItems: 'center',
    marginBottom: 8,
  },
  scenarioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  scenarioTypeBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  scenarioTypeText: {
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
  scenarioSteps: {
    marginBottom: 12,
  },
  scenarioStepsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  scenarioStep: {
    fontSize: 12,
    color: '#666',
    lineHeight: 16,
    marginBottom: 4,
  },
  scenarioMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  scenarioMetric: {
    alignItems: 'center',
  },
  scenarioMetricLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  scenarioMetricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  scenarioButton: {
    alignSelf: 'center',
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  modelCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 16,
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
    marginBottom: 4,
  },
  modelAlgorithm: {
    fontSize: 12,
    color: '#007AFF',
    fontWeight: '500',
  },
  modelStatus: {
    alignItems: 'flex-end',
  },
  modelStatusText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  modelAccuracy: {
    fontSize: 12,
    color: '#34C759',
    fontWeight: '600',
  },
  progressContainer: {
    marginBottom: 12,
  },
  progressText: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  progressBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#007AFF',
  },
  modelActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  modelActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  dashboardTab: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  dashboardTabTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 8,
    textAlign: 'center',
  },
  dashboardTabDescription: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 32,
  },
  dashboardButton: {
    paddingHorizontal: 32,
    paddingVertical: 16,
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

// ============================================================================
// EXPORTS
// ============================================================================

export default AIModelManagementDemo;