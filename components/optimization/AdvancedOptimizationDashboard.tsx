import React, { useState, useEffect, useMemo } from 'react';
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, Alert } from 'react-native';
import { OptimizedTranslatedText } from '../i18n-components/OptimizedTranslatedText';
import { advancedOptimizer, getAdaptiveMetrics, predictOptimizationImpact } from '../../utils/optimization/AdvancedOptimizer';
import { performanceMonitor } from '../../utils/performance/PerformanceMonitor';
import { cacheManager } from '../../utils/caching/CacheManager';
import { analytics } from '../../utils/analytics/AnalyticsService';

interface AdvancedOptimizationDashboardProps {
  onOptimize?: () => void;
  onConfigure?: () => void;
  style?: any;
}

interface AdaptiveMetricCardProps {
  title: string;
  value: number | string;
  unit?: string;
  status: 'excellent' | 'good' | 'warning' | 'critical';
  description: string;
  trend?: number;
}

const AdaptiveMetricCard: React.FC<AdaptiveMetricCardProps> = ({ 
  title, value, unit, status, description, trend 
}) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'excellent': return '#4CAF50';
      case 'good': return '#8BC34A';
      case 'warning': return '#FF9800';
      case 'critical': return '#F44336';
      default: return '#9E9E9E';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent': return '✅';
      case 'good': return '🟢';
      case 'warning': return '⚠️';
      case 'critical': return '🔴';
      default: return '⚪';
    }
  };

  return (
    <View style={[styles.metricCard, { borderLeftColor: getStatusColor(status) }]}>
      <View style={styles.metricHeader}>
        <Text style={styles.metricTitle}>{title}</Text>
        <Text style={styles.statusIcon}>{getStatusIcon(status)}</Text>
      </View>
      <View style={styles.metricValue}>
        <Text style={styles.valueText}>
          {typeof value === 'number' ? value.toFixed(2) : value}
          {unit && <Text style={styles.unitText}> {unit}</Text>}
        </Text>
        {trend !== undefined && (
          <Text style={[styles.trendText, { color: trend > 0 ? '#4CAF50' : '#F44336' }]}>
            {trend > 0 ? '↗' : '↘'} {Math.abs(trend).toFixed(1)}%
          </Text>
        )}
      </View>
      <Text style={styles.metricDescription}>{description}</Text>
    </View>
  );
};

export const AdvancedOptimizationDashboard: React.FC<AdvancedOptimizationDashboardProps> = ({
  onOptimize, onConfigure, style,
}) => {
  const [metrics, setMetrics] = useState<any>({});
  const [isOptimizing, setIsOptimizing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());
  const [prediction, setPrediction] = useState<any>(null);

  const fetchMetrics = async () => {
    try {
      const adaptiveMetrics = getAdaptiveMetrics();
      const performanceReport = performanceMonitor.getReport();
      const cacheStats = cacheManager.getStats();
      
      setMetrics({
        adaptive: adaptiveMetrics,
        performance: performanceReport,
        cache: cacheStats,
      });
      
      setLastUpdate(new Date());
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchPrediction = async () => {
    try {
      const predictionResult = await predictOptimizationImpact();
      setPrediction(predictionResult);
    } catch (error) {
      console.error('Failed to fetch prediction:', error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    fetchPrediction();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchMetrics();
      fetchPrediction();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const handleAdvancedOptimize = async () => {
    if (isOptimizing) return;
    
    setIsOptimizing(true);
    try {
      const result = await advancedOptimizer.applyAdvancedOptimization();
      
      Alert.alert(
        'Advanced Optimization Complete',
        `Optimization completed in ${result.duration}ms\nPredicted improvement: ${result.prediction.expectedImprovement.toFixed(1)}%`,
        [{ text: 'OK' }]
      );
      
      fetchMetrics();
      fetchPrediction();
      
      if (onOptimize) onOptimize();
    } catch (error) {
      Alert.alert('Optimization Failed', error.message);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleMLOptimize = async () => {
    try {
      await advancedOptimizer.applyMLBasedOptimization();
      Alert.alert('ML Optimization', 'ML-based optimization applied successfully');
      fetchMetrics();
    } catch (error) {
      Alert.alert('ML Optimization Failed', error.message);
    }
  };

  const handlePredictiveCache = async () => {
    try {
      await advancedOptimizer.applyAdaptiveCaching();
      Alert.alert('Predictive Caching', 'Adaptive caching applied successfully');
      fetchMetrics();
    } catch (error) {
      Alert.alert('Predictive Caching Failed', error.message);
    }
  };

  const handleIntelligentPrefetch = async () => {
    try {
      await advancedOptimizer.applyIntelligentPrefetching();
      Alert.alert('Intelligent Prefetching', 'Smart prefetching applied successfully');
      fetchMetrics();
    } catch (error) {
      Alert.alert('Intelligent Prefetching Failed', error.message);
    }
  };

  const overallScore = useMemo(() => {
    if (!metrics.adaptive) return 0;
    
    const performanceScore = metrics.performance?.averageRenderTime ? 
      Math.max(0, 100 - metrics.performance.averageRenderTime) : 0;
    const cacheScore = metrics.cache?.hitRate ? metrics.cache.hitRate * 100 : 0;
    const predictionScore = prediction?.predictedPerformance || 0;
    
    return (performanceScore + cacheScore + predictionScore) / 3;
  }, [metrics, prediction]);

  const getStatus = (value: number, thresholds: { excellent: number; good: number; warning: number }) => {
    if (value >= thresholds.excellent) return 'excellent';
    if (value >= thresholds.good) return 'good';
    if (value >= thresholds.warning) return 'warning';
    return 'critical';
  };

  return (
    <ScrollView style={[styles.container, style]} showsVerticalScrollIndicator={false}>
      {/* Header */}
      <View style={styles.header}>
        <OptimizedTranslatedText
          translationKey="optimization.advanced_dashboard_title"
          style={styles.headerTitle}
        />
        <Text style={styles.lastUpdate}>
          Last update: {lastUpdate.toLocaleTimeString()}
        </Text>
      </View>

      {/* Overall Score */}
      <View style={styles.scoreContainer}>
        <Text style={styles.scoreLabel}>Advanced Optimization Score</Text>
        <Text style={[styles.scoreValue, { color: getStatus(overallScore, { excellent: 90, good: 75, warning: 60 }).color }]}>
          {overallScore.toFixed(1)}%
        </Text>
        <Text style={styles.scoreDescription}>
          Based on ML predictions, adaptive caching, and performance trends
        </Text>
      </View>

      {/* Action Buttons */}
      <View style={styles.actionButtons}>
        <TouchableOpacity
          style={[styles.actionButton, styles.primaryButton]}
          onPress={handleAdvancedOptimize}
          disabled={isOptimizing}
        >
          <Text style={styles.buttonText}>
            {isOptimizing ? 'Optimizing...' : 'Run Advanced Optimization'}
          </Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={handleMLOptimize}
        >
          <Text style={styles.buttonText}>ML Optimization</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={handlePredictiveCache}
        >
          <Text style={styles.buttonText}>Predictive Caching</Text>
        </TouchableOpacity>
        
        <TouchableOpacity
          style={[styles.actionButton, styles.secondaryButton]}
          onPress={handleIntelligentPrefetch}
        >
          <Text style={styles.buttonText}>Smart Prefetching</Text>
        </TouchableOpacity>
      </View>

      {/* Prediction Section */}
      {prediction && (
        <View style={styles.predictionSection}>
          <Text style={styles.sectionTitle}>Performance Prediction</Text>
          <AdaptiveMetricCard
            title="Predicted Performance"
            value={prediction.predictedPerformance}
            unit="%"
            status={getStatus(prediction.predictedPerformance, { excellent: 90, good: 75, warning: 60 })}
            description={`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`}
          />
          <AdaptiveMetricCard
            title="Expected Improvement"
            value={prediction.expectedImprovement}
            unit="%"
            status={getStatus(prediction.expectedImprovement, { excellent: 20, good: 10, warning: 5 })}
            description={`Risk Level: ${prediction.riskLevel.toUpperCase()}`}
          />
        </View>
      )}

      {/* Adaptive Metrics */}
      {metrics.adaptive && (
        <View style={styles.metricsSection}>
          <Text style={styles.sectionTitle}>Adaptive Metrics</Text>
          
          <AdaptiveMetricCard
            title="User Behavior Patterns"
            value={metrics.adaptive.userBehaviorPatterns.size}
            unit="patterns"
            status={getStatus(metrics.adaptive.userBehaviorPatterns.size, { excellent: 10, good: 5, warning: 2 })}
            description="Tracked user interaction patterns"
          />
          
          <AdaptiveMetricCard
            title="Performance Trends"
            value={metrics.adaptive.performanceTrends.size}
            unit="metrics"
            status={getStatus(metrics.adaptive.performanceTrends.size, { excellent: 8, good: 5, warning: 3 })}
            description="Active performance trend tracking"
          />
          
          <AdaptiveMetricCard
            title="Cache Effectiveness"
            value={metrics.adaptive.cacheEffectiveness.size}
            unit="strategies"
            status={getStatus(metrics.adaptive.cacheEffectiveness.size, { excellent: 5, good: 3, warning: 1 })}
            description="Optimized caching strategies"
          />
          
          <AdaptiveMetricCard
            title="Resource Utilization"
            value={metrics.adaptive.resourceUtilization.size}
            unit="resources"
            status={getStatus(metrics.adaptive.resourceUtilization.size, { excellent: 6, good: 4, warning: 2 })}
            description="Monitored resource types"
          />
        </View>
      )}

      {/* Optimization History */}
      {metrics.adaptive?.optimizationHistory && metrics.adaptive.optimizationHistory.length > 0 && (
        <View style={styles.historySection}>
          <Text style={styles.sectionTitle}>Recent Optimizations</Text>
          {metrics.adaptive.optimizationHistory.slice(-5).map((opt: any, index: number) => (
            <View key={index} style={styles.historyItem}>
              <Text style={styles.historyOptimization}>{opt.optimization}</Text>
              <Text style={[styles.historyStatus, { color: opt.success ? '#4CAF50' : '#F44336' }]}>
                {opt.success ? 'Success' : 'Failed'}
              </Text>
              <Text style={styles.historyTime}>
                {new Date(opt.timestamp).toLocaleTimeString()}
              </Text>
            </View>
          ))}
        </View>
      )}

      {/* Recommendations */}
      {prediction?.recommendations && prediction.recommendations.length > 0 && (
        <View style={styles.recommendationsSection}>
          <Text style={styles.sectionTitle}>AI Recommendations</Text>
          {prediction.recommendations.map((rec: string, index: number) => (
            <View key={index} style={styles.recommendationItem}>
              <Text style={styles.recommendationBullet}>•</Text>
              <Text style={styles.recommendationText}>{rec}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  header: {
    padding: 20,
    backgroundColor: '#fff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 5,
  },
  lastUpdate: {
    fontSize: 12,
    color: '#666',
  },
  scoreContainer: {
    padding: 20,
    backgroundColor: '#fff',
    margin: 10,
    borderRadius: 10,
    alignItems: 'center',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#666',
    marginBottom: 10,
  },
  scoreValue: {
    fontSize: 48,
    fontWeight: 'bold',
    marginBottom: 5,
  },
  scoreDescription: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  actionButtons: {
    padding: 10,
    gap: 10,
  },
  actionButton: {
    padding: 15,
    borderRadius: 8,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#2196F3',
  },
  secondaryButton: {
    backgroundColor: '#4CAF50',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  predictionSection: {
    margin: 10,
    gap: 10,
  },
  metricsSection: {
    margin: 10,
    gap: 10,
  },
  historySection: {
    margin: 10,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
  },
  recommendationsSection: {
    margin: 10,
    backgroundColor: '#fff',
    borderRadius: 10,
    padding: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  metricCard: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    borderLeftWidth: 4,
    marginBottom: 10,
  },
  metricHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 10,
  },
  metricTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  statusIcon: {
    fontSize: 16,
  },
  metricValue: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 5,
  },
  valueText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
  },
  unitText: {
    fontSize: 16,
    color: '#666',
  },
  trendText: {
    fontSize: 14,
    fontWeight: '600',
  },
  metricDescription: {
    fontSize: 12,
    color: '#666',
  },
  historyItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  historyOptimization: {
    fontSize: 14,
    fontWeight: '500',
    color: '#333',
    flex: 1,
  },
  historyStatus: {
    fontSize: 12,
    fontWeight: '600',
    marginHorizontal: 10,
  },
  historyTime: {
    fontSize: 12,
    color: '#666',
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  recommendationBullet: {
    fontSize: 16,
    color: '#2196F3',
    marginRight: 8,
    marginTop: 2,
  },
  recommendationText: {
    fontSize: 14,
    color: '#333',
    flex: 1,
    lineHeight: 20,
  },
}); 