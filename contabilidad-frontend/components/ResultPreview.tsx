'use client';

import { TaskResult } from '@/types/api';
import { CopyButton } from './CopyButton';

interface ResultPreviewProps {
  result: TaskResult;
  onFullView?: () => void;
  maxLength?: number;
}

export function ResultPreview({ result, onFullView, maxLength = 200 }: ResultPreviewProps) {
  const preview = result.resultado.length > maxLength
    ? result.resultado.substring(0, maxLength) + '...'
    : result.resultado;

  return (
    <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-4 border border-gray-200 dark:border-gray-700">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-gray-900 dark:text-white text-sm">Vista Previa</h4>
        <div className="flex gap-2">
          <CopyButton text={result.resultado} label="Copiar" />
          {onFullView && result.resultado.length > maxLength && (
            <button
              onClick={onFullView}
              className="px-2 py-1 text-xs bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded hover:bg-blue-200 dark:hover:bg-blue-800"
            >
              Ver completo
            </button>
          )}
        </div>
      </div>
      <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap line-clamp-3">
        {preview}
      </p>
      {result.tokens_used && (
        <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 text-xs text-gray-500 dark:text-gray-400">
          Tokens: {result.tokens_used.toLocaleString()}
        </div>
      )}
    </div>
  );
}














