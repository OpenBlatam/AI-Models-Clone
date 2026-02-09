'use client';

import { ReactNode, memo } from 'react';

interface CardProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  actions?: ReactNode;
  className?: string;
  hover?: boolean;
}

function CardComponent({
  children,
  title,
  subtitle,
  actions,
  className = '',
  hover = false,
}: CardProps) {
  return (
    <div
      className={`bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 ${
        hover ? 'transition-transform hover:scale-105 hover:shadow-xl' : ''
      } ${className}`}
    >
      {(title || subtitle || actions) && (
        <div className="flex justify-between items-start mb-4">
          <div>
            {title && (
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                {title}
              </h3>
            )}
            {subtitle && (
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                {subtitle}
              </p>
            )}
          </div>
          {actions && <div>{actions}</div>}
        </div>
      )}
      {children}
    </div>
  );
}

export const Card = memo(CardComponent);
