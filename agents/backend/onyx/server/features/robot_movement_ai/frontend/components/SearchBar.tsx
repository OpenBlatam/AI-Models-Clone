'use client';

import { useState, useRef, useEffect } from 'react';
import { Search, X, Command } from 'lucide-react';

interface SearchResult {
  id: string;
  type: 'command' | 'tab' | 'feature';
  title: string;
  description: string;
  action: () => void;
}

interface SearchBarProps {
  onResultSelect: (result: SearchResult) => void;
  tabs?: Array<{ id: string; label: string; action: () => void }>;
}

export default function SearchBar({ onResultSelect, tabs = [] }: SearchBarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        setIsOpen(true);
        setTimeout(() => inputRef.current?.focus(), 0);
      }
      if (e.key === 'Escape' && isOpen) {
        setIsOpen(false);
        setQuery('');
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const searchResults: SearchResult[] = [];

    // Search tabs
    tabs.forEach((tab) => {
      if (tab.label.toLowerCase().includes(query.toLowerCase())) {
        searchResults.push({
          id: `tab-${tab.id}`,
          type: 'tab',
          title: tab.label,
          description: `Ir a ${tab.label}`,
          action: tab.action,
        });
      }
    });

    // Search commands
    const commands = [
      { title: 'Mover a posición', command: 'move to (x, y, z)' },
      { title: 'Ir a home', command: 'go home' },
      { title: 'Detener', command: 'stop' },
      { title: 'Estado', command: 'status' },
    ];

    commands.forEach((cmd) => {
      if (
        cmd.title.toLowerCase().includes(query.toLowerCase()) ||
        cmd.command.toLowerCase().includes(query.toLowerCase())
      ) {
        searchResults.push({
          id: `cmd-${cmd.title}`,
          type: 'command',
          title: cmd.title,
          description: cmd.command,
          action: () => {
            // Command action would be handled by parent
            onResultSelect({
              id: `cmd-${cmd.title}`,
              type: 'command',
              title: cmd.title,
              description: cmd.command,
              action: () => {},
            });
          },
        });
      }
    });

    setResults(searchResults.slice(0, 8));
  }, [query, tabs, onResultSelect]);

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        className="flex items-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-lg transition-colors text-sm"
      >
        <Search className="w-4 h-4" />
        <span className="hidden sm:inline">Buscar...</span>
        <kbd className="hidden sm:inline px-2 py-1 bg-gray-600 rounded text-xs">Ctrl+K</kbd>
      </button>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-20 px-4">
      <div className="absolute inset-0 bg-black/50" onClick={() => setIsOpen(false)} />
      <div className="relative w-full max-w-2xl bg-gray-800 rounded-lg border border-gray-700 shadow-2xl">
        <div className="flex items-center gap-3 p-4 border-b border-gray-700">
          <Search className="w-5 h-5 text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Buscar comandos, tabs, características..."
            className="flex-1 bg-transparent text-white placeholder-gray-500 focus:outline-none"
            autoFocus
          />
          <button
            onClick={() => {
              setIsOpen(false);
              setQuery('');
            }}
            className="p-1 hover:bg-gray-700 rounded"
          >
            <X className="w-4 h-4 text-gray-400" />
          </button>
        </div>

        {results.length > 0 && (
          <div className="max-h-96 overflow-y-auto p-2">
            {results.map((result) => (
              <button
                key={result.id}
                onClick={() => {
                  result.action();
                  setIsOpen(false);
                  setQuery('');
                }}
                className="w-full flex items-start gap-3 p-3 hover:bg-gray-700 rounded-lg transition-colors text-left"
              >
                {result.type === 'command' ? (
                  <Command className="w-5 h-5 text-primary-400 mt-0.5" />
                ) : (
                  <Search className="w-5 h-5 text-blue-400 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="text-white font-medium">{result.title}</p>
                  <p className="text-sm text-gray-400">{result.description}</p>
                </div>
                <span className="text-xs text-gray-500 uppercase">{result.type}</span>
              </button>
            ))}
          </div>
        )}

        {query && results.length === 0 && (
          <div className="p-8 text-center text-gray-400">
            No se encontraron resultados para "{query}"
          </div>
        )}

        {!query && (
          <div className="p-4 text-sm text-gray-400 border-t border-gray-700">
            <p className="mb-2">Sugerencias:</p>
            <div className="flex flex-wrap gap-2">
              <kbd className="px-2 py-1 bg-gray-700 rounded text-xs">Ctrl+K</kbd>
              <span className="text-gray-500">para buscar</span>
              <kbd className="px-2 py-1 bg-gray-700 rounded text-xs">Esc</kbd>
              <span className="text-gray-500">para cerrar</span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

