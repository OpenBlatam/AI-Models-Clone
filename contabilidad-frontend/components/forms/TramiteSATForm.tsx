'use client';

import { useState } from 'react';
import { TaskService } from '@/lib';
import { TramiteSATRequest } from '@/types/api';
import { TRAMITES_SAT_SUGGESTIONS } from '@/lib/constants';
import { AutoCompleteInput } from '../AutoCompleteInput';
import { Tooltip } from '../Tooltip';

interface TramiteSATFormProps {
  onTaskCreated: (taskId: string) => void;
  onCancel: () => void;
}

export function TramiteSATForm({ onTaskCreated, onCancel }: TramiteSATFormProps) {
  const [formData, setFormData] = useState<TramiteSATRequest>({
    tipo_tramite: '',
    detalles: {
      persona_fisica: true,
    },
    priority: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await TaskService.tramiteSAT(formData);
      onTaskCreated(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error al crear la tarea');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
        Trámites SAT
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo de Trámite{' '}
            <Tooltip content="Ejemplos: Alta en RFC, Cambio de Régimen Fiscal, Baja de Actividades">
              <span className="text-blue-500 cursor-help">ℹ️</span>
            </Tooltip>
          </label>
          <AutoCompleteInput
            value={formData.tipo_tramite}
            onChange={(value) => setFormData({ ...formData, tipo_tramite: value })}
            suggestions={TRAMITES_SAT_SUGGESTIONS}
            placeholder="Ej: Alta en RFC"
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          />
        </div>

        <div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={formData.detalles?.persona_fisica || false}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  detalles: { ...formData.detalles, persona_fisica: e.target.checked },
                })
              }
              className="rounded border-gray-300 dark:border-gray-600"
            />
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Persona Física
            </span>
          </label>
        </div>

        {error && (
          <div className="p-3 bg-red-100 dark:bg-red-900/20 border border-red-400 dark:border-red-600 rounded-lg">
            <p className="text-red-700 dark:text-red-400 text-sm">{error}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={isSubmitting}
            className="flex-1 bg-orange-600 hover:bg-orange-700 disabled:bg-orange-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {isSubmitting ? 'Enviando...' : 'Obtener Información'}
          </button>
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Cancelar
          </button>
        </div>
      </form>
    </div>
  );
}

