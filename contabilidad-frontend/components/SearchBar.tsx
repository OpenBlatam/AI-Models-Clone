'use client';

import { useState, useEffect, useCallback, useMemo, memo } from 'react';
import { debounce, DEBOUNCE_DELAY } from '@/lib';

interface SearchBarProps {
  onSearch: (query: string) => void;
  placeholder?: string;
  debounceMs?: number;
}

function SearchBarComponent({
  onSearch,
  placeholder = 'Buscar...',
  debounceMs = DEBOUNCE_DELAY,
}: SearchBarProps) {
  const [query, setQuery] = useState('');

  const debouncedSearch = useMemo(
    () => debounce(onSearch, debounceMs),
    [onSearch, debounceMs]
  );

  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    debouncedSearch(value);
  }, [debouncedSearch]);

  const handleClear = useCallback(() => {
    setQuery('');
    onSearch('');
  }, [onSearch]);

  useEffect(() => {
    return () => {
      // Cleanup debounce on unmount
      debouncedSearch.cancel?.();
    };
  }, [debouncedSearch]);

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        onChange={handleChange}
        placeholder={placeholder}
        className="w-full px-4 py-2 pl-10 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400"
      />
      <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 dark:text-gray-500">
        🔍
      </div>
      {query && (
        <button
          onClick={handleClear}
          className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="Limpiar búsqueda"
        >
          ×
        </button>
      )}
    </div>
  );
}

export const SearchBar = memo(SearchBarComponent);

