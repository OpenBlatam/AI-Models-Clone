'use client';

import { useState } from 'react';
import { TaskService } from '@/lib';
import { CalcularImpuestosRequest } from '@/types/api';
import { REGIMENES_FISCALES, TIPOS_IMPUESTO } from '@/lib/constants';
import { Tooltip } from '../Tooltip';

interface CalcularImpuestosFormProps {
  onTaskCreated: (taskId: string) => void;
  onCancel: () => void;
}

export function CalcularImpuestosForm({ onTaskCreated, onCancel }: CalcularImpuestosFormProps) {
  const [formData, setFormData] = useState<CalcularImpuestosRequest>({
    regimen: 'RESICO',
    tipo_impuesto: 'ISR',
    datos: {
      ingresos: '',
      gastos: '',
      periodo: new Date().toISOString().slice(0, 7),
    },
    priority: 0,
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});

  const validateForm = () => {
    const errors: Record<string, string> = {};
    
    const ingresos = parseFloat(formData.datos.ingresos as string);
    if (isNaN(ingresos) || ingresos < 0) {
      errors.ingresos = 'Ingresos debe ser un número positivo';
    }

    const gastos = parseFloat(formData.datos.gastos as string);
    if (isNaN(gastos) || gastos < 0) {
      errors.gastos = 'Gastos debe ser un número positivo';
    }

    if (gastos > ingresos) {
      errors.gastos = 'Los gastos no pueden ser mayores que los ingresos';
    }

    if (!formData.datos.periodo) {
      errors.periodo = 'El período es requerido';
    }

    setFieldErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setFieldErrors({});

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const request: CalcularImpuestosRequest = {
        ...formData,
        datos: {
          ingresos: parseFloat(formData.datos.ingresos as string),
          gastos: parseFloat(formData.datos.gastos as string),
          periodo: formData.datos.periodo || new Date().toISOString().slice(0, 7),
        },
      };

      const response = await TaskService.calcularImpuestos(request);
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
        Cálculo de Impuestos
      </h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Régimen Fiscal{' '}
            <Tooltip content="El régimen fiscal determina cómo se calculan tus impuestos">
              <span className="text-blue-500 cursor-help">ℹ️</span>
            </Tooltip>
          </label>
          <select
            value={formData.regimen}
            onChange={(e) => setFormData({ ...formData, regimen: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          >
            {REGIMENES_FISCALES.map((regimen) => (
              <option key={regimen} value={regimen}>
                {regimen}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Tipo de Impuesto{' '}
            <Tooltip content="ISR: Impuesto Sobre la Renta, IVA: Impuesto al Valor Agregado, IEPS: Impuesto Especial sobre Producción y Servicios">
              <span className="text-blue-500 cursor-help">ℹ️</span>
            </Tooltip>
          </label>
          <select
            value={formData.tipo_impuesto}
            onChange={(e) => setFormData({ ...formData, tipo_impuesto: e.target.value })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            required
          >
            {TIPOS_IMPUESTO.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Ingresos <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.datos.ingresos}
            onChange={(e) => {
              setFormData({
                ...formData,
                datos: { ...formData.datos, ingresos: e.target.value },
              });
              if (fieldErrors.ingresos) {
                setFieldErrors({ ...fieldErrors, ingresos: '' });
              }
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
              fieldErrors.ingresos
                ? 'border-red-500 dark:border-red-500'
                : 'border-gray-300 dark:border-gray-600'
            }`}
            required
            aria-invalid={!!fieldErrors.ingresos}
            aria-describedby={fieldErrors.ingresos ? 'ingresos-error' : undefined}
          />
          {fieldErrors.ingresos && (
            <p id="ingresos-error" className="mt-1 text-sm text-red-500">
              {fieldErrors.ingresos}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Gastos <span className="text-red-500">*</span>
          </label>
          <input
            type="number"
            step="0.01"
            min="0"
            value={formData.datos.gastos}
            onChange={(e) => {
              setFormData({
                ...formData,
                datos: { ...formData.datos, gastos: e.target.value },
              });
              if (fieldErrors.gastos) {
                setFieldErrors({ ...fieldErrors, gastos: '' });
              }
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
              fieldErrors.gastos
                ? 'border-red-500 dark:border-red-500'
                : 'border-gray-300 dark:border-gray-600'
            }`}
            required
            aria-invalid={!!fieldErrors.gastos}
            aria-describedby={fieldErrors.gastos ? 'gastos-error' : undefined}
          />
          {fieldErrors.gastos && (
            <p id="gastos-error" className="mt-1 text-sm text-red-500">
              {fieldErrors.gastos}
            </p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Período (YYYY-MM) <span className="text-red-500">*</span>
          </label>
          <input
            type="month"
            value={formData.datos.periodo}
            onChange={(e) => {
              setFormData({
                ...formData,
                datos: { ...formData.datos, periodo: e.target.value },
              });
              if (fieldErrors.periodo) {
                setFieldErrors({ ...fieldErrors, periodo: '' });
              }
            }}
            className={`w-full px-4 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white ${
              fieldErrors.periodo
                ? 'border-red-500 dark:border-red-500'
                : 'border-gray-300 dark:border-gray-600'
            }`}
            required
            aria-invalid={!!fieldErrors.periodo}
            aria-describedby={fieldErrors.periodo ? 'periodo-error' : undefined}
          />
          {fieldErrors.periodo && (
            <p id="periodo-error" className="mt-1 text-sm text-red-500">
              {fieldErrors.periodo}
            </p>
          )}
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
            className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-semibold py-2 px-4 rounded-lg transition-colors"
          >
            {isSubmitting ? 'Enviando...' : 'Calcular'}
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

