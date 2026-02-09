'use client';

import { ReactNode } from 'react';
import { Tooltip } from './Tooltip';

interface FormFieldProps {
  label: string;
  error?: string;
  hint?: string;
  required?: boolean;
  children: ReactNode;
  className?: string;
}

export function FormField({
  label,
  error,
  hint,
  required = false,
  children,
  className = '',
}: FormFieldProps) {
  return (
    <div className={className}>
      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
        {hint && (
          <Tooltip content={hint}>
            <span className="text-blue-500 cursor-help ml-1">ℹ️</span>
          </Tooltip>
        )}
      </label>
      {children}
      {error && (
        <p className="mt-1 text-sm text-red-500" role="alert">
          {error}
        </p>
      )}
    </div>
  );
}














