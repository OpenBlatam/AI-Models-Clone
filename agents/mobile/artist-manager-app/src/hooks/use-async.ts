import { useState, useCallback, useEffect, useRef } from 'react';

interface AsyncState<T> {
  data: T | null;
  error: Error | null;
  isLoading: boolean;
}

interface UseAsyncOptions {
  immediate?: boolean;
  onSuccess?: (data: unknown) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook for handling async operations with loading and error states
 */
export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  options: UseAsyncOptions = {}
) {
  const { immediate = false, onSuccess, onError } = options;
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    error: null,
    isLoading: false,
  });
  const isMountedRef = useRef(true);

  useEffect(() => {
    isMountedRef.current = true;
    return () => {
      isMountedRef.current = false;
    };
  }, []);

  const execute = useCallback(async () => {
    setState({ data: null, error: null, isLoading: true });

    try {
      const data = await asyncFunction();
      if (isMountedRef.current) {
        setState({ data, error: null, isLoading: false });
        onSuccess?.(data);
      }
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Unknown error');
      if (isMountedRef.current) {
        setState({ data: null, error: err, isLoading: false });
        onError?.(err);
      }
      throw err;
    }
  }, [asyncFunction, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
    reset: useCallback(() => {
      setState({ data: null, error: null, isLoading: false });
    }, []),
  };
}


