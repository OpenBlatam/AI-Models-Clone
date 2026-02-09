'use client';

import { useState, useEffect } from 'react';

interface TourStep {
  id: string;
  title: string;
  content: string;
  target: string; // selector CSS
  position?: 'top' | 'bottom' | 'left' | 'right';
}

interface TourProps {
  steps: TourStep[];
  isActive: boolean;
  onComplete: () => void;
  onSkip: () => void;
}

export function Tour({ steps, isActive, onComplete, onSkip }: TourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [targetElement, setTargetElement] = useState<HTMLElement | null>(null);

  useEffect(() => {
    if (!isActive || currentStep >= steps.length) {
      onComplete();
      return;
    }

    const step = steps[currentStep];
    const element = document.querySelector(step.target) as HTMLElement;

    if (element) {
      setTargetElement(element);
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  }, [isActive, currentStep, steps, onComplete]);

  if (!isActive || currentStep >= steps.length || !targetElement) {
    return null;
  }

  const step = steps[currentStep];
  const rect = targetElement.getBoundingClientRect();

  const positionStyles = {
    top: {
      bottom: `${window.innerHeight - rect.top + 10}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: 'translateX(-50%)',
    },
    bottom: {
      top: `${rect.bottom + 10}px`,
      left: `${rect.left + rect.width / 2}px`,
      transform: 'translateX(-50%)',
    },
    left: {
      right: `${window.innerWidth - rect.left + 10}px`,
      top: `${rect.top + rect.height / 2}px`,
      transform: 'translateY(-50%)',
    },
    right: {
      left: `${rect.right + 10}px`,
      top: `${rect.top + rect.height / 2}px`,
      transform: 'translateY(-50%)',
    },
  };

  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 z-40" />
      <div
        className="fixed z-50 bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 max-w-sm"
        style={positionStyles[step.position || 'bottom']}
      >
        <div className="flex justify-between items-start mb-4">
          <div>
            <h3 className="font-bold text-gray-900 dark:text-white">
              {step.title}
            </h3>
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Paso {currentStep + 1} de {steps.length}
            </p>
          </div>
          <button
            onClick={onSkip}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            ×
          </button>
        </div>
        <p className="text-gray-700 dark:text-gray-300 mb-4">{step.content}</p>
        <div className="flex gap-2">
          {currentStep > 0 && (
            <button
              onClick={() => setCurrentStep(currentStep - 1)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
            >
              Anterior
            </button>
          )}
          <button
            onClick={() => {
              if (currentStep < steps.length - 1) {
                setCurrentStep(currentStep + 1);
              } else {
                onComplete();
              }
            }}
            className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg"
          >
            {currentStep < steps.length - 1 ? 'Siguiente' : 'Finalizar'}
          </button>
        </div>
      </div>
    </>
  );
}














