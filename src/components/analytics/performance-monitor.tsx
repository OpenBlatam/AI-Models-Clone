/**
 * @fileoverview Performance monitoring component
 * @author Blaze AI Team
 */

import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAnalyticsContext } from './analytics-provider';
import { PerformanceEvent } from '../../lib/analytics/analytics-types';

interface PerformanceMonitorProps {
  readonly screenName?: string;
  readonly trackRenderTime?: boolean;
  readonly trackMemoryUsage?: boolean;
  readonly trackNetworkRequests?: boolean;
  readonly trackUserInteractions?: boolean;
  readonly showMetrics?: boolean;
}

interface PerformanceMetrics {
  readonly renderTime: number;
  readonly memoryUsage: number;
  readonly networkRequests: number;
  readonly userInteractions: number;
}

/**
 * Component for monitoring and tracking performance metrics
 */
export function PerformanceMonitor({
  screenName = 'unknown',
  trackRenderTime = true,
  trackMemoryUsage = true,
  trackNetworkRequests = true,
  trackUserInteractions = true,
  showMetrics = false
}: PerformanceMonitorProps): React.JSX.Element {
  const analytics = useAnalyticsContext();
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    networkRequests: 0,
    userInteractions: 0
  });

  /**
   * Tracks render time
   */
  useEffect(() => {
    if (trackRenderTime) {
      renderStartTime.current = Date.now();
      
      return () => {
        const renderTime = Date.now() - renderStartTime.current;
        
        setMetrics(prev => ({ ...prev, renderTime }));
        
        if (analytics.isInitialized) {
          const performanceEvent: PerformanceEvent = {
            metricName: 'component_render_time',
            value: renderTime,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
        }
      };
    }
  }, [analytics, screenName, trackRenderTime]);

  /**
   * Tracks memory usage
   */
  useEffect(() => {
    if (trackMemoryUsage && analytics.isInitialized) {
      const trackMemory = (): void => {
        // Get memory usage (approximate)
        const memoryUsage = (performance as any).memory?.usedJSHeapSize || 0;
        
        setMetrics(prev => ({ ...prev, memoryUsage }));
        
        const performanceEvent: PerformanceEvent = {
          metricName: 'memory_usage',
          value: memoryUsage,
          unit: 'bytes',
          screenName,
          properties: {
            componentType: 'performance_monitor',
            timestamp: Date.now()
          }
        };
        
        analytics.trackPerformance(performanceEvent);
      };

      // Track memory usage periodically
      const interval = setInterval(trackMemory, 5000);
      
      return () => clearInterval(interval);
    }
  }, [analytics, screenName, trackMemoryUsage]);

  /**
   * Tracks network requests
   */
  useEffect(() => {
    if (trackNetworkRequests && analytics.isInitialized) {
      let requestCount = 0;
      
      const originalFetch = global.fetch;
      
      global.fetch = async (...args) => {
        const startTime = Date.now();
        requestCount++;
        
        try {
          const response = await originalFetch(...args);
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          setMetrics(prev => ({ ...prev, networkRequests: requestCount }));
          
          const performanceEvent: PerformanceEvent = {
            metricName: 'network_request_duration',
            value: duration,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              requestCount,
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
          
          return response;
        } catch (error) {
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          const performanceEvent: PerformanceEvent = {
            metricName: 'network_request_error',
            value: duration,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              requestCount,
              error: error.message,
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
          
          throw error;
        }
      };
      
      return () => {
        global.fetch = originalFetch;
      };
    }
  }, [analytics, screenName, trackNetworkRequests]);

  /**
   * Tracks user interactions
   */
  useEffect(() => {
    if (trackUserInteractions && analytics.isInitialized) {
      let interactionCount = 0;
      
      const handleInteraction = (): void => {
        interactionCount++;
        setMetrics(prev => ({ ...prev, userInteractions: interactionCount }));
        
        const performanceEvent: PerformanceEvent = {
          metricName: 'user_interaction_count',
          value: interactionCount,
          unit: 'count',
          screenName,
          properties: {
            componentType: 'performance_monitor',
            timestamp: Date.now()
          }
        };
        
        analytics.trackPerformance(performanceEvent);
      };
      
      // Add event listeners for user interactions
      const events = ['touchstart', 'click', 'scroll', 'keydown'];
      events.forEach(event => {
        document.addEventListener(event, handleInteraction, { passive: true });
      });
      
      return () => {
        events.forEach(event => {
          document.removeEventListener(event, handleInteraction);
        });
      };
    }
  }, [analytics, screenName, trackUserInteractions]);

  if (!showMetrics) {
    return <View />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance Metrics</Text>
      <View style={styles.metricsContainer}>
        <Text style={styles.metric}>
          Render Time: {metrics.renderTime}ms
        </Text>
        <Text style={styles.metric}>
          Memory: {(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB
        </Text>
        <Text style={styles.metric}>
          Network Requests: {metrics.networkRequests}
        </Text>
        <Text style={styles.metric}>
          User Interactions: {metrics.userInteractions}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F3F4F6',
    padding: 16,
    borderRadius: 8,
    margin: 16
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8
  },
  metricsContainer: {
    gap: 4
  },
  metric: {
    fontSize: 14,
    color: '#6B7280',
    fontFamily: 'monospace'
  }
});
 * @fileoverview Performance monitoring component
 * @author Blaze AI Team
 */

import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useAnalyticsContext } from './analytics-provider';
import { PerformanceEvent } from '../../lib/analytics/analytics-types';

interface PerformanceMonitorProps {
  readonly screenName?: string;
  readonly trackRenderTime?: boolean;
  readonly trackMemoryUsage?: boolean;
  readonly trackNetworkRequests?: boolean;
  readonly trackUserInteractions?: boolean;
  readonly showMetrics?: boolean;
}

interface PerformanceMetrics {
  readonly renderTime: number;
  readonly memoryUsage: number;
  readonly networkRequests: number;
  readonly userInteractions: number;
}

/**
 * Component for monitoring and tracking performance metrics
 */
export function PerformanceMonitor({
  screenName = 'unknown',
  trackRenderTime = true,
  trackMemoryUsage = true,
  trackNetworkRequests = true,
  trackUserInteractions = true,
  showMetrics = false
}: PerformanceMonitorProps): React.JSX.Element {
  const analytics = useAnalyticsContext();
  const renderStartTime = useRef<number>(0);
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    renderTime: 0,
    memoryUsage: 0,
    networkRequests: 0,
    userInteractions: 0
  });

  /**
   * Tracks render time
   */
  useEffect(() => {
    if (trackRenderTime) {
      renderStartTime.current = Date.now();
      
      return () => {
        const renderTime = Date.now() - renderStartTime.current;
        
        setMetrics(prev => ({ ...prev, renderTime }));
        
        if (analytics.isInitialized) {
          const performanceEvent: PerformanceEvent = {
            metricName: 'component_render_time',
            value: renderTime,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
        }
      };
    }
  }, [analytics, screenName, trackRenderTime]);

  /**
   * Tracks memory usage
   */
  useEffect(() => {
    if (trackMemoryUsage && analytics.isInitialized) {
      const trackMemory = (): void => {
        // Get memory usage (approximate)
        const memoryUsage = (performance as any).memory?.usedJSHeapSize || 0;
        
        setMetrics(prev => ({ ...prev, memoryUsage }));
        
        const performanceEvent: PerformanceEvent = {
          metricName: 'memory_usage',
          value: memoryUsage,
          unit: 'bytes',
          screenName,
          properties: {
            componentType: 'performance_monitor',
            timestamp: Date.now()
          }
        };
        
        analytics.trackPerformance(performanceEvent);
      };

      // Track memory usage periodically
      const interval = setInterval(trackMemory, 5000);
      
      return () => clearInterval(interval);
    }
  }, [analytics, screenName, trackMemoryUsage]);

  /**
   * Tracks network requests
   */
  useEffect(() => {
    if (trackNetworkRequests && analytics.isInitialized) {
      let requestCount = 0;
      
      const originalFetch = global.fetch;
      
      global.fetch = async (...args) => {
        const startTime = Date.now();
        requestCount++;
        
        try {
          const response = await originalFetch(...args);
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          setMetrics(prev => ({ ...prev, networkRequests: requestCount }));
          
          const performanceEvent: PerformanceEvent = {
            metricName: 'network_request_duration',
            value: duration,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              requestCount,
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
          
          return response;
        } catch (error) {
          const endTime = Date.now();
          const duration = endTime - startTime;
          
          const performanceEvent: PerformanceEvent = {
            metricName: 'network_request_error',
            value: duration,
            unit: 'ms',
            screenName,
            properties: {
              componentType: 'performance_monitor',
              requestCount,
              error: error.message,
              timestamp: Date.now()
            }
          };
          
          analytics.trackPerformance(performanceEvent);
          
          throw error;
        }
      };
      
      return () => {
        global.fetch = originalFetch;
      };
    }
  }, [analytics, screenName, trackNetworkRequests]);

  /**
   * Tracks user interactions
   */
  useEffect(() => {
    if (trackUserInteractions && analytics.isInitialized) {
      let interactionCount = 0;
      
      const handleInteraction = (): void => {
        interactionCount++;
        setMetrics(prev => ({ ...prev, userInteractions: interactionCount }));
        
        const performanceEvent: PerformanceEvent = {
          metricName: 'user_interaction_count',
          value: interactionCount,
          unit: 'count',
          screenName,
          properties: {
            componentType: 'performance_monitor',
            timestamp: Date.now()
          }
        };
        
        analytics.trackPerformance(performanceEvent);
      };
      
      // Add event listeners for user interactions
      const events = ['touchstart', 'click', 'scroll', 'keydown'];
      events.forEach(event => {
        document.addEventListener(event, handleInteraction, { passive: true });
      });
      
      return () => {
        events.forEach(event => {
          document.removeEventListener(event, handleInteraction);
        });
      };
    }
  }, [analytics, screenName, trackUserInteractions]);

  if (!showMetrics) {
    return <View />;
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Performance Metrics</Text>
      <View style={styles.metricsContainer}>
        <Text style={styles.metric}>
          Render Time: {metrics.renderTime}ms
        </Text>
        <Text style={styles.metric}>
          Memory: {(metrics.memoryUsage / 1024 / 1024).toFixed(2)}MB
        </Text>
        <Text style={styles.metric}>
          Network Requests: {metrics.networkRequests}
        </Text>
        <Text style={styles.metric}>
          User Interactions: {metrics.userInteractions}
        </Text>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    backgroundColor: '#F3F4F6',
    padding: 16,
    borderRadius: 8,
    margin: 16
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8
  },
  metricsContainer: {
    gap: 4
  },
  metric: {
    fontSize: 14,
    color: '#6B7280',
    fontFamily: 'monospace'
  }
});


