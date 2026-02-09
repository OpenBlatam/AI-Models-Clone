'use client';

import { useState, useEffect, useRef, useMemo, useCallback, memo } from 'react';
import { useTaskHistory } from '@/lib';

interface QuickSearchProps {
  onSelect: (taskId: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

function QuickSearchComponent({ onSelect, isOpen, onClose }: QuickSearchProps) {
  const [query, setQuery] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const { history } = useTaskHistory();

  const filteredTasks = useMemo(
    () =>
      history
        .filter(
          (task) =>
            task.title.toLowerCase().includes(query.toLowerCase()) ||
            task.serviceType.toLowerCase().includes(query.toLowerCase()) ||
            task.taskId.toLowerCase().includes(query.toLowerCase())
        )
        .slice(0, 10),
    [history, query]
  );

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) {
      setQuery('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.min(prev + 1, filteredTasks.length - 1));
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => Math.max(prev - 1, 0));
      } else if (e.key === 'Enter' && filteredTasks[selectedIndex]) {
        e.preventDefault();
        onSelect(filteredTasks[selectedIndex].taskId);
        onClose();
      } else if (e.key === 'Escape') {
        onClose();
      }
    },
    [filteredTasks, selectedIndex, onSelect, onClose]
  );

  const handleQueryChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setSelectedIndex(0);
  }, []);

  const handleTaskSelect = useCallback(
    (taskId: string) => {
      onSelect(taskId);
      onClose();
    },
    [onSelect, onClose]
  );

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-start justify-center pt-20 z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-full max-w-2xl">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleQueryChange}
            onKeyDown={handleKeyDown}
            placeholder="Buscar tareas... (↑↓ para navegar, Enter para seleccionar, Esc para cerrar)"
            className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        {filteredTasks.length > 0 && (
          <div className="max-h-96 overflow-y-auto">
            {filteredTasks.map((task, index) => (
              <button
                key={task.taskId}
                onClick={() => handleTaskSelect(task.taskId)}
                className={`w-full text-left px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-900 transition-colors ${
                  index === selectedIndex
                    ? 'bg-blue-50 dark:bg-blue-900/20 border-l-4 border-blue-500'
                    : 'border-l-4 border-transparent'
                }`}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-semibold text-gray-900 dark:text-white">
                      {task.title}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {task.serviceType.replace('_', ' ')} • {task.status}
                    </p>
                  </div>
                  <span className="text-xs text-gray-400 dark:text-gray-500">
                    {task.taskId.substring(0, 8)}...
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
        {query && filteredTasks.length === 0 && (
          <div className="p-8 text-center text-gray-500 dark:text-gray-400">
            No se encontraron tareas
          </div>
        )}
      </div>
    </div>
  );
}

export const QuickSearch = memo(QuickSearchComponent);





