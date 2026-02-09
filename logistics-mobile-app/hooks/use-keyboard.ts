import { useEffect, useState } from 'react';
import { Keyboard, KeyboardEvent } from 'react-native';

interface KeyboardState {
  isVisible: boolean;
  height: number;
}

export function useKeyboard() {
  const [keyboardState, setKeyboardState] = useState<KeyboardState>({
    isVisible: false,
    height: 0,
  });

  useEffect(() => {
    function onKeyboardShow(e: KeyboardEvent) {
      setKeyboardState({
        isVisible: true,
        height: e.endCoordinates.height,
      });
    }

    function onKeyboardHide() {
      setKeyboardState({
        isVisible: false,
        height: 0,
      });
    }

    const showSubscription = Keyboard.addListener('keyboardDidShow', onKeyboardShow);
    const hideSubscription = Keyboard.addListener('keyboardDidHide', onKeyboardHide);

    return () => {
      showSubscription.remove();
      hideSubscription.remove();
    };
  }, []);

  function dismiss() {
    Keyboard.dismiss();
  }

  return {
    ...keyboardState,
    dismiss,
  };
}


