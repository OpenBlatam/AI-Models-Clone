'use client';

import { useState, useEffect } from 'react';
import { TaskResult, TaskStatus } from '@/types/api';
import { CopyButton } from './CopyButton';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  task: { status: TaskStatus; result: TaskResult } | null;
}

export function ShareModal({ isOpen, onClose, task }: ShareModalProps) {
  const [shareUrl, setShareUrl] = useState('');

  useEffect(() => {
    if (task && isOpen) {
      // En producción, esto generaría una URL compartible
      const url = `${window.location.origin}/task/${task.status.id}`;
      setShareUrl(url);
    }
  }, [task, isOpen]);

  if (!isOpen || !task) return null;

  const shareText = `Resultado de ${task.status.service_type.replace('_', ' ')}:\n\n${task.result.resultado}`;

  const shareOptions = [
    {
      name: 'Copiar URL',
      icon: '🔗',
      action: () => {
        navigator.clipboard.writeText(shareUrl);
      },
    },
    {
      name: 'Copiar Texto',
      icon: '📋',
      action: () => {
        navigator.clipboard.writeText(shareText);
      },
    },
    {
      name: 'Compartir en Twitter',
      icon: '🐦',
      action: () => {
        const url = `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}`;
        window.open(url, '_blank');
      },
    },
    {
      name: 'Compartir en LinkedIn',
      icon: '💼',
      action: () => {
        const url = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(shareUrl)}`;
        window.open(url, '_blank');
      },
    },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-md w-full">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              Compartir Resultado
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              aria-label="Cerrar"
            >
              ×
            </button>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                URL Compartible
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={shareUrl}
                  readOnly
                  className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-white"
                />
                <CopyButton text={shareUrl} />
              </div>
            </div>

            <div>
              <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                Compartir en
              </h3>
              <div className="grid grid-cols-2 gap-2">
                {shareOptions.map((option) => (
                  <button
                    key={option.name}
                    onClick={option.action}
                    className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <span>{option.icon}</span>
                    <span className="text-sm text-gray-700 dark:text-gray-300">
                      {option.name}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  );
}

