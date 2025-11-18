'use client';

import { useEffect, useState } from 'react';
import { useRecordingStore } from '@/lib/store/recordingStore';
import { useRobotStore } from '@/lib/store/robotStore';
import { Record, Square, Play, Trash2, Download, Upload, Save } from 'lucide-react';
import { toast } from '@/lib/utils/toast';

export default function RecordingPanel() {
  const {
    isRecording,
    isPlaying,
    records,
    startRecording,
    stopRecording,
    clearRecords,
    startPlayback,
    stopPlayback,
    nextRecord,
  } = useRecordingStore();
  const { moveTo, stop, currentPosition } = useRobotStore();
  const [playbackSpeed, setPlaybackSpeed] = useState(1);

  useEffect(() => {
    if (isPlaying && records.length > 0) {
      const interval = setInterval(() => {
        const record = nextRecord();
        if (record) {
          if (record.action === 'move') {
            moveTo(record.position);
          } else if (record.action === 'stop') {
            stop();
          }
        } else {
          stopPlayback();
          toast.success('Reproducción completada');
        }
      }, 1000 / playbackSpeed);

      return () => clearInterval(interval);
    }
  }, [isPlaying, records, playbackSpeed, nextRecord, moveTo, stop, stopPlayback]);

  const handleRecord = () => {
    if (isRecording) {
      stopRecording();
      toast.success(`Grabación detenida. ${records.length} movimientos guardados.`);
    } else {
      startRecording();
      toast.info('Grabación iniciada');
    }
  };

  const handlePlay = () => {
    if (records.length === 0) {
      toast.error('No hay movimientos grabados');
      return;
    }
    if (isPlaying) {
      stopPlayback();
    } else {
      startPlayback();
      toast.info('Reproducción iniciada');
    }
  };

  const handleSave = () => {
    if (records.length === 0) {
      toast.error('No hay movimientos para guardar');
      return;
    }
    const dataStr = JSON.stringify(records, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `robot-recording-${Date.now()}.json`;
    link.click();
    URL.revokeObjectURL(url);
    toast.success('Grabación guardada');
  };

  const handleLoad = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
          try {
            const data = JSON.parse(event.target?.result as string);
            useRecordingStore.setState({ records: data });
            toast.success('Grabación cargada');
          } catch (error) {
            toast.error('Error al cargar el archivo');
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  return (
    <div className="bg-gray-800/50 backdrop-blur-sm rounded-lg p-6 border border-gray-700">
      <div className="flex items-center gap-2 mb-6">
        <Record className="w-5 h-5 text-primary-400" />
        <h3 className="text-lg font-semibold text-white">Grabación y Reproducción</h3>
      </div>

      <div className="space-y-4">
        {/* Controls */}
        <div className="flex gap-3">
          <button
            onClick={handleRecord}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isRecording
                ? 'bg-red-600 hover:bg-red-700 text-white'
                : 'bg-gray-700 hover:bg-gray-600 text-white'
            }`}
          >
            {isRecording ? (
              <>
                <Square className="w-4 h-4" />
                Detener Grabación
              </>
            ) : (
              <>
                <Record className="w-4 h-4" />
                Iniciar Grabación
              </>
            )}
          </button>
          <button
            onClick={handlePlay}
            disabled={records.length === 0}
            className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
              isPlaying
                ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                : 'bg-green-600 hover:bg-green-700 text-white'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {isPlaying ? (
              <>
                <Square className="w-4 h-4" />
                Detener
              </>
            ) : (
              <>
                <Play className="w-4 h-4" />
                Reproducir
              </>
            )}
          </button>
        </div>

        {/* Playback Speed */}
        {isPlaying && (
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Velocidad de Reproducción: {playbackSpeed}x
            </label>
            <input
              type="range"
              min="0.5"
              max="3"
              step="0.1"
              value={playbackSpeed}
              onChange={(e) => setPlaybackSpeed(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="p-3 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Movimientos Grabados</p>
            <p className="text-2xl font-bold text-white">{records.length}</p>
          </div>
          <div className="p-3 bg-gray-700/50 rounded-lg">
            <p className="text-sm text-gray-400">Estado</p>
            <p className="text-lg font-semibold text-white">
              {isRecording ? 'Grabando...' : isPlaying ? 'Reproduciendo...' : 'Inactivo'}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-3">
          <button
            onClick={handleSave}
            disabled={records.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Download className="w-4 h-4" />
            Guardar
          </button>
          <button
            onClick={handleLoad}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
          >
            <Upload className="w-4 h-4" />
            Cargar
          </button>
          <button
            onClick={clearRecords}
            disabled={records.length === 0}
            className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Trash2 className="w-4 h-4" />
            Limpiar
          </button>
        </div>

        {/* Records List */}
        {records.length > 0 && (
          <div className="mt-4">
            <h4 className="text-sm font-medium text-white mb-2">Movimientos Grabados</h4>
            <div className="max-h-48 overflow-y-auto space-y-1">
              {records.map((record, index) => (
                <div
                  key={index}
                  className="p-2 bg-gray-700/50 rounded text-sm text-gray-300"
                >
                  <span className="font-mono">
                    {record.action} - ({record.position.x.toFixed(2)}, {record.position.y.toFixed(2)}, {record.position.z.toFixed(2)})
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

