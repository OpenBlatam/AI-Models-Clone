import { useSharedValue, useAnimatedStyle, withSpring, withTiming, Easing } from 'react-native-reanimated';

interface AnimationConfig {
  duration?: number;
  damping?: number;
  stiffness?: number;
  easing?: (value: number) => number;
}

/**
 * Hook for creating animated values with common animations
 */
export function useAnimation(initialValue = 0) {
  const animatedValue = useSharedValue(initialValue);

  const animateTo = (toValue: number, config: AnimationConfig = {}) => {
    const { duration = 300, damping, stiffness, easing } = config;

    if (damping && stiffness) {
      animatedValue.value = withSpring(toValue, { damping, stiffness });
    } else if (easing) {
      animatedValue.value = withTiming(toValue, { duration, easing });
    } else {
      animatedValue.value = withTiming(toValue, {
        duration,
        easing: Easing.out(Easing.ease),
      });
    }
  };

  const fadeIn = (config?: AnimationConfig) => {
    animateTo(1, config);
  };

  const fadeOut = (config?: AnimationConfig) => {
    animateTo(0, config);
  };

  const slideIn = (distance: number, config?: AnimationConfig) => {
    animatedValue.value = withSpring(distance, config);
  };

  const slideOut = (distance: number, config?: AnimationConfig) => {
    animatedValue.value = withSpring(distance, config);
  };

  const reset = () => {
    animatedValue.value = initialValue;
  };

  return {
    animatedValue,
    animateTo,
    fadeIn,
    fadeOut,
    slideIn,
    slideOut,
    reset,
  };
}


