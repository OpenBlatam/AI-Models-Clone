'use client';

import { useState, useMemo, useCallback, memo } from 'react';
import { CalcularImpuestosForm } from './forms/CalcularImpuestosForm';
import { AsesoriaFiscalForm } from './forms/AsesoriaFiscalForm';
import { GuiaFiscalForm } from './forms/GuiaFiscalForm';
import { TramiteSATForm } from './forms/TramiteSATForm';
import { AyudaDeclaracionForm } from './forms/AyudaDeclaracionForm';
import { SERVICES, type ServiceType } from '@/lib';

interface DashboardProps {
  onTaskCreated: (taskId: string) => void;
}

function DashboardComponent({ onTaskCreated }: DashboardProps) {
  const [activeService, setActiveService] = useState<ServiceType | null>(null);

  const handleServiceSelect = useCallback((serviceId: ServiceType) => {
    setActiveService(serviceId);
  }, []);

  const handleCancel = useCallback(() => {
    setActiveService(null);
  }, []);

  const renderForm = useCallback(() => {
    const formProps = {
      onTaskCreated,
      onCancel: handleCancel,
    };

    switch (activeService) {
      case 'calcular-impuestos':
        return <CalcularImpuestosForm {...formProps} />;
      case 'asesoria-fiscal':
        return <AsesoriaFiscalForm {...formProps} />;
      case 'guia-fiscal':
        return <GuiaFiscalForm {...formProps} />;
      case 'tramite-sat':
        return <TramiteSATForm {...formProps} />;
      case 'ayuda-declaracion':
        return <AyudaDeclaracionForm {...formProps} />;
      default:
        return null;
    }
  }, [activeService, onTaskCreated, handleCancel]);

  return (
    <div className="space-y-6">
      {!activeService ? (
        <>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Servicios Disponibles
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              Selecciona un servicio para comenzar
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 md:gap-4">
              {SERVICES.map((service) => (
                <button
                  key={service.id}
                  onClick={() => handleServiceSelect(service.id)}
                  className={`${service.color} ${service.hoverColor} text-white p-4 md:p-6 rounded-lg shadow-md transition-all duration-200 transform hover:scale-105 hover:shadow-xl active:scale-95 text-left focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white/50 min-h-[120px] md:min-h-[140px]`}
                  aria-label={`Seleccionar ${service.title}`}
                >
                  <div className="text-3xl mb-2">{service.icon}</div>
                  <h3 className="text-xl font-bold mb-2">{service.title}</h3>
                  <p className="text-sm opacity-90">{service.description}</p>
                </button>
              ))}
            </div>
          </div>
        </>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 animate-fade-in">
          <button
            onClick={() => setActiveService(null)}
            className="mb-4 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors flex items-center gap-2"
            aria-label="Volver a servicios"
          >
            <span>←</span>
            <span>Volver a servicios</span>
          </button>
          {renderForm()}
        </div>
      )}
    </div>
  );
}

export const Dashboard = memo(DashboardComponent);

