/**
 * @fileoverview AI Global Deployment Dashboard
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
import { 
  aiGlobalDeploymentManager,
  AIGlobalRegion,
  AIGlobalDeployment,
  AIGlobalLoadBalancer,
  AIGlobalCDN,
  AIGlobalMonitoring,
  AIGlobalScalingEvent
} from '../../lib/ai/ai-global-deployment';

// ============================================================================
// COMPONENT INTERFACES
// ============================================================================

interface RegionCardProps {
  region: AIGlobalRegion;
  onViewDetails: (region: AIGlobalRegion) => void;
  onUpdateStatus: (region: AIGlobalRegion) => void;
}

interface DeploymentCardProps {
  deployment: AIGlobalDeployment;
  onViewDetails: (deployment: AIGlobalDeployment) => void;
  onScale: (deployment: AIGlobalDeployment) => void;
  onStop: (deployment: AIGlobalDeployment) => void;
}

interface LoadBalancerCardProps {
  loadBalancer: AIGlobalLoadBalancer;
  onViewDetails: (loadBalancer: AIGlobalLoadBalancer) => void;
  onUpdateTargets: (loadBalancer: AIGlobalLoadBalancer) => void;
}

// ============================================================================
// REGION CARD COMPONENT
// ============================================================================

const RegionCard: React.FC<RegionCardProps> = ({ region, onViewDetails, onUpdateStatus }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'maintenance': return '#FF9500';
      case 'offline': return '#FF3B30';
      case 'degraded': return '#FFCC00';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.regionCard}>
      <View style={styles.regionHeader}>
        <View style={styles.regionInfo}>
          <Text style={styles.regionName}>{region.name}</Text>
          <Text style={styles.regionLocation}>{region.location}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(region.status) }]}>
          <Text style={styles.statusBadgeText}>{region.status.toUpperCase()}</Text>
        </View>
      </View>
      
      <View style={styles.regionCapabilities}>
        <View style={styles.capabilityItem}>
          <Text style={styles.capabilityLabel}>CPU</Text>
          <Text style={styles.capabilityValue}>{region.capabilities.compute.cpu}</Text>
        </View>
        <View style={styles.capabilityItem}>
          <Text style={styles.capabilityLabel}>Memory</Text>
          <Text style={styles.capabilityValue}>{region.capabilities.compute.memory}GB</Text>
        </View>
        <View style={styles.capabilityItem}>
          <Text style={styles.capabilityLabel}>GPU</Text>
          <Text style={styles.capabilityValue}>{region.capabilities.compute.gpu}</Text>
        </View>
        <View style={styles.capabilityItem}>
          <Text style={styles.capabilityLabel}>Storage</Text>
          <Text style={styles.capabilityValue}>{region.capabilities.compute.storage}TB</Text>
        </View>
      </View>
      
      <View style={styles.regionMetrics}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Latency</Text>
          <Text style={styles.metricValue}>{region.capabilities.latency.average}ms</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Availability</Text>
          <Text style={styles.metricValue}>{region.capabilities.availability}%</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Models</Text>
          <Text style={styles.metricValue}>{region.capabilities.models.length}</Text>
        </View>
      </View>
      
      <View style={styles.regionActions}>
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(region)}
          style={styles.regionActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Update Status"
          onPress={() => onUpdateStatus(region)}
          style={styles.regionActionButton}
          variant="secondary"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// DEPLOYMENT CARD COMPONENT
// ============================================================================

const DeploymentCard: React.FC<DeploymentCardProps> = ({ deployment, onViewDetails, onScale, onStop }) => {
  const getStatusColor = (status: string): string => {
    switch (status) {
      case 'active': return '#34C759';
      case 'deploying': return '#007AFF';
      case 'scaling': return '#FF9500';
      case 'updating': return '#AF52DE';
      case 'failed': return '#FF3B30';
      case 'stopped': return '#8E8E93';
      default: return '#8E8E93';
    }
  };

  return (
    <View style={styles.deploymentCard}>
      <View style={styles.deploymentHeader}>
        <View style={styles.deploymentInfo}>
          <Text style={styles.deploymentName}>{deployment.name}</Text>
          <Text style={styles.deploymentType}>{deployment.type.toUpperCase()}</Text>
        </View>
        <View style={[styles.statusBadge, { backgroundColor: getStatusColor(deployment.status) }]}>
          <Text style={styles.statusBadgeText}>{deployment.status.toUpperCase()}</Text>
        </View>
      </View>
      
      <View style={styles.deploymentDetails}>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Regions</Text>
          <Text style={styles.detailValue}>{deployment.regions.join(', ')}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Replicas</Text>
          <Text style={styles.detailValue}>{deployment.configuration.replicas}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>CPU</Text>
          <Text style={styles.detailValue}>{deployment.configuration.resources.cpu}</Text>
        </View>
        <View style={styles.detailItem}>
          <Text style={styles.detailLabel}>Memory</Text>
          <Text style={styles.detailValue}>{deployment.configuration.resources.memory}GB</Text>
        </View>
      </View>
      
      <View style={styles.deploymentTraffic}>
        <Text style={styles.trafficTitle}>Traffic</Text>
        <View style={styles.trafficMetrics}>
          <Text style={styles.trafficMetric}>
            Total: {deployment.traffic.total.toLocaleString()}
          </Text>
          <Text style={styles.trafficMetric}>
            Errors: {deployment.traffic.errors}
          </Text>
          <Text style={styles.trafficMetric}>
            Latency: {deployment.traffic.latency.average.toFixed(0)}ms
          </Text>
        </View>
      </View>
      
      <View style={styles.deploymentActions}>
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(deployment)}
          style={styles.deploymentActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Scale"
          onPress={() => onScale(deployment)}
          style={styles.deploymentActionButton}
          variant="secondary"
          size="small"
        />
        {deployment.status === 'active' && (
          <AccessibleButton
            title="Stop"
            onPress={() => onStop(deployment)}
            style={styles.deploymentActionButton}
            variant="danger"
            size="small"
          />
        )}
      </View>
    </View>
  );
};

// ============================================================================
// LOAD BALANCER CARD COMPONENT
// ============================================================================

const LoadBalancerCard: React.FC<LoadBalancerCardProps> = ({ loadBalancer, onViewDetails, onUpdateTargets }) => {
  const healthyTargets = loadBalancer.targets.filter(t => t.health === 'healthy').length;
  const totalTargets = loadBalancer.targets.length;

  return (
    <View style={styles.loadBalancerCard}>
      <View style={styles.loadBalancerHeader}>
        <View style={styles.loadBalancerInfo}>
          <Text style={styles.loadBalancerName}>{loadBalancer.name}</Text>
          <Text style={styles.loadBalancerStrategy}>{loadBalancer.strategy.replace('_', ' ').toUpperCase()}</Text>
        </View>
        <View style={styles.targetsInfo}>
          <Text style={styles.targetsText}>{healthyTargets}/{totalTargets} Healthy</Text>
        </View>
      </View>
      
      <View style={styles.loadBalancerMetrics}>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>RPS</Text>
          <Text style={styles.metricValue}>{loadBalancer.metrics.requestsPerSecond.toFixed(0)}</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Latency</Text>
          <Text style={styles.metricValue}>{loadBalancer.metrics.averageLatency.toFixed(0)}ms</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Error Rate</Text>
          <Text style={styles.metricValue}>{(loadBalancer.metrics.errorRate * 100).toFixed(2)}%</Text>
        </View>
        <View style={styles.metricItem}>
          <Text style={styles.metricLabel}>Availability</Text>
          <Text style={styles.metricValue}>{loadBalancer.metrics.availability.toFixed(2)}%</Text>
        </View>
      </View>
      
      <View style={styles.loadBalancerActions}>
        <AccessibleButton
          title="Details"
          onPress={() => onViewDetails(loadBalancer)}
          style={styles.loadBalancerActionButton}
          variant="outline"
          size="small"
        />
        <AccessibleButton
          title="Update Targets"
          onPress={() => onUpdateTargets(loadBalancer)}
          style={styles.loadBalancerActionButton}
          variant="secondary"
          size="small"
        />
      </View>
    </View>
  );
};

// ============================================================================
// MAIN DASHBOARD COMPONENT
// ============================================================================

export function AIGlobalDeploymentDashboard(): JSX.Element {
  // ============================================================================
  // HOOKS AND STATE
  // ============================================================================

  const [activeTab, setActiveTab] = useState<'overview' | 'regions' | 'deployments' | 'loadbalancers' | 'monitoring'>('overview');
  const [regions, setRegions] = useState<AIGlobalRegion[]>([]);
  const [deployments, setDeployments] = useState<AIGlobalDeployment[]>([]);
  const [loadBalancers, setLoadBalancers] = useState<AIGlobalLoadBalancer[]>([]);
  const [monitoring, setMonitoring] = useState<AIGlobalMonitoring[]>([]);
  const [scalingEvents, setScalingEvents] = useState<AIGlobalScalingEvent[]>([]);
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
      aiGlobalDeploymentManager.on('regionCreated', () => refreshData());
      aiGlobalDeploymentManager.on('deploymentCreated', () => refreshData());
      aiGlobalDeploymentManager.on('loadBalancerCreated', () => refreshData());
      aiGlobalDeploymentManager.on('metricsCollected', () => refreshData());
      aiGlobalDeploymentManager.on('scalingEvent', () => refreshData());

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
      const regionsData = aiGlobalDeploymentManager.getRegions();
      const deploymentsData = Array.from(aiGlobalDeploymentManager['deployments'].values());
      const loadBalancersData = aiGlobalDeploymentManager.getLoadBalancers();
      const monitoringData = aiGlobalDeploymentManager.getMonitoringData();
      const scalingEventsData = aiGlobalDeploymentManager.getScalingEvents();
      
      setRegions(regionsData);
      setDeployments(deploymentsData);
      setLoadBalancers(loadBalancersData);
      setMonitoring(monitoringData);
      setScalingEvents(scalingEventsData);
    } catch (error) {
      console.error('Failed to refresh data:', error);
    }
  }, []);

  const handleViewRegionDetails = useCallback((region: AIGlobalRegion) => {
    Alert.alert(
      region.name,
      `Location: ${region.location}\nStatus: ${region.status}\nCPU: ${region.capabilities.compute.cpu}\nMemory: ${region.capabilities.compute.memory}GB\nGPU: ${region.capabilities.compute.gpu}\nStorage: ${region.capabilities.compute.storage}TB\nLatency: ${region.capabilities.latency.average}ms\nAvailability: ${region.capabilities.availability}%\nModels: ${region.capabilities.models.join(', ')}`
    );
  }, []);

  const handleUpdateRegionStatus = useCallback((region: AIGlobalRegion) => {
    Alert.alert(
      'Update Region Status',
      `Current status: ${region.status}`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Active', onPress: () => {
          const success = aiGlobalDeploymentManager.updateRegionStatus(region.id, 'active');
          if (success) {
            Alert.alert('Success', 'Region status updated to active');
            refreshData();
          }
        }},
        { text: 'Maintenance', onPress: () => {
          const success = aiGlobalDeploymentManager.updateRegionStatus(region.id, 'maintenance');
          if (success) {
            Alert.alert('Success', 'Region status updated to maintenance');
            refreshData();
          }
        }},
        { text: 'Offline', onPress: () => {
          const success = aiGlobalDeploymentManager.updateRegionStatus(region.id, 'offline');
          if (success) {
            Alert.alert('Success', 'Region status updated to offline');
            refreshData();
          }
        }},
      ]
    );
  }, [refreshData]);

  const handleViewDeploymentDetails = useCallback((deployment: AIGlobalDeployment) => {
    Alert.alert(
      deployment.name,
      `Type: ${deployment.type}\nStatus: ${deployment.status}\nRegions: ${deployment.regions.join(', ')}\nReplicas: ${deployment.configuration.replicas}\nCPU: ${deployment.configuration.resources.cpu}\nMemory: ${deployment.configuration.resources.memory}GB\nTraffic: ${deployment.traffic.total.toLocaleString()}\nErrors: ${deployment.traffic.errors}\nLatency: ${deployment.traffic.latency.average.toFixed(0)}ms`
    );
  }, []);

  const handleScaleDeployment = useCallback((deployment: AIGlobalDeployment) => {
    Alert.prompt(
      'Scale Deployment',
      `Current replicas: ${deployment.configuration.replicas}\nMin: ${deployment.configuration.scaling.minReplicas}\nMax: ${deployment.configuration.scaling.maxReplicas}`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Scale', onPress: (text) => {
          const replicas = parseInt(text || '0');
          if (replicas >= deployment.configuration.scaling.minReplicas && 
              replicas <= deployment.configuration.scaling.maxReplicas) {
            const success = aiGlobalDeploymentManager.scaleDeployment(deployment.id, replicas);
            if (success) {
              Alert.alert('Success', `Deployment scaled to ${replicas} replicas`);
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to scale deployment');
            }
          } else {
            Alert.alert('Error', 'Invalid replica count');
          }
        }},
      ],
      'plain-text',
      deployment.configuration.replicas.toString()
    );
  }, [refreshData]);

  const handleStopDeployment = useCallback((deployment: AIGlobalDeployment) => {
    Alert.alert(
      'Stop Deployment',
      `Are you sure you want to stop deployment "${deployment.name}"?`,
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Stop',
          style: 'destructive',
          onPress: () => {
            const success = aiGlobalDeploymentManager.updateDeploymentStatus(deployment.id, 'stopped');
            if (success) {
              Alert.alert('Success', 'Deployment stopped successfully');
              refreshData();
            } else {
              Alert.alert('Error', 'Failed to stop deployment');
            }
          },
        },
      ]
    );
  }, [refreshData]);

  const handleViewLoadBalancerDetails = useCallback((loadBalancer: AIGlobalLoadBalancer) => {
    const targetsText = loadBalancer.targets.map(t => 
      `${t.region}: ${t.health} (${t.latency}ms, weight: ${t.weight})`
    ).join('\n');
    
    Alert.alert(
      loadBalancer.name,
      `Strategy: ${loadBalancer.strategy}\nRPS: ${loadBalancer.metrics.requestsPerSecond.toFixed(0)}\nLatency: ${loadBalancer.metrics.averageLatency.toFixed(0)}ms\nError Rate: ${(loadBalancer.metrics.errorRate * 100).toFixed(2)}%\nAvailability: ${loadBalancer.metrics.availability.toFixed(2)}%\n\nTargets:\n${targetsText}`
    );
  }, []);

  const handleUpdateLoadBalancerTargets = useCallback((loadBalancer: AIGlobalLoadBalancer) => {
    Alert.alert('Update Targets', 'Target update functionality would be implemented here');
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
    const stats = aiGlobalDeploymentManager.getGlobalStats();
    const recentDeployments = deployments.slice(0, 3);
    const recentScalingEvents = scalingEvents.slice(0, 5);

    return (
      <ScrollView 
        style={styles.tabContent} 
        showsVerticalScrollIndicator={false}
        refreshControl={
          <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
        }
      >
        {/* Global Stats */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Global Deployment Overview</Text>
          <View style={styles.statsGrid}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalRegions}</Text>
              <Text style={styles.statLabel}>Total Regions</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeRegions}</Text>
              <Text style={styles.statLabel}>Active Regions</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalDeployments}</Text>
              <Text style={styles.statLabel}>Total Deployments</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.activeDeployments}</Text>
              <Text style={styles.statLabel}>Active Deployments</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalLoadBalancers}</Text>
              <Text style={styles.statLabel}>Load Balancers</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.totalCDNs}</Text>
              <Text style={styles.statLabel}>CDNs</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.averageLatency.toFixed(0)}ms</Text>
              <Text style={styles.statLabel}>Avg Latency</Text>
            </View>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{stats.globalAvailability.toFixed(2)}%</Text>
              <Text style={styles.statLabel}>Availability</Text>
            </View>
          </View>
        </View>

        {/* Recent Deployments */}
        {recentDeployments.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Deployments</Text>
            {recentDeployments.map(deployment => (
              <DeploymentCard
                key={deployment.id}
                deployment={deployment}
                onViewDetails={handleViewDeploymentDetails}
                onScale={handleScaleDeployment}
                onStop={handleStopDeployment}
              />
            ))}
          </View>
        )}

        {/* Recent Scaling Events */}
        {recentScalingEvents.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Recent Scaling Events</Text>
            {recentScalingEvents.map(event => (
              <View key={event.id} style={styles.scalingEventCard}>
                <View style={styles.scalingEventHeader}>
                  <Text style={styles.scalingEventType}>{event.type.replace('_', ' ').toUpperCase()}</Text>
                  <Text style={styles.scalingEventTime}>
                    {new Date(event.timestamp).toLocaleString()}
                  </Text>
                </View>
                <Text style={styles.scalingEventDetails}>
                  {event.deploymentId}: {event.from.replicas} → {event.to.replicas} replicas
                </Text>
                <Text style={styles.scalingEventReason}>
                  Reason: {event.reason.replace('_', ' ')}
                </Text>
              </View>
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
              title="🌍 View Regions"
              onPress={() => handleTabChange('regions')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
            <AccessibleButton
              title="🚀 View Deployments"
              onPress={() => handleTabChange('deployments')}
              style={styles.actionButton}
              variant="secondary"
              size="small"
            />
          </View>
        </View>
      </ScrollView>
    );
  };

  const renderRegionsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Global Regions</Text>
        {regions.length > 0 ? (
          regions.map(region => (
            <RegionCard
              key={region.id}
              region={region}
              onViewDetails={handleViewRegionDetails}
              onUpdateStatus={handleUpdateRegionStatus}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No regions available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderDeploymentsTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Global Deployments</Text>
        {deployments.length > 0 ? (
          deployments.map(deployment => (
            <DeploymentCard
              key={deployment.id}
              deployment={deployment}
              onViewDetails={handleViewDeploymentDetails}
              onScale={handleScaleDeployment}
              onStop={handleStopDeployment}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No deployments available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderLoadBalancersTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Load Balancers</Text>
        {loadBalancers.length > 0 ? (
          loadBalancers.map(loadBalancer => (
            <LoadBalancerCard
              key={loadBalancer.id}
              loadBalancer={loadBalancer}
              onViewDetails={handleViewLoadBalancerDetails}
              onUpdateTargets={handleUpdateLoadBalancerTargets}
            />
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No load balancers available</Text>
          </View>
        )}
      </View>
    </ScrollView>
  );

  const renderMonitoringTab = (): JSX.Element => (
    <ScrollView 
      style={styles.tabContent} 
      showsVerticalScrollIndicator={false}
      refreshControl={
        <RefreshControl refreshing={isRefreshing} onRefresh={handleRefresh} />
      }
    >
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Global Monitoring</Text>
        {monitoring.length > 0 ? (
          monitoring.slice(0, 10).map((monitoring, index) => (
            <View key={index} style={styles.monitoringCard}>
              <View style={styles.monitoringHeader}>
                <Text style={styles.monitoringDeployment}>{monitoring.deploymentId}</Text>
                <Text style={styles.monitoringRegion}>{monitoring.region}</Text>
                <Text style={styles.monitoringTime}>
                  {new Date(monitoring.timestamp).toLocaleString()}
                </Text>
              </View>
              <View style={styles.monitoringMetrics}>
                <Text style={styles.monitoringMetric}>
                  CPU: {monitoring.metrics.cpu.toFixed(1)}%
                </Text>
                <Text style={styles.monitoringMetric}>
                  Memory: {monitoring.metrics.memory.toFixed(1)}%
                </Text>
                <Text style={styles.monitoringMetric}>
                  Requests: {monitoring.metrics.requests.total}
                </Text>
                <Text style={styles.monitoringMetric}>
                  Latency: {monitoring.metrics.latency.average.toFixed(0)}ms
                </Text>
              </View>
              {monitoring.alerts.length > 0 && (
                <View style={styles.monitoringAlerts}>
                  <Text style={styles.alertsTitle}>Alerts:</Text>
                  {monitoring.alerts.map(alert => (
                    <Text key={alert.id} style={styles.alertText}>
                      {alert.type}: {alert.message}
                    </Text>
                  ))}
                </View>
              )}
            </View>
          ))
        ) : (
          <View style={styles.emptyState}>
            <Text style={styles.emptyStateText}>No monitoring data available</Text>
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
        <Text style={styles.headerTitle}>AI Global Deployment</Text>
        <Text style={styles.headerSubtitle}>
          Global AI Platform Deployment & Scaling Management
        </Text>
      </View>

      {/* Tab Navigation */}
      <View style={styles.tabContainer}>
        {renderTabButton('overview', 'Overview')}
        {renderTabButton('regions', 'Regions')}
        {renderTabButton('deployments', 'Deployments')}
        {renderTabButton('loadbalancers', 'Load Balancers')}
        {renderTabButton('monitoring', 'Monitoring')}
      </View>

      {/* Tab Content */}
      <View style={styles.contentContainer}>
        {activeTab === 'overview' && renderOverviewTab()}
        {activeTab === 'regions' && renderRegionsTab()}
        {activeTab === 'deployments' && renderDeploymentsTab()}
        {activeTab === 'loadbalancers' && renderLoadBalancersTab()}
        {activeTab === 'monitoring' && renderMonitoringTab()}
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
  regionCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  regionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  regionInfo: {
    flex: 1,
  },
  regionName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  regionLocation: {
    fontSize: 14,
    color: '#666',
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
  regionCapabilities: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  capabilityItem: {
    alignItems: 'center',
  },
  capabilityLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
  },
  capabilityValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  regionMetrics: {
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
    marginBottom: 4,
  },
  metricValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  regionActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  regionActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  deploymentCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  deploymentHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  deploymentInfo: {
    flex: 1,
  },
  deploymentName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  deploymentType: {
    fontSize: 12,
    color: '#666',
  },
  deploymentDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 12,
  },
  detailItem: {
    width: '50%',
    marginBottom: 8,
  },
  detailLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 2,
  },
  detailValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  deploymentTraffic: {
    marginBottom: 12,
  },
  trafficTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  trafficMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  trafficMetric: {
    fontSize: 12,
    color: '#666',
    marginRight: 16,
    marginBottom: 4,
  },
  deploymentActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  deploymentActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  loadBalancerCard: {
    backgroundColor: '#f8f9fa',
    padding: 16,
    borderRadius: 8,
    marginBottom: 12,
  },
  loadBalancerHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  loadBalancerInfo: {
    flex: 1,
  },
  loadBalancerName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 4,
  },
  loadBalancerStrategy: {
    fontSize: 12,
    color: '#666',
  },
  targetsInfo: {
    alignItems: 'flex-end',
  },
  targetsText: {
    fontSize: 12,
    color: '#666',
  },
  loadBalancerMetrics: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 12,
  },
  loadBalancerActions: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  loadBalancerActionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginHorizontal: 4,
  },
  scalingEventCard: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  scalingEventHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  scalingEventType: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  scalingEventTime: {
    fontSize: 12,
    color: '#666',
  },
  scalingEventDetails: {
    fontSize: 14,
    color: '#333',
    marginBottom: 2,
  },
  scalingEventReason: {
    fontSize: 12,
    color: '#666',
  },
  monitoringCard: {
    backgroundColor: '#f8f9fa',
    padding: 12,
    borderRadius: 8,
    marginBottom: 8,
  },
  monitoringHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  monitoringDeployment: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
  },
  monitoringRegion: {
    fontSize: 12,
    color: '#666',
  },
  monitoringTime: {
    fontSize: 12,
    color: '#666',
  },
  monitoringMetrics: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8,
  },
  monitoringMetric: {
    fontSize: 12,
    color: '#666',
    marginRight: 16,
    marginBottom: 4,
  },
  monitoringAlerts: {
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingTop: 8,
  },
  alertsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FF3B30',
    marginBottom: 4,
  },
  alertText: {
    fontSize: 12,
    color: '#FF3B30',
    marginBottom: 2,
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

export default AIGlobalDeploymentDashboard;
