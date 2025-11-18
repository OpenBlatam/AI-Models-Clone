/**
 * @fileoverview AI Enterprise Platform Dashboard
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
  aiEnterprisePlatform,
  AIEnterpriseTenant,
  AIEnterpriseUser,
  AIEnterpriseAPIKey,
  AIEnterpriseAuditLog,
  AIEnterpriseCompliance,
  AIEnterpriseMetrics
} from '../../lib/ai/ai-enterprise-platform';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface TenantCardProps {
  tenant: AIEnterpriseTenant;
  onViewDetails: (tenant: AIEnterpriseTenant) => void;
  onEdit: (tenant: AIEnterpriseTenant) => void;
  onSuspend: (tenant: AIEnterpriseTenant) => void;
}

interface UserCardProps {
  user: AIEnterpriseUser;
  onViewDetails: (user: AIEnterpriseUser) => void;
  onEdit: (user: AIEnterpriseUser) => void;
  onSuspend: (user: AIEnterpriseUser) => void;
}

interface ComplianceCardProps {
  compliance: AIEnterpriseCompliance;
  onViewDetails: (compliance: AIEnterpriseCompliance) => void;
  onRunCheck: (compliance: AIEnterpriseCompliance) => void;
}

interface MetricsCardProps {
  metrics: AIEnterpriseMetrics;
  onViewDetails: (metrics: AIEnterpriseMetrics) => void;
}

// ============================================================================
// TENANT CARD COMPONENT
// ============================================================================

const TenantCard: React.FC<TenantCardProps> = ({ tenant, onViewDetails, onEdit, onSuspend }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'suspended': return '#FF9500';
      case 'pending': return '#FFCC00';
      case 'disabled': return '#FF3B30';
      default: return '#8E8E93';
    }
  };

  const getPlanColor = (plan: string): string => {
    switch (plan) {
      case 'enterprise': return '#007AFF';
      case 'professional': return '#34C759';
      case 'basic': return '#FF9500';
      case 'custom': return '#AF52DE';
      default: return '#8E8E93';
    }
  };

  const getUsagePercentage = (used: number, limit: number): number => {
    return limit > 0 ? (used / limit) * 100 : 0;
  };

  return (
    <TouchableOpacity
      style={styles.tenantCard}
      onPress={() => onViewDetails(tenant)}
      activeOpacity={0.7}
    >
      <View style={styles.tenantHeader}>
        <View style={styles.tenantInfo}>
          <Text style={styles.tenantName}>{tenant.name}</Text>
          <Text style={styles.tenantDomain}>{tenant.domain}</Text>
        </View>
        <View style={styles.tenantControls}>
          <View style={[styles.planBadge, { backgroundColor: getPlanColor(tenant.plan) }]}>
            <Text style={styles.planBadgeText}>{tenant.plan.toUpperCase()}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(tenant.status) }]}>
            <Text style={styles.statusBadgeText}>{tenant.status.toUpperCase()}</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.tenantUsage}>
        <View style={styles.usageItem}>
          <Text style={styles.usageLabel}>Models</Text>
          <View style={styles.usageBar}>
            <View 
              style={[
                styles.usageBarFill, 
                { 
                  width: `${getUsagePercentage(tenant.usage.models, tenant.limits.models)}%`,
                  backgroundColor: getUsagePercentage(tenant.usage.models, tenant.limits.models) > 80 ? '#FF3B30' : '#007AFF'
                }
              ]} 
            />
          </View>
          <Text style={styles.usageText}>{tenant.usage.models}/{tenant.limits.models}</Text>
        </View>
        
        <View style={styles.usageItem}>
          <Text style={styles.usageLabel}>Users</Text>
          <View style={styles.usageBar}>
            <View 
              style={[
                styles.usageBarFill, 
                { 
                  width: `${getUsagePercentage(tenant.usage.users, tenant.limits.users)}%`,
                  backgroundColor: getUsagePercentage(tenant.usage.users, tenant.limits.users) > 80 ? '#FF3B30' : '#007AFF'
                }
              ]} 
            />
          </View>
          <Text style={styles.usageText}>{tenant.usage.users}/{tenant.limits.users}</Text>
        </View>
        
        <View style={styles.usageItem}>
          <Text style={styles.usageLabel}>API Calls</Text>
          <View style={styles.usageBar}>
            <View 
              style={[
                styles.usageBarFill, 
                { 
                  width: `${getUsagePercentage(tenant.usage.apiCalls, tenant.limits.apiCalls)}%`,
                  backgroundColor: getUsagePercentage(tenant.usage.apiCalls, tenant.limits.apiCalls) > 80 ? '#FF3B30' : '#007AFF'
                }
              ]} 
            />
          </View>
          <Text style={styles.usageText}>{tenant.usage.apiCalls.toLocaleString()}/{tenant.limits.apiCalls.toLocaleString()}</Text>
        </View>
      </View>
      
      <View style={styles.tenantActions}>
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(tenant)}
          style={styles.tenantActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Edit"
          onPress={() => onEdit(tenant)}
          style={styles.tenantActionButton}
          variant="secondary"
          size="small"
        />
        {tenant.status === 'active' && (
          <AccessibleButton
            title="Suspend"
            onPress={() => onSuspend(tenant)}
            style={styles.tenantActionButton}
            variant="danger"
            size="small"
          />
        )}
      </View>
    </TouchableOpacity>
  );
};

// ============================================================================
// USER CARD COMPONENT
// ============================================================================

const UserCard: React.FC<UserCardProps> = ({ user, onViewDetails, onEdit, onSuspend }) => {
  const getRoleColor = (role: string): string => {
    switch (role) {
      case 'admin': return '#FF3B30';
      case 'developer': return '#007AFF';
      case 'analyst': return '#34C759';
      case 'viewer': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'inactive': return '#8E8E93';
      case 'suspended': return '#FF9500';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.userCard}>
      <View style={styles.userHeader}>
        <View style={styles.userInfo}>
          <Text style={styles.userName}>{user.name}</Text>
          <Text style={styles.userEmail}>{user.email}</Text>
        </View>
        <View style={styles.userControls}>
          <View style={[styles.roleBadge, { backgroundColor: getRoleColor(user.role) }]}>
            <Text style={styles.roleBadgeText}>{user.role.toUpperCase()}</Text>
          </View>
          <View style={[styles.statusBadge, { backgroundColor: getStatusColor(user.status) }]}>
            <Text style={styles.statusBadgeText}>{user.status.toUpperCase()}</Text>
          </View>
        </View>
      </View>
      
      <View style={styles.userDetails}>
        <Text style={styles.userDetail}>
          Last Login: {user.lastLogin ? new Date(user.lastLogin).toLocaleDateString() : 'Never'}
        </Text>
        <Text style={styles.userDetail}>
          MFA: {user.security.mfaEnabled ? 'Enabled' : 'Disabled'}
        </Text>
        <Text style={styles.userDetail}>
          Created: {new Date(user.createdAt).toLocaleDateString()}
        </Text>
      </View>
      
      <View style={styles.userActions}>
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(user)}
          style={styles.userActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Edit"
          onPress={() => onEdit(user)}
          style={styles.userActionButton}
          variant="secondary"
          size="small"
        />
        {user.status === 'active' && (
          <AccessibleButton
            title="Suspend"
            onPress={() => onSuspend(user)}
            style={styles.userActionButton}
            variant="danger"
            size="small"
          />
        )}
      </View>
    </View>
  );
};

// ============================================================================
// COMPLIANCE CARD COMPONENT
// ============================================================================

const ComplianceCard: React.FC<ComplianceCardProps> = ({ compliance, onViewDetails, onRunCheck }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'compliant': return '#34C759';
      case 'non_compliant': return '#FF3B30';
      case 'pending': return '#FF9500';
      case 'exempt': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  const getFrameworkIcon = (framework: string): string => {
    switch (framework) {
      case 'GDPR': return '🇪🇺';
      case 'CCPA': return '🇺🇸';
      case 'HIPAA': return '🏥';
      case 'SOX': return '📊';
      case 'ISO27001': return '🔒';
      case 'SOC2': return '☁️';
      default: return '📋';
    }
  };

  const metRequirements = compliance.requirements.filter(req => req.status === 'met').length;
  const totalRequirements = compliance.requirements.length;
  const compliancePercentage = totalRequirements > 0 ? (metRequirements / totalRequirements) * 100 : 0;

  return (
    <View style={styles.complianceCard}>
      <View style={styles.complianceHeader}>
        <View style={styles.complianceInfo}>
          <Text style={styles.complianceIcon}>{getFrameworkIcon(compliance.framework)}</Text>
          <View style={styles.complianceDetails}>
            <Text style={styles.complianceFramework}>{compliance.framework}</Text>
            <Text style={styles.complianceDescription}>
              {metRequirements}/{totalRequirements} requirements met
            </Text>
          </View>
        </View>
        <View style={[styles.complianceStatusBadge, { backgroundColor: getStatusColor(compliance.status) }]}>
          <Text style={styles.complianceStatusText}>{compliance.status.replace('_', ' ').toUpperCase()}</Text>
        </View>
      </View>
      
      <View style={styles.complianceProgress}>
        <View style={styles.progressBar}>
          <View 
            style={[
              styles.progressBarFill, 
              { 
                width: `${compliancePercentage}%`,
                backgroundColor: getStatusColor(compliance.status)
              }
            ]} 
          />
        </View>
        <Text style={styles.progressText}>{compliancePercentage.toFixed(1)}%</Text>
      </View>
      
      <View style={styles.complianceDetails}>
        <Text style={styles.complianceDetail}>
          Last Audit: {new Date(compliance.lastAudit).toLocaleDateString()}
        </Text>
        <Text style={styles.complianceDetail}>
          Next Audit: {new Date(compliance.nextAudit).toLocaleDateString()}
        </Text>
      </View>
      
      <View style={styles.complianceActions}>
        <AccessibleButton
          title="View Details"
          onPress={() => onViewDetails(compliance)}
          style={styles.complianceActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Run Check"
          onPress={() => onRunCheck(compliance)}
          style={styles.complianceActionButton}
          variant="primary"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// METRICS CARD COMPONENT
// ============================================================================

const MetricsCard: React.FC<MetricsCardProps> = ({ metrics, onViewDetails }) => {
  return (
    <TouchableOpacity
      style={styles.metricsCard}
      onPress={() => onViewDetails(metrics)}
      activeOpacity={0.7}
    >
      <View style={styles.metricsHeader}>
        <Text style={styles.metricsTitle}>Tenant Metrics</Text>
        <Text style={styles.metricsPeriod}>{metrics.period.toUpperCase()}</Text>
      </View>
      
      <View style={styles.metricsGrid}>
        <View style={styles.metricItem}>
          <Text style={styles.metricValue}>{metrics.metrics.activeUsers}</Text>
          <Text style={styles.metricLabel}>Active Users</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricValue}>{metrics.metrics.apiCalls.toLocaleString()}</Text>
          <Text style={styles.metricLabel}>API Calls</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricValue}>{metrics.metrics.modelInferences.toLocaleString()}</Text>
          <Text style={styles.metricLabel}>Model Inferences</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricValue}>{metrics.metrics.workflowExecutions}</Text>
          <Text style={styles.metricLabel}>Workflow Executions</Text>
        </View>
      </View>
      
      <View style={styles.metricsPerformance}>
        <Text style={styles.performanceTitle}>Performance</Text>
        <View style={styles.performanceMetrics}>
          <Text style={styles.performanceMetric}>
            Response Time: {metrics.performance.averageResponseTime.toFixed(0)}ms
          </Text>
          <Text style={styles.performanceMetric}>
            Throughput: {metrics.performance.throughput.toFixed(0)}/s
          </Text>
          <Text style={styles.performanceMetric}>
            Error Rate: {(metrics.performance.errorRate * 100).toFixed(2)}%
          </Text>
          <Text style={styles.performanceMetric}>
            Availability: {metrics.performance.availability.toFixed(2)}%
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

export function AIEnterpriseDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'tenants' | 'users' | 'compliance' | 'metrics'>('overview');
  const [tenants, setTenants] = useState<AIEnterpriseTenant[]>([]);
  const [users, setUsers] = useState<AIEnterpriseUser[]>([]);
  const [compliance, setCompliance] = useState<AIEnterpriseCompliance[]>([]);
  const [metrics, setMetrics] = useState<AIEnterpriseMetrics[]>([]);
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
      aiEnterprisePlatform.on('tenantCreated', () => refreshData());
      aiEnterprisePlatform.on('tenantUpdated', () => refreshData());
      aiEnterprisePlatform.on('userCreated', () => refreshData());
      aiEnterprisePlatform.on('complianceUpdated', () => refreshData());
      aiEnterprisePlatform.on('metricsCollected', () => refreshData());

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
      const tenantsData = aiEnterprisePlatform.getTenants();
      const usersData = Array.from(aiEnterprisePlatform['users'].values());
      const complianceData = Array.from(aiEnterprisePlatform['compliance'].values());
      const metricsData = Array.from(aiEnterprisePlatform['metrics'].values());
      
      setTenants(tenantsData);
      setUsers(usersData);
      setCompliance(complianceData);
      setMetrics(metricsData);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewTenantDetails = useCallback((tenant: AIEnterpriseTenant) => {
    Alert.alert(
      tenant.name,
      `Domain: ${tenant.domain}\nPlan: ${tenant.plan}\nStatus: ${tenant.status}\nUsers: ${tenant.usage.users}/${tenant.limits.users}\nModels: ${tenant.usage.models}/${tenant.limits.models}`
    );
  }, []);

  const handleEditTenant = useCallback((tenant: AIEnterpriseTenant) => {
    Alert.alert('Edit Tenant', `Edit functionality for tenant: ${tenant.name}`);
  }, []);

  const handleSuspendTenant = useCallback((tenant: AIEnterpriseTenant) => {
    Alert.alert(
      'Suspend Tenant',
      `Are you sure you want to suspend tenant "${tenant.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Suspend',
          style: 'destructive',
          onPress: () => {
            const success = aiEnterprisePlatform.updateTenant(tenant.id, { status: 'suspended' });
            if (success) {
              Alert.alert('Success', 'Tenant suspended successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to suspend tenant');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleViewUserDetails = useCallback((user: AIEnterpriseUser) => {
    Alert.alert(
      user.name,
      `Email: ${user.email}\nRole: ${user.role}\nStatus: ${user.status}\nLast Login: ${user.lastLogin ? new Date(user.lastLogin).toLocaleString() : 'Never'}\nMFA: ${user.security.mfaEnabled ? 'Enabled' : 'Disabled'}`
    );
  }, []);

  const handleEditUser = useCallback((user: AIEnterpriseUser) => {
    Alert.alert('Edit User', `Edit functionality for user: ${user.name}`);
  }, []);

  const handleSuspendUser = useCallback((user: AIEnterpriseUser) => {
    Alert.alert(
      'Suspend User',
      `Are you sure you want to suspend user "${user.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Suspend',
          style: 'destructive',
          onPress: () => {
            const success = aiEnterprisePlatform.updateUser(user.id, { status: 'suspended' });
            if (success) {
              Alert.alert('Success', 'User suspended successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to suspend user');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleViewComplianceDetails = useCallback((compliance: AIEnterpriseCompliance) => {
    const metRequirements = compliance.requirements.filter(req => req.status === 'met').length;
    const totalRequirements = compliance.requirements.length;
    
    Alert.alert(
      `${compliance.framework} Compliance`,
      `Status: ${compliance.status}\nRequirements Met: ${metRequirements}/${totalRequirements}\nLast Audit: ${new Date(compliance.lastAudit).toLocaleDateString()}\nNext Audit: ${new Date(compliance.nextAudit).toLocaleDateString()}`
    );
  }, []);

  const handleRunComplianceCheck = useCallback((compliance: AIEnterpriseCompliance) => {
    Alert.alert('Run Compliance Check', `Running compliance check for ${compliance.framework}...`);
    // In real implementation, this would trigger a compliance check
  }, []);

  const handleViewMetricsDetails = useCallback((metrics: AIEnterpriseMetrics) => {
    Alert.alert(
      'Metrics Details',
      `Period: ${metrics.period}\nActive Users: ${metrics.metrics.activeUsers}\nAPI Calls: ${metrics.metrics.apiCalls.toLocaleString()}\nModel Inferences: ${metrics.metrics.modelInferences.toLocaleString()}\nResponse Time: ${metrics.performance.averageResponseTime.toFixed(0)}ms\nAvailability: ${metrics.performance.availability.toFixed(2)}%`
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
    const stats = aiEnterprisePlatform.getSystemStats();
    const recentTenants = tenants.slice(0, 3);
    const recentUsers = users.slice(0, 5);
    const recentCompliance = compliance.slice(0, 3);

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
          <Text style={styles.sectionTitle}>Enterprise Platform Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalTenants}</Text>
              <Text style={styles.statLabel}>Total Tenants</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeTenants}</Text>
              <Text style={styles.statLabel}>Active Tenants</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalUsers}</Text>
              <Text style={styles.statLabel}>Total Users</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeUsers}</Text>
              <Text style={styles.statLabel}>Active Users</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalAPIKeys}</Text>
              <Text style={styles.statLabel}>API Keys</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.complianceStatus.compliant}</Text>
              <Text style={styles.statLabel}>Compliant</Text>
            </View>
          </View>
        </View>

        {/* Recent Tenants */}
        {recentTenants.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Tenants</Text>
            {recentTenants.map(tenant => (
              <TenantCard
                key={tenant.id}
                tenant={tenant}
                onViewDetails={handleViewTenantDetails}
                onEdit={handleEditTenant}
                onSuspend={handleSuspendTenant}
              />
            ))}
          </View>
        )}

        {/* Recent Users */}
        {recentUsers.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Users</Text>
            {recentUsers.map(user => (
              <UserCard
                key={user.id}
                user={user}
                onViewDetails={handleViewUserDetails}
                onEdit={handleEditUser}
                onSuspend={handleSuspendUser}
              />
            ))}
          </View>
        )}

        {/* Compliance Status */}
        {recentCompliance.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Compliance Status</Text>
            {recentCompliance.map(compliance => (
              <ComplianceCard
                key={compliance.id}
                compliance={compliance}
                onViewDetails={handleViewComplianceDetails}
                onRunCheck={handleRunComplianceCheck}
              />
            ))}
          </View>
        )}

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
              title="🏢 View Tenants"
              onPress={() => handleTabChange('tenants')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="👥 View Users"
              onPress={() => handleTabChange('users')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderTenantsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Tenant Management</Text>
        {tenants.length > 0 ? (
          tenants.map(tenant => (
            <TenantCard
              key={tenant.id}
              tenant={tenant}
              onViewDetails={handleViewTenantDetails}
              onEdit={handleEditTenant}
              onSuspend={handleSuspendTenant}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No tenants available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderUsersTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>User Management</Text>
        {users.length > 0 ? (
          users.map(user => (
            <UserCard
              key={user.id}
              user={user}
              onViewDetails={handleViewUserDetails}
              onEdit={handleEditUser}
              onSuspend={handleSuspendUser}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No users available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderComplianceTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Compliance Management</Text>
        {compliance.length > 0 ? (
          compliance.map(compliance => (
            <ComplianceCard
              key={compliance.id}
              compliance={compliance}
              onViewDetails={handleViewComplianceDetails}
              onRunCheck={handleRunComplianceCheck}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No compliance records available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderMetricsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>System Metrics</Text>
        {metrics.length > 0 ? (
          metrics.slice(0, 10).map((metrics, index) => (
            <MetricsCard
              key={index}
              metrics={metrics}
              onViewDetails={handleViewMetricsDetails}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No metrics available</Text>
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
        <Text style={styles.headerTitle}>AI Enterprise Platform</Text>
        <Text style={styles.headerSubtitle}>
          Multi-Tenant AI Platform Management & Compliance
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('tenants', 'Tenants')}
        {renderTabButton('users', 'Users')}
        {renderTabButton('compliance', 'Compliance')}
        {renderTabButton('metrics', 'Metrics')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'tenants' && renderTenantsTab()}
        {activeTab === 'users' && renderUsersTab()}
        {activeTab === 'compliance' && renderComplianceTab()}
        {activeTab === 'metrics' && renderMetricsTab()}
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
  tenantCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  tenantHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  tenantInfo: {
    flex: 1,
  },
  tenantName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  tenantDomain: {
    fontSize: 14,
    color: '#666',
  },
  tenantControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  planBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  planBadgeText: {
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
  tenantUsage: {
    marginBottom: 12,
  },
  usageItem: {
    marginBottom: 8,
  },
  usageLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  usageBar: {
    height: 4,
    backgroundColor: '#e0e0e0',
    borderRadius: 2,
    overflow: 'hidden',
  },
  usageBarFill: {
    height: '100%',
    borderRadius: 2,
  },
  usageText: {
    fontSize: 12,
    color: '#333',
    marginTop: 2,
  },
  tenantActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  tenantActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  userCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  userHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  userInfo: {
    flex: 1,
  },
  userName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  userEmail: {
    fontSize: 14,
    color: '#666',
  },
  userControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  roleBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
    marginRight: 8,
  },
  roleBadgeText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  userDetails: {
    marginBottom: 12,
  },
  userDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  userActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  userActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  complianceCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  complianceHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  complianceInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  complianceIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  complianceDetails: {
    flex: 1,
  },
  complianceFramework: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  complianceDescription: {
    fontSize: 14,
    color: '#666',
  },
  complianceStatusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  complianceStatusText: {
    color: '#ffffff',
    fontSize: 10,
    fontWeight: 'bold',
  },
  complianceProgress: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressBar: {
    flex: 1,
    height: 8,
    backgroundColor: '#e0e0e0',
    borderRadius: 4,
    overflow: 'hidden',
    marginRight: 12,
  },
  progressBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  progressText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#333',
  },
  complianceDetail: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  complianceActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  complianceActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  metricsCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  metricsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  metricsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
  },
  metricsPeriod: {
    fontSize: 12,
    color: '#666',
  },
  metricsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  metricItem: {
    width: '48%',
    alignItems: 'center',
    marginBottom: 8,
  },
  metricValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#007AFF',
    marginBottom: 4,
  },
  metricLabel: {
    fontSize: 12,
    color: '#666',
    textAlign: 'center',
  },
  metricsPerformance: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 12,
  },
  performanceTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  performanceMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  performanceMetric: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
    width: '50%',
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

export default AIEnterpriseDashboard;

