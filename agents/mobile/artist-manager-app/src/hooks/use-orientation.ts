import { useState, useEffect } from 'react';
import { Dimensions, ScaledSize } from 'react-native';

type Orientation = 'portrait' | 'landscape';

/**
 * Hook for tracking device orientation
 */
export function useOrientation() {
  const [orientation, setOrientation] = useState<Orientation>(() => {
    const { width, height } = Dimensions.get('window');
    return width > height ? 'landscape' : 'portrait';
  });

  useEffect(() => {
    function onChange({ window }: { window: ScaledSize }) {
      setOrientation(window.width > window.height ? 'landscape' : 'portrait');
    }

    const subscription = Dimensions.addEventListener('change', onChange);
    return () => subscription?.remove();
  }, []);

  return {
    orientation,
    isPortrait: orientation === 'portrait',
    isLandscape: orientation === 'landscape',
  };
}


