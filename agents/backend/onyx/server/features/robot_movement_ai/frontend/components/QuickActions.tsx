'use client';

import { useRobotStore } from '@/lib/store/robotStore';
import { Zap, Home, Square, RotateCcw, Play, Pause } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

export default function QuickActions() {
  const { moveTo, stop, currentPosition } = useRobotStore();

  const quickActions = [
    {
      name: 'Home',
      icon: <Home className="w-5 h-5" />,
      action: () => {
        moveTo({ x: 0, y: 0, z: 0 });
        toast.info('Moviendo a posición home');
      },
      color: 'bg-blue-600 hover:bg-blue-700',
    },
    {
      name: 'Stop',
      icon: <Square className="w-5 h-5" />,
      action: () => {
        stop();
        toast.warning('Robot detenido');
      },
      color: 'bg-red-600 hover:bg-red-700',
    },
    {
      name: 'Reset',
      icon: <RotateCcw className="w-5 h-5" />,
      action: () => {
        if (currentPosition) {
          moveTo(currentPosition);
          toast.info('Posición reiniciada');
        }
      },
      color: 'bg-yellow-600 hover:bg-yellow-700',
    },
  ];

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-4 border border-gray-700">
      <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
        <Zap className="w-4 h-4 text-primary-400" />
        Acciones Rápidas
      </h3>
      <div className="grid grid-cols-3 gap-2">
        {quickActions.map((action, index) => (
          <button
            key={index}
            onClick={action.action}
            className={`${action.color} text-white p-3 rounded-lg transition-colors flex flex-col items-center gap-1`}
          >
            {action.icon}
            <span className="text-xs">{action.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}


