'use client';

import { useState } from 'react';
import {
  HelpCircle,
  Book,
  Video,
  Code,
  MessageSquare,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';

interface HelpSection {
  id: string;
  title: string;
  icon: React.ReactNode;
  content: string;
  items?: string[];
}

const helpSections: HelpSection[] = [
  {
    id: 'getting-started',
    title: 'Empezar',
    icon: <Book className="w-5 h-5" />,
    content: 'Guía rápida para comenzar a usar el sistema',
    items: [
      'Conecta el robot al backend',
      'Verifica el estado en la pestaña Estado',
      'Usa Control para mover el robot',
      'Prueba comandos en Chat',
    ],
  },
  {
    id: 'commands',
    title: 'Comandos Disponibles',
    icon: <Code className="w-5 h-5" />,
    content: 'Lista de comandos que puedes usar',
    items: [
      'move to (x, y, z) - Mover a posición absoluta',
      'move relative (x, y, z) - Mover relativamente',
      'go home - Ir a posición home',
      'stop - Detener movimiento',
      'status - Obtener estado del robot',
    ],
  },
  {
    id: 'shortcuts',
    title: 'Atajos de Teclado',
    icon: <MessageSquare className="w-5 h-5" />,
    content: 'Atajos rápidos para operaciones comunes',
    items: [
      'Ctrl + H - Ir a posición home',
      'Ctrl + S - Detener robot',
      'Ctrl + R - Iniciar/Detener grabación',
    ],
  },
  {
    id: 'features',
    title: 'Características',
    icon: <Video className="w-5 h-5" />,
    content: 'Funcionalidades principales del sistema',
    items: [
      'Visualización 3D del robot',
      'Grabación y reproducción de movimientos',
      'Optimización de trayectorias',
      'Métricas y análisis en tiempo real',
      'Sistema de alertas',
      'Logs del sistema',
    ],
  },
];

export default function HelpPanel() {
  const [expanded, setExpanded] = useState<string | null>('getting-started');

  const toggleSection = (id: string) => {
    setExpanded(expanded === id ? null : id);
  };

  return (
    <div className="space-y-4">
      <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
        <div className="flex items-center gap-2 mb-4">
          <HelpCircle className="w-6 h-6 text-primary-400" />
          <h2 className="text-2xl font-bold text-white">Centro de Ayuda</h2>
        </div>
        <p className="text-gray-300">
          Encuentra información sobre cómo usar el sistema, comandos disponibles y más.
        </p>
      </div>

      {helpSections.map((section) => (
        <div
          key={section.id}
          className="bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 overflow-hidden"
        >
          <button
            onClick={() => toggleSection(section.id)}
            className="w-full flex items-center justify-between p-4 hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex items-center gap-3">
              {section.icon}
              <div className="text-left">
                <h3 className="font-semibold text-white">{section.title}</h3>
                <p className="text-sm text-gray-400">{section.content}</p>
              </div>
            </div>
            {expanded === section.id ? (
              <ChevronDown className="w-5 h-5 text-gray-400" />
            ) : (
              <ChevronRight className="w-5 h-5 text-gray-400" />
            )}
          </button>

          {expanded === section.id && section.items && (
            <div className="px-4 pb-4">
              <ul className="space-y-2">
                {section.items.map((item, index) => (
                  <li key={index} className="flex items-start gap-2 text-gray-300">
                    <span className="text-primary-400 mt-1">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      ))}

      {/* Quick Tips */}
      <div className="bg-primary-500/10 border border-primary-500/50 rounded-lg p-6">
        <h3 className="font-semibold text-primary-400 mb-3">💡 Consejos Rápidos</h3>
        <ul className="space-y-2 text-sm text-gray-300">
          <li>• Usa la visualización 3D para ver el robot en tiempo real</li>
          <li>• Graba movimientos para reproducirlos después</li>
          <li>• Compara algoritmos de optimización para elegir el mejor</li>
          <li>• Revisa los logs para diagnosticar problemas</li>
          <li>• Configura alertas para estar informado</li>
        </ul>
      </div>
    </div>
  );
}

