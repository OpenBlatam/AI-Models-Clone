'use client';

import { useState } from 'react';

interface FormTemplate {
  id: string;
  name: string;
  description: string;
  data: Record<string, any>;
}

interface FormTemplateProps {
  templates: FormTemplate[];
  onSelect: (template: FormTemplate) => void;
}

export function FormTemplateSelector({ templates, onSelect }: FormTemplateProps) {
  const [isOpen, setIsOpen] = useState(false);

  if (templates.length === 0) return null;

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="px-3 py-1 text-sm bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
      >
        📋 Plantillas
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50">
            <div className="p-2">
              <h3 className="px-2 py-1 text-sm font-semibold text-gray-900 dark:text-white mb-1">
                Plantillas
              </h3>
              {templates.map((template) => (
                <button
                  key={template.id}
                  onClick={() => {
                    onSelect(template);
                    setIsOpen(false);
                  }}
                  className="w-full text-left px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-900 rounded text-sm transition-colors"
                >
                  <p className="font-medium text-gray-900 dark:text-white">
                    {template.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {template.description}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}














