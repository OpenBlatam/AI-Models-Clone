'use client';

import React, { useState, useCallback } from 'react';
import { Search, X } from 'lucide-react';
import { clsx } from 'clsx';

interface SearchBarProps {
  placeholder?: string;
  onSearch: (query: string) => void;
  onClear?: () => void;
  className?: string;
  debounceMs?: number;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  placeholder = 'Buscar...',
  onSearch,
  onClear,
  className,
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState('');
  const [debounceTimer, setDebounceTimer] = useState<NodeJS.Timeout | null>(null);

  const handleChange = useCallback(
    (value: string) => {
      setQuery(value);

      if (debounceTimer) {
        clearTimeout(debounceTimer);
      }

      const timer = setTimeout(() => {
        onSearch(value);
      }, debounceMs);

      setDebounceTimer(timer);
    },
    [onSearch, debounceMs, debounceTimer]
  );

  const handleClear = () => {
    setQuery('');
    if (debounceTimer) {
      clearTimeout(debounceTimer);
    }
    onSearch('');
    if (onClear) {
      onClear();
    }
  };

  return (
    <div className={clsx('relative', className)}>
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Search className="h-5 w-5 text-gray-400" />
      </div>
      <input
        type="text"
        value={query}
        onChange={(e) => handleChange(e.target.value)}
        placeholder={placeholder}
        className="block w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
      />
      {query && (
        <button
          onClick={handleClear}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          aria-label="Limpiar búsqueda"
        >
          <X className="h-5 w-5" />
        </button>
      )}
    </div>
  );
};

