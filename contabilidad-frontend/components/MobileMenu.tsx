'use client';

import { useState } from 'react';

interface MobileMenuProps {
  children: React.ReactNode;
  trigger: React.ReactNode;
}

export function MobileMenu({ children, trigger }: MobileMenuProps) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden"
        aria-label="Menú"
        aria-expanded={isOpen}
      >
        {trigger}
      </button>
      {isOpen && (
        <>
          <div
            className="fixed inset-0 bg-black bg-opacity-50 z-40 md:hidden"
            onClick={() => setIsOpen(false)}
          />
          <div className="fixed top-0 right-0 h-full w-64 bg-white dark:bg-gray-800 shadow-xl z-50 md:hidden transform transition-transform">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
              <h2 className="font-bold text-gray-900 dark:text-white">Menú</h2>
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
                aria-label="Cerrar menú"
              >
                ×
              </button>
            </div>
            <div className="p-4 overflow-y-auto h-full">{children}</div>
          </div>
        </>
      )}
    </>
  );
}














