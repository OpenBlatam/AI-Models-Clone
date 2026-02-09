import { useSharedValue, useAnimatedGestureHandler } from 'react-native-reanimated';
import { PanGestureHandlerGestureEvent } from 'react-native-gesture-handler';

interface GestureCallbacks {
  onStart?: () => void;
  onActive?: (translationX: number, translationY: number) => void;
  onEnd?: (velocityX: number, velocityY: number) => void;
}

/**
 * Hook for handling pan gestures
 */
export function useGesture(callbacks: GestureCallbacks = {}) {
  const translateX = useSharedValue(0);
  const translateY = useSharedValue(0);

  const gestureHandler = useAnimatedGestureHandler<PanGestureHandlerGestureEvent>({
    onStart: () => {
      callbacks.onStart?.();
    },
    onActive: (event) => {
      translateX.value = event.translationX;
      translateY.value = event.translationY;
      callbacks.onActive?.(event.translationX, event.translationY);
    },
    onEnd: (event) => {
      callbacks.onEnd?.(event.velocityX, event.velocityY);
    },
  });

  return {
    translateX,
    translateY,
    gestureHandler,
  };
}


