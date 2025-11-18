'use client';

import React from 'react';
import { Filter, X } from 'lucide-react';
import { Button } from './Button';
import { clsx } from 'clsx';

export interface FilterOption {
  label: string;
  value: string;
}

interface FilterBarProps {
  filters: {
    label: string;
    options: FilterOption[];
    value: string;
    onChange: (value: string) => void;
  }[];
  onClearAll?: () => void;
  className?: string;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  filters,
  onClearAll,
  className,
}) => {
  const hasActiveFilters = filters.some((f) => f.value !== '');

  return (
    <div
      className={clsx(
        'flex flex-wrap items-center gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700',
        className
      )}
    >
      <div className="flex items-center space-x-2 text-gray-700 dark:text-gray-300">
        <Filter className="h-4 w-4" />
        <span className="text-sm font-medium">Filtros:</span>
      </div>

      {filters.map((filter, index) => (
        <div key={index} className="flex items-center space-x-2">
          <label className="text-sm text-gray-600 dark:text-gray-400">
            {filter.label}:
          </label>
          <select
            value={filter.value}
            onChange={(e) => filter.onChange(e.target.value)}
            className="px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-700 rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">Todos</option>
            {filter.options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      ))}

      {hasActiveFilters && onClearAll && (
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearAll}
          className="ml-auto"
        >
          <X className="h-4 w-4 mr-1" />
          Limpiar Filtros
        </Button>
      )}
    </div>
  );
};

