import { useState, useMemo, useCallback } from 'react';

type FilterFn<T> = (item: T) => boolean;

interface UseFilterOptions<T> {
  data: T[];
  initialFilters?: FilterFn<T>[];
}

/**
 * Hook for filtering data with multiple filters
 */
export function useFilter<T>({ data, initialFilters = [] }: UseFilterOptions<T>) {
  const [filters, setFilters] = useState<FilterFn<T>[]>(initialFilters);

  const filteredData = useMemo(() => {
    if (filters.length === 0) {
      return data;
    }

    return data.filter((item) => filters.every((filter) => filter(item)));
  }, [data, filters]);

  const addFilter = useCallback((filter: FilterFn<T>) => {
    setFilters((prev) => [...prev, filter]);
  }, []);

  const removeFilter = useCallback((filter: FilterFn<T>) => {
    setFilters((prev) => prev.filter((f) => f !== filter));
  }, []);

  const clearFilters = useCallback(() => {
    setFilters([]);
  }, []);

  return {
    filteredData,
    filters,
    addFilter,
    removeFilter,
    clearFilters,
    hasFilters: filters.length > 0,
  };
}


