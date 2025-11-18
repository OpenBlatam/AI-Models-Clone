'use client';

import { useState, useEffect } from 'react';
import { Grid, Maximize2, Minimize2, X, GripVertical } from 'lucide-react';
import { useRobotStore } from '@/lib/store/robotStore';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface Widget {
  id: string;
  type: 'status' | 'metrics' | 'chart' | 'position';
  title: string;
  x: number;
  y: number;
  w: number;
  h: number;
  data?: any;
}

const defaultWidgets: Widget[] = [
  { id: '1', type: 'status', title: 'Estado del Robot', x: 0, y: 0, w: 4, h: 2 },
  { id: '2', type: 'position', title: 'Posición Actual', x: 4, y: 0, w: 4, h: 2 },
  { id: '3', type: 'metrics', title: 'Métricas Rápidas', x: 8, y: 0, w: 4, h: 2 },
  { id: '4', type: 'chart', title: 'Gráfico de Movimiento', x: 0, y: 2, w: 12, h: 4 },
];

export default function WidgetDashboard() {
  const { status } = useRobotStore();
  const [widgets, setWidgets] = useState<Widget[]>(defaultWidgets);
  const [isEditing, setIsEditing] = useState(false);
  const [draggedWidget, setDraggedWidget] = useState<string | null>(null);

  const renderWidget = (widget: Widget) => {
    switch (widget.type) {
      case 'status':
        return (
          <div className="p-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Conexión</span>
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    status?.robot_status.connected
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'
                  }`}
                >
                  {status?.robot_status.connected ? 'Conectado' : 'Desconectado'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Movimiento</span>
                <span
                  className={`px-2 py-1 rounded text-sm ${
                    status?.robot_status.moving
                      ? 'bg-yellow-500/20 text-yellow-400'
                      : 'bg-gray-500/20 text-gray-400'
                  }`}
                >
                  {status?.robot_status.moving ? 'En Movimiento' : 'Detenido'}
                </span>
              </div>
            </div>
          </div>
        );

      case 'position':
        return (
          <div className="p-4">
            {status?.robot_status.position ? (
              <div className="space-y-2">
                <div className="text-sm">
                  <span className="text-gray-400">X: </span>
                  <span className="text-white font-mono">
                    {status.robot_status.position.x.toFixed(3)}m
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Y: </span>
                  <span className="text-white font-mono">
                    {status.robot_status.position.y.toFixed(3)}m
                  </span>
                </div>
                <div className="text-sm">
                  <span className="text-gray-400">Z: </span>
                  <span className="text-white font-mono">
                    {status.robot_status.position.z.toFixed(3)}m
                  </span>
                </div>
              </div>
            ) : (
              <p className="text-gray-400 text-sm">No hay posición disponible</p>
            )}
          </div>
        );

      case 'metrics':
        return (
          <div className="p-4">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <p className="text-xs text-gray-400">CPU</p>
                <p className="text-lg font-bold text-white">45%</p>
              </div>
              <div>
                <p className="text-xs text-gray-400">Memoria</p>
                <p className="text-lg font-bold text-white">62%</p>
              </div>
            </div>
          </div>
        );

      case 'chart':
        const chartData = Array.from({ length: 20 }, (_, i) => ({
          name: `T${i}`,
          value: Math.random() * 100,
        }));
        return (
          <div className="p-4 h-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#0EA5E9"
                  fill="#0EA5E9"
                  fillOpacity={0.3}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Grid className="w-5 h-5 text-primary-400" />
          <h3 className="text-lg font-semibold text-white">Dashboard Personalizable</h3>
        </div>
        <button
          onClick={() => setIsEditing(!isEditing)}
          className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors text-sm"
        >
          {isEditing ? 'Guardar' : 'Editar'}
        </button>
      </div>

      <div className="grid grid-cols-12 gap-4 auto-rows-[100px]">
        {widgets.map((widget) => (
          <div
            key={widget.id}
            className={`col-span-${widget.w} row-span-${widget.h} bg-gray-800/50 backdrop-blur-sm rounded-lg border border-gray-700 relative ${
              isEditing ? 'cursor-move' : ''
            }`}
            style={{
              gridColumn: `span ${widget.w}`,
              gridRow: `span ${widget.h}`,
            }}
          >
            {isEditing && (
              <div className="absolute top-2 right-2 flex gap-1 z-10">
                <button className="p-1 bg-gray-700 hover:bg-gray-600 rounded">
                  <GripVertical className="w-4 h-4 text-gray-300" />
                </button>
                <button
                  onClick={() => setWidgets(widgets.filter((w) => w.id !== widget.id))}
                  className="p-1 bg-red-600 hover:bg-red-700 rounded"
                >
                  <X className="w-4 h-4 text-white" />
                </button>
              </div>
            )}
            <div className="p-2 border-b border-gray-700">
              <h4 className="text-sm font-medium text-white">{widget.title}</h4>
            </div>
            <div className="h-full overflow-hidden">{renderWidget(widget)}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

