'use client';

import { useState } from 'react';
import { TaskService } from '@/lib';
import { AyudaDeclaracionRequest } from '@/types/api';
import { TIPOS_DECLARACION } from '@/lib/constants';

interface AyudaDeclaracionFormProps {
  onTaskCreated: (taskId: string) => void;
  onCancel: () => void;
}

export function AyudaDeclaracionForm({ onTaskCreated, onCancel }: AyudaDeclaracionFormProps) {
  const [formData, setFormData] = useState<AyudaDeclaracionRequest>({
    tipo_declaracion: 'mensual',
    periodo: '',
    datos: {
      rfc: '',
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
      const response = await TaskService.ayudaDeclaracion(formData);
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
        Ayuda con Declaraciones
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo de Declaración
          </label>
          <select
            value={formData.tipo_declaracion}
            onChange={(e) => setFormData({ ...formData, tipo_declaracion: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          >
            {TIPOS_DECLARACION.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo.charAt(0).toUpperCase() + tipo.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Período (YYYY-MM)
          </label>
          <input
            type="month"
            value={formData.periodo}
            onChange={(e) => setFormData({ ...formData, periodo: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            RFC (opcional)
          </label>
          <input
            type="text"
            value={formData.datos?.rfc || ''}
            onChange={(e) =>
              setFormData({
                ...formData,
                datos: { ...formData.datos, rfc: e.target.value },
              })
            }
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            placeholder="ABC123456789"
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
            className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-red-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {isSubmitting ? 'Enviando...' : 'Obtener Ayuda'}
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



