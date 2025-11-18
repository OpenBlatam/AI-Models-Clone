/**
 * @fileoverview React hook for analytics functionality
 * @author Blaze AI Team
 */

import { useEffect, useCallback, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { AnalyticsManagerImpl } from '../../lib/analytics/analytics-manager';
import { 
  UserProperties, 
  SessionProperties, 
  UserActionEvent,
  PerformanceEvent,
  ErrorEvent,
  ConversionEvent,
  AnalyticsConfig
} from '../../lib/analytics/analytics-types';

interface UseAnalyticsReturn {
  readonly isInitialized: boolean;
  readonly trackEvent: (eventName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackScreenView: (screenName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackUserAction: (action: UserActionEvent) => Promise<void>;
  readonly trackPerformance: (metric: PerformanceEvent) => Promise<void>;
  readonly trackError: (error: ErrorEvent) => Promise<void>;
  readonly trackConversion: (conversion: ConversionEvent) => Promise<void>;
  readonly startFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly completeFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly setUserProperties: (properties: Partial<UserProperties>) => Promise<void>;
  readonly setSessionProperties: (properties: Partial<SessionProperties>) => Promise<void>;
  readonly flush: () => Promise<void>;
  readonly reset: () => Promise<void>;
}

/**
 * Custom hook for analytics functionality
 */
export function useAnalytics(config?: Partial<AnalyticsConfig>): UseAnalyticsReturn {
  const analyticsManagerRef = useRef<AnalyticsManagerImpl | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  /**
   * Initializes the analytics manager
   */
  const initializeAnalytics = useCallback(async (): Promise<void> => {
    try {
      const manager = new AnalyticsManagerImpl(config);
      await manager.initialize();
      analyticsManagerRef.current = manager;
    } catch (error) {
      console.error('Failed to initialize analytics:', error);
    }
  }, [config]);

  /**
   * Handles app state changes
   */
  const handleAppStateChange = useCallback((nextAppState: AppStateStatus): void => {
    if (appStateRef.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to the foreground
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.trackEvent('app_foreground', {
          timestamp: Date.now()
        });
      }
    } else if (appStateRef.current === 'active' && nextAppState.match(/inactive|background/)) {
      // App has gone to the background
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.trackEvent('app_background', {
          timestamp: Date.now()
        });
        analyticsManagerRef.current.flush();
      }
    }
    appStateRef.current = nextAppState;
  }, []);

  /**
   * Tracks a custom event
   */
  const trackEvent = useCallback(async (
    eventName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackEvent(eventName, properties);
  }, []);

  /**
   * Tracks a screen view
   */
  const trackScreenView = useCallback(async (
    screenName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackScreenView(screenName, properties);
  }, []);

  /**
   * Tracks a user action
   */
  const trackUserAction = useCallback(async (action: UserActionEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackUserAction(action);
  }, []);

  /**
   * Tracks a performance metric
   */
  const trackPerformance = useCallback(async (metric: PerformanceEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackPerformance(metric);
  }, []);

  /**
   * Tracks an error
   */
  const trackError = useCallback(async (error: ErrorEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackError(error);
  }, []);

  /**
   * Tracks a conversion event
   */
  const trackConversion = useCallback(async (conversion: ConversionEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackConversion(conversion);
  }, []);

  /**
   * Starts a funnel analysis
   */
  const startFunnel = useCallback(async (
    funnelName: string, 
    stepName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.startFunnel(funnelName, stepName, properties);
  }, []);

  /**
   * Completes a funnel step
   */
  const completeFunnel = useCallback(async (
    funnelName: string, 
    stepName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.completeFunnel(funnelName, stepName, properties);
  }, []);

  /**
   * Sets user properties
   */
  const setUserProperties = useCallback(async (properties: Partial<UserProperties>): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.setUserProperties(properties);
  }, []);

  /**
   * Sets session properties
   */
  const setSessionProperties = useCallback(async (properties: Partial<SessionProperties>): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.setSessionProperties(properties);
  }, []);

  /**
   * Flushes queued events
   */
  const flush = useCallback(async (): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.flush();
  }, []);

  /**
   * Resets analytics data
   */
  const reset = useCallback(async (): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.reset();
  }, []);

  // Initialize analytics on mount
  useEffect(() => {
    initializeAnalytics();
  }, [initializeAnalytics]);

  // Set up app state listener
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [handleAppStateChange]);

  // Flush events on unmount
  useEffect(() => {
    return () => {
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.flush();
      }
    };
  }, []);

  return {
    isInitialized: analyticsManagerRef.current !== null,
    trackEvent,
    trackScreenView,
    trackUserAction,
    trackPerformance,
    trackError,
    trackConversion,
    startFunnel,
    completeFunnel,
    setUserProperties,
    setSessionProperties,
    flush,
    reset
  };
}
 * @fileoverview React hook for analytics functionality
 * @author Blaze AI Team
 */

import { useEffect, useCallback, useRef } from 'react';
import { AppState, AppStateStatus } from 'react-native';
import { AnalyticsManagerImpl } from '../../lib/analytics/analytics-manager';
import { 
  UserProperties, 
  SessionProperties, 
  UserActionEvent,
  PerformanceEvent,
  ErrorEvent,
  ConversionEvent,
  AnalyticsConfig
} from '../../lib/analytics/analytics-types';

interface UseAnalyticsReturn {
  readonly isInitialized: boolean;
  readonly trackEvent: (eventName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackScreenView: (screenName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackUserAction: (action: UserActionEvent) => Promise<void>;
  readonly trackPerformance: (metric: PerformanceEvent) => Promise<void>;
  readonly trackError: (error: ErrorEvent) => Promise<void>;
  readonly trackConversion: (conversion: ConversionEvent) => Promise<void>;
  readonly startFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly completeFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly setUserProperties: (properties: Partial<UserProperties>) => Promise<void>;
  readonly setSessionProperties: (properties: Partial<SessionProperties>) => Promise<void>;
  readonly flush: () => Promise<void>;
  readonly reset: () => Promise<void>;
}

/**
 * Custom hook for analytics functionality
 */
export function useAnalytics(config?: Partial<AnalyticsConfig>): UseAnalyticsReturn {
  const analyticsManagerRef = useRef<AnalyticsManagerImpl | null>(null);
  const appStateRef = useRef<AppStateStatus>(AppState.currentState);

  /**
   * Initializes the analytics manager
   */
  const initializeAnalytics = useCallback(async (): Promise<void> => {
    try {
      const manager = new AnalyticsManagerImpl(config);
      await manager.initialize();
      analyticsManagerRef.current = manager;
    } catch (error) {
      console.error('Failed to initialize analytics:', error);
    }
  }, [config]);

  /**
   * Handles app state changes
   */
  const handleAppStateChange = useCallback((nextAppState: AppStateStatus): void => {
    if (appStateRef.current.match(/inactive|background/) && nextAppState === 'active') {
      // App has come to the foreground
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.trackEvent('app_foreground', {
          timestamp: Date.now()
        });
      }
    } else if (appStateRef.current === 'active' && nextAppState.match(/inactive|background/)) {
      // App has gone to the background
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.trackEvent('app_background', {
          timestamp: Date.now()
        });
        analyticsManagerRef.current.flush();
      }
    }
    appStateRef.current = nextAppState;
  }, []);

  /**
   * Tracks a custom event
   */
  const trackEvent = useCallback(async (
    eventName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackEvent(eventName, properties);
  }, []);

  /**
   * Tracks a screen view
   */
  const trackScreenView = useCallback(async (
    screenName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackScreenView(screenName, properties);
  }, []);

  /**
   * Tracks a user action
   */
  const trackUserAction = useCallback(async (action: UserActionEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackUserAction(action);
  }, []);

  /**
   * Tracks a performance metric
   */
  const trackPerformance = useCallback(async (metric: PerformanceEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackPerformance(metric);
  }, []);

  /**
   * Tracks an error
   */
  const trackError = useCallback(async (error: ErrorEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackError(error);
  }, []);

  /**
   * Tracks a conversion event
   */
  const trackConversion = useCallback(async (conversion: ConversionEvent): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.trackConversion(conversion);
  }, []);

  /**
   * Starts a funnel analysis
   */
  const startFunnel = useCallback(async (
    funnelName: string, 
    stepName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.startFunnel(funnelName, stepName, properties);
  }, []);

  /**
   * Completes a funnel step
   */
  const completeFunnel = useCallback(async (
    funnelName: string, 
    stepName: string, 
    properties?: Record<string, any>
  ): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.completeFunnel(funnelName, stepName, properties);
  }, []);

  /**
   * Sets user properties
   */
  const setUserProperties = useCallback(async (properties: Partial<UserProperties>): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.setUserProperties(properties);
  }, []);

  /**
   * Sets session properties
   */
  const setSessionProperties = useCallback(async (properties: Partial<SessionProperties>): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.setSessionProperties(properties);
  }, []);

  /**
   * Flushes queued events
   */
  const flush = useCallback(async (): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.flush();
  }, []);

  /**
   * Resets analytics data
   */
  const reset = useCallback(async (): Promise<void> => {
    if (!analyticsManagerRef.current) {
      console.warn('Analytics manager not initialized');
      return;
    }
    
    await analyticsManagerRef.current.reset();
  }, []);

  // Initialize analytics on mount
  useEffect(() => {
    initializeAnalytics();
  }, [initializeAnalytics]);

  // Set up app state listener
  useEffect(() => {
    const subscription = AppState.addEventListener('change', handleAppStateChange);
    return () => subscription?.remove();
  }, [handleAppStateChange]);

  // Flush events on unmount
  useEffect(() => {
    return () => {
      if (analyticsManagerRef.current) {
        analyticsManagerRef.current.flush();
      }
    };
  }, []);

  return {
    isInitialized: analyticsManagerRef.current !== null,
    trackEvent,
    trackScreenView,
    trackUserAction,
    trackPerformance,
    trackError,
    trackConversion,
    startFunnel,
    completeFunnel,
    setUserProperties,
    setSessionProperties,
    flush,
    reset
  };
}


