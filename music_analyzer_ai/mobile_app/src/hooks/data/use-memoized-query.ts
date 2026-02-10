import { useMemo } from 'react';
import { useQuery, UseQueryOptions, UseQueryResult } from '@tanstack/react-query';

export function useMemoizedQuery<TData, TError = Error>(
  queryKey: unknown[],
  queryFn: () => Promise<TData>,
  options?: Omit<UseQueryOptions<TData, TError>, 'queryKey' | 'queryFn'>
): UseQueryResult<TData, TError> {
  const memoizedQueryKey = useMemo(() => queryKey, [JSON.stringify(queryKey)]);

  return useQuery<TData, TError>({
    queryKey: memoizedQueryKey,
    queryFn,
    ...options,
  });
}


