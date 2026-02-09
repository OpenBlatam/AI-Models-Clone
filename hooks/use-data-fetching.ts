'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { z } from 'zod';

export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastFetched: Date | null;
}

export interface FetchOptions {
  immediate?: boolean;
  cacheTime?: number; // milliseconds
  retryCount?: number;
  retryDelay?: number; // milliseconds
  onSuccess?: (data: any) => void;
  onError?: (error: Error) => void;
}

export interface UseDataFetchingReturn<T> extends FetchState<T> {
  refetch: () => Promise<void>;
  clearCache: () => void;
  updateData: (updater: (data: T | null) => T | null) => void;
  setData: (data: T) => void;
}

// In-memory cache (use Redis in production)
const cache = new Map<string, { data: any; timestamp: number; ttl: number }>();

/**
 * Advanced hook for data fetching with caching, error handling, and retry logic
 * 
 * @param url - The URL to fetch data from
 * @param schema - Zod schema for data validation
 * @param options - Configuration options
 * @returns Object with data, loading state, error state, and control functions
 * 
 * @example
 * ```tsx
 * const { data, loading, error, refetch } = useDataFetching(
 *   '/api/users',
 *   userSchema,
 *   { immediate: true, cacheTime: 5 * 60 * 1000 }
 * );
 * ```
 */
export function useDataFetching<T>(
  url: string,
  schema: z.ZodSchema<T>,
  options: FetchOptions = {}
): UseDataFetchingReturn<T> {
  const {
    immediate = true,
    cacheTime = 5 * 60 * 1000, // 5 minutes default
    retryCount = 3,
    retryDelay = 1000, // 1 second
    onSuccess,
    onError,
  } = options;

  const [state, setState] = useState<FetchState<T>>({
    data: null,
    loading: false,
    error: null,
    lastFetched: null,
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Generate cache key
  const cacheKey = `fetch:${url}`;

  // Check if data is cached and still valid
  const getCachedData = useCallback((): T | null => {
    const cached = cache.get(cacheKey);
    if (cached && Date.now() - cached.timestamp < cached.ttl) {
      return cached.data;
    }
    // Remove expired cache entry
    if (cached) {
      cache.delete(cacheKey);
    }
    return null;
  }, [cacheKey]);

  // Set cached data
  const setCachedData = useCallback((data: T) => {
    cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
      ttl: cacheTime,
    });
  }, [cacheKey, cacheTime]);

  // Clear cache for this URL
  const clearCache = useCallback(() => {
    cache.delete(cacheKey);
  }, [cacheKey]);

  // Update local state
  const updateState = useCallback((updates: Partial<FetchState<T>>) => {
    setState(current => ({ ...current, ...updates }));
  }, []);

  // Update data with custom logic
  const updateData = useCallback((updater: (data: T | null) => T | null) => {
    setState(current => ({
      ...current,
      data: updater(current.data),
    }));
  }, []);

  // Set data directly
  const setData = useCallback((data: T) => {
    updateState({ data, error: null });
    setCachedData(data);
  }, [updateState, setCachedData]);

  // Fetch data with retry logic
  const fetchData = useCallback(async (retryAttempt = 0): Promise<void> => {
    // Check cache first
    const cachedData = getCachedData();
    if (cachedData) {
      updateState({
        data: cachedData,
        loading: false,
        error: null,
        lastFetched: new Date(),
      });
      onSuccess?.(cachedData);
      return;
    }

    // Abort previous request if still pending
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new abort controller
    abortControllerRef.current = new AbortController();

    try {
      updateState({ loading: true, error: null });

      const response = await fetch(url, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const rawData = await response.json();

      // Validate data with Zod schema
      const validatedData = schema.parse(rawData);

      // Update state and cache
      updateState({
        data: validatedData,
        loading: false,
        error: null,
        lastFetched: new Date(),
      });

      setCachedData(validatedData);
      onSuccess?.(validatedData);

    } catch (error) {
      // Don't update state if request was aborted
      if (error instanceof Error && error.name === 'AbortError') {
        return;
      }

      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';

      // Retry logic
      if (retryAttempt < retryCount) {
        retryTimeoutRef.current = setTimeout(() => {
          fetchData(retryAttempt + 1);
        }, retryDelay * Math.pow(2, retryAttempt)); // Exponential backoff
        return;
      }

      // Final error state
      updateState({
        loading: false,
        error: errorMessage,
      });

      onError?.(error instanceof Error ? error : new Error(errorMessage));
    }
  }, [url, schema, getCachedData, setCachedData, updateState, onSuccess, onError, retryCount, retryDelay]);

  // Refetch function
  const refetch = useCallback(async () => {
    clearCache();
    await fetchData();
  }, [clearCache, fetchData]);

  // Effect for immediate fetch
  useEffect(() => {
    if (immediate) {
      fetchData();
    }

    // Cleanup function
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, [immediate, fetchData]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  return {
    ...state,
    refetch,
    clearCache,
    updateData,
    setData,
  };
}

/**
 * Hook for optimistic updates with rollback capability
 */
export function useOptimisticUpdate<T>(
  initialData: T | null,
  updateFn: (data: T, update: Partial<T>) => T
) {
  const [data, setData] = useState<T | null>(initialData);
  const [originalData, setOriginalData] = useState<T | null>(initialData);
  const [isUpdating, setIsUpdating] = useState(false);

  const optimisticUpdate = useCallback(async (
    update: Partial<T>,
    apiCall: () => Promise<void>
  ) => {
    if (!data) return;

    // Store original data for potential rollback
    setOriginalData(data);
    
    // Apply optimistic update
    const optimisticData = updateFn(data, update);
    setData(optimisticData);
    
    setIsUpdating(true);

    try {
      await apiCall();
      // Success - keep optimistic data
    } catch (error) {
      // Rollback on error
      setData(originalData);
      throw error;
    } finally {
      setIsUpdating(false);
    }
  }, [data, originalData, updateFn]);

  return {
    data,
    isUpdating,
    optimisticUpdate,
    setData,
  };
}

/**
 * Hook for infinite scrolling with pagination
 */
export function useInfiniteScroll<T>(
  fetchFn: (page: number) => Promise<{ data: T[]; hasMore: boolean }>,
  pageSize: number = 20
) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  const loadMore = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn(page);
      
      setData(prev => page === 1 ? result.data : [...prev, ...result.data]);
      setHasMore(result.hasMore);
      setPage(prev => prev + 1);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [fetchFn, page, loading, hasMore]);

  const reset = useCallback(() => {
    setData([]);
    setPage(1);
    setHasMore(true);
    setError(null);
  }, []);

  return {
    data,
    loading,
    error,
    hasMore,
    loadMore,
    reset,
  };
}





