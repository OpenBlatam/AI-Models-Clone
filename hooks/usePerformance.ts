import { useState, useEffect, useCallback, useRef } from 'react';

export interface PerformanceMetrics {
  pageLoadTime: number;
  timeToFirstByte: number;
  timeToInteractive: number;
  firstContentfulPaint: number;
  largestContentfulPaint: number;
  cumulativeLayoutShift: number;
  firstInputDelay: number;
}

export interface PerformanceObserver {
  disconnect: () => void;
}

/**
 * Custom hook for monitoring web performance metrics
 * @returns Performance metrics and monitoring functions
 */
export function usePerformance() {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    pageLoadTime: 0,
    timeToFirstByte: 0,
    timeToInteractive: 0,
    firstContentfulPaint: 0,
    largestContentfulPaint: 0,
    cumulativeLayoutShift: 0,
    firstInputDelay: 0,
  });

  const [isMonitoring, setIsMonitoring] = useState(false);
  const observers = useRef<PerformanceObserver[]>([]);

  // Measure page load time
  const measurePageLoad = useCallback(() => {
    if (typeof window !== 'undefined' && 'performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
        setMetrics(prev => ({ ...prev, pageLoadTime: loadTime }));
      }
    }
  }, []);

  // Measure Time to First Byte
  const measureTTFB = useCallback(() => {
    if (typeof window !== 'undefined' && 'performance' in window) {
      const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
      if (navigation) {
        const ttfb = navigation.responseStart - navigation.requestStart;
        setMetrics(prev => ({ ...prev, timeToFirstByte: ttfb }));
      }
    }
  }, []);

  // Measure First Contentful Paint
  const measureFCP = useCallback(() => {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const fcpEntry = entries.find(entry => entry.name === 'first-contentful-paint');
          if (fcpEntry) {
            setMetrics(prev => ({ ...prev, firstContentfulPaint: fcpEntry.startTime }));
            observer.disconnect();
          }
        });
        
        observer.observe({ entryTypes: ['paint'] });
        observers.current.push(observer);
      } catch (error) {
        console.warn('FCP measurement not supported:', error);
      }
    }
  }, []);

  // Measure Largest Contentful Paint
  const measureLCP = useCallback(() => {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const lastEntry = entries[entries.length - 1];
          if (lastEntry) {
            setMetrics(prev => ({ ...prev, largestContentfulPaint: lastEntry.startTime }));
          }
        });
        
        observer.observe({ entryTypes: ['largest-contentful-paint'] });
        observers.current.push(observer);
      } catch (error) {
        console.warn('LCP measurement not supported:', error);
      }
    }
  }, []);

  // Measure Cumulative Layout Shift
  const measureCLS = useCallback(() => {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      try {
        let clsValue = 0;
        const observer = new PerformanceObserver((list) => {
          for (const entry of list.getEntries()) {
            if (!entry.hadRecentInput) {
              clsValue += (entry as any).value;
            }
          }
          setMetrics(prev => ({ ...prev, cumulativeLayoutShift: clsValue }));
        });
        
        observer.observe({ entryTypes: ['layout-shift'] });
        observers.current.push(observer);
      } catch (error) {
        console.warn('CLS measurement not supported:', error);
      }
    }
  }, []);

  // Measure First Input Delay
  const measureFID = useCallback(() => {
    if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
      try {
        const observer = new PerformanceObserver((list) => {
          const entries = list.getEntries();
          for (const entry of entries) {
            const fid = entry.processingStart - entry.startTime;
            setMetrics(prev => ({ ...prev, firstInputDelay: fid }));
            break; // Only measure the first input
          }
        });
        
        observer.observe({ entryTypes: ['first-input'] });
        observers.current.push(observer);
      } catch (error) {
        console.warn('FID measurement not supported:', error);
      }
    }
  }, []);

  // Start monitoring all metrics
  const startMonitoring = useCallback(() => {
    if (typeof window === 'undefined') return;

    setIsMonitoring(true);
    
    // Measure immediate metrics
    measurePageLoad();
    measureTTFB();
    
    // Start observing performance events
    measureFCP();
    measureLCP();
    measureCLS();
    measureFID();
    
    // Measure Time to Interactive (approximation)
    if (document.readyState === 'complete') {
      const tti = performance.now();
      setMetrics(prev => ({ ...prev, timeToInteractive: tti }));
    } else {
      window.addEventListener('load', () => {
        const tti = performance.now();
        setMetrics(prev => ({ ...prev, timeToInteractive: tti }));
      });
    }
  }, [measurePageLoad, measureTTFB, measureFCP, measureLCP, measureCLS, measureFID]);

  // Stop monitoring
  const stopMonitoring = useCallback(() => {
    setIsMonitoring(false);
    observers.current.forEach(observer => observer.disconnect());
    observers.current = [];
  }, []);

  // Reset metrics
  const resetMetrics = useCallback(() => {
    setMetrics({
      pageLoadTime: 0,
      timeToFirstByte: 0,
      timeToInteractive: 0,
      firstContentfulPaint: 0,
      largestContentfulPaint: 0,
      cumulativeLayoutShift: 0,
      firstInputDelay: 0,
    });
  }, []);

  // Get performance score based on metrics
  const getPerformanceScore = useCallback(() => {
    let score = 100;
    
    // FCP scoring (0-100)
    if (metrics.firstContentfulPaint > 1800) score -= 20;
    else if (metrics.firstContentfulPaint > 1000) score -= 10;
    
    // LCP scoring (0-100)
    if (metrics.largestContentfulPaint > 4000) score -= 25;
    else if (metrics.largestContentfulPaint > 2500) score -= 15;
    
    // CLS scoring (0-100)
    if (metrics.cumulativeLayoutShift > 0.25) score -= 25;
    else if (metrics.cumulativeLayoutShift > 0.1) score -= 15;
    
    // FID scoring (0-100)
    if (metrics.firstInputDelay > 300) score -= 20;
    else if (metrics.firstInputDelay > 100) score -= 10;
    
    return Math.max(0, score);
  }, [metrics]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopMonitoring();
    };
  }, [stopMonitoring]);

  return {
    metrics,
    isMonitoring,
    startMonitoring,
    stopMonitoring,
    resetMetrics,
    getPerformanceScore,
    performanceScore: getPerformanceScore(),
  };
}

/**
 * Hook for measuring component render performance
 * @param componentName - Name of the component for identification
 * @returns Performance measurement functions
 */
export function useComponentPerformance(componentName: string) {
  const renderStart = useRef<number>(0);
  const renderCount = useRef<number>(0);

  useEffect(() => {
    renderStart.current = performance.now();
    renderCount.current++;

    return () => {
      const renderTime = performance.now() - renderStart.current;
      if (process.env.NODE_ENV === 'development') {
        console.log(`${componentName} render #${renderCount.current}: ${renderTime.toFixed(2)}ms`);
      }
    };
  });

  const measureOperation = useCallback((operationName: string, operation: () => void) => {
    const start = performance.now();
    operation();
    const duration = performance.now() - start;
    
    if (process.env.NODE_ENV === 'development') {
      console.log(`${componentName} ${operationName}: ${duration.toFixed(2)}ms`);
    }
    
    return duration;
  }, [componentName]);

  return {
    renderCount: renderCount.current,
    measureOperation,
  };
}
