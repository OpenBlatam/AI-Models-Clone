'use client';

import { TaskHistoryItem } from '@/lib/hooks/useTaskHistory';

type FilterStatus = 'all' | TaskHistoryItem['status'];

interface FilterBarProps {
  onFilterChange: (status: FilterStatus) => void;
  activeFilter: FilterStatus;
}

export function FilterBar({ onFilterChange, activeFilter }: FilterBarProps) {
  const filters: { value: FilterStatus; label: string; color: string }[] = [
    { value: 'all', label: 'Todas', color: 'bg-gray-500' },
    { value: 'completed', label: 'Completadas', color: 'bg-green-500' },
    { value: 'running', label: 'En Proceso', color: 'bg-blue-500' },
    { value: 'pending', label: 'Pendientes', color: 'bg-yellow-500' },
    { value: 'failed', label: 'Fallidas', color: 'bg-red-500' },
  ];

  return (
    <div className="flex flex-wrap gap-2">
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => onFilterChange(filter.value)}
          className={`px-3 py-1 rounded-full text-sm font-medium transition-all ${
            activeFilter === filter.value
              ? `${filter.color} text-white shadow-md`
              : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}














