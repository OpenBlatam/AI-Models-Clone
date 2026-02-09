/**
 * @fileoverview Analytics context provider for React components
 * @author Blaze AI Team
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useAnalytics } from '../../hooks/analytics/use-analytics';
import { AnalyticsConfig } from '../../lib/analytics/analytics-types';

interface AnalyticsContextValue {
  readonly trackEvent: (eventName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackScreenView: (screenName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackUserAction: (action: any) => Promise<void>;
  readonly trackPerformance: (metric: any) => Promise<void>;
  readonly trackError: (error: any) => Promise<void>;
  readonly trackConversion: (conversion: any) => Promise<void>;
  readonly startFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly completeFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly setUserProperties: (properties: any) => Promise<void>;
  readonly setSessionProperties: (properties: any) => Promise<void>;
  readonly flush: () => Promise<void>;
  readonly reset: () => Promise<void>;
  readonly isInitialized: boolean;
}

const AnalyticsContext = createContext<AnalyticsContextValue | null>(null);

interface AnalyticsProviderProps {
  readonly children: ReactNode;
  readonly config?: Partial<AnalyticsConfig>;
}

/**
 * Analytics context provider component
 */
export function AnalyticsProvider({ children, config }: AnalyticsProviderProps): React.JSX.Element {
  const analytics = useAnalytics(config);

  const contextValue: AnalyticsContextValue = {
    trackEvent: analytics.trackEvent,
    trackScreenView: analytics.trackScreenView,
    trackUserAction: analytics.trackUserAction,
    trackPerformance: analytics.trackPerformance,
    trackError: analytics.trackError,
    trackConversion: analytics.trackConversion,
    startFunnel: analytics.startFunnel,
    completeFunnel: analytics.completeFunnel,
    setUserProperties: analytics.setUserProperties,
    setSessionProperties: analytics.setSessionProperties,
    flush: analytics.flush,
    reset: analytics.reset,
    isInitialized: analytics.isInitialized
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
}

/**
 * Hook to use analytics context
 */
export function useAnalyticsContext(): AnalyticsContextValue {
  const context = useContext(AnalyticsContext);
  
  if (!context) {
    throw new Error('useAnalyticsContext must be used within an AnalyticsProvider');
  }
  
  return context;
}
 * @fileoverview Analytics context provider for React components
 * @author Blaze AI Team
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useAnalytics } from '../../hooks/analytics/use-analytics';
import { AnalyticsConfig } from '../../lib/analytics/analytics-types';

interface AnalyticsContextValue {
  readonly trackEvent: (eventName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackScreenView: (screenName: string, properties?: Record<string, any>) => Promise<void>;
  readonly trackUserAction: (action: any) => Promise<void>;
  readonly trackPerformance: (metric: any) => Promise<void>;
  readonly trackError: (error: any) => Promise<void>;
  readonly trackConversion: (conversion: any) => Promise<void>;
  readonly startFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly completeFunnel: (funnelName: string, stepName: string, properties?: Record<string, any>) => Promise<void>;
  readonly setUserProperties: (properties: any) => Promise<void>;
  readonly setSessionProperties: (properties: any) => Promise<void>;
  readonly flush: () => Promise<void>;
  readonly reset: () => Promise<void>;
  readonly isInitialized: boolean;
}

const AnalyticsContext = createContext<AnalyticsContextValue | null>(null);

interface AnalyticsProviderProps {
  readonly children: ReactNode;
  readonly config?: Partial<AnalyticsConfig>;
}

/**
 * Analytics context provider component
 */
export function AnalyticsProvider({ children, config }: AnalyticsProviderProps): React.JSX.Element {
  const analytics = useAnalytics(config);

  const contextValue: AnalyticsContextValue = {
    trackEvent: analytics.trackEvent,
    trackScreenView: analytics.trackScreenView,
    trackUserAction: analytics.trackUserAction,
    trackPerformance: analytics.trackPerformance,
    trackError: analytics.trackError,
    trackConversion: analytics.trackConversion,
    startFunnel: analytics.startFunnel,
    completeFunnel: analytics.completeFunnel,
    setUserProperties: analytics.setUserProperties,
    setSessionProperties: analytics.setSessionProperties,
    flush: analytics.flush,
    reset: analytics.reset,
    isInitialized: analytics.isInitialized
  };

  return (
    <AnalyticsContext.Provider value={contextValue}>
      {children}
    </AnalyticsContext.Provider>
  );
}

/**
 * Hook to use analytics context
 */
export function useAnalyticsContext(): AnalyticsContextValue {
  const context = useContext(AnalyticsContext);
  
  if (!context) {
    throw new Error('useAnalyticsContext must be used within an AnalyticsProvider');
  }
  
  return context;
}


