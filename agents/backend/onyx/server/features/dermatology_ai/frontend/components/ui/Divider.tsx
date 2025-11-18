'use client';

import React from 'react';
import { clsx } from 'clsx';

interface DividerProps {
  text?: string;
  orientation?: 'horizontal' | 'vertical';
  variant?: 'solid' | 'dashed' | 'dotted';
  className?: string;
}

export const Divider: React.FC<DividerProps> = ({
  text,
  orientation = 'horizontal',
  variant = 'solid',
  className,
}) => {
  const variantClasses = {
    solid: 'border-solid',
    dashed: 'border-dashed',
    dotted: 'border-dotted',
  };
  if (orientation === 'vertical') {
    return (
      <div
        className={clsx(
          'w-px bg-gray-200 dark:bg-gray-700 self-stretch',
          className
        )}
        role="separator"
      />
    );
  }

  if (text) {
    return (
      <div className={clsx('flex items-center my-4', className)}>
        <div
          className={clsx(
            'flex-1 border-t border-gray-200 dark:border-gray-700',
            variantClasses[variant]
          )}
        />
        <span className="px-4 text-sm text-gray-500 dark:text-gray-400">
          {text}
        </span>
        <div
          className={clsx(
            'flex-1 border-t border-gray-200 dark:border-gray-700',
            variantClasses[variant]
          )}
        />
      </div>
    );
  }

  return (
    <div
      className={clsx(
        'border-t border-gray-200 dark:border-gray-700 my-4',
        variantClasses[variant],
        className
      )}
      role="separator"
    />
  );
};

