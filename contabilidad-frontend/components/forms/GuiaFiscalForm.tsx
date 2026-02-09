'use client';

import { useState } from 'react';
import { TaskService } from '@/lib';
import { GuiaFiscalRequest } from '@/types/api';
import { GUIAS_FISCALES_SUGGESTIONS, NIVELES_DETALLE } from '@/lib/constants';
import { AutoCompleteInput } from '../AutoCompleteInput';
import { Tooltip } from '../Tooltip';

interface GuiaFiscalFormProps {
  onTaskCreated: (taskId: string) => void;
  onCancel: () => void;
}

export function GuiaFiscalForm({ onTaskCreated, onCancel }: GuiaFiscalFormProps) {
  const [formData, setFormData] = useState<GuiaFiscalRequest>({
    tema: '',
    nivel_detalle: 'completo',
    priority: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await TaskService.guiaFiscal(formData);
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
        Guía Fiscal
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tema{' '}
            <Tooltip content="Temas comunes: Deducciones, Obligaciones, Declaraciones, etc.">
              <span className="text-blue-500 cursor-help">ℹ️</span>
            </Tooltip>
          </label>
          <AutoCompleteInput
            value={formData.tema}
            onChange={(value) => setFormData({ ...formData, tema: value })}
            suggestions={GUIAS_FISCALES_SUGGESTIONS}
            placeholder="Ej: Deducciones RESICO"
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Nivel de Detalle
          </label>
          <select
            value={formData.nivel_detalle}
            onChange={(e) => setFormData({ ...formData, nivel_detalle: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            {NIVELES_DETALLE.map((nivel) => (
              <option key={nivel} value={nivel}>
                {nivel.charAt(0).toUpperCase() + nivel.slice(1)}
              </option>
            ))}
          </select>
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
            className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {isSubmitting ? 'Enviando...' : 'Obtener Guía'}
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

