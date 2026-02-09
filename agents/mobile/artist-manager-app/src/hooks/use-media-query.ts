import { useState, useEffect } from 'react';
import { useWindowDimensions } from './use-window-dimensions';

interface MediaQueryOptions {
  minWidth?: number;
  maxWidth?: number;
  minHeight?: number;
  maxHeight?: number;
}

/**
 * Hook for responsive design based on window dimensions
 */
export function useMediaQuery(options: MediaQueryOptions): boolean {
  const { width, height } = useWindowDimensions();
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    const {
      minWidth = 0,
      maxWidth = Infinity,
      minHeight = 0,
      maxHeight = Infinity,
    } = options;

    const matchesWidth = width >= minWidth && width <= maxWidth;
    const matchesHeight = height >= minHeight && height <= maxHeight;

    setMatches(matchesWidth && matchesHeight);
  }, [width, height, options]);

  return matches;
}


