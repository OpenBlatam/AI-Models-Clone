import { useState, useCallback } from 'react';
import { AccessibilityInfo } from 'react-native';

/**
 * Hook for accessibility features
 */
export function useAccessibility() {
  const [isScreenReaderEnabled, setIsScreenReaderEnabled] = useState(false);
  const [reduceMotionEnabled, setReduceMotionEnabled] = useState(false);
  const [reduceTransparencyEnabled, setReduceTransparencyEnabled] = useState(false);

  const checkScreenReader = useCallback(async () => {
    const enabled = await AccessibilityInfo.isScreenReaderEnabled();
    setIsScreenReaderEnabled(enabled);
  }, []);

  const checkReduceMotion = useCallback(async () => {
    const enabled = await AccessibilityInfo.isReduceMotionEnabled();
    setReduceMotionEnabled(enabled);
  }, []);

  const checkReduceTransparency = useCallback(async () => {
    const enabled = await AccessibilityInfo.isReduceTransparencyEnabled();
    setReduceTransparencyEnabled(enabled);
  }, []);

  const announceForAccessibility = useCallback((message: string) => {
    AccessibilityInfo.announceForAccessibility(message);
  }, []);

  return {
    isScreenReaderEnabled,
    reduceMotionEnabled,
    reduceTransparencyEnabled,
    checkScreenReader,
    checkReduceMotion,
    checkReduceTransparency,
    announceForAccessibility,
  };
}


