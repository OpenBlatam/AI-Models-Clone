'use client';

import { useRobotStore } from '@/lib/store/robotStore';
import { TrendingUp, Activity, Zap, Clock } from 'lucide-react';

export default function QuickStats() {
  const { status } = useRobotStore();

  const stats = [
    {
      label: 'Estado',
      value: status?.robot_status.connected ? 'Conectado' : 'Desconectado',
      icon: <Activity className="w-5 h-5" />,
      color: status?.robot_status.connected ? 'text-green-400' : 'text-red-400',
    },
    {
      label: 'Movimiento',
      value: status?.robot_status.moving ? 'En movimiento' : 'Detenido',
      icon: <TrendingUp className="w-5 h-5" />,
      color: status?.robot_status.moving ? 'text-blue-400' : 'text-gray-400',
    },
    {
      label: 'Velocidad',
      value: status?.robot_status.velocity
        ? `${Math.sqrt(
            status.robot_status.velocity[0] ** 2 +
            status.robot_status.velocity[1] ** 2 +
            status.robot_status.velocity[2] ** 2
          ).toFixed(2)} m/s`
        : '0.00 m/s',
      icon: <Zap className="w-5 h-5" />,
      color: 'text-yellow-400',
    },
    {
      label: 'Tiempo activo',
      value: '2h 34m',
      icon: <Clock className="w-5 h-5" />,
      color: 'text-purple-400',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((stat, index) => (
        <div
          key={index}
          className="p-4 bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700"
        >
          <div className="flex items-center gap-2 mb-2">
            <div className={stat.color}>{stat.icon}</div>
            <span className="text-xs text-gray-400">{stat.label}</span>
          </div>
          <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
        </div>
      ))}
    </div>
  );
}


