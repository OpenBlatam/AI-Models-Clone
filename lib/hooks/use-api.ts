import { useState, useCallback } from 'react';
import type { ApiResponse, PaginationParams, PaginatedResponse } from '@/lib/utils/type-helpers';

interface UseApiOptions<T> {
  onSuccess?: (data: T) => void;
  onError?: (error: string) => void;
  initialData?: T;
}

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

export function useApi<T = unknown>(
  url: string,
  options: UseApiOptions<T> = {}
): [UseApiState<T>, (params?: RequestInit) => Promise<void>] {
  const [state, setState] = useState<UseApiState<T>>({
    data: options.initialData || null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async (params?: RequestInit) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
        },
        ...params,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ApiResponse<T> = await response.json();
      
      if (result.success) {
        setState({ data: result.data, loading: false, error: null });
        options.onSuccess?.(result.data);
      } else {
        throw new Error(result.error || 'Request failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      options.onError?.(errorMessage);
    }
  }, [url, options]);

  return [state, execute];
}

// Paginated API hook
export function usePaginatedApi<T>(
  baseUrl: string,
  options: UseApiOptions<PaginatedResponse<T>> = {}
) {
  const [state, setState] = useState<UseApiState<PaginatedResponse<T>>>({
    data: options.initialData || null,
    loading: false,
    error: null,
  });

  const fetchPage = useCallback(async (params: PaginationParams) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const searchParams = new URLSearchParams({
        page: params.page.toString(),
        limit: params.limit.toString(),
        ...(params.sortBy && { sortBy: params.sortBy }),
        ...(params.sortOrder && { sortOrder: params.sortOrder }),
      });

      const response = await fetch(`${baseUrl}?${searchParams}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: ApiResponse<PaginatedResponse<T>> = await response.json();
      
      if (result.success) {
        setState({ data: result.data, loading: false, error: null });
        options.onSuccess?.(result.data);
      } else {
        throw new Error(result.error || 'Request failed');
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      setState(prev => ({ ...prev, loading: false, error: errorMessage }));
      options.onError?.(errorMessage);
    }
  }, [baseUrl, options]);

  return [state, fetchPage];
} 