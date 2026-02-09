'use client';

import { useState, useEffect } from 'react';
import { StorageService } from '@/lib';
import { STORAGE_KEYS } from '@/lib/constants';

interface NotesPanelProps {
  taskId: string;
  initialNotes?: string;
  onSave?: (notes: string) => void;
}

export function NotesPanel({ taskId, initialNotes = '', onSave }: NotesPanelProps) {
  const [notes, setNotes] = useState(initialNotes);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    // Cargar notas guardadas
    const saved = StorageService.get<string>(STORAGE_KEYS.notes(taskId));
    if (saved) {
      setNotes(saved);
    }
  }, [taskId]);

  const handleSave = async () => {
    setIsSaving(true);
    StorageService.set(STORAGE_KEYS.notes(taskId), notes);
    onSave?.(notes);
    setTimeout(() => setIsSaving(false), 500);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">
          📝 Notas
        </h3>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="px-3 py-1 text-xs bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors"
        >
          {isSaving ? 'Guardando...' : 'Guardar'}
        </button>
      </div>
      <textarea
        value={notes}
        onChange={(e) => setNotes(e.target.value)}
        placeholder="Agrega notas sobre esta tarea..."
        className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 resize-none"
        rows={4}
      />
      <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
        {notes.length} caracteres
      </p>
    </div>
  );
}



