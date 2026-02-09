'use client';

import { useState } from 'react';
import { TaskService } from '@/lib/services/taskService';
import { AsesoriaFiscalRequest } from '@/types/api';
import { REGIMENES_FISCALES } from '@/lib/constants';

interface AsesoriaFiscalFormProps {
  onTaskCreated: (taskId: string) => void;
  onCancel: () => void;
}

export function AsesoriaFiscalForm({ onTaskCreated, onCancel }: AsesoriaFiscalFormProps) {
  const [formData, setFormData] = useState<AsesoriaFiscalRequest>({
    pregunta: '',
    contexto: {
      regimen: '',
      ingresos_anuales: '',
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
      const request: AsesoriaFiscalRequest = {
        pregunta: formData.pregunta,
        contexto: formData.contexto?.regimen
          ? {
              regimen: formData.contexto.regimen,
              ingresos_anuales: formData.contexto.ingresos_anuales
                ? parseFloat(formData.contexto.ingresos_anuales as string)
                : undefined,
            }
          : undefined,
        priority: formData.priority,
      };

      const response = await TaskService.asesoriaFiscal(request);
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
        Asesoría Fiscal
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Pregunta
          </label>
          <textarea
            value={formData.pregunta}
            onChange={(e) => setFormData({ ...formData, pregunta: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            rows={4}
            placeholder="Ej: ¿Puedo deducir gastos de home office?"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Régimen Fiscal (opcional)
          </label>
          <select
            value={formData.contexto?.regimen || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                contexto: { ...formData.contexto, regimen: e.target.value },
              })
            }
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value="">Seleccionar...</option>
            {REGIMENES_FISCALES.map((regimen) => (
              <option key={regimen} value={regimen}>
                {regimen}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Ingresos Anuales (opcional)
          </label>
          <input
            type="number"
            step="0.01"
            value={formData.contexto?.ingresos_anuales || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                contexto: { ...formData.contexto, ingresos_anuales: e.target.value },
              })
            }
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="Ej: 500000"
          />
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
            className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {isSubmitting ? 'Enviando...' : 'Obtener Asesoría'}
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



