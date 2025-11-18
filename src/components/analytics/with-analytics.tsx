/**
 * @fileoverview Higher-order component for automatic screen tracking
 * @author Blaze AI Team
 */

import React, { useEffect, ComponentType } from 'react';
import { useAnalyticsContext } from './analytics-provider';

interface WithAnalyticsOptions {
  readonly screenName?: string;
  readonly trackScreenView?: boolean;
  readonly trackUserActions?: boolean;
  readonly trackPerformance?: boolean;
  readonly trackErrors?: boolean;
}

/**
 * Higher-order component that automatically tracks screen views and user interactions
 */
export function withAnalytics<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: WithAnalyticsOptions = {}
) {
  const {
    screenName,
    trackScreenView = true,
    trackUserActions = true,
    trackPerformance = true,
    trackErrors = true
  } = options;

  const WithAnalyticsComponent = (props: P): React.JSX.Element => {
    const analytics = useAnalyticsContext();
    const componentName = screenName || WrappedComponent.displayName || WrappedComponent.name || 'Unknown';

    /**
     * Tracks screen view when component mounts
     */
    useEffect(() => {
      if (trackScreenView && analytics.isInitialized) {
        analytics.trackScreenView(componentName, {
          componentType: 'screen',
          timestamp: Date.now()
        });
      }
    }, [analytics, componentName, trackScreenView]);

    /**
     * Sets up error boundary for automatic error tracking
     */
    useEffect(() => {
      if (trackErrors && analytics.isInitialized) {
        const originalError = console.error;
        
        console.error = (...args) => {
          originalError(...args);
          
          analytics.trackError({
            errorType: 'javascript',
            errorMessage: args.join(' '),
            screenName: componentName,
            timestamp: Date.now()
          });
        };

        return () => {
          console.error = originalError;
        };
      }
    }, [analytics, componentName, trackErrors]);

    /**
     * Tracks performance metrics
     */
    useEffect(() => {
      if (trackPerformance && analytics.isInitialized) {
        const startTime = Date.now();
        
        return () => {
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          analytics.trackPerformance({
            metricName: 'screen_load_time',
            value: duration,
            unit: 'ms',
            screenName: componentName,
            timestamp: Date.now()
          });
        };
      }
    }, [analytics, componentName, trackPerformance]);

    return <WrappedComponent {...props} />;
  };

  WithAnalyticsComponent.displayName = `withAnalytics(${componentName})`;

  return WithAnalyticsComponent;
}
 * @fileoverview Higher-order component for automatic screen tracking
 * @author Blaze AI Team
 */

import React, { useEffect, ComponentType } from 'react';
import { useAnalyticsContext } from './analytics-provider';

interface WithAnalyticsOptions {
  readonly screenName?: string;
  readonly trackScreenView?: boolean;
  readonly trackUserActions?: boolean;
  readonly trackPerformance?: boolean;
  readonly trackErrors?: boolean;
}

/**
 * Higher-order component that automatically tracks screen views and user interactions
 */
export function withAnalytics<P extends object>(
  WrappedComponent: ComponentType<P>,
  options: WithAnalyticsOptions = {}
) {
  const {
    screenName,
    trackScreenView = true,
    trackUserActions = true,
    trackPerformance = true,
    trackErrors = true
  } = options;

  const WithAnalyticsComponent = (props: P): React.JSX.Element => {
    const analytics = useAnalyticsContext();
    const componentName = screenName || WrappedComponent.displayName || WrappedComponent.name || 'Unknown';

    /**
     * Tracks screen view when component mounts
     */
    useEffect(() => {
      if (trackScreenView && analytics.isInitialized) {
        analytics.trackScreenView(componentName, {
          componentType: 'screen',
          timestamp: Date.now()
        });
      }
    }, [analytics, componentName, trackScreenView]);

    /**
     * Sets up error boundary for automatic error tracking
     */
    useEffect(() => {
      if (trackErrors && analytics.isInitialized) {
        const originalError = console.error;
        
        console.error = (...args) => {
          originalError(...args);
          
          analytics.trackError({
            errorType: 'javascript',
            errorMessage: args.join(' '),
            screenName: componentName,
            timestamp: Date.now()
          });
        };

        return () => {
          console.error = originalError;
        };
      }
    }, [analytics, componentName, trackErrors]);

    /**
     * Tracks performance metrics
     */
    useEffect(() => {
      if (trackPerformance && analytics.isInitialized) {
        const startTime = Date.now();
        
        return () => {
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          analytics.trackPerformance({
            metricName: 'screen_load_time',
            value: duration,
            unit: 'ms',
            screenName: componentName,
            timestamp: Date.now()
          });
        };
      }
    }, [analytics, componentName, trackPerformance]);

    return <WrappedComponent {...props} />;
  };

  WithAnalyticsComponent.displayName = `withAnalytics(${componentName})`;

  return WithAnalyticsComponent;
}


