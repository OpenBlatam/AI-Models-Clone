"use client";

import React, { createContext, useContext, useEffect, useState, useCallback, useMemo } from "react";
import { useRouter } from "next/navigation";

interface PerformanceMetrics {
  memoryUsage: number;
  cpuUsage: number;
  networkSpeed: number;
  deviceType: 'mobile' | 'tablet' | 'desktop';
  batteryLevel?: number;
}

interface PerformanceContextType {
  isSlowConnection: boolean;
  prefetchEnabled: boolean;
  imageQuality: 'low' | 'medium' | 'high';
  performanceMetrics: PerformanceMetrics;
  preloadCriticalRoutes: () => void;
  optimizeForDevice: () => void;
  getPerformanceScore: () => number;
}

const PerformanceContext = createContext<PerformanceContextType>({
  isSlowConnection: false,
  prefetchEnabled: true,
  imageQuality: 'high',
  performanceMetrics: {
    memoryUsage: 0,
    cpuUsage: 0,
    networkSpeed: 0,
    deviceType: 'desktop'
  },
  preloadCriticalRoutes: () => {},
  optimizeForDevice: () => {},
  getPerformanceScore: () => 0,
});

const CRITICAL_ROUTES = [
  '/dashboard/academy',
  '/dashboard/videos',
  '/dashboard/lessons',
  '/dashboard/games'
] as const;

const PERFORMANCE_THRESHOLDS = {
  MEMORY_WARNING: 80, // 80% memory usage
  CPU_WARNING: 90,    // 90% CPU usage
  NETWORK_SLOW: 1.5,  // 1.5 Mbps
  BATTERY_LOW: 20     // 20% battery
} as const;

export function PerformanceProvider({ children }: { children: React.ReactNode }) {
  const [isSlowConnection, setIsSlowConnection] = useState(false);
  const [prefetchEnabled, setPrefetchEnabled] = useState(true);
  const [imageQuality, setImageQuality] = useState<'low' | 'medium' | 'high'>('high');
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics>({
    memoryUsage: 0,
    cpuUsage: 0,
    networkSpeed: 0,
    deviceType: 'desktop'
  });
  
  const router = useRouter();

  // Detect device type
  const detectDeviceType = useCallback((): 'mobile' | 'tablet' | 'desktop' => {
    if (typeof window === 'undefined') return 'desktop';
    
    const width = window.innerWidth;
    if (width < 768) return 'mobile';
    if (width < 1024) return 'tablet';
    return 'desktop';
  }, []);

  // Get performance metrics
  const getPerformanceMetrics = useCallback((): PerformanceMetrics => {
    if (typeof window === 'undefined') {
      return {
        memoryUsage: 0,
        cpuUsage: 0,
        networkSpeed: 0,
        deviceType: 'desktop'
      };
    }

    const connection = (navigator as any).connection;
    const networkSpeed = connection?.downlink || 0;
    
    // Estimate memory usage (rough calculation)
    const memoryUsage = performance.memory 
      ? (performance.memory.usedJSHeapSize / performance.memory.jsHeapSizeLimit) * 100
      : 0;

    return {
      memoryUsage: Math.round(memoryUsage),
      cpuUsage: 0, // Would need Web Workers for accurate CPU measurement
      networkSpeed,
      deviceType: detectDeviceType(),
      batteryLevel: (navigator as any).getBattery?.()?.then((battery: any) => battery.level * 100)
    };
  }, [detectDeviceType]);

  // Optimize based on device performance
  const optimizeForDevice = useCallback(() => {
    const metrics = getPerformanceMetrics();
    const { memoryUsage, networkSpeed, deviceType } = metrics;

    // Adjust image quality based on performance
    if (memoryUsage > PERFORMANCE_THRESHOLDS.MEMORY_WARNING || networkSpeed < PERFORMANCE_THRESHOLDS.NETWORK_SLOW) {
      setImageQuality('low');
    } else if (networkSpeed < 5) {
      setImageQuality('medium');
    } else {
      setImageQuality('high');
    }

    // Disable prefetching on slow connections or low-end devices
    const shouldDisablePrefetch = networkSpeed < PERFORMANCE_THRESHOLDS.NETWORK_SLOW || 
                                 memoryUsage > PERFORMANCE_THRESHOLDS.MEMORY_WARNING ||
                                 deviceType === 'mobile';
    
    setPrefetchEnabled(!shouldDisablePrefetch);
    setIsSlowConnection(shouldDisablePrefetch);

    // Log performance warnings
    if (memoryUsage > PERFORMANCE_THRESHOLDS.MEMORY_WARNING) {
      console.warn(`High memory usage detected: ${memoryUsage}%`);
    }
    if (networkSpeed < PERFORMANCE_THRESHOLDS.NETWORK_SLOW) {
      console.warn(`Slow network detected: ${networkSpeed} Mbps`);
    }
  }, [getPerformanceMetrics]);

  // Calculate performance score (0-100)
  const getPerformanceScore = useCallback((): number => {
    const { memoryUsage, networkSpeed, deviceType } = performanceMetrics;
    
    let score = 100;
    
    // Deduct points for high memory usage
    if (memoryUsage > PERFORMANCE_THRESHOLDS.MEMORY_WARNING) {
      score -= (memoryUsage - PERFORMANCE_THRESHOLDS.MEMORY_WARNING) * 2;
    }
    
    // Deduct points for slow network
    if (networkSpeed < PERFORMANCE_THRESHOLDS.NETWORK_SLOW) {
      score -= (PERFORMANCE_THRESHOLDS.NETWORK_SLOW - networkSpeed) * 10;
    }
    
    // Adjust for device type
    if (deviceType === 'mobile') score -= 10;
    if (deviceType === 'tablet') score -= 5;
    
    return Math.max(0, Math.min(100, score));
  }, [performanceMetrics]);

  const preloadCriticalRoutes = useCallback(() => {
    if (!prefetchEnabled) return;
    
    CRITICAL_ROUTES.forEach((route, index) => {
      setTimeout(() => {
        router.prefetch(route);
      }, index * 100); // Stagger prefetch requests
    });
  }, [prefetchEnabled, router]);

  // Monitor performance metrics
  useEffect(() => {
    const updateMetrics = () => {
      const metrics = getPerformanceMetrics();
      setPerformanceMetrics(metrics);
      optimizeForDevice();
    };

    // Initial measurement
    updateMetrics();

    // Set up monitoring intervals
    const memoryInterval = setInterval(updateMetrics, 5000); // Every 5 seconds
    const networkInterval = setInterval(updateMetrics, 10000); // Every 10 seconds

    // Monitor connection changes
    if (typeof window !== 'undefined' && 'connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', updateMetrics);
      
      return () => {
        clearInterval(memoryInterval);
        clearInterval(networkInterval);
        connection.removeEventListener('change', updateMetrics);
      };
    }

    return () => {
      clearInterval(memoryInterval);
      clearInterval(networkInterval);
    };
  }, [getPerformanceMetrics, optimizeForDevice]);

  // Initialize service worker and route preloading
  useEffect(() => {
    const initializePerformance = async () => {
      // Register service worker
      if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
        try {
          await navigator.serviceWorker.register('/sw.js');
        } catch (error) {
          console.warn('Service worker registration failed:', error);
        }
      }

      // Preload critical routes after a delay
      setTimeout(preloadCriticalRoutes, 2000);
    };

    initializePerformance();
  }, [preloadCriticalRoutes]);

  const contextValue = useMemo(() => ({
    isSlowConnection,
    prefetchEnabled,
    imageQuality,
    performanceMetrics,
    preloadCriticalRoutes,
    optimizeForDevice,
    getPerformanceScore
  }), [
    isSlowConnection,
    prefetchEnabled,
    imageQuality,
    performanceMetrics,
    preloadCriticalRoutes,
    optimizeForDevice,
    getPerformanceScore
  ]);

  return (
    <PerformanceContext.Provider value={contextValue}>
      {children}
    </PerformanceContext.Provider>
  );
}

export const usePerformance = () => useContext(PerformanceContext);
