import { useRef, useCallback, useMemo } from 'react';
import { Animated, Easing, ViewStyle } from 'react-native';

interface AnimationConfig {
  duration?: number;
  easing?: Animated.EasingFunction;
  delay?: number;
  useNativeDriver?: boolean;
}

interface UseOptimizedAnimationOptions {
  initialValue?: number;
  targetValue?: number;
  config?: AnimationConfig;
}

interface AnimationControls {
  value: Animated.Value;
  start: (toValue?: number, config?: AnimationConfig) => void;
  stop: () => void;
  reset: () => void;
  interpolate: (inputRange: number[], outputRange: any[]) => Animated.AnimatedInterpolation;
}

export const useOptimizedAnimation = ({
  initialValue = 0,
  targetValue = 1,
  config = {},
}: UseOptimizedAnimationOptions = {}): AnimationControls => {
  const animationValue = useRef(new Animated.Value(initialValue)).current;
  const animationRef = useRef<Animated.CompositeAnimation | null>(null);

  const defaultConfig: AnimationConfig = {
    duration: 300,
    easing: Easing.inOut(Easing.ease),
    delay: 0,
    useNativeDriver: true,
    ...config,
  };

  const start = useCallback((toValue?: number, customConfig?: AnimationConfig) => {
    const finalConfig = { ...defaultConfig, ...customConfig };
    const finalValue = toValue ?? targetValue;

    // Stop any ongoing animation
    if (animationRef.current) {
      animationRef.current.stop();
    }

    animationRef.current = Animated.timing(animationValue, {
      toValue: finalValue,
      duration: finalConfig.duration!,
      easing: finalConfig.easing!,
      delay: finalConfig.delay!,
      useNativeDriver: finalConfig.useNativeDriver!,
    });

    animationRef.current.start();
  }, [animationValue, targetValue, defaultConfig]);

  const stop = useCallback(() => {
    if (animationRef.current) {
      animationRef.current.stop();
      animationRef.current = null;
    }
  }, []);

  const reset = useCallback(() => {
    stop();
    animationValue.setValue(initialValue);
  }, [stop, animationValue, initialValue]);

  const interpolate = useCallback((inputRange: number[], outputRange: any[]) => {
    return animationValue.interpolate({
      inputRange,
      outputRange,
      extrapolate: 'clamp',
    });
  }, [animationValue]);

  const controls = useMemo((): AnimationControls => ({
    value: animationValue,
    start,
    stop,
    reset,
    interpolate,
  }), [animationValue, start, stop, reset, interpolate]);

  return controls;
};

// Predefined animation hooks
export const useFadeAnimation = (config?: AnimationConfig) => {
  return useOptimizedAnimation({
    initialValue: 0,
    targetValue: 1,
    config: { duration: 300, ...config },
  });
};

export const useSlideAnimation = (config?: AnimationConfig) => {
  return useOptimizedAnimation({
    initialValue: 100,
    targetValue: 0,
    config: { duration: 400, easing: Easing.out(Easing.cubic), ...config },
  });
};

export const useScaleAnimation = (config?: AnimationConfig) => {
  return useOptimizedAnimation({
    initialValue: 0,
    targetValue: 1,
    config: { duration: 300, easing: Easing.elastic(1), ...config },
  });
};

export const useRotationAnimation = (config?: AnimationConfig) => {
  return useOptimizedAnimation({
    initialValue: 0,
    targetValue: 360,
    config: { duration: 1000, easing: Easing.linear, ...config },
  });
};

// Animation style helpers
export const createAnimatedStyle = (
  animation: AnimationControls,
  styleMap: Record<string, { inputRange: number[]; outputRange: any[] }>
): ViewStyle => {
  const animatedStyle: any = {};
  
  Object.entries(styleMap).forEach(([property, config]) => {
    animatedStyle[property] = animation.interpolate(config.inputRange, config.outputRange);
  });
  
  return animatedStyle;
};

// Common animation patterns
export const fadeInStyle = (animation: AnimationControls): ViewStyle => {
  return createAnimatedStyle(animation, {
    opacity: {
      inputRange: [0, 1],
      outputRange: [0, 1],
    },
  });
};

export const slideUpStyle = (animation: AnimationControls): ViewStyle => {
  return createAnimatedStyle(animation, {
    transform: [{
      translateY: {
        inputRange: [0, 1],
        outputRange: [50, 0],
      },
    }],
    opacity: {
      inputRange: [0, 1],
      outputRange: [0, 1],
    },
  });
};

export const scaleInStyle = (animation: AnimationControls): ViewStyle => {
  return createAnimatedStyle(animation, {
    transform: [{
      scale: {
        inputRange: [0, 1],
        outputRange: [0, 1],
      },
    }],
  });
}; 