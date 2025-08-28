import { useCallback, useMemo, useRef, useEffect } from 'react';
import { InteractionManager, Platform } from 'react-native';

// Performance monitoring utilities
export const performanceUtils = {
  // Measure execution time
  measureTime: <T>(fn: () => T): { result: T; duration: number } => {
    const start = performance.now();
    const result = fn();
    const duration = performance.now() - start;
    return { result, duration };
  },

  // Debounce function execution
  debounce: <T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): ((...args: Parameters<T>) => void) => {
    let timeoutId: NodeJS.Timeout;
    return (...args: Parameters<T>) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => func(...args), delay);
    };
  },

  // Throttle function execution
  throttle: <T extends (...args: any[]) => any>(
    func: T,
    delay: number
  ): ((...args: Parameters<T>) => void) => {
    let lastCall = 0;
    return (...args: Parameters<T>) => {
      const now = Date.now();
      if (now - lastCall >= delay) {
        lastCall = now;
        func(...args);
      }
    };
  },

  // Batch multiple operations
  batch: <T>(operations: (() => T)[], batchSize: number = 10): Promise<T[]> => {
    return new Promise((resolve) => {
      const results: T[] = [];
      let currentIndex = 0;

      const processBatch = () => {
        const batch = operations.slice(currentIndex, currentIndex + batchSize);
        const batchResults = batch.map(op => op());
        results.push(...batchResults);
        currentIndex += batchSize;

        if (currentIndex < operations.length) {
          requestAnimationFrame(processBatch);
        } else {
          resolve(results);
        }
      };

      processBatch();
    });
  },
};

// React performance hooks
export const usePerformanceOptimizedCallback = <T extends (...args: any[]) => any>(
  callback: T,
  dependencies: any[],
  options: {
    debounce?: number;
    throttle?: number;
  } = {}
): T => {
  const { debounce, throttle } = options;

  const optimizedCallback = useCallback(callback, dependencies);

  if (debounce) {
    return useMemo(
      () => performanceUtils.debounce(optimizedCallback, debounce) as T,
      [optimizedCallback, debounce]
    );
  }

  if (throttle) {
    return useMemo(
      () => performanceUtils.throttle(optimizedCallback, throttle) as T,
      [optimizedCallback, throttle]
    );
  }

  return optimizedCallback;
};

export const usePerformanceOptimizedMemo = <T>(
  factory: () => T,
  dependencies: any[],
  options: {
    maxAge?: number;
  } = {}
): T => {
  const { maxAge } = options;
  const lastUpdateRef = useRef<number>(0);
  const lastValueRef = useRef<T | null>(null);

  return useMemo(() => {
    const now = Date.now();
    
    if (maxAge && lastValueRef.current !== null) {
      const timeSinceLastUpdate = now - lastUpdateRef.current;
      if (timeSinceLastUpdate < maxAge) {
        return lastValueRef.current;
      }
    }

    const newValue = factory();
    lastValueRef.current = newValue;
    lastUpdateRef.current = now;
    
    return newValue;
  }, dependencies);
};

// Memory management utilities
export const useMemoryOptimizedList = <T>(
  items: T[],
  options: {
    maxItems?: number;
    keepRecent?: boolean;
  } = {}
) => {
  const { maxItems = 100, keepRecent = true } = options;

  return useMemo(() => {
    if (items.length <= maxItems) {
      return items;
    }

    if (keepRecent) {
      return items.slice(-maxItems);
    }

    return items.slice(0, maxItems);
  }, [items, maxItems, keepRecent]);
};

// Interaction management
export const useInteractionOptimizedEffect = (
  effect: () => void | (() => void),
  dependencies: any[] = []
) => {
  useEffect(() => {
    const cleanup = InteractionManager.runAfterInteractions(() => {
      return effect();
    });

    return cleanup;
  }, dependencies);
};

// Platform-specific optimizations
export const usePlatformOptimizedStyle = (
  iosStyle: any,
  androidStyle: any,
  webStyle?: any
) => {
  return useMemo(() => {
    if (Platform.OS === 'ios') {
      return iosStyle;
    }
    if (Platform.OS === 'android') {
      return androidStyle;
    }
    return webStyle || iosStyle;
  }, [iosStyle, androidStyle, webStyle]);
};

// Image optimization utilities
export const imageOptimizationUtils = {
  // Calculate optimal image dimensions
  calculateOptimalDimensions: (
    originalWidth: number,
    originalHeight: number,
    maxWidth: number,
    maxHeight: number
  ) => {
    const aspectRatio = originalWidth / originalHeight;
    
    if (originalWidth <= maxWidth && originalHeight <= maxHeight) {
      return { width: originalWidth, height: originalHeight };
    }

    if (aspectRatio > 1) {
      // Landscape
      const width = Math.min(originalWidth, maxWidth);
      const height = width / aspectRatio;
      return { width, height: Math.min(height, maxHeight) };
    } else {
      // Portrait
      const height = Math.min(originalHeight, maxHeight);
      const width = height * aspectRatio;
      return { width: Math.min(width, maxWidth), height };
    }
  },

  // Generate responsive image sizes
  generateResponsiveSizes: (baseWidth: number, baseHeight: number) => {
    const sizes = [0.5, 1, 1.5, 2, 3];
    return sizes.map(scale => ({
      width: Math.round(baseWidth * scale),
      height: Math.round(baseHeight * scale),
      scale,
    }));
  },
};

// Network optimization utilities
export const networkOptimizationUtils = {
  // Retry with exponential backoff
  retryWithBackoff: async <T>(
    operation: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> => {
    let lastError: Error;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        
        if (attempt === maxRetries) {
          throw lastError;
        }

        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError!;
  },

  // Cache with TTL
  createCacheWithTTL = <T>(ttl: number = 5 * 60 * 1000) => {
    const cache = new Map<string, { value: T; timestamp: number }>();

    return {
      get: (key: string): T | null => {
        const item = cache.get(key);
        if (!item) return null;

        const isExpired = Date.now() - item.timestamp > ttl;
        if (isExpired) {
          cache.delete(key);
          return null;
        }

        return item.value;
      },

      set: (key: string, value: T): void => {
        cache.set(key, { value, timestamp: Date.now() });
      },

      clear: (): void => {
        cache.clear();
      },

      size: (): number => {
        return cache.size;
      },
    };
  },
}; 