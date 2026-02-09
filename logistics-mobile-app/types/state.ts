// State Management Types

export interface AsyncState<T = unknown> {
  data: T | null;
  isLoading: boolean;
  error: Error | null;
  isSuccess: boolean;
  isError: boolean;
}

export interface PaginatedState<T> extends AsyncState<T[]> {
  page: number;
  limit: number;
  total: number;
  hasMore: boolean;
  isRefreshing: boolean;
  isLoadingMore: boolean;
}

export interface InfiniteScrollState<T> extends AsyncState<T[]> {
  pages: T[][];
  pageParams: unknown[];
  hasNextPage: boolean;
  isFetchingNextPage: boolean;
}

export interface CacheState<T> {
  data: T | null;
  timestamp: number;
  ttl: number;
  isStale: boolean;
}

export interface FormState<T extends Record<string, unknown>> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  touched: Partial<Record<keyof T, boolean>>;
  isValid: boolean;
  isDirty: boolean;
  isSubmitting: boolean;
}

export interface FilterState<T extends Record<string, unknown>> {
  filters: Partial<T>;
  activeFilters: (keyof T)[];
  hasActiveFilters: boolean;
}

export interface SortState<T> {
  field: keyof T | null;
  direction: 'asc' | 'desc';
}

export interface SearchState {
  query: string;
  results: unknown[];
  isSearching: boolean;
  hasResults: boolean;
}

export interface SelectionState<T> {
  selected: T[];
  isAllSelected: boolean;
  isIndeterminate: boolean;
}

export interface ToggleState {
  value: boolean;
  setTrue: () => void;
  setFalse: () => void;
  toggle: () => void;
}

export interface CounterState {
  count: number;
  increment: () => void;
  decrement: () => void;
  reset: () => void;
  setCount: (count: number) => void;
}

export interface LoadingState {
  isLoading: boolean;
  startLoading: () => void;
  stopLoading: () => void;
}

export interface ErrorState {
  error: Error | null;
  setError: (error: Error | null) => void;
  clearError: () => void;
  hasError: boolean;
}

