/**
 * @fileoverview Comprehensive analytics system demo
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAnalyticsContext } from '../analytics/analytics-provider';
import { AnalyticsButton } from '../analytics/analytics-button';
import { PerformanceMonitor } from '../analytics/performance-monitor';
import { 
  UserActionEvent, 
  PerformanceEvent, 
  ErrorEvent, 
  ConversionEvent 
} from '../../lib/analytics/analytics-types';

/**
 * Comprehensive demo of the analytics system
 */
export function AnalyticsDemo(): React.JSX.Element {
  const analytics = useAnalyticsContext();
  const [eventCount, setEventCount] = useState(0);
  const [funnelStep, setFunnelStep] = useState(1);

  /**
   * Tracks a custom event
   */
  const trackCustomEvent = async (): Promise<void> => {
    try {
      await analytics.trackEvent('custom_demo_event', {
        eventCount: eventCount + 1,
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setEventCount(prev => prev + 1);
      Alert.alert('Event Tracked', 'Custom event has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track custom event');
    }
  };

  /**
   * Tracks a user action
   */
  const trackUserAction = async (): Promise<void> => {
    try {
      const userAction: UserActionEvent = {
        actionType: 'tap',
        elementType: 'button',
        elementId: 'demo_action_button',
        elementText: 'Track User Action',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackUserAction(userAction);
      Alert.alert('Action Tracked', 'User action has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track user action');
    }
  };

  /**
   * Tracks a performance metric
   */
  const trackPerformanceMetric = async (): Promise<void> => {
    try {
      const performanceEvent: PerformanceEvent = {
        metricName: 'demo_metric',
        value: Math.random() * 1000,
        unit: 'ms',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackPerformance(performanceEvent);
      Alert.alert('Metric Tracked', 'Performance metric has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track performance metric');
    }
  };

  /**
   * Tracks an error
   */
  const trackError = async (): Promise<void> => {
    try {
      const errorEvent: ErrorEvent = {
        errorType: 'javascript',
        errorMessage: 'Demo error for testing purposes',
        errorCode: 'DEMO_ERROR_001',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackError(errorEvent);
      Alert.alert('Error Tracked', 'Error has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track error');
    }
  };

  /**
   * Tracks a conversion event
   */
  const trackConversion = async (): Promise<void> => {
    try {
      const conversionEvent: ConversionEvent = {
        conversionType: 'feature_usage',
        value: 99.99,
        currency: 'USD',
        properties: {
          feature: 'analytics_demo',
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackConversion(conversionEvent);
      Alert.alert('Conversion Tracked', 'Conversion event has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track conversion');
    }
  };

  /**
   * Starts a funnel analysis
   */
  const startFunnel = async (): Promise<void> => {
    try {
      await analytics.startFunnel('demo_funnel', 'step_1', {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setFunnelStep(1);
      Alert.alert('Funnel Started', 'Demo funnel has been started');
    } catch (error) {
      Alert.alert('Error', 'Failed to start funnel');
    }
  };

  /**
   * Completes a funnel step
   */
  const completeFunnelStep = async (): Promise<void> => {
    try {
      const stepName = `step_${funnelStep + 1}`;
      await analytics.completeFunnel('demo_funnel', stepName, {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setFunnelStep(prev => prev + 1);
      Alert.alert('Funnel Step', `Completed ${stepName}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to complete funnel step');
    }
  };

  /**
   * Sets user properties
   */
  const setUserProperties = async (): Promise<void> => {
    try {
      await analytics.setUserProperties({
        userId: 'demo_user_123',
        email: 'demo@example.com',
        name: 'Demo User',
        subscriptionTier: 'premium',
        registrationDate: Date.now(),
        lastActiveDate: Date.now(),
        totalSessions: 1,
        totalEvents: eventCount
      });
      
      Alert.alert('User Properties Set', 'User properties have been updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to set user properties');
    }
  };

  /**
   * Flushes analytics events
   */
  const flushEvents = async (): Promise<void> => {
    try {
      await analytics.flush();
      Alert.alert('Events Flushed', 'Analytics events have been flushed');
    } catch (error) {
      Alert.alert('Error', 'Failed to flush events');
    }
  };

  /**
   * Resets analytics data
   */
  const resetAnalytics = async (): Promise<void> => {
    try {
      await analytics.reset();
      setEventCount(0);
      setFunnelStep(1);
      Alert.alert('Analytics Reset', 'Analytics data has been reset');
    } catch (error) {
      Alert.alert('Error', 'Failed to reset analytics');
    }
  };

  // Track screen view on mount
  useEffect(() => {
    if (analytics.isInitialized) {
      analytics.trackScreenView('analytics_demo', {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
    }
  }, [analytics]);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Analytics System Demo</Text>
          <Text style={styles.subtitle}>
            Comprehensive user behavior tracking and analytics
          </Text>
        </View>

        {/* Status Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Initialized:</Text>
            <Text style={[styles.statusValue, { 
              color: analytics.isInitialized ? '#10B981' : '#EF4444' 
            }]}>
              {analytics.isInitialized ? 'Yes' : 'No'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Events Tracked:</Text>
            <Text style={styles.statusValue}>{eventCount}</Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Funnel Step:</Text>
            <Text style={styles.statusValue}>{funnelStep}</Text>
          </View>
        </View>

        {/* Event Tracking */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Event Tracking</Text>
          
          <AnalyticsButton
            title="Track Custom Event"
            eventName="demo_custom_event"
            eventProperties={{ source: 'analytics_demo' }}
            screenName="analytics_demo"
            onPress={trackCustomEvent}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track User Action"
            eventName="demo_user_action"
            screenName="analytics_demo"
            onPress={trackUserAction}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track Performance Metric"
            eventName="demo_performance"
            screenName="analytics_demo"
            onPress={trackPerformanceMetric}
            style={styles.actionButton}
          />
        </View>

        {/* Error & Conversion Tracking */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Error & Conversion Tracking</Text>
          
          <AnalyticsButton
            title="Track Error"
            eventName="demo_error"
            screenName="analytics_demo"
            onPress={trackError}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track Conversion"
            eventName="demo_conversion"
            screenName="analytics_demo"
            onPress={trackConversion}
            style={styles.actionButton}
          />
        </View>

        {/* Funnel Analysis */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Funnel Analysis</Text>
          
          <AnalyticsButton
            title="Start Funnel"
            eventName="demo_funnel_start"
            screenName="analytics_demo"
            onPress={startFunnel}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Complete Funnel Step"
            eventName="demo_funnel_step"
            screenName="analytics_demo"
            onPress={completeFunnelStep}
            style={styles.actionButton}
          />
        </View>

        {/* User Properties */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>User Properties</Text>
          
          <AnalyticsButton
            title="Set User Properties"
            eventName="demo_user_properties"
            screenName="analytics_demo"
            onPress={setUserProperties}
            style={styles.actionButton}
          />
        </View>

        {/* System Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Actions</Text>
          
          <AnalyticsButton
            title="Flush Events"
            eventName="demo_flush"
            screenName="analytics_demo"
            onPress={flushEvents}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Reset Analytics"
            eventName="demo_reset"
            screenName="analytics_demo"
            onPress={resetAnalytics}
            style={[styles.actionButton, styles.dangerButton]}
          />
        </View>

        {/* Performance Monitor */}
        <PerformanceMonitor
          screenName="analytics_demo"
          showMetrics={true}
          trackRenderTime={true}
          trackMemoryUsage={true}
          trackNetworkRequests={true}
          trackUserInteractions={true}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  scrollView: {
    flex: 1
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  statusLabel: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  },
  statusValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '600'
  },
  actionButton: {
    marginBottom: 12,
    paddingVertical: 14,
    borderRadius: 10
  },
  dangerButton: {
    backgroundColor: '#EF4444'
  }
});
 * @fileoverview Comprehensive analytics system demo
 * @author Blaze AI Team
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  Alert
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useAnalyticsContext } from '../analytics/analytics-provider';
import { AnalyticsButton } from '../analytics/analytics-button';
import { PerformanceMonitor } from '../analytics/performance-monitor';
import { 
  UserActionEvent, 
  PerformanceEvent, 
  ErrorEvent, 
  ConversionEvent 
} from '../../lib/analytics/analytics-types';

/**
 * Comprehensive demo of the analytics system
 */
export function AnalyticsDemo(): React.JSX.Element {
  const analytics = useAnalyticsContext();
  const [eventCount, setEventCount] = useState(0);
  const [funnelStep, setFunnelStep] = useState(1);

  /**
   * Tracks a custom event
   */
  const trackCustomEvent = async (): Promise<void> => {
    try {
      await analytics.trackEvent('custom_demo_event', {
        eventCount: eventCount + 1,
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setEventCount(prev => prev + 1);
      Alert.alert('Event Tracked', 'Custom event has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track custom event');
    }
  };

  /**
   * Tracks a user action
   */
  const trackUserAction = async (): Promise<void> => {
    try {
      const userAction: UserActionEvent = {
        actionType: 'tap',
        elementType: 'button',
        elementId: 'demo_action_button',
        elementText: 'Track User Action',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackUserAction(userAction);
      Alert.alert('Action Tracked', 'User action has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track user action');
    }
  };

  /**
   * Tracks a performance metric
   */
  const trackPerformanceMetric = async (): Promise<void> => {
    try {
      const performanceEvent: PerformanceEvent = {
        metricName: 'demo_metric',
        value: Math.random() * 1000,
        unit: 'ms',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackPerformance(performanceEvent);
      Alert.alert('Metric Tracked', 'Performance metric has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track performance metric');
    }
  };

  /**
   * Tracks an error
   */
  const trackError = async (): Promise<void> => {
    try {
      const errorEvent: ErrorEvent = {
        errorType: 'javascript',
        errorMessage: 'Demo error for testing purposes',
        errorCode: 'DEMO_ERROR_001',
        screenName: 'analytics_demo',
        properties: {
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackError(errorEvent);
      Alert.alert('Error Tracked', 'Error has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track error');
    }
  };

  /**
   * Tracks a conversion event
   */
  const trackConversion = async (): Promise<void> => {
    try {
      const conversionEvent: ConversionEvent = {
        conversionType: 'feature_usage',
        value: 99.99,
        currency: 'USD',
        properties: {
          feature: 'analytics_demo',
          timestamp: Date.now(),
          source: 'analytics_demo'
        }
      };

      await analytics.trackConversion(conversionEvent);
      Alert.alert('Conversion Tracked', 'Conversion event has been tracked successfully');
    } catch (error) {
      Alert.alert('Error', 'Failed to track conversion');
    }
  };

  /**
   * Starts a funnel analysis
   */
  const startFunnel = async (): Promise<void> => {
    try {
      await analytics.startFunnel('demo_funnel', 'step_1', {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setFunnelStep(1);
      Alert.alert('Funnel Started', 'Demo funnel has been started');
    } catch (error) {
      Alert.alert('Error', 'Failed to start funnel');
    }
  };

  /**
   * Completes a funnel step
   */
  const completeFunnelStep = async (): Promise<void> => {
    try {
      const stepName = `step_${funnelStep + 1}`;
      await analytics.completeFunnel('demo_funnel', stepName, {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
      
      setFunnelStep(prev => prev + 1);
      Alert.alert('Funnel Step', `Completed ${stepName}`);
    } catch (error) {
      Alert.alert('Error', 'Failed to complete funnel step');
    }
  };

  /**
   * Sets user properties
   */
  const setUserProperties = async (): Promise<void> => {
    try {
      await analytics.setUserProperties({
        userId: 'demo_user_123',
        email: 'demo@example.com',
        name: 'Demo User',
        subscriptionTier: 'premium',
        registrationDate: Date.now(),
        lastActiveDate: Date.now(),
        totalSessions: 1,
        totalEvents: eventCount
      });
      
      Alert.alert('User Properties Set', 'User properties have been updated');
    } catch (error) {
      Alert.alert('Error', 'Failed to set user properties');
    }
  };

  /**
   * Flushes analytics events
   */
  const flushEvents = async (): Promise<void> => {
    try {
      await analytics.flush();
      Alert.alert('Events Flushed', 'Analytics events have been flushed');
    } catch (error) {
      Alert.alert('Error', 'Failed to flush events');
    }
  };

  /**
   * Resets analytics data
   */
  const resetAnalytics = async (): Promise<void> => {
    try {
      await analytics.reset();
      setEventCount(0);
      setFunnelStep(1);
      Alert.alert('Analytics Reset', 'Analytics data has been reset');
    } catch (error) {
      Alert.alert('Error', 'Failed to reset analytics');
    }
  };

  // Track screen view on mount
  useEffect(() => {
    if (analytics.isInitialized) {
      analytics.trackScreenView('analytics_demo', {
        timestamp: Date.now(),
        source: 'analytics_demo'
      });
    }
  }, [analytics]);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
        <View style={styles.header}>
          <Text style={styles.title}>Analytics System Demo</Text>
          <Text style={styles.subtitle}>
            Comprehensive user behavior tracking and analytics
          </Text>
        </View>

        {/* Status Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Status</Text>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Initialized:</Text>
            <Text style={[styles.statusValue, { 
              color: analytics.isInitialized ? '#10B981' : '#EF4444' 
            }]}>
              {analytics.isInitialized ? 'Yes' : 'No'}
            </Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Events Tracked:</Text>
            <Text style={styles.statusValue}>{eventCount}</Text>
          </View>
          
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>Funnel Step:</Text>
            <Text style={styles.statusValue}>{funnelStep}</Text>
          </View>
        </View>

        {/* Event Tracking */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Event Tracking</Text>
          
          <AnalyticsButton
            title="Track Custom Event"
            eventName="demo_custom_event"
            eventProperties={{ source: 'analytics_demo' }}
            screenName="analytics_demo"
            onPress={trackCustomEvent}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track User Action"
            eventName="demo_user_action"
            screenName="analytics_demo"
            onPress={trackUserAction}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track Performance Metric"
            eventName="demo_performance"
            screenName="analytics_demo"
            onPress={trackPerformanceMetric}
            style={styles.actionButton}
          />
        </View>

        {/* Error & Conversion Tracking */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Error & Conversion Tracking</Text>
          
          <AnalyticsButton
            title="Track Error"
            eventName="demo_error"
            screenName="analytics_demo"
            onPress={trackError}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Track Conversion"
            eventName="demo_conversion"
            screenName="analytics_demo"
            onPress={trackConversion}
            style={styles.actionButton}
          />
        </View>

        {/* Funnel Analysis */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Funnel Analysis</Text>
          
          <AnalyticsButton
            title="Start Funnel"
            eventName="demo_funnel_start"
            screenName="analytics_demo"
            onPress={startFunnel}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Complete Funnel Step"
            eventName="demo_funnel_step"
            screenName="analytics_demo"
            onPress={completeFunnelStep}
            style={styles.actionButton}
          />
        </View>

        {/* User Properties */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>User Properties</Text>
          
          <AnalyticsButton
            title="Set User Properties"
            eventName="demo_user_properties"
            screenName="analytics_demo"
            onPress={setUserProperties}
            style={styles.actionButton}
          />
        </View>

        {/* System Actions */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>System Actions</Text>
          
          <AnalyticsButton
            title="Flush Events"
            eventName="demo_flush"
            screenName="analytics_demo"
            onPress={flushEvents}
            style={styles.actionButton}
          />
          
          <AnalyticsButton
            title="Reset Analytics"
            eventName="demo_reset"
            screenName="analytics_demo"
            onPress={resetAnalytics}
            style={[styles.actionButton, styles.dangerButton]}
          />
        </View>

        {/* Performance Monitor */}
        <PerformanceMonitor
          screenName="analytics_demo"
          showMetrics={true}
          trackRenderTime={true}
          trackMemoryUsage={true}
          trackNetworkRequests={true}
          trackUserInteractions={true}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF'
  },
  scrollView: {
    flex: 1
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 24,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB'
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    lineHeight: 24
  },
  section: {
    paddingHorizontal: 20,
    paddingVertical: 16
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16
  },
  statusItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  statusLabel: {
    fontSize: 16,
    color: '#374151',
    fontWeight: '500'
  },
  statusValue: {
    fontSize: 16,
    color: '#1F2937',
    fontWeight: '600'
  },
  actionButton: {
    marginBottom: 12,
    paddingVertical: 14,
    borderRadius: 10
  },
  dangerButton: {
    backgroundColor: '#EF4444'
  }
});


