'use client';

import { useMemo, memo } from 'react';
import { TaskResult } from '@/types/api';
import { formatDateTime } from '@/lib';

interface ResultViewerProps {
  result: TaskResult;
}

function ResultViewerComponent({ result }: ResultViewerProps) {
  // Función para formatear el texto con mejor legibilidad
  const formattedResult = useMemo(() => {
    const text = result.resultado;
    // Dividir por líneas y procesar
    const lines = text.split('\n');
    const formatted: JSX.Element[] = [];

    lines.forEach((line, index) => {
      // Detectar títulos (líneas que terminan con :)
      if (line.trim().endsWith(':') && line.length < 50) {
        formatted.push(
          <h4 key={index} className="font-bold text-lg mt-4 mb-2 text-gray-900 dark:text-white">
            {line.trim()}
          </h4>
        );
      }
      // Detectar listas (líneas que empiezan con -, *, o números)
      else if (/^[\s]*[-*•]\s/.test(line) || /^[\s]*\d+[\.\)]\s/.test(line)) {
        formatted.push(
          <li key={index} className="ml-4 mb-1 text-gray-700 dark:text-gray-300">
            {line.trim().replace(/^[\s]*[-*•\d+\.\)]\s*/, '')}
          </li>
        );
      }
      // Detectar código o valores numéricos importantes
      else if (/^\$[\d,]+\.?\d*/.test(line.trim()) || /[\d,]+\.?\d*%/.test(line.trim())) {
        formatted.push(
          <p key={index} className="font-mono text-blue-600 dark:text-blue-400 font-semibold my-2">
            {line}
          </p>
        );
      }
      // Párrafos normales
      else if (line.trim()) {
        formatted.push(
          <p key={index} className="mb-2 text-gray-700 dark:text-gray-300 leading-relaxed">
            {line}
          </p>
        );
      }
      // Líneas vacías
      else {
        formatted.push(<br key={index} />);
      }
    });

    return formatted;
  }, [result.resultado]);

  return (
    <div className="space-y-4">
      <div className="prose dark:prose-invert max-w-none">
        <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6 border border-gray-200 dark:border-gray-700">
          <div className="space-y-2">
            {formattedResult}
          </div>
        </div>
      </div>
      
      {(result.tokens_used || result.model) && (
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex flex-wrap gap-4 text-xs text-gray-500 dark:text-gray-400">
            {result.tokens_used && (
              <div className="flex items-center gap-1">
                <span className="font-semibold">Tokens:</span>
                <span>{result.tokens_used.toLocaleString()}</span>
              </div>
            )}
            {result.model && (
              <div className="flex items-center gap-1">
                <span className="font-semibold">Modelo:</span>
                <span className="font-mono">{result.model}</span>
              </div>
            )}
            {result.tiempo_calculo && (
              <div className="flex items-center gap-1">
                <span className="font-semibold">Tiempo:</span>
                <span>{formatDateTime(new Date(result.tiempo_calculo))}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export const ResultViewer = memo(ResultViewerComponent);





