'use client';

import React from 'react';
import { clsx } from 'clsx';
import { Spinner } from './Spinner';

interface LoadingOverlayProps {
  isLoading: boolean;
  message?: string;
  fullScreen?: boolean;
  className?: string;
}

export const LoadingOverlay: React.FC<LoadingOverlayProps> = ({
  isLoading,
  message,
  fullScreen = false,
  className,
}) => {
  if (!isLoading) return null;

  return (
    <div
      className={clsx(
        'absolute inset-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-sm z-50 flex items-center justify-center',
        fullScreen && 'fixed',
        className
      )}
    >
      <div className="flex flex-col items-center space-y-4">
        <Spinner size="lg" />
        {message && (
          <p className="text-gray-700 dark:text-gray-300 font-medium">
            {message}
          </p>
        )}
      </div>
    </div>
  );
};


