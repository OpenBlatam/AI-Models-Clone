import { useState, useEffect } from 'react';
import { Dimensions, ScaledSize } from 'react-native';

interface WindowDimensions {
  width: number;
  height: number;
  scale: number;
  fontScale: number;
}

export function useWindowDimensions(): WindowDimensions {
  const [dimensions, setDimensions] = useState(() => {
    const { width, height, scale, fontScale } = Dimensions.get('window');
    return { width, height, scale, fontScale };
  });

  useEffect(() => {
    function onChange({ window }: { window: ScaledSize }) {
      setDimensions({
        width: window.width,
        height: window.height,
        scale: window.scale,
        fontScale: window.fontScale,
      });
    }

    const subscription = Dimensions.addEventListener('change', onChange);
    return () => subscription?.remove();
  }, []);

  return dimensions;
}


