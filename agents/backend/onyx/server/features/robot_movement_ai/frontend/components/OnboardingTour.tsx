'use client';

import { useState } from 'react';
import { useLocalStorage } from '@/lib/hooks/useLocalStorage';
import { X, ArrowRight, ArrowLeft, CheckCircle } from 'lucide-react';

interface TourStep {
  id: string;
  title: string;
  description: string;
  target?: string; // CSS selector
}

export default function OnboardingTour() {
  const [completed, setCompleted] = useLocalStorage('onboarding-completed', false);
  const [currentStep, setCurrentStep] = useState(0);
  const [isActive, setIsActive] = useState(!completed);

  const steps: TourStep[] = [
    {
      id: 'welcome',
      title: '¡Bienvenido a Robot Movement AI!',
      description: 'Esta es una plataforma completa para controlar y monitorear robots. Te guiaremos por las características principales.',
    },
    {
      id: 'control',
      title: 'Control del Robot',
      description: 'Usa la pestaña de Control para mover el robot, detenerlo o llevarlo a la posición inicial.',
    },
    {
      id: '3d',
      title: 'Visualización 3D',
      description: 'La visualización 3D te permite ver el robot en tiempo real desde cualquier ángulo.',
    },
    {
      id: 'chat',
      title: 'Chat Inteligente',
      description: 'Puedes comunicarte con el robot usando comandos de texto natural.',
    },
    {
      id: 'metrics',
      title: 'Métricas y Análisis',
      description: 'Monitorea el rendimiento del robot con métricas en tiempo real y análisis avanzados.',
    },
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleSkip = () => {
    handleComplete();
  };

  const handleComplete = () => {
    setCompleted(true);
    setIsActive(false);
  };

  if (!isActive) return null;

  const currentStepData = steps[currentStep];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="relative max-w-md w-full mx-4 bg-gray-800 rounded-lg border border-gray-700 shadow-xl">
        {/* Close Button */}
        <button
          onClick={handleSkip}
          className="absolute top-4 right-4 p-2 text-gray-400 hover:text-white transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Content */}
        <div className="p-6">
          <div className="mb-4">
            <div className="flex items-center justify-between mb-2">
              <h3 className="text-xl font-bold text-white">{currentStepData.title}</h3>
              <span className="text-sm text-gray-400">
                {currentStep + 1} / {steps.length}
              </span>
            </div>
            <p className="text-gray-300">{currentStepData.description}</p>
          </div>

          {/* Progress */}
          <div className="mb-6">
            <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
              <div
                className="h-full bg-primary-500 transition-all duration-300"
                style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Steps Indicators */}
          <div className="flex gap-2 mb-6 justify-center">
            {steps.map((step, index) => (
              <div
                key={step.id}
                className={`w-2 h-2 rounded-full transition-colors ${
                  index <= currentStep ? 'bg-primary-500' : 'bg-gray-600'
                }`}
              />
            ))}
          </div>

          {/* Actions */}
          <div className="flex gap-3">
            {currentStep > 0 && (
              <button
                onClick={handlePrevious}
                className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Anterior
              </button>
            )}
            <button
              onClick={handleNext}
              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  <CheckCircle className="w-4 h-4" />
                  Completar
                </>
              ) : (
                <>
                  Siguiente
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>

          {/* Skip */}
          <button
            onClick={handleSkip}
            className="w-full mt-3 text-sm text-gray-400 hover:text-white transition-colors"
          >
            Omitir tour
          </button>
        </div>
      </div>
    </div>
  );
}


