import { useState, useEffect } from 'react';
import { Keyboard, KeyboardEvent } from 'react-native';

interface KeyboardState {
  isVisible: boolean;
  height: number;
}

/**
 * Hook for tracking keyboard visibility and height
 */
export function useKeyboard() {
  const [keyboard, setKeyboard] = useState<KeyboardState>({
    isVisible: false,
    height: 0,
  });

  useEffect(() => {
    const showSubscription = Keyboard.addListener('keyboardDidShow', (e: KeyboardEvent) => {
      setKeyboard({
        isVisible: true,
        height: e.endCoordinates.height,
      });
    });

    const hideSubscription = Keyboard.addListener('keyboardDidHide', () => {
      setKeyboard({
        isVisible: false,
        height: 0,
      });
    });

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  return keyboard;
}


