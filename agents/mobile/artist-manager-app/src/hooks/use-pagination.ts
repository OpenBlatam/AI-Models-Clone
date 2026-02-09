import { useState, useCallback } from 'react';

interface PaginationState {
  page: number;
  pageSize: number;
  total: number;
}

interface UsePaginationOptions {
  initialPage?: number;
  initialPageSize?: number;
  total?: number;
}

/**
 * Hook for managing pagination state
 */
export function usePagination(options: UsePaginationOptions = {}) {
  const { initialPage = 1, initialPageSize = 10, total = 0 } = options;

  const [state, setState] = useState<PaginationState>({
    page: initialPage,
    pageSize: initialPageSize,
    total,
  });

  const setPage = useCallback((page: number) => {
    setState((prev) => ({ ...prev, page }));
  }, []);

  const setPageSize = useCallback((pageSize: number) => {
    setState((prev) => ({ ...prev, pageSize, page: 1 }));
  }, []);

  const setTotal = useCallback((total: number) => {
    setState((prev) => ({ ...prev, total }));
  }, []);

  const nextPage = useCallback(() => {
    setState((prev) => {
      const maxPage = Math.ceil(prev.total / prev.pageSize);
      return { ...prev, page: Math.min(prev.page + 1, maxPage) };
    });
  }, []);

  const previousPage = useCallback(() => {
    setState((prev) => ({
      ...prev,
      page: Math.max(prev.page - 1, 1),
    }));
  }, []);

  const goToFirstPage = useCallback(() => {
    setState((prev) => ({ ...prev, page: 1 }));
  }, []);

  const goToLastPage = useCallback(() => {
    setState((prev) => {
      const maxPage = Math.ceil(prev.total / prev.pageSize);
      return { ...prev, page: maxPage };
    });
  }, []);

  const totalPages = Math.ceil(state.total / state.pageSize);
  const hasNextPage = state.page < totalPages;
  const hasPreviousPage = state.page > 1;

  return {
    ...state,
    totalPages,
    hasNextPage,
    hasPreviousPage,
    setPage,
    setPageSize,
    setTotal,
    nextPage,
    previousPage,
    goToFirstPage,
    goToLastPage,
  };
}


