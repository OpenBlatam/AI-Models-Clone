/**
 * @fileoverview Comprehensive AI Platform Demo - Master Demo Component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIEnterpriseDemo } from './ai-enterprise-demo';
import { AIGlobalDeploymentDashboard } from '../dashboard/ai-global-deployment-dashboard';
import { AIEnterpriseDashboard } from '../dashboard/ai-enterprise-dashboard';
import { AIModelManagementDashboard } from '../dashboard/ai-model-management-dashboard';
import { AIInsightsDashboard } from '../dashboard/ai-insights-dashboard';
import { AIWorkflowAutomationDashboard } from '../dashboard/ai-workflow-automation-dashboard';
import { AIAutomationDashboard } from '../dashboard/ai-automation-dashboard';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface SystemCardProps {
  title: string;
  description: string;
  icon: string;
  status: 'active' | 'maintenance' | 'offline';
  features: string[];
  onOpen: () => void;
  onViewDetails: () => void;
}

interface StatsCardProps {
  title: string;
  value: string;
  subtitle: string;
  trend?: 'up' | 'down' | 'stable';
  color?: string;
}

// ============================================================================
// SYSTEM CARD COMPONENT
// ============================================================================

const SystemCard: React.FC<SystemCardProps> = ({ 
  title, 
  description, 
  icon, 
  status, 
  features, 
  onOpen, 
  onViewDetails 
}) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'maintenance': return '#FF9500';
      case 'offline': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.systemCard}>
      <View style={styles.systemHeader}>
        <View style={styles.systemInfo}>
          <Text style={styles.systemIcon}>{icon}</Text>
          <View style={styles.systemDetails}>
            <Text style={styles.systemTitle}>{title}</Text>
            <Text style={styles.systemDescription}>{description}</Text>
          </View>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(status) }]}>
          <Text style={styles.statusBadgeText}>{status.toUpperCase()}</Text>
        </View>
      </View>
      
      <View style={styles.systemFeatures}>
        <Text style={styles.featuresTitle}>Key Features:</Text>
        {features.slice(0, 3).map((feature, index) => (
          <Text key={index} style={styles.featureItem}>• {feature}</Text>
        ))}
        {features.length > 3 && (
          <Text style={styles.featureItem}>• +{features.length - 3} more features</Text>
        )}
      </View>
      
      <View style={styles.systemActions}>
        <AccessibleButton
          title="Open System"
          onPress={onOpen}
          style={styles.systemActionButton}
          variant="primary"
          size="small"
        />
        <AccessibleButton
          title="View Details"
          onPress={onViewDetails}
          style={styles.systemActionButton}
          variant="outline"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// STATS CARD COMPONENT
// ============================================================================

const StatsCard: React.FC<StatsCardProps> = ({ title, value, subtitle, trend, color = '#007AFF' }) => {
  const getTrendIcon = (trend?: string): string => {
    switch (trend) {
      case 'up': return '📈';
      case 'down': return '📉';
      case 'stable': return '➡️';
      default: return '';
    }
  };

  return (
    <View style={styles.statsCard}>
      <Text style={styles.statsTitle}>{title}</Text>
      <View style={styles.statsValueContainer}>
        <Text style={[styles.statsValue, { color }]}>{value}</Text>
        {trend && (
          <Text style={styles.trendIcon}>{getTrendIcon(trend)}</Text>
        )}
      </View>
      <Text style={styles.statsSubtitle}>{subtitle}</Text>
    </View>
  );
};

// ============================================================================
// MAIN DEMO COMPONENT
// ============================================================================

export function ComprehensiveAIPlatformDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeView, setActiveView] = useState<'overview' | 'systems' | 'analytics' | 'deployment'>('overview');
  const [selectedSystem, setSelectedSystem] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [systemStats, setSystemStats] = useState({
    totalSystems: 7,
    activeSystems: 7,
    totalUsers: 1250,
    activeUsers: 1180,
    totalModels: 45,
    activeModels: 42,
    totalWorkflows: 23,
    activeWorkflows: 21,
    totalDeployments: 8,
    activeDeployments: 8,
    globalRegions: 4,
    activeRegions: 4,
    complianceScore: 98.5,
    systemUptime: 99.9,
    performanceScore: 96.8,
  });

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
      // Simulate initialization
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSystemStats(prev => ({ ...prev }));
    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo');
    } finally {
      setIsLoading(false);
    }
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleViewChange = useCallback((view: typeof activeView) => {
    setActiveView(view);
  }, []);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      // Simulate refresh
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSystemStats(prev => ({ ...prev }));
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh data');
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  const handleOpenSystem = useCallback((systemId: string) => {
    setSelectedSystem(systemId);
  }, []);

  const handleViewSystemDetails = useCallback((systemId: string) => {
    const systemDetails = {
      'ai-models': 'AI Model Management System - Complete model lifecycle management with automated training, deployment, and optimization.',
      'ai-analytics': 'AI Analytics & Predictive Systems - Advanced analytics engine with ML-powered insights and predictions.',
      'ai-automation': 'AI Workflow Automation & Orchestration - Intelligent automation with rule engines and task orchestration.',
      'ai-enterprise': 'AI Enterprise Platform - Multi-tenant platform with compliance, audit logging, and enterprise features.',
      'ai-deployment': 'AI Global Deployment & Scaling - Global deployment system with auto-scaling and multi-region support.',
      'ai-security': 'AI Security & Authentication - Comprehensive security with biometric authentication and enterprise features.',
    };

    Alert.alert(
      'System Details',
      systemDetails[systemId] || 'System details not available'
    );
  }, []);

  const handleBackToOverview = useCallback(() => {
    setSelectedSystem(null);
    setActiveView('overview');
  }, []);

  // ============================================================================
  // SYSTEM CONFIGURATIONS
  // ============================================================================

  const systems = [
    {
      id: 'ai-models',
      title: 'AI Model Management',
      description: 'Complete model lifecycle management with automated training, deployment, and optimization',
      icon: '🤖',
      status: 'active' as const,
      features: [
        'Model lifecycle management',
        'Automated training',
        'Smart deployment',
        'Performance monitoring',
        'A/B testing',
        'Version control',
        'Resource optimization',
        'Recommendation engine'
      ],
    },
    {
      id: 'ai-analytics',
      title: 'AI Analytics & Predictive',
      description: 'Advanced analytics engine with ML-powered insights and predictions',
      icon: '📊',
      status: 'active' as const,
      features: [
        'Intelligent data collection',
        'Automated insights',
        'Predictive analytics',
        'Real-time dashboards',
        'Query optimization',
        'Alert systems',
        'Funnel analysis',
        'Cohort analysis'
      ],
    },
    {
      id: 'ai-automation',
      title: 'AI Workflow Automation',
      description: 'Intelligent automation with rule engines and task orchestration',
      icon: '⚙️',
      status: 'active' as const,
      features: [
        'Rule-based automation',
        'Workflow orchestration',
        'Load balancing',
        'Task queuing',
        'Event-driven architecture',
        'System coordination',
        'Retry policies',
        'Resource constraints'
      ],
    },
    {
      id: 'ai-enterprise',
      title: 'AI Enterprise Platform',
      description: 'Multi-tenant platform with compliance, audit logging, and enterprise features',
      icon: '🏢',
      status: 'active' as const,
      features: [
        'Multi-tenant architecture',
        'Role-based access control',
        'API key management',
        'Audit logging',
        'Compliance monitoring',
        'Real-time metrics',
        'Billing tracking',
        'Security management'
      ],
    },
    {
      id: 'ai-deployment',
      title: 'AI Global Deployment',
      description: 'Global deployment system with auto-scaling and multi-region support',
      icon: '🌍',
      status: 'active' as const,
      features: [
        'Global region management',
        'Intelligent load balancing',
        'Auto-scaling',
        'CDN integration',
        'Real-time monitoring',
        'Cost optimization',
        'Disaster recovery',
        'Multi-cloud support'
      ],
    },
    {
      id: 'ai-security',
      title: 'AI Security & Authentication',
      description: 'Comprehensive security with biometric authentication and enterprise features',
      icon: '🔐',
      status: 'active' as const,
      features: [
        'Biometric authentication',
        'Encrypted storage',
        'Permission management',
        'Deep linking security',
        'Session management',
        'Security monitoring',
        'Audit trails',
        'Compliance validation'
      ],
    },
    {
      id: 'performance-monitoring',
      title: 'Performance Monitoring',
      description: 'Comprehensive performance monitoring with real-time metrics and optimization',
      icon: '📊',
      status: 'active' as const,
      features: [
        'Real-time metrics collection',
        'Intelligent alerting',
        'Performance optimization',
        'Comprehensive reporting',
        'System monitoring',
        'Performance insights',
        'Automated suggestions',
        'Trend analysis'
      ],
    },
  ];

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderViewButton = (view: typeof activeView, label: string, icon: string): JSX.Element => (
    <AccessibleButton
      title={`${icon} ${label}`}
      accessibilityLabel={`Switch to ${label} view`}
      onPress={() => handleViewChange(view)}
      style={[styles.viewButton, activeView === view && styles.viewButtonActive]}
      textStyle={[styles.viewButtonText, activeView === view && styles.viewButtonTextActive]}
      variant="ghost"
      size="small"
    />
  );

  const renderOverviewTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Platform Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🚀 Comprehensive AI Platform</Text>
        <Text style={styles.sectionDescription}>
          A world-class, production-ready AI Enterprise Platform that transforms the original Python-based Blaze AI system into a sophisticated, enterprise-grade mobile application with comprehensive AI capabilities, global scalability, and enterprise features.
        </Text>
      </View>

      {/* System Stats */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Platform Statistics</Text>
        <View style={styles.statsGrid}>
          <StatsCard
            title="Total Systems"
            value={systemStats.totalSystems.toString()}
            subtitle="AI subsystems"
            trend="stable"
            color="#007AFF"
          />
          <StatsCard
            title="Active Systems"
            value={systemStats.activeSystems.toString()}
            subtitle="Currently running"
            trend="up"
            color="#34C759"
          />
          <StatsCard
            title="Total Users"
            value={systemStats.totalUsers.toLocaleString()}
            subtitle="Platform users"
            trend="up"
            color="#AF52DE"
          />
          <StatsCard
            title="Active Users"
            value={systemStats.activeUsers.toLocaleString()}
            subtitle="Online now"
            trend="up"
            color="#34C759"
          />
          <StatsCard
            title="AI Models"
            value={systemStats.totalModels.toString()}
            subtitle="Managed models"
            trend="up"
            color="#FF9500"
          />
          <StatsCard
            title="Workflows"
            value={systemStats.totalWorkflows.toString()}
            subtitle="Automated workflows"
            trend="up"
            color="#FF3B30"
          />
          <StatsCard
            title="Global Regions"
            value={systemStats.globalRegions.toString()}
            subtitle="Deployment regions"
            trend="stable"
            color="#007AFF"
          />
          <StatsCard
            title="Compliance Score"
            value={`${systemStats.complianceScore}%`}
            subtitle="Overall compliance"
            trend="up"
            color="#34C759"
          />
        </View>
      </View>

      {/* System Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 AI Systems Overview</Text>
        <View style={styles.systemsGrid}>
          {systems.map(system => (
            <SystemCard
              key={system.id}
              title={system.title}
              description={system.description}
              icon={system.icon}
              status={system.status}
              features={system.features}
              onOpen={() => handleOpenSystem(system.id)}
              onViewDetails={() => handleViewSystemDetails(system.id)}
            />
          ))}
        </View>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Quick Actions</Text>
        <View style={styles.actionButtons}>
          <AccessibleButton
            title="🔄 Refresh All Systems"
            onPress={handleRefresh}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="📊 View Analytics"
            onPress={() => handleViewChange('analytics')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="🌍 View Deployment"
            onPress={() => handleViewChange('deployment')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="🎯 View Systems"
            onPress={() => handleViewChange('systems')}
            style={styles.actionButton}
            variant="outline"
            size="small"
          />
        </View>
      </View>

      {/* Platform Features */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>✨ Platform Features</Text>
        <View style={styles.featuresList}>
          <Text style={styles.featureItem}>🎯 Complete AI Ecosystem - From model management to global deployment</Text>
          <Text style={styles.featureItem}>🏢 Enterprise-Grade Features - Multi-tenancy, compliance, audit logging</Text>
          <Text style={styles.featureItem}>🌍 Global Scalability - Multi-region deployment with intelligent load balancing</Text>
          <Text style={styles.featureItem}>🔐 Advanced Security - Biometric authentication, encrypted storage</Text>
          <Text style={styles.featureItem}>📱 Mobile Excellence - React Native/Expo with native performance</Text>
          <Text style={styles.featureItem}>⚡ Performance Optimized - 60fps rendering, offline-first architecture</Text>
          <Text style={styles.featureItem}>🧪 Production Ready - Extensive testing, documentation, real-world scenarios</Text>
          <Text style={styles.featureItem}>📊 Business Intelligence - Advanced AI-powered analytics and insights</Text>
        </View>
      </View>
    </ScrollView>
  );

  const renderSystemsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 AI Systems Management</Text>
        <Text style={styles.sectionDescription}>
          Manage and monitor all AI subsystems from a centralized location. Each system is independently deployable and maintainable.
        </Text>
        <View style={styles.systemsGrid}>
          {systems.map(system => (
            <SystemCard
              key={system.id}
              title={system.title}
              description={system.description}
              icon={system.icon}
              status={system.status}
              features={system.features}
              onOpen={() => handleOpenSystem(system.id)}
              onViewDetails={() => handleViewSystemDetails(system.id)}
            />
          ))}
        </View>
      </View>
    </ScrollView>
  );

  const renderAnalyticsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Platform Analytics</Text>
        <Text style={styles.sectionDescription}>
          Comprehensive analytics and insights across all AI systems and platform usage.
        </Text>
        
        {/* Analytics Overview */}
        <View style={styles.analyticsOverview}>
          <View style={styles.analyticsCard}>
            <Text style={styles.analyticsTitle}>System Performance</Text>
            <Text style={styles.analyticsValue}>99.9% Uptime</Text>
            <Text style={styles.analyticsSubtitle}>Last 30 days</Text>
          </View>
          <View style={styles.analyticsCard}>
            <Text style={styles.analyticsTitle}>User Engagement</Text>
            <Text style={styles.analyticsValue}>94.2%</Text>
            <Text style={styles.analyticsSubtitle}>Active users</Text>
          </View>
          <View style={styles.analyticsCard}>
            <Text style={styles.analyticsTitle}>AI Model Usage</Text>
            <Text style={styles.analyticsValue}>2.4M</Text>
            <Text style={styles.analyticsSubtitle}>Inferences today</Text>
          </View>
          <View style={styles.analyticsCard}>
            <Text style={styles.analyticsTitle}>Workflow Executions</Text>
            <Text style={styles.analyticsValue}>15.7K</Text>
            <Text style={styles.analyticsSubtitle}>Automated tasks</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionButtons}>
          <AccessibleButton
            title="📈 View Detailed Analytics"
            onPress={() => Alert.alert('Analytics', 'Detailed analytics dashboard would open here')}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="🔍 Generate Report"
            onPress={() => Alert.alert('Report', 'Report generation would start here')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderDeploymentTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🌍 Global Deployment</Text>
        <Text style={styles.sectionDescription}>
          Monitor and manage global deployment across multiple regions with auto-scaling and load balancing.
        </Text>
        
        {/* Deployment Overview */}
        <View style={styles.deploymentOverview}>
          <View style={styles.deploymentCard}>
            <Text style={styles.deploymentTitle}>Active Regions</Text>
            <Text style={styles.deploymentValue}>{systemStats.activeRegions}</Text>
            <Text style={styles.deploymentSubtitle}>Global regions</Text>
          </View>
          <View style={styles.deploymentCard}>
            <Text style={styles.deploymentTitle}>Active Deployments</Text>
            <Text style={styles.deploymentValue}>{systemStats.activeDeployments}</Text>
            <Text style={styles.deploymentSubtitle}>Running deployments</Text>
          </View>
          <View style={styles.deploymentCard}>
            <Text style={styles.deploymentTitle}>Load Balancers</Text>
            <Text style={styles.deploymentValue}>12</Text>
            <Text style={styles.deploymentSubtitle}>Active balancers</Text>
          </View>
          <View style={styles.deploymentCard}>
            <Text style={styles.deploymentTitle}>CDN Endpoints</Text>
            <Text style={styles.deploymentValue}>8</Text>
            <Text style={styles.deploymentSubtitle}>Global endpoints</Text>
          </View>
        </View>

        {/* Quick Actions */}
        <View style={styles.actionButtons}>
          <AccessibleButton
            title="🌍 View Global Dashboard"
            onPress={() => Alert.alert('Deployment', 'Global deployment dashboard would open here')}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="📊 View Metrics"
            onPress={() => Alert.alert('Metrics', 'Deployment metrics would open here')}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderSelectedSystem = (): JSX.Element => {
    switch (selectedSystem) {
      case 'ai-models':
        return <AIModelManagementDashboard />;
      case 'ai-analytics':
        return <AIInsightsDashboard />;
      case 'ai-automation':
        return <AIWorkflowAutomationDashboard />;
      case 'ai-enterprise':
        return <AIEnterpriseDashboard />;
      case 'ai-deployment':
        return <AIGlobalDeploymentDashboard />;
      case 'ai-security':
        return <AIEnterpriseDemo />; // Using enterprise demo for security
      case 'performance-monitoring':
        return <PerformanceDemo />;
      default:
        return <View style={styles.emptyState}>
          <Text style={styles.emptyStateText}>System not found</Text>
        </View>;
    }
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (selectedSystem) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.header}>
          <AccessibleButton
            title="← Back to Overview"
            onPress={handleBackToOverview}
            style={styles.backButton}
            variant="ghost"
            size="small"
          />
          <Text style={styles.headerTitle}>
            {systems.find(s => s.id === selectedSystem)?.title || 'System'}
          </Text>
        </View>
        <View style={styles.contentContainer}>
          {renderSelectedSystem()}
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Comprehensive AI Platform</Text>
        <Text style={styles.headerSubtitle}>
          World-Class AI Enterprise Platform with Global Scalability
        </Text>
      </View>

      {/* View Navigation */}
      <View style={styles.viewContainer}>
        {renderViewButton('overview', 'Overview', '🏠')}
        {renderViewButton('systems', 'Systems', '🎯')}
        {renderViewButton('analytics', 'Analytics', '📊')}
        {renderViewButton('deployment', 'Deployment', '🌍')}
      </View>

      {/* Content */}
      <View style={styles.contentContainer}>
        {activeView === 'overview' && renderOverviewTab()}
        {activeView === 'systems' && renderSystemsTab()}
        {activeView === 'analytics' && renderAnalyticsTab()}
        {activeView === 'deployment' && renderDeploymentTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading platform...</Text>
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
  backButton: {
    position: 'absolute',
    left: 20,
    top: 20,
    zIndex: 1,
  },
  viewContainer: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  viewButton: {
    flex: 1,
    paddingVertical: 16,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  viewButtonActive: {
    borderBottomColor: '#007AFF',
  },
  viewButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#666',
  },
  viewButtonTextActive: {
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
    marginBottom: 12,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statsCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statsTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  statsValueContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 4,
  },
  statsValue: {
    fontSize: 24,
    fontWeight: 'bold',
    marginRight: 4,
  },
  trendIcon: {
    fontSize: 16,
  },
  statsSubtitle: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  systemsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  systemCard: {
    width: width > 768 ? '48%' : '100%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  systemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  systemInfo: {
    flexDirection: 'row',
    flex: 1,
  },
  systemIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  systemDetails: {
    flex: 1,
  },
  systemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  systemDescription: {
    fontSize: 12,
    color: '#666',
    lineHeight: 16,
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
  systemFeatures: {
    marginBottom: 12,
  },
  featuresTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  featureItem: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
    lineHeight: 16,
  },
  systemActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  systemActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  analyticsOverview: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  analyticsCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  analyticsTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  analyticsValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  analyticsSubtitle: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  deploymentOverview: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  deploymentCard: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  deploymentTitle: {
    fontSize: 12,
    color: '#666',
    marginBottom: 8,
    textAlign: 'center',
  },
  deploymentValue: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#34C759',
    marginBottom: 4,
  },
  deploymentSubtitle: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  featuresList: {
    marginTop: 8,
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
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
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

export default ComprehensiveAIPlatformDemo;
