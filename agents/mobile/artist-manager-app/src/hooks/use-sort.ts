import { useState, useMemo, useCallback } from 'react';

type SortDirection = 'asc' | 'desc';

interface SortConfig<T> {
  key: keyof T;
  direction: SortDirection;
}

interface UseSortOptions<T> {
  data: T[];
  initialSort?: SortConfig<T>;
}

/**
 * Hook for sorting data
 */
export function useSort<T>({ data, initialSort }: UseSortOptions<T>) {
  const [sortConfig, setSortConfig] = useState<SortConfig<T> | null>(initialSort || null);

  const sortedData = useMemo(() => {
    if (!sortConfig) {
      return data;
    }

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key];
      const bValue = b[sortConfig.key];

      if (aValue === bValue) {
        return 0;
      }

      const comparison = aValue > bValue ? 1 : -1;
      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }, [data, sortConfig]);

  const sortBy = useCallback((key: keyof T, direction: SortDirection = 'asc') => {
    setSortConfig({ key, direction });
  }, []);

  const toggleSort = useCallback((key: keyof T) => {
    setSortConfig((prev) => {
      if (prev?.key === key) {
        return {
          key,
          direction: prev.direction === 'asc' ? 'desc' : 'asc',
        };
      }
      return { key, direction: 'asc' };
    });
  }, []);

  const clearSort = useCallback(() => {
    setSortConfig(null);
  }, []);

  return {
    sortedData,
    sortConfig,
    sortBy,
    toggleSort,
    clearSort,
  };
}


