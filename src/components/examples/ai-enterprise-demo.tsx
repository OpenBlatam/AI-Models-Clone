/**
 * @fileoverview AI Enterprise Platform Demo Component
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
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AccessibleButton } from '../accessibility/accessible-button';
import { AIEnterpriseDashboard } from '../dashboard/ai-enterprise-dashboard';
import { 
  aiEnterprisePlatform,
  AIEnterpriseTenant,
  AIEnterpriseUser,
  AIEnterpriseAPIKey,
  AIEnterpriseCompliance
} from '../../lib/ai/ai-enterprise-platform';

// ============================================================================
// DEMO DATA
// ============================================================================

const DEMO_TENANTS: AIEnterpriseTenant[] = [
  {
    id: 'tenant_tech_corp',
    name: 'TechCorp Solutions',
    domain: 'techcorp.blaze-ai.com',
    status: 'active',
    plan: 'enterprise',
    limits: {
      models: 200,
      workflows: 100,
      users: 2000,
      storage: 2000,
      apiCalls: 2000000,
      computeHours: 20000,
    },
    usage: {
      models: 45,
      workflows: 23,
      users: 1250,
      storage: 850,
      apiCalls: 450000,
      computeHours: 3200,
    },
    features: {
      advancedAnalytics: true,
      predictiveAnalytics: true,
      automation: true,
      customModels: true,
      apiAccess: true,
      sso: true,
      auditLogs: true,
      compliance: true,
    },
    billing: {
      billingCycle: 'monthly',
      nextBillingDate: Date.now() + (15 * 24 * 60 * 60 * 1000),
      lastPaymentDate: Date.now() - (5 * 24 * 60 * 60 * 1000),
      amount: 2499,
      currency: 'USD',
    },
    metadata: {
      industry: 'Technology',
      region: 'us-west-2',
      contact: 'admin@techcorp.com',
    },
    createdAt: Date.now() - (180 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
  {
    id: 'tenant_health_plus',
    name: 'HealthPlus Medical',
    domain: 'healthplus.blaze-ai.com',
    status: 'active',
    plan: 'professional',
    limits: {
      models: 50,
      workflows: 25,
      users: 500,
      storage: 500,
      apiCalls: 500000,
      computeHours: 5000,
    },
    usage: {
      models: 12,
      workflows: 8,
      users: 180,
      storage: 120,
      apiCalls: 85000,
      computeHours: 650,
    },
    features: {
      advancedAnalytics: true,
      predictiveAnalytics: true,
      automation: false,
      customModels: false,
      apiAccess: true,
      sso: false,
      auditLogs: true,
      compliance: true,
    },
    billing: {
      billingCycle: 'yearly',
      nextBillingDate: Date.now() + (300 * 24 * 60 * 60 * 1000),
      lastPaymentDate: Date.now() - (30 * 24 * 60 * 60 * 1000),
      amount: 999,
      currency: 'USD',
    },
    metadata: {
      industry: 'Healthcare',
      region: 'us-east-1',
      contact: 'admin@healthplus.com',
      compliance: ['HIPAA'],
    },
    createdAt: Date.now() - (90 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
  {
    id: 'tenant_fintech_startup',
    name: 'FinTech Startup',
    domain: 'fintech.blaze-ai.com',
    status: 'pending',
    plan: 'basic',
    limits: {
      models: 10,
      workflows: 5,
      users: 50,
      storage: 100,
      apiCalls: 100000,
      computeHours: 1000,
    },
    usage: {
      models: 2,
      workflows: 1,
      users: 8,
      storage: 15,
      apiCalls: 5000,
      computeHours: 45,
    },
    features: {
      advancedAnalytics: false,
      predictiveAnalytics: false,
      automation: false,
      customModels: false,
      apiAccess: true,
      sso: false,
      auditLogs: false,
      compliance: false,
    },
    billing: {
      billingCycle: 'monthly',
      nextBillingDate: Date.now() + (7 * 24 * 60 * 60 * 1000),
      lastPaymentDate: 0,
      amount: 99,
      currency: 'USD',
    },
    metadata: {
      industry: 'Financial Services',
      region: 'eu-west-1',
      contact: 'admin@fintech.com',
      stage: 'startup',
    },
    createdAt: Date.now() - (7 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
];

const DEMO_USERS: AIEnterpriseUser[] = [
  {
    id: 'user_tech_admin',
    tenantId: 'tenant_tech_corp',
    email: 'admin@techcorp.com',
    name: 'Sarah Johnson',
    role: 'admin',
    permissions: {
      models: ['*'],
      analytics: ['*'],
      automation: ['*'],
      system: ['*'],
    },
    status: 'active',
    lastLogin: Date.now() - (2 * 60 * 60 * 1000), // 2 hours ago
    preferences: {
      theme: 'dark',
      language: 'en',
      timezone: 'America/Los_Angeles',
      notifications: {
        email: true,
        push: true,
        sms: false,
      },
    },
    security: {
      mfaEnabled: true,
      lastPasswordChange: Date.now() - (30 * 24 * 60 * 60 * 1000),
      failedLoginAttempts: 0,
    },
    metadata: {
      department: 'IT',
      title: 'CTO',
    },
    createdAt: Date.now() - (180 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
  {
    id: 'user_tech_dev',
    tenantId: 'tenant_tech_corp',
    email: 'dev@techcorp.com',
    name: 'Michael Chen',
    role: 'developer',
    permissions: {
      models: ['create', 'update', 'deploy'],
      analytics: ['read', 'create'],
      automation: ['read', 'create'],
      system: ['read'],
    },
    status: 'active',
    lastLogin: Date.now() - (30 * 60 * 1000), // 30 minutes ago
    preferences: {
      theme: 'light',
      language: 'en',
      timezone: 'America/Los_Angeles',
      notifications: {
        email: true,
        push: false,
        sms: false,
      },
    },
    security: {
      mfaEnabled: true,
      lastPasswordChange: Date.now() - (15 * 24 * 60 * 60 * 1000),
      failedLoginAttempts: 0,
    },
    metadata: {
      department: 'Engineering',
      title: 'Senior AI Engineer',
    },
    createdAt: Date.now() - (120 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
  {
    id: 'user_health_admin',
    tenantId: 'tenant_health_plus',
    email: 'admin@healthplus.com',
    name: 'Dr. Emily Rodriguez',
    role: 'admin',
    permissions: {
      models: ['read', 'create'],
      analytics: ['*'],
      automation: ['read'],
      system: ['read'],
    },
    status: 'active',
    lastLogin: Date.now() - (4 * 60 * 60 * 1000), // 4 hours ago
    preferences: {
      theme: 'auto',
      language: 'en',
      timezone: 'America/New_York',
      notifications: {
        email: true,
        push: true,
        sms: true,
      },
    },
    security: {
      mfaEnabled: true,
      lastPasswordChange: Date.now() - (45 * 24 * 60 * 60 * 1000),
      failedLoginAttempts: 0,
    },
    metadata: {
      department: 'Medical',
      title: 'Chief Medical Officer',
      certifications: ['HIPAA'],
    },
    createdAt: Date.now() - (90 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
];

const DEMO_API_KEYS: AIEnterpriseAPIKey[] = [
  {
    id: 'api_key_tech_prod',
    tenantId: 'tenant_tech_corp',
    userId: 'user_tech_admin',
    name: 'Production API Key',
    key: 'sk-prod-1234567890abcdef',
    permissions: {
      models: ['*'],
      analytics: ['*'],
      automation: ['*'],
      system: ['read'],
    },
    rateLimits: {
      requestsPerMinute: 1000,
      requestsPerHour: 10000,
      requestsPerDay: 100000,
    },
    usage: {
      requestsToday: 15420,
      requestsThisMonth: 245000,
      lastUsed: Date.now() - (5 * 60 * 1000), // 5 minutes ago
    },
    status: 'active',
    expiresAt: Date.now() + (365 * 24 * 60 * 60 * 1000), // 1 year
    metadata: {
      environment: 'production',
      description: 'Main production API key for TechCorp',
    },
    createdAt: Date.now() - (60 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
  {
    id: 'api_key_health_dev',
    tenantId: 'tenant_health_plus',
    userId: 'user_health_admin',
    name: 'Development API Key',
    key: 'sk-dev-abcdef1234567890',
    permissions: {
      models: ['read', 'create'],
      analytics: ['read', 'create'],
      automation: ['read'],
      system: ['read'],
    },
    rateLimits: {
      requestsPerMinute: 100,
      requestsPerHour: 1000,
      requestsPerDay: 10000,
    },
    usage: {
      requestsToday: 450,
      requestsThisMonth: 8500,
      lastUsed: Date.now() - (2 * 60 * 60 * 1000), // 2 hours ago
    },
    status: 'active',
    expiresAt: Date.now() + (90 * 24 * 60 * 60 * 1000), // 90 days
    metadata: {
      environment: 'development',
      description: 'Development API key for HealthPlus',
    },
    createdAt: Date.now() - (30 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now(),
  },
];

const DEMO_COMPLIANCE: AIEnterpriseCompliance[] = [
  {
    id: 'compliance_tech_gdpr',
    tenantId: 'tenant_tech_corp',
    framework: 'GDPR',
    status: 'compliant',
    requirements: [
      {
        id: 'data_protection',
        description: 'Data protection and privacy controls',
        status: 'met',
        evidence: ['Privacy policy implemented', 'Data encryption enabled'],
        lastChecked: Date.now() - (7 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'consent_management',
        description: 'Consent management system',
        status: 'met',
        evidence: ['Consent forms implemented', 'Opt-out mechanisms available'],
        lastChecked: Date.now() - (7 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'data_retention',
        description: 'Data retention policies',
        status: 'met',
        evidence: ['Retention policies documented', 'Automated deletion configured'],
        lastChecked: Date.now() - (7 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'right_to_erasure',
        description: 'Right to erasure implementation',
        status: 'met',
        evidence: ['Data deletion API implemented', 'User request handling automated'],
        lastChecked: Date.now() - (7 * 24 * 60 * 60 * 1000),
      },
    ],
    lastAudit: Date.now() - (7 * 24 * 60 * 60 * 1000),
    nextAudit: Date.now() + (23 * 24 * 60 * 60 * 1000),
    metadata: {
      auditor: 'External Compliance Team',
      certification: 'GDPR Compliant',
    },
    createdAt: Date.now() - (180 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now() - (7 * 24 * 60 * 60 * 1000),
  },
  {
    id: 'compliance_health_hipaa',
    tenantId: 'tenant_health_plus',
    framework: 'HIPAA',
    status: 'compliant',
    requirements: [
      {
        id: 'administrative_safeguards',
        description: 'Administrative safeguards',
        status: 'met',
        evidence: ['Security policies documented', 'Staff training completed'],
        lastChecked: Date.now() - (14 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'physical_safeguards',
        description: 'Physical safeguards',
        status: 'met',
        evidence: ['Data center security verified', 'Access controls implemented'],
        lastChecked: Date.now() - (14 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'technical_safeguards',
        description: 'Technical safeguards',
        status: 'met',
        evidence: ['Encryption at rest and in transit', 'Access logging enabled'],
        lastChecked: Date.now() - (14 * 24 * 60 * 60 * 1000),
      },
      {
        id: 'breach_notification',
        description: 'Breach notification procedures',
        status: 'met',
        evidence: ['Incident response plan documented', 'Notification procedures tested'],
        lastChecked: Date.now() - (14 * 24 * 60 * 60 * 1000),
      },
    ],
    lastAudit: Date.now() - (14 * 24 * 60 * 60 * 1000),
    nextAudit: Date.now() + (16 * 24 * 60 * 60 * 1000),
    metadata: {
      auditor: 'Healthcare Compliance Officer',
      certification: 'HIPAA Compliant',
    },
    createdAt: Date.now() - (90 * 24 * 60 * 60 * 1000),
    updatedAt: Date.now() - (14 * 24 * 60 * 60 * 1000),
  },
];

// ============================================================================
// MAIN DEMO COMPONENT
// ============================================================================

export function AIEnterpriseDemo(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'demo' | 'dashboard' | 'scenarios'>('demo');
  const [isLoading, setIsLoading] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [demoDataLoaded, setDemoDataLoaded] = useState(false);

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
      await loadDemoData();
      setDemoDataLoaded(true);
    } catch (error) {
      Alert.alert('Error', 'Failed to initialize demo data');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const loadDemoData = useCallback(async () => {
    // Load demo tenants
    DEMO_TENANTS.forEach(tenant => {
      aiEnterprisePlatform.createTenant(tenant);
    });

    // Load demo users
    DEMO_USERS.forEach(user => {
      aiEnterprisePlatform.createUser(user);
    });

    // Load demo API keys
    DEMO_API_KEYS.forEach(apiKey => {
      aiEnterprisePlatform.createAPIKey(apiKey);
    });

    // Load demo compliance records
    DEMO_COMPLIANCE.forEach(compliance => {
      aiEnterprisePlatform.createCompliance(compliance);
    });

    // Run compliance checks for additional frameworks
    const frameworks = ['CCPA', 'SOX', 'ISO27001', 'SOC2'];
    DEMO_TENANTS.forEach(tenant => {
      frameworks.forEach(framework => {
        aiEnterprisePlatform.runComplianceCheck(tenant.id, framework);
      });
    });
  }, []);

  // ============================================================================
  // EVENT HANDLERS
  // ============================================================================

  const handleTabChange = useCallback((tab: typeof activeTab) => {
    setActiveTab(tab);
  }, []);

  const handleRefresh = useCallback(async () => {
    setIsRefreshing(true);
    try {
      await loadDemoData();
    } catch (error) {
      Alert.alert('Error', 'Failed to refresh demo data');
    } finally {
      setIsRefreshing(false);
    }
  }, [loadDemoData]);

  const handleCreateTenant = useCallback(() => {
    Alert.alert(
      'Create New Tenant',
      'This would open a form to create a new tenant with custom configuration.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Create',
          onPress: () => {
            // In real implementation, this would open a form
            Alert.alert('Success', 'Tenant creation form would open here');
          },
        },
      ]
    );
  }, []);

  const handleCreateUser = useCallback(() => {
    Alert.alert(
      'Create New User',
      'This would open a form to create a new user with role and permissions.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Create',
          onPress: () => {
            // In real implementation, this would open a form
            Alert.alert('Success', 'User creation form would open here');
          },
        },
      ]
    );
  }, []);

  const handleCreateAPIKey = useCallback(() => {
    Alert.alert(
      'Create New API Key',
      'This would open a form to create a new API key with specific permissions and rate limits.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Create',
          onPress: () => {
            // In real implementation, this would open a form
            Alert.alert('Success', 'API key creation form would open here');
          },
        },
      ]
    );
  }, []);

  const handleRunComplianceCheck = useCallback(() => {
    Alert.alert(
      'Run Compliance Check',
      'This would trigger a comprehensive compliance check across all frameworks for all tenants.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Run Check',
          onPress: () => {
            // Simulate running compliance checks
            const tenants = aiEnterprisePlatform.getTenants();
            const frameworks = ['GDPR', 'CCPA', 'HIPAA', 'SOX', 'ISO27001', 'SOC2'];
            
            tenants.forEach(tenant => {
              frameworks.forEach(framework => {
                aiEnterprisePlatform.runComplianceCheck(tenant.id, framework);
              });
            });
            
            Alert.alert('Success', 'Compliance checks completed for all tenants');
          },
        },
      ]
    );
  }, []);

  const handleViewSystemStats = useCallback(() => {
    const stats = aiEnterprisePlatform.getSystemStats();
    Alert.alert(
      'System Statistics',
      `Total Tenants: ${stats.totalTenants}\nActive Tenants: ${stats.activeTenants}\nTotal Users: ${stats.totalUsers}\nActive Users: ${stats.activeUsers}\nTotal API Keys: ${stats.totalAPIKeys}\nActive API Keys: ${stats.activeAPIKeys}\nTotal Audit Logs: ${stats.totalAuditLogs}\nCompliant: ${stats.complianceStatus.compliant}\nNon-Compliant: ${stats.complianceStatus.nonCompliant}\nPending: ${stats.complianceStatus.pending}`
    );
  }, []);

  const handleViewAuditLogs = useCallback(() => {
    const auditLogs = aiEnterprisePlatform.getAuditLogs();
    const recentLogs = auditLogs.slice(0, 5);
    
    const logsText = recentLogs.map(log => 
      `${new Date(log.timestamp).toLocaleString()}: ${log.action} on ${log.resource}`
    ).join('\n');
    
    Alert.alert(
      'Recent Audit Logs',
      logsText || 'No audit logs available'
    );
  }, []);

  // ============================================================================
  // RENDER FUNCTIONS
  // ============================================================================

  const renderTabButton = (tab: typeof activeTab, label: string, icon: string): JSX.Element => (
    <AccessibleButton
      title={`${icon} ${label}`}
      accessibilityLabel={`Switch to ${label} tab`}
      onPress={() => handleTabChange(tab)}
      style={[styles.tabButton, activeTab === tab && styles.tabButtonActive]}
      textStyle={[styles.tabButtonText, activeTab === tab && styles.tabButtonTextActive]}
      variant="ghost"
      size="small"
    />
  );

  const renderDemoTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Demo Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🚀 AI Enterprise Platform Demo</Text>
        <Text style={styles.sectionDescription}>
          This demo showcases a comprehensive multi-tenant AI platform with enterprise-grade features including:
        </Text>
        <View style={styles.featureList}>
          <Text style={styles.featureItem}>• Multi-tenant architecture with isolated resources</Text>
          <Text style={styles.featureItem}>• Role-based access control and permissions</Text>
          <Text style={styles.featureItem}>• API key management with rate limiting</Text>
          <Text style={styles.featureItem}>• Comprehensive audit logging</Text>
          <Text style={styles.featureItem}>• Compliance monitoring (GDPR, HIPAA, SOX, etc.)</Text>
          <Text style={styles.featureItem}>• Real-time metrics and performance monitoring</Text>
          <Text style={styles.featureItem}>• Billing and usage tracking</Text>
          <Text style={styles.featureItem}>• Security and authentication management</Text>
        </View>
      </View>

      {/* Demo Data Status */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>📊 Demo Data Status</Text>
        <View style={styles.statusGrid}>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>{DEMO_TENANTS.length}</Text>
            <Text style={styles.statusLabel}>Demo Tenants</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>{DEMO_USERS.length}</Text>
            <Text style={styles.statusLabel}>Demo Users</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>{DEMO_API_KEYS.length}</Text>
            <Text style={styles.statusLabel}>Demo API Keys</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusValue}>{DEMO_COMPLIANCE.length}</Text>
            <Text style={styles.statusLabel}>Compliance Records</Text>
          </View>
        </View>
        <Text style={styles.statusDescription}>
          Demo data has been loaded into the enterprise platform. You can now explore the dashboard and test various scenarios.
        </Text>
      </View>

      {/* Quick Actions */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>⚡ Quick Actions</Text>
        <View style={styles.actionGrid}>
          <AccessibleButton
            title="🏢 Create Tenant"
            onPress={handleCreateTenant}
            style={styles.actionButton}
            variant="primary"
            size="small"
          />
          <AccessibleButton
            title="👥 Create User"
            onPress={handleCreateUser}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="🔑 Create API Key"
            onPress={handleCreateAPIKey}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="📋 Run Compliance Check"
            onPress={handleRunComplianceCheck}
            style={styles.actionButton}
            variant="secondary"
            size="small"
          />
          <AccessibleButton
            title="📊 View System Stats"
            onPress={handleViewSystemStats}
            style={styles.actionButton}
            variant="outline"
            size="small"
          />
          <AccessibleButton
            title="📝 View Audit Logs"
            onPress={handleViewAuditLogs}
            style={styles.actionButton}
            variant="outline"
            size="small"
          />
        </View>
      </View>

      {/* Demo Scenarios */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Demo Scenarios</Text>
        <View style={styles.scenarioList}>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Enterprise Tenant Management</Text>
            <Text style={styles.scenarioDescription}>
              Manage multiple tenants with different plans, usage limits, and feature sets. Monitor resource usage and billing.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>User Role & Permission Management</Text>
            <Text style={styles.scenarioDescription}>
              Create users with different roles (admin, developer, analyst, viewer) and granular permissions for models, analytics, and automation.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>API Key & Rate Limiting</Text>
            <Text style={styles.scenarioDescription}>
              Generate API keys with specific permissions and rate limits. Monitor usage and enforce quotas per tenant.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Compliance Monitoring</Text>
            <Text style={styles.scenarioDescription}>
              Track compliance across multiple frameworks (GDPR, HIPAA, SOX, ISO27001, SOC2) with automated checks and reporting.
            </Text>
          </View>
          <View style={styles.scenarioItem}>
            <Text style={styles.scenarioTitle}>Audit Logging & Security</Text>
            <Text style={styles.scenarioDescription}>
              Comprehensive audit trail of all system activities, user actions, and security events with detailed logging.
            </Text>
          </View>
        </View>
      </View>

      {/* Navigation */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🧭 Navigation</Text>
        <View style={styles.navigationButtons}>
          <AccessibleButton
            title="📊 Open Dashboard"
            onPress={() => handleTabChange('dashboard')}
            style={styles.navigationButton}
            variant="primary"
            size="medium"
          />
          <AccessibleButton
            title="🔄 Refresh Demo Data"
            onPress={handleRefresh}
            style={styles.navigationButton}
            variant="secondary"
            size="medium"
          />
        </View>
      </View>
    </ScrollView>
  );

  const renderDashboardTab = (): JSX.Element => {
    if (!demoDataLoaded) {
      return (
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Loading dashboard...</Text>
        </View>
      );
    }

    return <AIEnterpriseDashboard />;
  };

  const renderScenariosTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      {/* Scenario Overview */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🎯 Enterprise Scenarios</Text>
        <Text style={styles.sectionDescription}>
          Explore different enterprise scenarios and use cases for the AI platform:
        </Text>
      </View>

      {/* Scenario 1: Multi-Tenant SaaS */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏢 Multi-Tenant SaaS Platform</Text>
        <Text style={styles.scenarioDescription}>
          A software-as-a-service platform serving multiple organizations with isolated AI resources, custom models, and usage-based billing.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Tenant isolation and resource quotas</Text>
          <Text style={styles.scenarioFeature}>• Custom model training per tenant</Text>
          <Text style={styles.scenarioFeature}>• Usage-based billing and metering</Text>
          <Text style={styles.scenarioFeature}>• White-label customization options</Text>
        </View>
        <AccessibleButton
          title="Explore Multi-Tenant Scenario"
          onPress={() => Alert.alert('Scenario', 'Multi-tenant SaaS scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 2: Enterprise AI Governance */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🛡️ Enterprise AI Governance</Text>
        <Text style={styles.scenarioDescription}>
          Large enterprise with strict compliance requirements, audit trails, and centralized AI model management across departments.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Comprehensive audit logging</Text>
          <Text style={styles.scenarioFeature}>• Role-based access control</Text>
          <Text style={styles.scenarioFeature}>• Compliance monitoring and reporting</Text>
          <Text style={styles.scenarioFeature}>• Model versioning and approval workflows</Text>
        </View>
        <AccessibleButton
          title="Explore Governance Scenario"
          onPress={() => Alert.alert('Scenario', 'Enterprise AI governance scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 3: Healthcare AI Platform */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🏥 Healthcare AI Platform</Text>
        <Text style={styles.scenarioDescription}>
          HIPAA-compliant AI platform for healthcare organizations with patient data protection and medical AI model management.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• HIPAA compliance monitoring</Text>
          <Text style={styles.scenarioFeature}>• Patient data encryption and protection</Text>
          <Text style={styles.scenarioFeature}>• Medical AI model validation</Text>
          <Text style={styles.scenarioFeature}>• Healthcare-specific workflows</Text>
        </View>
        <AccessibleButton
          title="Explore Healthcare Scenario"
          onPress={() => Alert.alert('Scenario', 'Healthcare AI platform scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 4: Financial Services AI */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>💰 Financial Services AI</Text>
        <Text style={styles.scenarioDescription}>
          SOX-compliant AI platform for financial institutions with fraud detection, risk assessment, and regulatory reporting.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• SOX compliance and reporting</Text>
          <Text style={styles.scenarioFeature}>• Financial data security</Text>
          <Text style={styles.scenarioFeature}>• Risk assessment models</Text>
          <Text style={styles.scenarioFeature}>• Regulatory audit trails</Text>
        </View>
        <AccessibleButton
          title="Explore Financial Scenario"
          onPress={() => Alert.alert('Scenario', 'Financial services AI scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
      </View>

      {/* Scenario 5: Global AI Marketplace */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>🌍 Global AI Marketplace</Text>
        <Text style={styles.scenarioDescription}>
          Global platform connecting AI model providers with consumers, featuring multi-region deployment and cross-border compliance.
        </Text>
        <View style={styles.scenarioFeatures}>
          <Text style={styles.scenarioFeature}>• Multi-region deployment</Text>
          <Text style={styles.scenarioFeature}>• Cross-border data compliance</Text>
          <Text style={styles.scenarioFeature}>• AI model marketplace</Text>
          <Text style={styles.scenarioFeature}>• Global billing and payments</Text>
        </View>
        <AccessibleButton
          title="Explore Marketplace Scenario"
          onPress={() => Alert.alert('Scenario', 'Global AI marketplace scenario details would be shown here')}
          style={styles.scenarioButton}
          variant="primary"
          size="small"
        />
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
        <Text style={styles.headerTitle}>AI Enterprise Platform Demo</Text>
        <Text style={styles.headerSubtitle}>
          Comprehensive Multi-Tenant AI Platform with Enterprise Features
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('demo', 'Demo', '🚀')}
        {renderTabButton('dashboard', 'Dashboard', '📊')}
        {renderTabButton('scenarios', 'Scenarios', '🎯')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'demo' && renderDemoTab()}
        {activeTab === 'dashboard' && renderDashboardTab()}
        {activeTab === 'scenarios' && renderScenariosTab()}
      </View>

      {/* Loading Indicator */}
      {isLoading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color="#007AFF" />
          <Text style={styles.loadingText}>Initializing demo...</Text>
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
    marginBottom: 8,
  },
  sectionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
    marginBottom: 12,
  },
  featureList: {
    marginTop: 8,
  },
  featureItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
    lineHeight: 20,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  statusItem: {
    width: '48%',
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
    alignItems: 'center',
  },
  statusValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  statusLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  statusDescription: {
    fontSize: 14,
    color: '#666',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  actionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    width: '48%',
    paddingVertical: 12,
    marginBottom: 8,
  },
  scenarioList: {
    marginTop: 8,
  },
  scenarioItem: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 12,
  },
  scenarioTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  scenarioDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 18,
  },
  scenarioFeatures: {
    marginTop: 8,
  },
  scenarioFeature: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  scenarioButton: {
    marginTop: 12,
  },
  navigationButtons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  navigationButton: {
    paddingHorizontal: 20,
    paddingVertical: 12,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 32,
  },
  loadingText: {
    fontSize: 16,
    color: '#666',
    marginTop: 16,
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
});

export default AIEnterpriseDemo;