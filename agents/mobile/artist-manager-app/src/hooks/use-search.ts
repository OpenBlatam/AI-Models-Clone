import { useState, useMemo, useCallback } from 'react';
import { useDebounce } from './use-debounce';

interface UseSearchOptions<T> {
  data: T[];
  searchFn: (item: T, query: string) => boolean;
  debounceMs?: number;
}

/**
 * Hook for searching and filtering data
 */
export function useSearch<T>({ data, searchFn, debounceMs = 300 }: UseSearchOptions<T>) {
  const [searchQuery, setSearchQuery] = useState('');
  const debouncedQuery = useDebounce(searchQuery, debounceMs);

  const filteredData = useMemo(() => {
    if (!debouncedQuery.trim()) {
      return data;
    }

    return data.filter((item) => searchFn(item, debouncedQuery));
  }, [data, debouncedQuery, searchFn]);

  const clearSearch = useCallback(() => {
    setSearchQuery('');
  }, []);

  return {
    searchQuery,
    setSearchQuery,
    debouncedQuery,
    filteredData,
    clearSearch,
    resultsCount: filteredData.length,
  };
}


