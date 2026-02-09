'use client';

import { useState } from 'react';

interface HelpDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpDialog({ isOpen, onClose }: HelpDialogProps) {
  if (!isOpen) return null;

  const faqs = [
    {
      question: '¿Cómo calculo mis impuestos?',
      answer: 'Selecciona "Cálculo de Impuestos", completa el formulario con tu régimen fiscal, tipo de impuesto, ingresos, gastos y período. El sistema calculará automáticamente tus obligaciones fiscales.',
    },
    {
      question: '¿Qué regímenes fiscales están disponibles?',
      answer: 'El sistema soporta RESICO, General y Simplificado. Selecciona el régimen que corresponde a tu situación fiscal.',
    },
    {
      question: '¿Cómo veo el historial de mis tareas?',
      answer: 'Haz clic en "Mostrar Historial" en la parte superior. Puedes buscar y filtrar tus tareas anteriores. Usa Ctrl+H como atajo de teclado.',
    },
    {
      question: '¿Puedo exportar los resultados?',
      answer: 'Sí, cuando una tarea esté completada, verás un botón "Exportar" que te permite descargar los resultados en formato JSON, Texto o HTML/PDF.',
    },
    {
      question: '¿Cómo cambio entre modo claro y oscuro?',
      answer: 'Haz clic en el botón de sol/luna en la parte superior derecha. Tu preferencia se guardará automáticamente.',
    },
    {
      question: '¿Qué hago si una tarea falla?',
      answer: 'Si una tarea falla, verás un mensaje de error. Puedes intentar crear la tarea nuevamente o verificar la conexión con el backend usando el indicador de salud.',
    },
  ];

  const shortcuts = [
    { key: 'Ctrl + H', description: 'Mostrar/Ocultar historial' },
    { key: 'Escape', description: 'Cerrar/Limpiar selección' },
  ];

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Ayuda y Preguntas Frecuentes
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <div className="p-6 space-y-6">
          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Preguntas Frecuentes
            </h3>
            <div className="space-y-4">
              {faqs.map((faq, index) => (
                <div
                  key={index}
                  className="border border-gray-200 dark:border-gray-700 rounded-lg p-4"
                >
                  <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                    {faq.question}
                  </h4>
                  <p className="text-gray-600 dark:text-gray-300 text-sm">
                    {faq.answer}
                  </p>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Atajos de Teclado
            </h3>
            <div className="space-y-2">
              {shortcuts.map((shortcut, index) => (
                <div
                  key={index}
                  className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                >
                  <span className="text-gray-700 dark:text-gray-300">
                    {shortcut.description}
                  </span>
                  <kbd className="px-3 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm font-mono text-gray-900 dark:text-white">
                    {shortcut.key}
                  </kbd>
                </div>
              ))}
            </div>
          </section>

          <section>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Servicios Disponibles
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  💰 Cálculo de Impuestos
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Calcula ISR, IVA, IEPS según tu régimen fiscal
                </p>
              </div>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  💡 Asesoría Fiscal
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Obtén respuestas personalizadas a tus preguntas fiscales
                </p>
              </div>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  📚 Guía Fiscal
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Guías detalladas paso a paso sobre temas fiscales
                </p>
              </div>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  🏛️ Trámites SAT
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Información sobre trámites del SAT
                </p>
              </div>
              <div className="p-4 border border-gray-200 dark:border-gray-700 rounded-lg md:col-span-2">
                <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
                  📋 Ayuda con Declaraciones
                </h4>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Asistencia para preparar y presentar declaraciones fiscales
                </p>
              </div>
            </div>
          </section>
        </div>

        <div className="sticky bottom-0 bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-700 p-4 flex justify-end">
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














