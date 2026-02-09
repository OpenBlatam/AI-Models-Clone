'use client';

interface KeyboardShortcut {
  keys: string[];
  description: string;
  category: string;
}

interface KeyboardShortcutsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: KeyboardShortcutsModalProps) {
  if (!isOpen) return null;

  const shortcuts: KeyboardShortcut[] = [
    {
      keys: ['Ctrl', 'H'],
      description: 'Mostrar/Ocultar historial',
      category: 'Navegación',
    },
    {
      keys: ['Escape'],
      description: 'Cerrar/Limpiar selección',
      category: 'Navegación',
    },
    {
      keys: ['Ctrl', 'K'],
      description: 'Abrir búsqueda rápida',
      category: 'Búsqueda',
    },
    {
      keys: ['Ctrl', '/'],
      description: 'Mostrar atajos de teclado',
      category: 'Ayuda',
    },
  ];

  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = [];
    }
    acc[shortcut.category].push(shortcut);
    return acc;
  }, {} as Record<string, KeyboardShortcut[]>);

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 p-6 flex justify-between items-center">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Atajos de Teclado
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 text-2xl"
            aria-label="Cerrar"
          >
            ×
          </button>
        </div>

        <div className="p-6">
          {Object.entries(groupedShortcuts).map(([category, items]) => (
            <div key={category} className="mb-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-3">
                {category}
              </h3>
              <div className="space-y-2">
                {items.map((shortcut, index) => (
                  <div
                    key={index}
                    className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-900 rounded-lg"
                  >
                    <span className="text-gray-700 dark:text-gray-300">
                      {shortcut.description}
                    </span>
                    <div className="flex gap-1">
                      {shortcut.keys.map((key, keyIndex) => (
                        <kbd
                          key={keyIndex}
                          className="px-2 py-1 bg-gray-200 dark:bg-gray-700 rounded text-sm font-mono text-gray-900 dark:text-white"
                        >
                          {key}
                        </kbd>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
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














