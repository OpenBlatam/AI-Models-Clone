/**
 * @fileoverview AI insights dashboard component
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
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { aiAnalyticsEngine, AIAnalyticsInsight, AIAnalyticsDataPoint } from '../../lib/ai/ai-analytics-engine';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface InsightCardProps {
  insight: AIAnalyticsInsight;
  onViewDetails: (insight: AIAnalyticsInsight) => void;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  change?: number;
  icon: string;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
}

// ============================================================================
// INSIGHT CARD COMPONENT
// ============================================================================

const InsightCard: React.FC<InsightCardProps> = ({ insight, onViewDetails }) => {
  const getImpactColor = (impact: string): string => {
    switch (impact) {
      case 'critical': return '#FF3B30';
      case 'high': return '#FF9500';
      case 'medium': return '#FFCC00';
      case 'low': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'trend': return '📈';
      case 'anomaly': return '⚠️';
      case 'prediction': return '🔮';
      case 'recommendation': return '💡';
      case 'pattern': return '🔍';
      default: return '📊';
    }
  };

  return (
    <TouchableOpacity
      style={[styles.insightCard, { borderLeftColor: getImpactColor(insight.impact) }]}
      onPress={() => onViewDetails(insight)}
      activeOpacity={0.7}
    >
      <View style={styles.insightHeader}>
        <View style={styles.insightTitleRow}>
          <Text style={styles.insightTypeIcon}>{getTypeIcon(insight.type)}</Text>
          <Text style={styles.insightTitle}>{insight.title}</Text>
        </View>
        <View style={[styles.impactBadge, { backgroundColor: getImpactColor(insight.impact) }]}>
          <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
        </View>
      </View>
      
      <Text style={styles.insightDescription}>{insight.description}</Text>
      
      <View style={styles.insightData}>
        <View style={styles.dataRow}>
          <Text style={styles.dataLabel}>Current Value:</Text>
          <Text style={styles.dataValue}>{insight.data.current.toFixed(2)}</Text>
        </View>
        {insight.data.previous && (
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Previous:</Text>
            <Text style={styles.dataValue}>{insight.data.previous.toFixed(2)}</Text>
          </View>
        )}
        {insight.data.trend && (
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Trend:</Text>
            <Text style={[styles.dataValue, { color: insight.data.trend === 'increasing' ? '#FF3B30' : '#34C759' }]}>
              {insight.data.trend === 'increasing' ? '↗️' : '↘️'} {insight.data.trend}
            </Text>
          </View>
        )}
      </View>
      
      <View style={styles.confidenceBar}>
        <Text style={styles.confidenceLabel}>Confidence: {(insight.confidence * 100).toFixed(0)}%</Text>
        <View style={styles.confidenceBarBackground}>
          <View 
            style={[
              styles.confidenceBarFill, 
              { width: `${insight.confidence * 100}%` }
            ]} 
          />
        </View>
      </View>
      
      {insight.recommendations.length > 0 && (
        <View style={styles.recommendations}>
          <Text style={styles.recommendationsTitle}>Recommendations:</Text>
          {insight.recommendations.slice(0, 2).map((rec, index) => (
            <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
          ))}
          {insight.recommendations.length > 2 && (
            <Text style={styles.moreRecommendations}>
              +{insight.recommendations.length - 2} more recommendations
            </Text>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
};

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend, change, icon, color }) => {
  const getTrendIcon = (trend?: string): string => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '→';
      default: return '';
    }
  };

  const getTrendColor = (trend?: string): string => {
    switch (trend) {
      case 'up': return '#34C759';
      case 'down': return '#FF3B30';
      case 'stable': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <View style={styles.metricHeader}>
        <Text style={styles.metricIcon}>{icon}</Text>
        <Text style={styles.metricTitle}>{title}</Text>
      </View>
      
      <Text style={styles.metricValue}>{value}</Text>
      
      {trend && change && (
        <View style={styles.metricTrend}>
          <Text style={[styles.trendIcon, { color: getTrendColor(trend) }]}>
            {getTrendIcon(trend)}
          </Text>
          <Text style={[styles.trendValue, { color: getTrendColor(trend) }]}>
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </Text>
        </View>
      )}
    </View>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

/**
 * AI Insights Dashboard Component
 * Comprehensive dashboard for AI analytics and insights
 */
export function AIInsightsDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'insights' | 'metrics' | 'alerts' | 'reports'>('overview');
  const [insights, setInsights] = useState<AIAnalyticsInsight[]>([]);
  const [dataPoints, setDataPoints] = useState<AIAnalyticsDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState<AIAnalyticsInsight | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    initializeDashboard();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refreshData();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  const initializeDashboard = useCallback(async () => {
    setIsLoading(true);
    try {
      // Generate initial insights
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(newInsights);

      // Get recent data points
      const recentDataPoints = aiAnalyticsEngine.getDataPoints({
        startTime: Date.now() - (24 * 60 * 60 * 1000), // Last 24 hours
      });
      setDataPoints(recentDataPoints);

      // Set up event listeners
      aiAnalyticsEngine.on('insightGenerated', (insight: AIAnalyticsInsight) => {
        setInsights(prev => [insight, ...prev.filter(i => i.id !== insight.id)]);
      });

      aiAnalyticsEngine.on('dataPointAdded', (dataPoint: AIAnalyticsDataPoint) => {
        setDataPoints(prev => [dataPoint, ...prev.slice(0, 999)]); // Keep last 1000 data points
      });

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
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(newInsights);

      const recentDataPoints = aiAnalyticsEngine.getDataPoints({
        startTime: Date.now() - (24 * 60 * 60 * 1000),
      });
      setDataPoints(recentDataPoints);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewInsightDetails = useCallback((insight: AIAnalyticsInsight) => {
    setSelectedInsight(insight);
    Alert.alert(
      insight.title,
      `${insight.description}\n\nRecommendations:\n${insight.recommendations.map(rec => `• ${rec}`).join('\n')}`,
      [{ text: 'OK', onPress: () => setSelectedInsight(null) }]
    );
  }, []);

  const handleGenerateInsights = useCallback(async () => {
    setIsLoading(true);
    try {
      const newInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);
      Alert.alert('Success', `Generated ${newInsights.length} new insights`);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate insights');
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
    const recentInsights = insights.slice(0, 5);
    const criticalInsights = insights.filter(i => i.impact === 'critical' || i.impact === 'high');

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
          <Text style={styles.sectionTitle}>System Statistics</Text>
          <View style={styles.statsGrid}>
            <MetricCard
              title="Data Points"
              value={stats.totalDataPoints.toLocaleString()}
              icon="📊"
              color="#007AFF"
            />
            <MetricCard
              title="Insights"
              value={stats.totalInsights}
              icon="💡"
              color="#34C759"
            />
            <MetricCard
              title="Dashboards"
              value={stats.totalDashboards}
              icon="📈"
              color="#FF9500"
            />
            <MetricCard
              title="Alerts"
              value={stats.totalAlerts}
              icon="⚠️"
              color="#FF3B30"
            />
          </View>
        </View>

        {/* Critical Insights */}
        {criticalInsights.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Critical Insights</Text>
            {criticalInsights.slice(0, 3).map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
            ))}
          </View>
        )}

        {/* Recent Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Insights</Text>
          {recentInsights.length > 0 ? (
            recentInsights.map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
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

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="🔄 Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.actionButton}
              variant="primary"
              size="small"
              isDisabled={isLoading}
            />
            <AccessibleButton
              title="📊 View Metrics"
              onPress={() => handleTabChange('metrics')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="⚠️ View Alerts"
              onPress={() => handleTabChange('alerts')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderInsightsTab = (): JSX.Element => {
    const insightsByCategory = insights.reduce((acc, insight) => {
      if (!acc[insight.category]) {
        acc[insight.category] = [];
      }
      acc[insight.category].push(insight);
      return acc;
    }, {} as Record<string, AIAnalyticsInsight[]>);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {Object.entries(insightsByCategory).map(([category, categoryInsights]) => (
          <View key={category} style={styles.section}>
            <Text style={styles.sectionTitle}>{category.charAt(0).toUpperCase() + category.slice(1)} Insights</Text>
            {categoryInsights.map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
            ))}
          </View>
        ))}
        
        {insights.length === 0 && (
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
      </ScrollView>
    );
  };

  const renderMetricsTab = (): JSX.Element => {
    const metricsByCategory = dataPoints.reduce((acc, dp) => {
      if (!acc[dp.category]) {
        acc[dp.category] = new Map();
      }
      if (!acc[dp.category].has(dp.metric)) {
        acc[dp.category].set(dp.metric, []);
      }
      acc[dp.category].get(dp.metric)!.push(dp);
      return acc;
    }, {} as Record<string, Map<string, AIAnalyticsDataPoint[]>>);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {Object.entries(metricsByCategory).map(([category, metrics]) => (
          <View key={category} style={styles.section}>
            <Text style={styles.sectionTitle}>{category.charAt(0).toUpperCase() + category.slice(1)} Metrics</Text>
            {Array.from(metrics.entries()).map(([metric, dataPoints]) => {
              const avgValue = dataPoints.reduce((sum, dp) => sum + dp.value, 0) / dataPoints.length;
              const latestValue = dataPoints[0]?.value || 0;
              
              return (
                <View key={metric} style={styles.metricRow}>
                  <View style={styles.metricInfo}>
                    <Text style={styles.metricName}>{metric}</Text>
                    <Text style={styles.metricDescription}>
                      {dataPoints.length} data points
                    </Text>
                  </View>
                  <View style={styles.metricValues}>
                    <Text style={styles.metricCurrentValue}>{latestValue.toFixed(2)}</Text>
                    <Text style={styles.metricAvgValue}>Avg: {avgValue.toFixed(2)}</Text>
                  </View>
                </View>
              );
            })}
          </View>
        ))}
        
        {dataPoints.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No metrics available</Text>
          </View>
        )}
      </ScrollView>
    );
  };

  const renderAlertsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Alert Management</Text>
        <Text style={styles.sectionDescription}>
          Configure and manage analytics alerts for proactive monitoring.
        </Text>
        
        <View style={styles.alertPlaceholder}>
          <Text style={styles.placeholderText}>🚨</Text>
          <Text style={styles.placeholderTitle}>Alert Management</Text>
          <Text style={styles.placeholderDescription}>
            Alert management features will be implemented in the next phase.
          </Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderReportsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Analytics Reports</Text>
        <Text style={styles.sectionDescription}>
          Generate and schedule comprehensive analytics reports.
        </Text>
        
        <View style={styles.reportPlaceholder}>
          <Text style={styles.placeholderText}>📊</Text>
          <Text style={styles.placeholderTitle}>Report Generation</Text>
          <Text style={styles.placeholderDescription}>
            Report generation features will be implemented in the next phase.
          </Text>
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
        <Text style={styles.headerTitle}>AI Insights Dashboard</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Analytics & Predictive Insights
        </Text>
        <View style={styles.headerControls}>
          <View style={styles.autoRefreshControl}>
            <Text style={styles.autoRefreshLabel}>Auto-refresh</Text>
            <Switch
              value={autoRefresh}
              onValueChange={setAutoRefresh}
              trackColor={{ false: '#767577', true: '#007AFF' }}
              thumbColor={autoRefresh ? '#ffffff' : '#f4f3f4'}
            />
          </View>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('insights', 'Insights')}
        {renderTabButton('metrics', 'Metrics')}
        {renderTabButton('alerts', 'Alerts')}
        {renderTabButton('reports', 'Reports')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'insights' && renderInsightsTab()}
        {activeTab === 'metrics' && renderMetricsTab()}
        {activeTab === 'alerts' && renderAlertsTab()}
        {activeTab === 'reports' && renderReportsTab()}
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
    marginBottom: 12,
  },
  headerControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  autoRefreshControl: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  autoRefreshLabel: {
    color: '#ffffff',
    fontSize: 14,
    marginRight: 8,
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
  statsGrid: {
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
    borderLeftWidth: 4,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  metricTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  metricTrend: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendIcon: {
    fontSize: 16,
    marginRight: 4,
  },
  trendValue: {
    fontSize: 12,
    fontWeight: '600',
  },
  insightCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  insightTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  insightTypeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  insightTitle: {
    fontSize: 16,
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
  insightDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  insightData: {
    marginBottom: 12,
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  dataLabel: {
    fontSize: 12,
    color: '#666',
  },
  dataValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
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
  moreRecommendations: {
    fontSize: 12,
    color: '#007AFF',
    fontStyle: 'italic',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  metricDescription: {
    fontSize: 12,
    color: '#666',
  },
  metricValues: {
    alignItems: 'flex-end',
  },
  metricCurrentValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  metricAvgValue: {
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
    paddingVertical: 12,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 120,
  },
  generateButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    marginTop: 16,
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
  alertPlaceholder: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  reportPlaceholder: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  placeholderText: {
    fontSize: 48,
    marginBottom: 16,
  },
  placeholderTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  placeholderDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
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

export default AIInsightsDashboard;
 * @fileoverview AI insights dashboard component
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
  RefreshControl,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { aiAnalyticsEngine, AIAnalyticsInsight, AIAnalyticsDataPoint } from '../../lib/ai/ai-analytics-engine';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface InsightCardProps {
  insight: AIAnalyticsInsight;
  onViewDetails: (insight: AIAnalyticsInsight) => void;
}

interface MetricCardProps {
  title: string;
  value: string | number;
  trend?: 'up' | 'down' | 'stable';
  change?: number;
  icon: string;
  color: string;
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    color: string;
  }[];
}

// ============================================================================
// INSIGHT CARD COMPONENT
// ============================================================================

const InsightCard: React.FC<InsightCardProps> = ({ insight, onViewDetails }) => {
  const getImpactColor = (impact: string): string => {
    switch (impact) {
      case 'critical': return '#FF3B30';
      case 'high': return '#FF9500';
      case 'medium': return '#FFCC00';
      case 'low': return '#34C759';
      default: return '#8E8E93';
    }
  };

  const getTypeIcon = (type: string): string => {
    switch (type) {
      case 'trend': return '📈';
      case 'anomaly': return '⚠️';
      case 'prediction': return '🔮';
      case 'recommendation': return '💡';
      case 'pattern': return '🔍';
      default: return '📊';
    }
  };

  return (
    <TouchableOpacity
      style={[styles.insightCard, { borderLeftColor: getImpactColor(insight.impact) }]}
      onPress={() => onViewDetails(insight)}
      activeOpacity={0.7}
    >
      <View style={styles.insightHeader}>
        <View style={styles.insightTitleRow}>
          <Text style={styles.insightTypeIcon}>{getTypeIcon(insight.type)}</Text>
          <Text style={styles.insightTitle}>{insight.title}</Text>
        </View>
        <View style={[styles.impactBadge, { backgroundColor: getImpactColor(insight.impact) }]}>
          <Text style={styles.impactBadgeText}>{insight.impact.toUpperCase()}</Text>
        </View>
      </View>
      
      <Text style={styles.insightDescription}>{insight.description}</Text>
      
      <View style={styles.insightData}>
        <View style={styles.dataRow}>
          <Text style={styles.dataLabel}>Current Value:</Text>
          <Text style={styles.dataValue}>{insight.data.current.toFixed(2)}</Text>
        </View>
        {insight.data.previous && (
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Previous:</Text>
            <Text style={styles.dataValue}>{insight.data.previous.toFixed(2)}</Text>
          </View>
        )}
        {insight.data.trend && (
          <View style={styles.dataRow}>
            <Text style={styles.dataLabel}>Trend:</Text>
            <Text style={[styles.dataValue, { color: insight.data.trend === 'increasing' ? '#FF3B30' : '#34C759' }]}>
              {insight.data.trend === 'increasing' ? '↗️' : '↘️'} {insight.data.trend}
            </Text>
          </View>
        )}
      </View>
      
      <View style={styles.confidenceBar}>
        <Text style={styles.confidenceLabel}>Confidence: {(insight.confidence * 100).toFixed(0)}%</Text>
        <View style={styles.confidenceBarBackground}>
          <View 
            style={[
              styles.confidenceBarFill, 
              { width: `${insight.confidence * 100}%` }
            ]} 
          />
        </View>
      </View>
      
      {insight.recommendations.length > 0 && (
        <View style={styles.recommendations}>
          <Text style={styles.recommendationsTitle}>Recommendations:</Text>
          {insight.recommendations.slice(0, 2).map((rec, index) => (
            <Text key={index} style={styles.recommendationItem}>• {rec}</Text>
          ))}
          {insight.recommendations.length > 2 && (
            <Text style={styles.moreRecommendations}>
              +{insight.recommendations.length - 2} more recommendations
            </Text>
          )}
        </View>
      )}
    </TouchableOpacity>
  );
};

// ============================================================================
// METRIC CARD COMPONENT
// ============================================================================

const MetricCard: React.FC<MetricCardProps> = ({ title, value, trend, change, icon, color }) => {
  const getTrendIcon = (trend?: string): string => {
    switch (trend) {
      case 'up': return '↗️';
      case 'down': return '↘️';
      case 'stable': return '→';
      default: return '';
    }
  };

  const getTrendColor = (trend?: string): string => {
    switch (trend) {
      case 'up': return '#34C759';
      case 'down': return '#FF3B30';
      case 'stable': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={[styles.metricCard, { borderLeftColor: color }]}>
      <View style={styles.metricHeader}>
        <Text style={styles.metricIcon}>{icon}</Text>
        <Text style={styles.metricTitle}>{title}</Text>
      </View>
      
      <Text style={styles.metricValue}>{value}</Text>
      
      {trend && change && (
        <View style={styles.metricTrend}>
          <Text style={[styles.trendIcon, { color: getTrendColor(trend) }]}>
            {getTrendIcon(trend)}
          </Text>
          <Text style={[styles.trendValue, { color: getTrendColor(trend) }]}>
            {change > 0 ? '+' : ''}{change.toFixed(1)}%
          </Text>
        </View>
      )}
    </View>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

/**
 * AI Insights Dashboard Component
 * Comprehensive dashboard for AI analytics and insights
 */
export function AIInsightsDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'insights' | 'metrics' | 'alerts' | 'reports'>('overview');
  const [insights, setInsights] = useState<AIAnalyticsInsight[]>([]);
  const [dataPoints, setDataPoints] = useState<AIAnalyticsDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [selectedInsight, setSelectedInsight] = useState<AIAnalyticsInsight | null>(null);
  const [autoRefresh, setAutoRefresh] = useState(true);

  // ============================================================================
  // EFFECTS
  // ============================================================================

  useEffect(() => {
    initializeDashboard();
  }, []);

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(() => {
        refreshData();
      }, 30000); // Refresh every 30 seconds

      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  // ============================================================================
  // INITIALIZATION
  // ============================================================================

  const initializeDashboard = useCallback(async () => {
    setIsLoading(true);
    try {
      // Generate initial insights
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(newInsights);

      // Get recent data points
      const recentDataPoints = aiAnalyticsEngine.getDataPoints({
        startTime: Date.now() - (24 * 60 * 60 * 1000), // Last 24 hours
      });
      setDataPoints(recentDataPoints);

      // Set up event listeners
      aiAnalyticsEngine.on('insightGenerated', (insight: AIAnalyticsInsight) => {
        setInsights(prev => [insight, ...prev.filter(i => i.id !== insight.id)]);
      });

      aiAnalyticsEngine.on('dataPointAdded', (dataPoint: AIAnalyticsDataPoint) => {
        setDataPoints(prev => [dataPoint, ...prev.slice(0, 999)]); // Keep last 1000 data points
      });

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
      const newInsights = aiAnalyticsEngine.generateInsights('24h');
      setInsights(newInsights);

      const recentDataPoints = aiAnalyticsEngine.getDataPoints({
        startTime: Date.now() - (24 * 60 * 60 * 1000),
      });
      setDataPoints(recentDataPoints);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewInsightDetails = useCallback((insight: AIAnalyticsInsight) => {
    setSelectedInsight(insight);
    Alert.alert(
      insight.title,
      `${insight.description}\n\nRecommendations:\n${insight.recommendations.map(rec => `• ${rec}`).join('\n')}`,
      [{ text: 'OK', onPress: () => setSelectedInsight(null) }]
    );
  }, []);

  const handleGenerateInsights = useCallback(async () => {
    setIsLoading(true);
    try {
      const newInsights = aiAnalyticsEngine.generateInsights('1h');
      setInsights(prev => [...newInsights, ...prev.filter(i => !newInsights.some(ni => ni.id === i.id))]);
      Alert.alert('Success', `Generated ${newInsights.length} new insights`);
    } catch (error) {
      Alert.alert('Error', 'Failed to generate insights');
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
    const recentInsights = insights.slice(0, 5);
    const criticalInsights = insights.filter(i => i.impact === 'critical' || i.impact === 'high');

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
          <Text style={styles.sectionTitle}>System Statistics</Text>
          <View style={styles.statsGrid}>
            <MetricCard
              title="Data Points"
              value={stats.totalDataPoints.toLocaleString()}
              icon="📊"
              color="#007AFF"
            />
            <MetricCard
              title="Insights"
              value={stats.totalInsights}
              icon="💡"
              color="#34C759"
            />
            <MetricCard
              title="Dashboards"
              value={stats.totalDashboards}
              icon="📈"
              color="#FF9500"
            />
            <MetricCard
              title="Alerts"
              value={stats.totalAlerts}
              icon="⚠️"
              color="#FF3B30"
            />
          </View>
        </View>

        {/* Critical Insights */}
        {criticalInsights.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Critical Insights</Text>
            {criticalInsights.slice(0, 3).map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
            ))}
          </View>
        )}

        {/* Recent Insights */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Recent Insights</Text>
          {recentInsights.length > 0 ? (
            recentInsights.map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
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

        {/* Quick Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Quick Actions</Text>
          <View style={styles.actionButtons}>
            <AccessibleButton
              title="🔄 Generate Insights"
              onPress={handleGenerateInsights}
              style={styles.actionButton}
              variant="primary"
              size="small"
              isDisabled={isLoading}
            />
            <AccessibleButton
              title="📊 View Metrics"
              onPress={() => handleTabChange('metrics')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="⚠️ View Alerts"
              onPress={() => handleTabChange('alerts')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderInsightsTab = (): JSX.Element => {
    const insightsByCategory = insights.reduce((acc, insight) => {
      if (!acc[insight.category]) {
        acc[insight.category] = [];
      }
      acc[insight.category].push(insight);
      return acc;
    }, {} as Record<string, AIAnalyticsInsight[]>);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {Object.entries(insightsByCategory).map(([category, categoryInsights]) => (
          <View key={category} style={styles.section}>
            <Text style={styles.sectionTitle}>{category.charAt(0).toUpperCase() + category.slice(1)} Insights</Text>
            {categoryInsights.map(insight => (
              <InsightCard
                key={insight.id}
                insight={insight}
                onViewDetails={handleViewInsightDetails}
              />
            ))}
          </View>
        ))}
        
        {insights.length === 0 && (
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
      </ScrollView>
    );
  };

  const renderMetricsTab = (): JSX.Element => {
    const metricsByCategory = dataPoints.reduce((acc, dp) => {
      if (!acc[dp.category]) {
        acc[dp.category] = new Map();
      }
      if (!acc[dp.category].has(dp.metric)) {
        acc[dp.category].set(dp.metric, []);
      }
      acc[dp.category].get(dp.metric)!.push(dp);
      return acc;
    }, {} as Record<string, Map<string, AIAnalyticsDataPoint[]>>);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {Object.entries(metricsByCategory).map(([category, metrics]) => (
          <View key={category} style={styles.section}>
            <Text style={styles.sectionTitle}>{category.charAt(0).toUpperCase() + category.slice(1)} Metrics</Text>
            {Array.from(metrics.entries()).map(([metric, dataPoints]) => {
              const avgValue = dataPoints.reduce((sum, dp) => sum + dp.value, 0) / dataPoints.length;
              const latestValue = dataPoints[0]?.value || 0;
              
              return (
                <View key={metric} style={styles.metricRow}>
                  <View style={styles.metricInfo}>
                    <Text style={styles.metricName}>{metric}</Text>
                    <Text style={styles.metricDescription}>
                      {dataPoints.length} data points
                    </Text>
                  </View>
                  <View style={styles.metricValues}>
                    <Text style={styles.metricCurrentValue}>{latestValue.toFixed(2)}</Text>
                    <Text style={styles.metricAvgValue}>Avg: {avgValue.toFixed(2)}</Text>
                  </View>
                </View>
              );
            })}
          </View>
        ))}
        
        {dataPoints.length === 0 && (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No metrics available</Text>
          </View>
        )}
      </ScrollView>
    );
  };

  const renderAlertsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Alert Management</Text>
        <Text style={styles.sectionDescription}>
          Configure and manage analytics alerts for proactive monitoring.
        </Text>
        
        <View style={styles.alertPlaceholder}>
          <Text style={styles.placeholderText}>🚨</Text>
          <Text style={styles.placeholderTitle}>Alert Management</Text>
          <Text style={styles.placeholderDescription}>
            Alert management features will be implemented in the next phase.
          </Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderReportsTab = (): JSX.Element => (
    <ScrollView style={styles.tabContent} showsVerticalScrollIndicator={false}>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Analytics Reports</Text>
        <Text style={styles.sectionDescription}>
          Generate and schedule comprehensive analytics reports.
        </Text>
        
        <View style={styles.reportPlaceholder}>
          <Text style={styles.placeholderText}>📊</Text>
          <Text style={styles.placeholderTitle}>Report Generation</Text>
          <Text style={styles.placeholderDescription}>
            Report generation features will be implemented in the next phase.
          </Text>
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
        <Text style={styles.headerTitle}>AI Insights Dashboard</Text>
        <Text style={styles.headerSubtitle}>
          Intelligent Analytics & Predictive Insights
        </Text>
        <View style={styles.headerControls}>
          <View style={styles.autoRefreshControl}>
            <Text style={styles.autoRefreshLabel}>Auto-refresh</Text>
            <Switch
              value={autoRefresh}
              onValueChange={setAutoRefresh}
              trackColor={{ false: '#767577', true: '#007AFF' }}
              thumbColor={autoRefresh ? '#ffffff' : '#f4f3f4'}
            />
          </View>
        </View>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('insights', 'Insights')}
        {renderTabButton('metrics', 'Metrics')}
        {renderTabButton('alerts', 'Alerts')}
        {renderTabButton('reports', 'Reports')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'insights' && renderInsightsTab()}
        {activeTab === 'metrics' && renderMetricsTab()}
        {activeTab === 'alerts' && renderAlertsTab()}
        {activeTab === 'reports' && renderReportsTab()}
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
    marginBottom: 12,
  },
  headerControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  autoRefreshControl: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  autoRefreshLabel: {
    color: '#ffffff',
    fontSize: 14,
    marginRight: 8,
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
  statsGrid: {
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
    borderLeftWidth: 4,
  },
  metricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  metricTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  metricValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 4,
  },
  metricTrend: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  trendIcon: {
    fontSize: 16,
    marginRight: 4,
  },
  trendValue: {
    fontSize: 12,
    fontWeight: '600',
  },
  insightCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    borderLeftWidth: 4,
  },
  insightHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  insightTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  insightTypeIcon: {
    fontSize: 20,
    marginRight: 8,
  },
  insightTitle: {
    fontSize: 16,
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
  insightDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  insightData: {
    marginBottom: 12,
  },
  dataRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  dataLabel: {
    fontSize: 12,
    color: '#666',
  },
  dataValue: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
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
  moreRecommendations: {
    fontSize: 12,
    color: '#007AFF',
    fontStyle: 'italic',
  },
  metricRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  metricInfo: {
    flex: 1,
  },
  metricName: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  metricDescription: {
    fontSize: 12,
    color: '#666',
  },
  metricValues: {
    alignItems: 'flex-end',
  },
  metricCurrentValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 2,
  },
  metricAvgValue: {
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
    paddingVertical: 12,
    marginHorizontal: 4,
    marginBottom: 8,
    minWidth: 120,
  },
  generateButton: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    marginTop: 16,
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
  alertPlaceholder: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  reportPlaceholder: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#f8f9fa',
    borderRadius: 8,
  },
  placeholderText: {
    fontSize: 48,
    marginBottom: 16,
  },
  placeholderTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  placeholderDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    lineHeight: 20,
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

export default AIInsightsDashboard;


