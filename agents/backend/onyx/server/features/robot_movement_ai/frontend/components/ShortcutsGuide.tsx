'use client';

import { useState } from 'react';
import { Keyboard, Search } from 'lucide-react';

interface Shortcut {
  category: string;
  shortcuts: Array<{ keys: string[]; description: string }>;
}

export default function ShortcutsGuide() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  const shortcuts: Shortcut[] = [
    {
      category: 'Navegación',
      shortcuts: [
        { keys: ['Ctrl', 'K'], description: 'Búsqueda global' },
        { keys: ['Ctrl', '1'], description: 'Ir a Control' },
        { keys: ['Ctrl', '2'], description: 'Ir a Chat' },
        { keys: ['Ctrl', '3'], description: 'Ir a 3D View' },
        { keys: ['Esc'], description: 'Cerrar modales' },
      ],
    },
    {
      category: 'Control del Robot',
      shortcuts: [
        { keys: ['Space'], description: 'Detener robot' },
        { keys: ['H'], description: 'Ir a Home' },
        { keys: ['Arrow Up'], description: 'Mover adelante' },
        { keys: ['Arrow Down'], description: 'Mover atrás' },
        { keys: ['Arrow Left'], description: 'Mover izquierda' },
        { keys: ['Arrow Right'], description: 'Mover derecha' },
      ],
    },
    {
      category: 'Grabación',
      shortcuts: [
        { keys: ['Ctrl', 'R'], description: 'Iniciar/Detener grabación' },
        { keys: ['Ctrl', 'P'], description: 'Reproducir grabación' },
        { keys: ['Ctrl', 'S'], description: 'Guardar grabación' },
      ],
    },
    {
      category: 'General',
      shortcuts: [
        { keys: ['Ctrl', '?'], description: 'Mostrar esta guía' },
        { keys: ['Ctrl', 'D'], description: 'Modo oscuro/claro' },
        { keys: ['Ctrl', 'E'], description: 'Exportar datos' },
        { keys: ['F11'], description: 'Pantalla completa' },
      ],
    },
  ];

  const filteredShortcuts = shortcuts
    .map((cat) => ({
      ...cat,
      shortcuts: cat.shortcuts.filter(
        (s) =>
          s.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
          s.keys.some((k) => k.toLowerCase().includes(searchTerm.toLowerCase()))
      ),
    }))
    .filter((cat) => cat.shortcuts.length > 0);

  const categories = ['all', ...shortcuts.map((s) => s.category)];

  const displayShortcuts =
    selectedCategory === 'all'
      ? filteredShortcuts
      : filteredShortcuts.filter((cat) => cat.category === selectedCategory);

  return (
    <div className="space-y-6">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-6">
          <Keyboard className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Guía de Atajos de Teclado</h3>
        </div>

        {/* Search */}
        <div className="mb-4 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Buscar atajos..."
            className="w-full pl-10 pr-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>

        {/* Categories */}
        <div className="flex gap-2 mb-6 flex-wrap">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1 rounded-lg text-sm transition-colors ${
                selectedCategory === cat
                  ? 'bg-primary-600 text-white'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
              }`}
            >
              {cat === 'all' ? 'Todas' : cat}
            </button>
          ))}
        </div>

        {/* Shortcuts List */}
        <div className="space-y-6">
          {displayShortcuts.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <Keyboard className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No se encontraron atajos</p>
            </div>
          ) : (
            displayShortcuts.map((category) => (
              <div key={category.category}>
                <h4 className="text-sm font-semibold text-gray-400 mb-3 uppercase">
                  {category.category}
                </h4>
                <div className="space-y-2">
                  {category.shortcuts.map((shortcut, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 bg-gray-700/50 rounded-lg border border-gray-600"
                    >
                      <span className="text-white">{shortcut.description}</span>
                      <div className="flex gap-1">
                        {shortcut.keys.map((key, keyIndex) => (
                          <span key={keyIndex}>
                            <kbd className="px-2 py-1 bg-gray-800 border border-gray-600 rounded text-sm text-white font-mono">
                              {key}
                            </kbd>
                            {keyIndex < shortcut.keys.length - 1 && (
                              <span className="mx-1 text-gray-400">+</span>
                            )}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}


