import { useState, useEffect, useCallback } from 'react';
import { useInterval } from './use-interval';

interface UseCountdownOptions {
  initialSeconds: number;
  onComplete?: () => void;
  autoStart?: boolean;
}

/**
 * Hook for countdown timer
 */
export function useCountdown({ initialSeconds, onComplete, autoStart = false }: UseCountdownOptions) {
  const [seconds, setSeconds] = useState(initialSeconds);
  const [isRunning, setIsRunning] = useState(autoStart);

  useInterval(
    () => {
      setSeconds((prev) => {
        if (prev <= 1) {
          setIsRunning(false);
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    },
    isRunning ? 1000 : null
  );

  const start = useCallback(() => {
    setIsRunning(true);
  }, []);

  const pause = useCallback(() => {
    setIsRunning(false);
  }, []);

  const reset = useCallback(() => {
    setSeconds(initialSeconds);
    setIsRunning(false);
  }, [initialSeconds]);

  const restart = useCallback(() => {
    setSeconds(initialSeconds);
    setIsRunning(true);
  }, [initialSeconds]);

  return {
    seconds,
    isRunning,
    start,
    pause,
    reset,
    restart,
    isComplete: seconds === 0,
  };
}


