'use client';

import { useState, useEffect } from 'react';
import { useRobotStore } from '@/lib/store/robotStore';
import { Command, Plus, Trash2, Play, Save, Load } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

interface CustomCommand {
  id: string;
  name: string;
  command: string;
  description?: string;
}

export default function CustomCommands() {
  const { sendChatMessage } = useRobotStore();
  const [commands, setCommands] = useState<CustomCommand[]>([]);
  const [newCommand, setNewCommand] = useState({ name: '', command: '', description: '' });
  const [editingId, setEditingId] = useState<string | null>(null);

  useEffect(() => {
    // Load from localStorage
    const saved = localStorage.getItem('custom-commands');
    if (saved) {
      setCommands(JSON.parse(saved));
    }
  }, []);

  const saveCommands = (cmds: CustomCommand[]) => {
    localStorage.setItem('custom-commands', JSON.stringify(cmds));
    setCommands(cmds);
  };

  const handleAdd = () => {
    if (!newCommand.name || !newCommand.command) {
      toast.error('Nombre y comando son requeridos');
      return;
    }

    const command: CustomCommand = {
      id: Date.now().toString(),
      name: newCommand.name,
      command: newCommand.command,
      description: newCommand.description,
    };

    saveCommands([...commands, command]);
    setNewCommand({ name: '', command: '', description: '' });
    toast.success('Comando agregado');
  };

  const handleDelete = (id: string) => {
    saveCommands(commands.filter((c) => c.id !== id));
    toast.success('Comando eliminado');
  };

  const handleExecute = (command: string) => {
    sendChatMessage(command);
    toast.info('Comando enviado');
  };

  const handleExport = () => {
    const dataStr = JSON.stringify(commands, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `custom-commands-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Comandos exportados');
  };

  const handleImport = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const imported = JSON.parse(event.target?.result as string);
            saveCommands(imported);
            toast.success('Comandos importados');
          } catch (error) {
            toast.error('Error al importar comandos');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Command className="w-5 h-5 text-primary-400" />
            <h3 className="text-lg font-semibold text-white">Comandos Personalizados</h3>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors text-sm"
            >
              <Save className="w-4 h-4" />
              Exportar
            </button>
            <button
              onClick={handleImport}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors text-sm"
            >
              <Load className="w-4 h-4" />
              Importar
            </button>
          </div>
        </div>

        {/* Add New Command */}
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Nombre</label>
            <input
              type="text"
              value={newCommand.name}
              onChange={(e) => setNewCommand({ ...newCommand, name: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Ej: Mover a posición segura"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Comando</label>
            <input
              type="text"
              value={newCommand.command}
              onChange={(e) => setNewCommand({ ...newCommand, command: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Ej: move to (0.5, 0.3, 0.2)"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">
              Descripción (opcional)
            </label>
            <input
              type="text"
              value={newCommand.description}
              onChange={(e) => setNewCommand({ ...newCommand, description: e.target.value })}
              className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
              placeholder="Descripción del comando"
            />
          </div>
          <button
            onClick={handleAdd}
            className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors"
          >
            <Plus className="w-4 h-4" />
            Agregar Comando
          </button>
        </div>
      </div>

      {/* Commands List */}
      <div className="space-y-2">
        {commands.length === 0 ? (
          <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-8 border border-gray-700 text-center text-gray-400">
            No hay comandos personalizados. Agrega uno para comenzar.
          </div>
        ) : (
          commands.map((cmd) => (
            <div
              key={cmd.id}
              className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="font-semibold text-white mb-1">{cmd.name}</h4>
                  <p className="text-sm text-gray-300 font-mono mb-1">{cmd.command}</p>
                  {cmd.description && (
                    <p className="text-xs text-gray-400">{cmd.description}</p>
                  )}
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => handleExecute(cmd.command)}
                    className="p-2 bg-green-600 hover:bg-green-700 text-white rounded transition-colors"
                    title="Ejecutar"
                  >
                    <Play className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(cmd.id)}
                    className="p-2 bg-red-600 hover:bg-red-700 text-white rounded transition-colors"
                    title="Eliminar"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

