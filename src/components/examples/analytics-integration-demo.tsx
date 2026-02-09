/**
 * @fileoverview Comprehensive analytics integration demo component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, Switch, Alert, TextInput } from 'react-native';
import { useAnalytics } from '../../hooks/analytics/use-analytics';
import { AnalyticsButton } from '../analytics/analytics-button';
import { withAnalytics } from '../analytics/with-analytics';
import { PerformanceMonitor } from '../analytics/performance-monitor';
import { AccessibleButton } from '../accessibility/accessible-button';
import { secureStorage } from '../../lib/security/secure-storage';
import { 
  AnalyticsEvent, 
  ScreenView, 
  UserProperties, 
  PerformanceMetric,
  AnalyticsConsent 
} from '../../lib/analytics/analytics-types';

/**
 * AnalyticsIntegrationDemo component demonstrates comprehensive analytics features
 */
function AnalyticsIntegrationDemo(): JSX.Element {
  const { 
    trackEvent, 
    trackScreenView, 
    setUserProperties, 
    setConsent, 
    getConsent,
    trackPerformanceMetric 
  } = useAnalytics();
  
  const [consent, setLocalConsent] = useState<AnalyticsConsent>({
    marketing: false,
    performance: false,
    functional: true,
  });
  const [showPerformanceOverlay, setShowPerformanceOverlay] = useState<boolean>(false);
  const [customEventName, setCustomEventName] = useState<string>('');
  const [customEventProperties, setCustomEventProperties] = useState<string>('');
  const [userId, setUserId] = useState<string>('user-123');
  const [userTier, setUserTier] = useState<string>('premium');

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * Loads initial consent and user properties
   */
  const loadInitialData = async (): Promise<void> => {
    try {
      const currentConsent = getConsent();
      setLocalConsent(currentConsent);

      // Set initial user properties
      await setUserProperties({ 
        userId: 'user-123', 
        userTier: 'premium', 
        appLanguage: 'en' 
      });

      // Track initial screen view
      trackScreenView({ 
        screenName: 'AnalyticsIntegrationDemo', 
        properties: { entryPoint: 'demo', timestamp: Date.now() } 
      });
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  /**
   * Handles consent toggle for different categories
   */
  const handleConsentToggle = async (category: keyof AnalyticsConsent, value: boolean): Promise<void> => {
    try {
      const newConsent = { ...consent, [category]: value };
      setLocalConsent(newConsent);
      await setConsent(newConsent);
      await secureStorage.saveData('analytics-consent', newConsent);
      
      // Track consent change
      trackEvent({
        name: 'consent-updated',
        properties: { category, value, previousValue: consent[category] }
      });
    } catch (error) {
      console.error('Failed to update consent:', error);
      Alert.alert('Error', 'Failed to update consent settings');
    }
  };

  /**
   * Tracks a custom event with user input
   */
  const trackCustomEvent = (): void => {
    if (!customEventName.trim()) {
      Alert.alert('Error', 'Please enter an event name');
      return;
    }

    try {
      let properties: Record<string, unknown> = {};
      if (customEventProperties.trim()) {
        try {
          properties = JSON.parse(customEventProperties);
        } catch {
          Alert.alert('Error', 'Invalid JSON properties');
          return;
        }
      }

      trackEvent({
        name: customEventName.trim(),
        properties: { ...properties, source: 'manual-input' }
      });

      Alert.alert('Success', `Event "${customEventName}" tracked successfully`);
      setCustomEventName('');
      setCustomEventProperties('');
    } catch (error) {
      console.error('Failed to track custom event:', error);
      Alert.alert('Error', 'Failed to track event');
    }
  };

  /**
   * Updates user properties
   */
  const updateUserProperties = async (): Promise<void> => {
    try {
      await setUserProperties({ 
        userId, 
        userTier, 
        lastActivity: new Date().toISOString(),
        appLanguage: 'en'
      });

      trackEvent({
        name: 'user-properties-updated',
        properties: { userId, userTier, timestamp: Date.now() }
      });

      Alert.alert('Success', 'User properties updated successfully');
    } catch (error) {
      console.error('Failed to update user properties:', error);
      Alert.alert('Error', 'Failed to update user properties');
    }
  };

  /**
   * Tracks a performance metric
   */
  const trackCustomPerformanceMetric = (): void => {
    try {
      const metric: PerformanceMetric = {
        name: 'custom-user-interaction',
        value: Math.random() * 1000,
        unit: 'ms',
        properties: { source: 'demo', userId, userTier }
      };

      trackPerformanceMetric(metric);
      Alert.alert('Success', 'Performance metric tracked successfully');
    } catch (error) {
      console.error('Failed to track performance metric:', error);
      Alert.alert('Error', 'Failed to track performance metric');
    }
  };

  /**
   * Simulates a funnel step
   */
  const simulateFunnelStep = (stepName: string, stepOrder: number): void => {
    trackEvent({
      name: 'funnel-step-completed',
      properties: { 
        funnelName: 'demo-funnel', 
        stepName, 
        stepOrder, 
        userId,
        timestamp: Date.now() 
      }
    });

    Alert.alert('Success', `Funnel step "${stepName}" completed`);
  };

  /**
   * Simulates a conversion event
   */
  const simulateConversion = (conversionType: string, value?: number): void => {
    trackEvent({
      name: 'conversion-completed',
      properties: { 
        conversionType, 
        value, 
        userId, 
        userTier,
        timestamp: Date.now() 
      }
    });

    Alert.alert('Success', `Conversion "${conversionType}" tracked successfully`);
  };

  return (
    <PerformanceMonitor showOverlay={showPerformanceOverlay}>
      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
        <Text style={styles.title}>Analytics Integration Demo</Text>
        <Text style={styles.subtitle}>Comprehensive analytics system demonstration</Text>

        <Text style={styles.sectionTitle}>Event Tracking</Text>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder="Event Name (e.g., button-clicked)"
            value={customEventName}
            onChangeText={setCustomEventName}
            accessibilityLabel="Custom Event Name Input"
          />
          <TextInput
            style={styles.textInput}
            placeholder="Properties (JSON format, optional)"
            value={customEventProperties}
            onChangeText={setCustomEventProperties}
            multiline
            accessibilityLabel="Custom Event Properties Input"
          />
          <AccessibleButton
            accessibilityLabel="Track Custom Event Button"
            style={styles.button}
            onPress={trackCustomEvent}
          >
            <Text style={styles.buttonText}>Track Custom Event</Text>
          </AccessibleButton>
        </View>

        <AnalyticsButton
          eventName="demo-button-clicked"
          eventProperties={{ buttonId: 'demo-button', location: 'event-section' }}
          accessibilityLabel="Track Demo Event Button"
          style={styles.button}
          onPress={() => console.log('Demo event button pressed!')}
        >
          <Text style={styles.buttonText}>Track Demo Event</Text>
        </AnalyticsButton>

        <Text style={styles.sectionTitle}>User Properties Management</Text>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder="User ID"
            value={userId}
            onChangeText={setUserId}
            accessibilityLabel="User ID Input"
          />
          <TextInput
            style={styles.textInput}
            placeholder="User Tier"
            value={userTier}
            onChangeText={setUserTier}
            accessibilityLabel="User Tier Input"
          />
          <AccessibleButton
            accessibilityLabel="Update User Properties Button"
            style={styles.button}
            onPress={updateUserProperties}
          >
            <Text style={styles.buttonText}>Update User Properties</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.sectionTitle}>Consent Management</Text>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Marketing Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('marketing', value)}
            value={consent.marketing}
            accessibilityLabel="Toggle Marketing Analytics Consent"
          />
        </View>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Performance Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('performance', value)}
            value={consent.performance}
            accessibilityLabel="Toggle Performance Analytics Consent"
          />
        </View>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Functional Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('functional', value)}
            value={consent.functional}
            disabled={true}
            accessibilityLabel="Functional Analytics Consent (cannot be disabled)"
          />
        </View>

        <Text style={styles.sectionTitle}>Performance Monitoring</Text>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Show Performance Overlay</Text>
          <Switch
            onValueChange={setShowPerformanceOverlay}
            value={showPerformanceOverlay}
            accessibilityLabel="Toggle Performance Overlay"
          />
        </View>
        <AccessibleButton
          accessibilityLabel="Track Performance Metric Button"
          style={styles.button}
          onPress={trackCustomPerformanceMetric}
        >
          <Text style={styles.buttonText}>Track Performance Metric</Text>
        </AccessibleButton>

        <Text style={styles.sectionTitle}>Funnel Analysis</Text>
        <View style={styles.buttonRow}>
          <AccessibleButton
            accessibilityLabel="Step 1 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-1', 1)}
          >
            <Text style={styles.buttonText}>Step 1</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Step 2 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-2', 2)}
          >
            <Text style={styles.buttonText}>Step 2</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Step 3 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-3', 3)}
          >
            <Text style={styles.buttonText}>Step 3</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.sectionTitle}>Conversion Tracking</Text>
        <View style={styles.buttonRow}>
          <AccessibleButton
            accessibilityLabel="Track Purchase Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('purchase', 99.99)}
          >
            <Text style={styles.buttonText}>Purchase</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Track Signup Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('signup')}
          >
            <Text style={styles.buttonText}>Signup</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Track Trial Start Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('trial_start')}
          >
            <Text style={styles.buttonText}>Trial Start</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.currentConsentText}>
          Current Consent: {JSON.stringify(consent, null, 2)}
        </Text>

        <Text style={styles.footerText}>
          Check console logs for analytics events and backend integration details.
        </Text>
      </ScrollView>
    </PerformanceMonitor>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  contentContainer: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '600',
    marginTop: 25,
    marginBottom: 15,
    color: '#555',
    alignSelf: 'flex-start',
    width: '100%',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  textInput: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    fontSize: 16,
    width: '100%',
  },
  button: {
    backgroundColor: '#007bff',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
    marginBottom: 15,
    width: '80%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  smallButton: {
    width: '30%',
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
  consentRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '80%',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  consentLabel: {
    fontSize: 16,
    color: '#333',
  },
  currentConsentText: {
    marginTop: 20,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    width: '90%',
    lineHeight: 20,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
  },
  footerText: {
    marginTop: 40,
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
  },
});

// Export the component wrapped with withAnalytics HOC for automatic screen tracking
export default withAnalytics(AnalyticsIntegrationDemo);
 * @fileoverview Comprehensive analytics integration demo component
 * @author Blaze AI Team
 */

import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, ScrollView, Switch, Alert, TextInput } from 'react-native';
import { useAnalytics } from '../../hooks/analytics/use-analytics';
import { AnalyticsButton } from '../analytics/analytics-button';
import { withAnalytics } from '../analytics/with-analytics';
import { PerformanceMonitor } from '../analytics/performance-monitor';
import { AccessibleButton } from '../accessibility/accessible-button';
import { secureStorage } from '../../lib/security/secure-storage';
import { 
  AnalyticsEvent, 
  ScreenView, 
  UserProperties, 
  PerformanceMetric,
  AnalyticsConsent 
} from '../../lib/analytics/analytics-types';

/**
 * AnalyticsIntegrationDemo component demonstrates comprehensive analytics features
 */
function AnalyticsIntegrationDemo(): JSX.Element {
  const { 
    trackEvent, 
    trackScreenView, 
    setUserProperties, 
    setConsent, 
    getConsent,
    trackPerformanceMetric 
  } = useAnalytics();
  
  const [consent, setLocalConsent] = useState<AnalyticsConsent>({
    marketing: false,
    performance: false,
    functional: true,
  });
  const [showPerformanceOverlay, setShowPerformanceOverlay] = useState<boolean>(false);
  const [customEventName, setCustomEventName] = useState<string>('');
  const [customEventProperties, setCustomEventProperties] = useState<string>('');
  const [userId, setUserId] = useState<string>('user-123');
  const [userTier, setUserTier] = useState<string>('premium');

  useEffect(() => {
    loadInitialData();
  }, []);

  /**
   * Loads initial consent and user properties
   */
  const loadInitialData = async (): Promise<void> => {
    try {
      const currentConsent = getConsent();
      setLocalConsent(currentConsent);

      // Set initial user properties
      await setUserProperties({ 
        userId: 'user-123', 
        userTier: 'premium', 
        appLanguage: 'en' 
      });

      // Track initial screen view
      trackScreenView({ 
        screenName: 'AnalyticsIntegrationDemo', 
        properties: { entryPoint: 'demo', timestamp: Date.now() } 
      });
    } catch (error) {
      console.error('Failed to load initial data:', error);
    }
  };

  /**
   * Handles consent toggle for different categories
   */
  const handleConsentToggle = async (category: keyof AnalyticsConsent, value: boolean): Promise<void> => {
    try {
      const newConsent = { ...consent, [category]: value };
      setLocalConsent(newConsent);
      await setConsent(newConsent);
      await secureStorage.saveData('analytics-consent', newConsent);
      
      // Track consent change
      trackEvent({
        name: 'consent-updated',
        properties: { category, value, previousValue: consent[category] }
      });
    } catch (error) {
      console.error('Failed to update consent:', error);
      Alert.alert('Error', 'Failed to update consent settings');
    }
  };

  /**
   * Tracks a custom event with user input
   */
  const trackCustomEvent = (): void => {
    if (!customEventName.trim()) {
      Alert.alert('Error', 'Please enter an event name');
      return;
    }

    try {
      let properties: Record<string, unknown> = {};
      if (customEventProperties.trim()) {
        try {
          properties = JSON.parse(customEventProperties);
        } catch {
          Alert.alert('Error', 'Invalid JSON properties');
          return;
        }
      }

      trackEvent({
        name: customEventName.trim(),
        properties: { ...properties, source: 'manual-input' }
      });

      Alert.alert('Success', `Event "${customEventName}" tracked successfully`);
      setCustomEventName('');
      setCustomEventProperties('');
    } catch (error) {
      console.error('Failed to track custom event:', error);
      Alert.alert('Error', 'Failed to track event');
    }
  };

  /**
   * Updates user properties
   */
  const updateUserProperties = async (): Promise<void> => {
    try {
      await setUserProperties({ 
        userId, 
        userTier, 
        lastActivity: new Date().toISOString(),
        appLanguage: 'en'
      });

      trackEvent({
        name: 'user-properties-updated',
        properties: { userId, userTier, timestamp: Date.now() }
      });

      Alert.alert('Success', 'User properties updated successfully');
    } catch (error) {
      console.error('Failed to update user properties:', error);
      Alert.alert('Error', 'Failed to update user properties');
    }
  };

  /**
   * Tracks a performance metric
   */
  const trackCustomPerformanceMetric = (): void => {
    try {
      const metric: PerformanceMetric = {
        name: 'custom-user-interaction',
        value: Math.random() * 1000,
        unit: 'ms',
        properties: { source: 'demo', userId, userTier }
      };

      trackPerformanceMetric(metric);
      Alert.alert('Success', 'Performance metric tracked successfully');
    } catch (error) {
      console.error('Failed to track performance metric:', error);
      Alert.alert('Error', 'Failed to track performance metric');
    }
  };

  /**
   * Simulates a funnel step
   */
  const simulateFunnelStep = (stepName: string, stepOrder: number): void => {
    trackEvent({
      name: 'funnel-step-completed',
      properties: { 
        funnelName: 'demo-funnel', 
        stepName, 
        stepOrder, 
        userId,
        timestamp: Date.now() 
      }
    });

    Alert.alert('Success', `Funnel step "${stepName}" completed`);
  };

  /**
   * Simulates a conversion event
   */
  const simulateConversion = (conversionType: string, value?: number): void => {
    trackEvent({
      name: 'conversion-completed',
      properties: { 
        conversionType, 
        value, 
        userId, 
        userTier,
        timestamp: Date.now() 
      }
    });

    Alert.alert('Success', `Conversion "${conversionType}" tracked successfully`);
  };

  return (
    <PerformanceMonitor showOverlay={showPerformanceOverlay}>
      <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
        <Text style={styles.title}>Analytics Integration Demo</Text>
        <Text style={styles.subtitle}>Comprehensive analytics system demonstration</Text>

        <Text style={styles.sectionTitle}>Event Tracking</Text>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder="Event Name (e.g., button-clicked)"
            value={customEventName}
            onChangeText={setCustomEventName}
            accessibilityLabel="Custom Event Name Input"
          />
          <TextInput
            style={styles.textInput}
            placeholder="Properties (JSON format, optional)"
            value={customEventProperties}
            onChangeText={setCustomEventProperties}
            multiline
            accessibilityLabel="Custom Event Properties Input"
          />
          <AccessibleButton
            accessibilityLabel="Track Custom Event Button"
            style={styles.button}
            onPress={trackCustomEvent}
          >
            <Text style={styles.buttonText}>Track Custom Event</Text>
          </AccessibleButton>
        </View>

        <AnalyticsButton
          eventName="demo-button-clicked"
          eventProperties={{ buttonId: 'demo-button', location: 'event-section' }}
          accessibilityLabel="Track Demo Event Button"
          style={styles.button}
          onPress={() => console.log('Demo event button pressed!')}
        >
          <Text style={styles.buttonText}>Track Demo Event</Text>
        </AnalyticsButton>

        <Text style={styles.sectionTitle}>User Properties Management</Text>
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.textInput}
            placeholder="User ID"
            value={userId}
            onChangeText={setUserId}
            accessibilityLabel="User ID Input"
          />
          <TextInput
            style={styles.textInput}
            placeholder="User Tier"
            value={userTier}
            onChangeText={setUserTier}
            accessibilityLabel="User Tier Input"
          />
          <AccessibleButton
            accessibilityLabel="Update User Properties Button"
            style={styles.button}
            onPress={updateUserProperties}
          >
            <Text style={styles.buttonText}>Update User Properties</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.sectionTitle}>Consent Management</Text>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Marketing Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('marketing', value)}
            value={consent.marketing}
            accessibilityLabel="Toggle Marketing Analytics Consent"
          />
        </View>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Performance Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('performance', value)}
            value={consent.performance}
            accessibilityLabel="Toggle Performance Analytics Consent"
          />
        </View>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Functional Analytics</Text>
          <Switch
            onValueChange={(value) => handleConsentToggle('functional', value)}
            value={consent.functional}
            disabled={true}
            accessibilityLabel="Functional Analytics Consent (cannot be disabled)"
          />
        </View>

        <Text style={styles.sectionTitle}>Performance Monitoring</Text>
        <View style={styles.consentRow}>
          <Text style={styles.consentLabel}>Show Performance Overlay</Text>
          <Switch
            onValueChange={setShowPerformanceOverlay}
            value={showPerformanceOverlay}
            accessibilityLabel="Toggle Performance Overlay"
          />
        </View>
        <AccessibleButton
          accessibilityLabel="Track Performance Metric Button"
          style={styles.button}
          onPress={trackCustomPerformanceMetric}
        >
          <Text style={styles.buttonText}>Track Performance Metric</Text>
        </AccessibleButton>

        <Text style={styles.sectionTitle}>Funnel Analysis</Text>
        <View style={styles.buttonRow}>
          <AccessibleButton
            accessibilityLabel="Step 1 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-1', 1)}
          >
            <Text style={styles.buttonText}>Step 1</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Step 2 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-2', 2)}
          >
            <Text style={styles.buttonText}>Step 2</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Step 3 Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateFunnelStep('step-3', 3)}
          >
            <Text style={styles.buttonText}>Step 3</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.sectionTitle}>Conversion Tracking</Text>
        <View style={styles.buttonRow}>
          <AccessibleButton
            accessibilityLabel="Track Purchase Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('purchase', 99.99)}
          >
            <Text style={styles.buttonText}>Purchase</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Track Signup Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('signup')}
          >
            <Text style={styles.buttonText}>Signup</Text>
          </AccessibleButton>
          <AccessibleButton
            accessibilityLabel="Track Trial Start Button"
            style={[styles.button, styles.smallButton]}
            onPress={() => simulateConversion('trial_start')}
          >
            <Text style={styles.buttonText}>Trial Start</Text>
          </AccessibleButton>
        </View>

        <Text style={styles.currentConsentText}>
          Current Consent: {JSON.stringify(consent, null, 2)}
        </Text>

        <Text style={styles.footerText}>
          Check console logs for analytics events and backend integration details.
        </Text>
      </ScrollView>
    </PerformanceMonitor>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f0f2f5',
  },
  contentContainer: {
    padding: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    marginBottom: 10,
    color: '#333',
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 30,
    textAlign: 'center',
  },
  sectionTitle: {
    fontSize: 22,
    fontWeight: '600',
    marginTop: 25,
    marginBottom: 15,
    color: '#555',
    alignSelf: 'flex-start',
    width: '100%',
  },
  inputContainer: {
    width: '100%',
    marginBottom: 20,
  },
  textInput: {
    backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    marginBottom: 10,
    fontSize: 16,
    width: '100%',
  },
  button: {
    backgroundColor: '#007bff',
    paddingVertical: 12,
    paddingHorizontal: 25,
    borderRadius: 8,
    marginBottom: 15,
    width: '80%',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 3,
  },
  smallButton: {
    width: '30%',
    marginHorizontal: 5,
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  buttonRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    marginBottom: 20,
  },
  consentRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    width: '80%',
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
    marginBottom: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.1,
    shadowRadius: 2,
    elevation: 2,
  },
  consentLabel: {
    fontSize: 16,
    color: '#333',
  },
  currentConsentText: {
    marginTop: 20,
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    width: '90%',
    lineHeight: 20,
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 8,
  },
  footerText: {
    marginTop: 40,
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
  },
});

// Export the component wrapped with withAnalytics HOC for automatic screen tracking
export default withAnalytics(AnalyticsIntegrationDemo);


