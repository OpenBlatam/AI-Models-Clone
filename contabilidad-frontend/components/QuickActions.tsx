'use client';

import { useState } from 'react';

interface QuickAction {
  id: string;
  label: string;
  icon: string;
  action: () => void;
  shortcut?: string;
}

interface QuickActionsProps {
  actions: QuickAction[];
}

export function QuickActions({ actions }: QuickActionsProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="fixed bottom-4 left-4 z-40">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="bg-gray-800 dark:bg-gray-700 text-white rounded-full w-14 h-14 shadow-lg flex items-center justify-center transition-transform hover:scale-110"
        aria-label="Acciones rápidas"
        aria-expanded={isOpen}
      >
        <span className="text-xl">{isOpen ? '✕' : '⚡'}</span>
      </button>

      {isOpen && (
        <div className="absolute bottom-16 left-0 space-y-2 animate-slide-down">
          {actions.map((action) => (
            <button
              key={action.id}
              onClick={() => {
                action.action();
                setIsOpen(false);
              }}
              className="flex items-center gap-3 bg-white dark:bg-gray-800 text-gray-900 dark:text-white px-4 py-3 rounded-lg shadow-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors w-full text-left"
              title={action.shortcut ? `Atajo: ${action.shortcut}` : undefined}
            >
              <span className="text-xl">{action.icon}</span>
              <span className="font-medium">{action.label}</span>
              {action.shortcut && (
                <kbd className="ml-auto px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-xs font-mono">
                  {action.shortcut}
                </kbd>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

