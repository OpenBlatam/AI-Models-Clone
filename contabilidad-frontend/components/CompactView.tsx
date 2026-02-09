'use client';

import { useState } from 'react';

interface CompactViewProps {
  children: React.ReactNode;
  defaultCompact?: boolean;
}

export function CompactView({ children, defaultCompact = false }: CompactViewProps) {
  const [isCompact, setIsCompact] = useState(defaultCompact);

  return (
    <div>
      <div className="flex justify-end mb-2">
        <button
          onClick={() => setIsCompact(!isCompact)}
          className="text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          aria-label={isCompact ? 'Expandir' : 'Compactar'}
        >
          {isCompact ? '⬇️ Expandir' : '⬆️ Compactar'}
        </button>
      </div>
      <div className={isCompact ? 'space-y-1' : 'space-y-4'}>
        {children}
      </div>
    </div>
  );
}














