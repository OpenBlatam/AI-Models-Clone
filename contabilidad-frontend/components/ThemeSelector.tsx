'use client';

import { useDarkMode } from '@/lib/hooks/useDarkMode';

export function ThemeSelector() {
  const { isDark, toggleDarkMode } = useDarkMode();

  return (
    <div className="flex items-center gap-2">
      <span className="text-sm text-gray-600 dark:text-gray-400">☀️</span>
      <button
        onClick={toggleDarkMode}
        className={`relative w-12 h-6 rounded-full transition-colors ${
          isDark ? 'bg-blue-600' : 'bg-gray-300'
        }`}
        aria-label={isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      >
        <span
          className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
            isDark ? 'translate-x-6' : 'translate-x-0'
          }`}
        ></span>
      </button>
      <span className="text-sm text-gray-600 dark:text-gray-400">🌙</span>
    </div>
  );
}














