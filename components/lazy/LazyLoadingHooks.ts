import React, { useState, useEffect, useCallback, useRef } from 'react';

// Hook for intersection observer lazy loading
export const useIntersectionObserver = (
  options: IntersectionObserverInit = { threshold: 0.1, rootMargin: '50px' }
) => {
  const [isIntersecting, setIsIntersecting] = useState(false);
  const [hasIntersected, setHasIntersected] = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const observer = new IntersectionObserver(([entry]) => {
      if (entry.isIntersecting) {
        setIsIntersecting(true);
        setHasIntersected(true);
        observer.disconnect();
      }
    }, options);

    observer.observe(element);

    return () => observer.disconnect();
  }, [options]);

  return { ref, isIntersecting, hasIntersected };
};

// Hook for viewport-based lazy loading
export const useViewportLazyLoading = (threshold = 0.5) => {
  const [isInViewport, setIsInViewport] = useState(false);
  const [hasBeenInViewport, setHasBeenInViewport] = useState(false);
  const ref = useRef<HTMLElement>(null);

  useEffect(() => {
    const element = ref.current;
    if (!element) return;

    const checkViewport = () => {
      const rect = element.getBoundingClientRect();
      const windowHeight = window.innerHeight;
      const elementTop = rect.top;
      const elementBottom = rect.bottom;
      
      const isVisible = elementTop < windowHeight * threshold && elementBottom > 0;
      
      if (isVisible && !hasBeenInViewport) {
        setIsInViewport(true);
        setHasBeenInViewport(true);
      }
    };

    checkViewport();
    window.addEventListener('scroll', checkViewport);
    window.addEventListener('resize', checkViewport);

    return () => {
      window.removeEventListener('scroll', checkViewport);
      window.removeEventListener('resize', checkViewport);
    };
  }, [threshold, hasBeenInViewport]);

  return { ref, isInViewport, hasBeenInViewport };
};

// Hook for network-aware lazy loading
export const useNetworkAwareLazyLoading = () => {
  const [connectionSpeed, setConnectionSpeed] = useState<'fast' | 'slow' | 'unknown'>('unknown');
  const [shouldLoadHeavy, setShouldLoadHeavy] = useState(true);

  useEffect(() => {
    const updateConnectionInfo = () => {
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        
        if (connection.effectiveType === '4g') {
          setConnectionSpeed('fast');
          setShouldLoadHeavy(true);
        } else if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
          setConnectionSpeed('slow');
          setShouldLoadHeavy(false);
        } else {
          setConnectionSpeed('unknown');
          setShouldLoadHeavy(true);
        }
      }
    };

    updateConnectionInfo();
    
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', updateConnectionInfo);
      return () => connection.removeEventListener('change', updateConnectionInfo);
    }
  }, []);

  return { connectionSpeed, shouldLoadHeavy };
};

// Hook for priority-based lazy loading
export const usePriorityLazyLoading = <T>(
  items: Array<{ key: string; priority: 'high' | 'medium' | 'low'; data: T }>,
  delays = { high: 0, medium: 1000, low: 3000 }
) => {
  const [loadedItems, setLoadedItems] = useState<Set<string>>(new Set());
  const [loadingStates, setLoadingStates] = useState<Record<string, boolean>>({});

  const loadItem = useCallback(async (key: string, data: T) => {
    setLoadingStates(prev => ({ ...prev, [key]: true }));
    
    try {
      // Simulate loading delay
      await new Promise(resolve => setTimeout(resolve, Math.random() * 500));
      setLoadedItems(prev => new Set([...prev, key]));
    } catch (error) {
      console.error(`Failed to load item ${key}:`, error);
    } finally {
      setLoadingStates(prev => ({ ...prev, [key]: false }));
    }
  }, []);

  useEffect(() => {
    const highPriority = items.filter(item => item.priority === 'high');
    const mediumPriority = items.filter(item => item.priority === 'medium');
    const lowPriority = items.filter(item => item.priority === 'low');

    // Load high priority immediately
    highPriority.forEach(({ key, data }) => {
      loadItem(key, data);
    });

    // Load medium priority after delay
    const mediumTimer = setTimeout(() => {
      mediumPriority.forEach(({ key, data }) => {
        loadItem(key, data);
      });
    }, delays.medium);

    // Load low priority after longer delay
    const lowTimer = setTimeout(() => {
      lowPriority.forEach(({ key, data }) => {
        loadItem(key, data);
      });
    }, delays.low);

    return () => {
      clearTimeout(mediumTimer);
      clearTimeout(lowTimer);
    };
  }, [items, delays, loadItem]);

  return { loadedItems, loadingStates };
};

// Hook for user interaction-based lazy loading
export const useInteractionLazyLoading = () => {
  const [interactions, setInteractions] = useState<Set<string>>(new Set());
  const [loadedFeatures, setLoadedFeatures] = useState<Set<string>>(new Set());

  const triggerInteraction = useCallback((feature: string) => {
    setInteractions(prev => new Set([...prev, feature]));
    
    if (!loadedFeatures.has(feature)) {
      setLoadedFeatures(prev => new Set([...prev, feature]));
    }
  }, [loadedFeatures]);

  return { interactions, loadedFeatures, triggerInteraction };
};

// Hook for performance-aware lazy loading
export const usePerformanceAwareLazyLoading = (threshold = 30) => {
  const [fps, setFps] = useState(60);
  const [shouldLoadHeavy, setShouldLoadHeavy] = useState(true);
  const frameCountRef = useRef(0);
  const lastTimeRef = useRef(performance.now());

  useEffect(() => {
    const measureFPS = () => {
      frameCountRef.current++;
      const currentTime = performance.now();
      
      if (currentTime - lastTimeRef.current >= 1000) {
        const currentFps = Math.round((frameCountRef.current * 1000) / (currentTime - lastTimeRef.current));
        setFps(currentFps);
        setShouldLoadHeavy(currentFps > threshold);
        
        frameCountRef.current = 0;
        lastTimeRef.current = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };

    requestAnimationFrame(measureFPS);
  }, [threshold]);

  return { fps, shouldLoadHeavy };
};

// Hook for route-based lazy loading
export const useRouteLazyLoading = (currentRoute: string) => {
  const [loadedRoutes, setLoadedRoutes] = useState<Set<string>>(new Set());
  const [loadingRoutes, setLoadingRoutes] = useState<Set<string>>(new Set());

  const loadRoute = useCallback(async (route: string) => {
    if (loadedRoutes.has(route)) return;
    
    setLoadingRoutes(prev => new Set([...prev, route]));
    
    try {
      // Simulate route loading
      await new Promise(resolve => setTimeout(resolve, Math.random() * 1000));
      setLoadedRoutes(prev => new Set([...prev, route]));
    } catch (error) {
      console.error(`Failed to load route ${route}:`, error);
    } finally {
      setLoadingRoutes(prev => {
        const newSet = new Set(prev);
        newSet.delete(route);
        return newSet;
      });
    }
  }, [loadedRoutes]);

  // Preload adjacent routes
  useEffect(() => {
    const adjacentRoutes = getAdjacentRoutes(currentRoute);
    adjacentRoutes.forEach(route => {
      if (!loadedRoutes.has(route)) {
        loadRoute(route);
      }
    });
  }, [currentRoute, loadedRoutes, loadRoute]);

  return { loadedRoutes, loadingRoutes, loadRoute };
};

// Helper function to get adjacent routes
const getAdjacentRoutes = (currentRoute: string): string[] => {
  // This would be customized based on your routing structure
  const routeMap: Record<string, string[]> = {
    '/dashboard': ['/dashboard/analytics', '/dashboard/settings'],
    '/academy': ['/academy/courses', '/academy/progress'],
    '/chat': ['/chat/history', '/chat/settings'],
    '/games': ['/games/leaderboard', '/games/settings']
  };
  
  return routeMap[currentRoute] || [];
};

// Hook for memory-aware lazy loading
export const useMemoryAwareLazyLoading = (memoryThreshold = 100) => {
  const [memoryUsage, setMemoryUsage] = useState<number | null>(null);
  const [shouldLoadHeavy, setShouldLoadHeavy] = useState(true);

  useEffect(() => {
    const checkMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        const usedMB = memory.usedJSHeapSize / 1024 / 1024;
        setMemoryUsage(usedMB);
        setShouldLoadHeavy(usedMB < memoryThreshold);
      }
    };

    checkMemory();
    const interval = setInterval(checkMemory, 5000);

    return () => clearInterval(interval);
  }, [memoryThreshold]);

  return { memoryUsage, shouldLoadHeavy };
}; 