'use client';

import { useState, useEffect } from 'react';
import { useRobotStore } from '@/lib/store/robotStore';
import { useRecordingStore } from '@/lib/store/recordingStore';
import { useKeyboardShortcuts } from '@/lib/utils/keyboard';
import { Move, Square, Home, Navigation, Loader2 } from 'lucide-react';
import { Position } from '@/lib/api/types';

export default function RobotControl() {
  const { moveTo, stop, isLoading, currentPosition } = useRobotStore();
  const { isRecording, addRecord } = useRecordingStore();
  const [position, setPosition] = useState<Position>({
    x: currentPosition?.x || 0,
    y: currentPosition?.y || 0,
    z: currentPosition?.z || 0,
  });

  useEffect(() => {
    if (currentPosition) {
      setPosition({
        x: currentPosition.x,
        y: currentPosition.y,
        z: currentPosition.z,
      });
    }
  }, [currentPosition]);

  const handleMove = async () => {
    await moveTo(position);
    if (isRecording) {
      addRecord(position, 'move');
    }
  };

  const handleStop = async () => {
    await stop();
    if (isRecording) {
      addRecord(position, 'stop');
    }
  };

  const handleHome = async () => {
    const homePos = { x: 0, y: 0, z: 0 };
    await moveTo(homePos);
    if (isRecording) {
      addRecord(homePos, 'home');
    }
  };

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'h',
      ctrl: true,
      action: handleHome,
      description: 'Ir a posición home',
    },
    {
      key: 's',
      ctrl: true,
      action: handleStop,
      description: 'Detener robot',
    },
  ]);

  const presetPositions = [
    { name: 'Posición 1', x: 0.5, y: 0.3, z: 0.2 },
    { name: 'Posición 2', x: 0.3, y: 0.5, z: 0.4 },
    { name: 'Posición 3', x: 0.7, y: 0.2, z: 0.3 },
  ];

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-semibold text-white mb-6">Control del Robot</h2>

      {/* Position Input */}
      <div className="mb-6">
        <h3 className="text-lg font-medium text-white mb-4">Posición Objetivo</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              X (m)
            </label>
            <input
              type="number"
              step="0.01"
              value={position.x}
              onChange={(e) =>
                setPosition({ ...position, x: parseFloat(e.target.value) || 0 })
              }
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Y (m)
            </label>
            <input
              type="number"
              step="0.01"
              value={position.y}
              onChange={(e) =>
                setPosition({ ...position, y: parseFloat(e.target.value) || 0 })
              }
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Z (m)
            </label>
            <input
              type="number"
              step="0.01"
              value={position.z}
              onChange={(e) =>
                setPosition({ ...position, z: parseFloat(e.target.value) || 0 })
              }
              className="w-full px-4 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 mb-6">
        <button
          onClick={handleMove}
          disabled={isLoading}
          className="flex-1 flex items-center justify-center gap-2 px-6 py-3 bg-primary-600 hover:bg-primary-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Move className="w-5 h-5" />
          Mover
        </button>
        <button
          onClick={handleStop}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Square className="w-5 h-5" />
          Detener
        </button>
        <button
          onClick={handleHome}
          disabled={isLoading}
          className="flex items-center justify-center gap-2 px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Home className="w-5 h-5" />
          Home
        </button>
      </div>

      {/* Preset Positions */}
      <div>
        <h3 className="text-lg font-medium text-white mb-4">Posiciones Predefinidas</h3>
        <div className="grid grid-cols-3 gap-4">
          {presetPositions.map((preset, index) => (
            <button
              key={index}
              onClick={() => {
                setPosition({ x: preset.x, y: preset.y, z: preset.z });
              }}
              className="p-4 bg-gray-700 hover:bg-gray-600 rounded-lg border border-gray-600 transition-colors"
            >
              <Navigation className="w-5 h-5 text-primary-400 mb-2 mx-auto" />
              <p className="text-white font-medium text-sm">{preset.name}</p>
              <p className="text-gray-400 text-xs mt-1">
                ({preset.x}, {preset.y}, {preset.z})
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* Loading Indicator */}
      {isLoading && (
        <div className="mt-6 flex items-center justify-center gap-2">
          <Loader2 className="w-5 h-5 animate-spin text-primary-400" />
          <span className="text-gray-300">Procesando...</span>
        </div>
      )}
    </div>
  );
}

