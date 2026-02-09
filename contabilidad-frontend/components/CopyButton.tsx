'use client';

import { useState, useCallback, memo } from 'react';
import { logger } from '@/lib';

interface CopyButtonProps {
  text: string;
  label?: string;
  className?: string;
}

function CopyButtonComponent({ text, label = 'Copiar', className = '' }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      logger.error('Error copying to clipboard', err instanceof Error ? err : new Error(String(err)), {
        component: 'CopyButton',
        textLength: text.length,
      });
    }
  }, [text]);

  return (
    <button
      onClick={handleCopy}
      className={`px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors ${className}`}
      title={copied ? 'Copiado!' : 'Copiar al portapapeles'}
    >
      {copied ? '✓ Copiado' : `📋 ${label}`}
    </button>
  );
}

export const CopyButton = memo(CopyButtonComponent);




