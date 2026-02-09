import { useState, useEffect } from 'react';
import { useWindowDimensions } from './use-window-dimensions';

/**
 * Hook for responsive breakpoints
 */
export function useMedia() {
  const { width } = useWindowDimensions();

  const isMobile = width < 768;
  const isTablet = width >= 768 && width < 1024;
  const isDesktop = width >= 1024;
  const isSmall = width < 375;
  const isMedium = width >= 375 && width < 768;
  const isLarge = width >= 1024;

  return {
    isMobile,
    isTablet,
    isDesktop,
    isSmall,
    isMedium,
    isLarge,
    width,
  };
}

