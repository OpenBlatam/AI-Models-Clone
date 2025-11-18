/**
 * @fileoverview Master Navigation Component - Central Navigation Hub
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Dimensions,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { ComprehensiveAIPlatformDemo } from '../examples/comprehensive-ai-platform-demo';
import { AIEnterpriseDemo } from '../examples/ai-enterprise-demo';
import { AIGlobalDeploymentDashboard } from '../dashboard/ai-global-deployment-dashboard';
import { AIEnterpriseDashboard } from '../dashboard/ai-enterprise-dashboard';
import { AIModelManagementDashboard } from '../dashboard/ai-model-management-dashboard';
import { AIInsightsDashboard } from '../dashboard/ai-insights-dashboard';
import { AIWorkflowAutomationDashboard } from '../dashboard/ai-workflow-automation-dashboard';
import { AIAutomationDashboard } from '../dashboard/ai-automation-dashboard';
import { AdvancedFeaturesDemo } from '../examples/advanced-features-demo';
import { AdvancedAnimationsDemo } from '../examples/advanced-animations-demo';
import { OfflineDemo } from '../examples/offline-demo';
import { NotificationDemo } from '../examples/notification-demo';
import { AnalyticsDemo } from '../examples/analytics-demo';
import { BiometricAuthDemo } from '../examples/biometric-auth-demo';
import { AIModelManagementDemo } from '../examples/ai-model-management-demo';
import { AIAnalyticsDemo } from '../examples/ai-analytics-demo';
import { AIWorkflowOrchestrationDemo } from '../examples/ai-workflow-orchestration-demo';
import { AIAutomationDemo } from '../examples/ai-automation-demo';
import { PerformanceDemo } from '../examples/performance-demo';
import { PerformanceDashboard } from '../dashboard/performance-dashboard';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface NavigationItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: 'overview' | 'ai-systems' | 'dashboards' | 'demos' | 'advanced';
  component: React.ComponentType;
  status: 'active' | 'beta' | 'coming-soon';
  features: string[];
}

interface CategorySectionProps {
  title: string;
  items: NavigationItem[];
  onItemPress: (item: NavigationItem) => void;
}

// ============================================================================
// CATEGORY SECTION COMPONENT
// ============================================================================

const CategorySection: React.FC<CategorySectionProps> = ({ title, items, onItemPress }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'beta': return '#FF9500';
      case 'coming-soon': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.categorySection}>
      <Text style={styles.categoryTitle}>{title}</Text>
      <View style={styles.itemsGrid}>
        {items.map(item => (
          <View key={item.id} style={styles.navigationItem}>
            <View style={styles.itemHeader}>
              <Text style={styles.itemIcon}>{item.icon}</Text>
              <View style={styles.itemInfo}>
                <Text style={styles.itemTitle}>{item.title}</Text>
                <Text style={styles.itemDescription}>{item.description}</Text>
              </View>
              <View style={[styles.statusBadge, { backgroundColor: getStatusColor(item.status) }]}>
                <Text style={styles.statusBadgeText}>{item.status.toUpperCase()}</Text>
              </View>
            </View>
            
            <View style={styles.itemFeatures}>
              {item.features.slice(0, 2).map((feature, index) => (
                <Text key={index} style={styles.featureItem}>• {feature}</Text>
              ))}
              {item.features.length > 2 && (
                <Text style={styles.featureItem}>• +{item.features.length - 2} more</Text>
              )}
            </View>
            
            <AccessibleButton
              title="Open"
              onPress={() => onItemPress(item)}
              style={styles.itemButton}
              variant="primary"
              size="small"
              disabled={item.status === 'coming-soon'}
            />
          </View>
        ))}
      </View>
    </View>
  );
};

// ============================================================================
// MAIN NAVIGATION COMPONENT
// ============================================================================

export function MasterNavigation(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeComponent, setActiveComponent] = useState<NavigationItem | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // ============================================================================
  // NAVIGATION ITEMS CONFIGURATION
  // ============================================================================

  const navigationItems: NavigationItem[] = [
    // Overview & Platform
    {
      id: 'comprehensive-platform',
      title: 'Comprehensive AI Platform',
      description: 'Master demo showcasing all AI systems and capabilities',
      icon: '🚀',
      category: 'overview',
      component: ComprehensiveAIPlatformDemo,
      status: 'active',
      features: ['Complete AI ecosystem', 'Enterprise features', 'Global scalability', 'Mobile excellence'],
    },
    {
      id: 'enterprise-platform',
      title: 'AI Enterprise Platform',
      description: 'Multi-tenant platform with compliance and enterprise features',
      icon: '🏢',
      category: 'overview',
      component: AIEnterpriseDemo,
      status: 'active',
      features: ['Multi-tenancy', 'Compliance', 'Audit logging', 'Security management'],
    },

    // AI Systems
    {
      id: 'ai-models',
      title: 'AI Model Management',
      description: 'Complete model lifecycle management with automated training',
      icon: '🤖',
      category: 'ai-systems',
      component: AIModelManagementDemo,
      status: 'active',
      features: ['Model lifecycle', 'Automated training', 'Smart deployment', 'Performance monitoring'],
    },
    {
      id: 'ai-analytics',
      title: 'AI Analytics & Predictive',
      description: 'Advanced analytics engine with ML-powered insights',
      icon: '📊',
      category: 'ai-systems',
      component: AIAnalyticsDemo,
      status: 'active',
      features: ['Intelligent analytics', 'Predictive insights', 'Real-time dashboards', 'Alert systems'],
    },
    {
      id: 'ai-automation',
      title: 'AI Workflow Automation',
      description: 'Intelligent automation with rule engines and orchestration',
      icon: '⚙️',
      category: 'ai-systems',
      component: AIWorkflowOrchestrationDemo,
      status: 'active',
      features: ['Rule-based automation', 'Workflow orchestration', 'Task queuing', 'Event-driven architecture'],
    },
    {
      id: 'ai-orchestration',
      title: 'AI Automation & Orchestration',
      description: 'Advanced automation and orchestration system',
      icon: '🎭',
      category: 'ai-systems',
      component: AIAutomationDemo,
      status: 'active',
      features: ['Advanced automation', 'System orchestration', 'Rules engine', 'Event coordination'],
    },
    {
      id: 'performance-monitoring',
      title: 'Performance Monitoring',
      description: 'Comprehensive performance monitoring with real-time metrics and optimization',
      icon: '📊',
      category: 'ai-systems',
      component: PerformanceDemo,
      status: 'active',
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

    // Dashboards
    {
      id: 'model-dashboard',
      title: 'Model Management Dashboard',
      description: 'Comprehensive dashboard for AI model management',
      icon: '📈',
      category: 'dashboards',
      component: AIModelManagementDashboard,
      status: 'active',
      features: ['Model overview', 'Training monitoring', 'Performance metrics', 'Deployment status'],
    },
    {
      id: 'insights-dashboard',
      title: 'AI Insights Dashboard',
      description: 'Advanced analytics and insights dashboard',
      icon: '🔍',
      category: 'dashboards',
      component: AIInsightsDashboard,
      status: 'active',
      features: ['Analytics overview', 'Insights generation', 'Metrics visualization', 'Alert management'],
    },
    {
      id: 'workflow-dashboard',
      title: 'Workflow Automation Dashboard',
      description: 'Dashboard for workflow automation and orchestration',
      icon: '🔄',
      category: 'dashboards',
      component: AIWorkflowAutomationDashboard,
      status: 'active',
      features: ['Workflow overview', 'Automation rules', 'Execution monitoring', 'Performance tracking'],
    },
    {
      id: 'automation-dashboard',
      title: 'AI Automation Dashboard',
      description: 'Advanced automation and orchestration dashboard',
      icon: '🎯',
      category: 'dashboards',
      component: AIAutomationDashboard,
      status: 'active',
      features: ['Automation overview', 'Rules management', 'Event monitoring', 'System coordination'],
    },
    {
      id: 'enterprise-dashboard',
      title: 'Enterprise Platform Dashboard',
      description: 'Multi-tenant enterprise platform dashboard',
      icon: '🏢',
      category: 'dashboards',
      component: AIEnterpriseDashboard,
      status: 'active',
      features: ['Tenant management', 'User management', 'Compliance monitoring', 'Audit logging'],
    },
    {
      id: 'global-deployment',
      title: 'Global Deployment Dashboard',
      description: 'Global deployment and scaling management dashboard',
      icon: '🌍',
      category: 'dashboards',
      component: AIGlobalDeploymentDashboard,
      status: 'active',
      features: ['Region management', 'Deployment monitoring', 'Load balancing', 'Auto-scaling'],
    },
    {
      id: 'performance-dashboard',
      title: 'Performance Dashboard',
      description: 'Comprehensive performance monitoring and optimization dashboard',
      icon: '📊',
      category: 'dashboards',
      component: PerformanceDashboard,
      status: 'active',
      features: ['Performance metrics', 'Alert management', 'Optimization tracking', 'Report generation'],
    },

    // Advanced Features
    {
      id: 'advanced-features',
      title: 'Advanced Features Demo',
      description: 'Comprehensive demo of advanced platform features',
      icon: '✨',
      category: 'advanced',
      component: AdvancedFeaturesDemo,
      status: 'active',
      features: ['Deep linking', 'Splash screen', 'Image optimization', 'Code splitting'],
    },
    {
      id: 'advanced-animations',
      title: 'Advanced Animations Demo',
      description: 'Advanced animation system with gesture interactions',
      icon: '🎭',
      category: 'advanced',
      component: AdvancedAnimationsDemo,
      status: 'active',
      features: ['Gesture interactions', 'Morphing animations', 'Staggered lists', 'Loading spinners'],
    },
    {
      id: 'offline-demo',
      title: 'Offline-First Demo',
      description: 'Offline-first architecture with data synchronization',
      icon: '📱',
      category: 'advanced',
      component: OfflineDemo,
      status: 'active',
      features: ['Network monitoring', 'Action queuing', 'Data sync', 'Conflict resolution'],
    },
    {
      id: 'notifications',
      title: 'Push Notifications Demo',
      description: 'Comprehensive push notification system',
      icon: '🔔',
      category: 'advanced',
      component: NotificationDemo,
      status: 'active',
      features: ['Notification lifecycle', 'Deep linking', 'Permission management', 'Settings'],
    },
    {
      id: 'analytics',
      title: 'Analytics Demo',
      description: 'Client-side analytics with consent management',
      icon: '📊',
      category: 'advanced',
      component: AnalyticsDemo,
      status: 'active',
      features: ['Event tracking', 'Consent management', 'User analytics', 'Performance monitoring'],
    },
    {
      id: 'biometric-auth',
      title: 'Biometric Authentication Demo',
      description: 'Comprehensive biometric authentication system',
      icon: '🔐',
      category: 'advanced',
      component: BiometricAuthDemo,
      status: 'active',
      features: ['Face ID/Touch ID', 'Secure storage', 'Backup codes', 'Advanced settings'],
    },
  ];

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleItemPress = useCallback(async (item: NavigationItem) => {
    if (item.status === 'coming-soon') {
      Alert.alert('Coming Soon', `${item.title} will be available in a future update.`);
      return;
    }

    setIsLoading(true);
    try {
      // Simulate loading time
      await new Promise(resolve => setTimeout(resolve, 500));
      setActiveComponent(item);
    } catch (error) {
      Alert.alert('Error', 'Failed to load component');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleBackToNavigation = useCallback(() => {
    setActiveComponent(null);
  }, []);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderNavigationItems = (): JSX.Element => {
    const categories = {
      overview: navigationItems.filter(item => item.category === 'overview'),
      'ai-systems': navigationItems.filter(item => item.category === 'ai-systems'),
      dashboards: navigationItems.filter(item => item.category === 'dashboards'),
      demos: navigationItems.filter(item => item.category === 'demos'),
      advanced: navigationItems.filter(item => item.category === 'advanced'),
    };

    return (
      <View style={styles.navigationContainer}>
        <CategorySection
          title="🚀 Platform Overview"
          items={categories.overview}
          onItemPress={handleItemPress}
        />
        <CategorySection
          title="🤖 AI Systems"
          items={categories['ai-systems']}
          onItemPress={handleItemPress}
        />
        <CategorySection
          title="📊 Dashboards"
          items={categories.dashboards}
          onItemPress={handleItemPress}
        />
        <CategorySection
          title="✨ Advanced Features"
          items={categories.advanced}
          onItemPress={handleItemPress}
        />
      </View>
    );
  };

  const renderActiveComponent = (): JSX.Element => {
    if (!activeComponent) return <View />;

    const Component = activeComponent.component;
    return (
      <View style={styles.componentContainer}>
        <View style={styles.componentHeader}>
          <AccessibleButton
            title="← Back to Navigation"
            onPress={handleBackToNavigation}
            style={styles.backButton}
            variant="ghost"
            size="small"
          />
          <View style={styles.componentInfo}>
            <Text style={styles.componentIcon}>{activeComponent.icon}</Text>
            <View style={styles.componentDetails}>
              <Text style={styles.componentTitle}>{activeComponent.title}</Text>
              <Text style={styles.componentDescription}>{activeComponent.description}</Text>
            </View>
          </View>
        </View>
        <View style={styles.componentContent}>
          <Component />
        </View>
      </View>
    );
  };

  // ============================================================================
  // MAIN RENDER
  // ============================================================================

  if (activeComponent) {
    return (
      <SafeAreaView style={styles.container}>
        {renderActiveComponent()}
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Blaze AI Platform</Text>
        <Text style={styles.headerSubtitle}>
          Master Navigation Hub - Access All AI Systems & Features
        </Text>
      </View>

      {/* Navigation Content */}
      <View style={styles.contentContainer}>
        {renderNavigationItems()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading...</Text>
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
    fontSize: 28,
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
  contentContainer: {
    flex: 1,
    padding: 16,
  },
  navigationContainer: {
    flex: 1,
  },
  categorySection: {
    marginBottom: 24,
  },
  categoryTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 16,
  },
  itemsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  navigationItem: {
    width: width > 768 ? '48%' : '100%',
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  itemHeader: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  itemIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  itemInfo: {
    flex: 1,
  },
  itemTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  itemDescription: {
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
  itemFeatures: {
    marginBottom: 12,
  },
  featureItem: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
    lineHeight: 16,
  },
  itemButton: {
    width: '100%',
  },
  componentContainer: {
    flex: 1,
  },
  componentHeader: {
    backgroundColor: '#007AFF',
    padding: 20,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    marginRight: 16,
  },
  componentInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  componentIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  componentDetails: {
    flex: 1,
  },
  componentTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffffff',
    marginBottom: 4,
  },
  componentDescription: {
    fontSize: 14,
    color: '#ffffff',
    opacity: 0.9,
  },
  componentContent: {
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

export default MasterNavigation;
