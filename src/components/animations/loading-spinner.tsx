import React, { useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  withSequence,
  interpolate,
  Extrapolate,
} from 'react-native-reanimated';
import { useLoadingAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth } = Dimensions.get('window');

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'spinner' | 'dots' | 'pulse' | 'wave' | 'bounce';
  color?: string;
  text?: string;
  showText?: boolean;
  testID?: string;
}

export function LoadingSpinner({
  size = 'medium',
  variant = 'spinner',
  color,
  text,
  showText = true,
  testID,
}: LoadingSpinnerProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const spinnerColor = color || theme.colors.primary;

  const getSizeValue = () => {
    switch (size) {
      case 'small':
        return 20;
      case 'large':
        return 60;
      default:
        return 40;
    }
  };

  const sizeValue = getSizeValue();

  if (variant === 'spinner') {
    return <SpinnerVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'dots') {
    return <DotsVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'pulse') {
    return <PulseVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'wave') {
    return <WaveVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'bounce') {
    return <BounceVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  return null;
}

// Spinner variant
function SpinnerVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const { animatedStyle, startLoading, stopLoading } = useLoadingAnimation();

  useEffect(() => {
    startLoading();
    return () => stopLoading();
  }, [startLoading, stopLoading]);

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.spinner,
          {
            width: size,
            height: size,
            borderColor: color,
            borderTopColor: 'transparent',
            borderWidth: size * 0.1,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

// Dots variant
function DotsVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const dot1 = useSharedValue(0);
  const dot2 = useSharedValue(0);
  const dot3 = useSharedValue(0);

  useEffect(() => {
    const animateDots = () => {
      dot1.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
      
      dot2.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 400 }),
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
      
      dot3.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 400 }),
          withTiming(0, { duration: 400 }),
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
    };

    animateDots();
  }, [dot1, dot2, dot3]);

  const dot1Style = useAnimatedStyle(() => ({
    opacity: dot1.value,
    transform: [{ scale: interpolate(dot1.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  const dot2Style = useAnimatedStyle(() => ({
    opacity: dot2.value,
    transform: [{ scale: interpolate(dot2.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  const dot3Style = useAnimatedStyle(() => ({
    opacity: dot3.value,
    transform: [{ scale: interpolate(dot3.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  return (
    <View style={styles.container}>
      <View testID={testID} style={styles.dotsContainer}>
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot1Style,
          ]}
        />
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot2Style,
          ]}
        />
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot3Style,
          ]}
        />
      </View>
    </View>
  );
}

// Pulse variant
function PulseVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  useEffect(() => {
    scale.value = withRepeat(
      withSequence(
        withTiming(1.2, { duration: 600 }),
        withTiming(1, { duration: 600 })
      ),
      -1,
      true
    );
    
    opacity.value = withRepeat(
      withSequence(
        withTiming(0.3, { duration: 600 }),
        withTiming(1, { duration: 600 })
      ),
      -1,
      true
    );
  }, [scale, opacity]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.pulse,
          {
            width: size,
            height: size,
            backgroundColor: color,
            borderRadius: size / 2,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

// Wave variant
function WaveVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const wave1 = useSharedValue(0);
  const wave2 = useSharedValue(0);
  const wave3 = useSharedValue(0);
  const wave4 = useSharedValue(0);
  const wave5 = useSharedValue(0);

  useEffect(() => {
    const animateWave = () => {
      wave1.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave2.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave3.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave4.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave5.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
    };

    animateWave();
  }, [wave1, wave2, wave3, wave4, wave5]);

  const getWaveStyle = (wave: Animated.SharedValue<number>) => {
    return useAnimatedStyle(() => ({
      height: interpolate(wave.value, [0, 1], [size * 0.2, size], Extrapolate.CLAMP),
      opacity: interpolate(wave.value, [0, 1], [0.3, 1], Extrapolate.CLAMP),
    }));
  };

  return (
    <View style={styles.container}>
      <View testID={testID} style={styles.waveContainer}>
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave1),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave2),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave3),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave4),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave5),
          ]}
        />
      </View>
    </View>
  );
}

// Bounce variant
function BounceVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const translateY = useSharedValue(0);

  useEffect(() => {
    translateY.value = withRepeat(
      withSequence(
        withTiming(-size * 0.5, { duration: 400 }),
        withTiming(0, { duration: 400 })
      ),
      -1,
      true
    );
  }, [translateY, size]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.bounce,
          {
            width: size,
            height: size,
            backgroundColor: color,
            borderRadius: size / 2,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  spinner: {
    borderRadius: 50,
  },
  dotsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dot: {
    borderRadius: 50,
  },
  pulse: {
    // Styles defined inline
  },
  waveContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 4,
  },
  wave: {
    borderRadius: 2,
  },
  bounce: {
    // Styles defined inline
  },
});
import {
  View,
  Text,
  StyleSheet,
  Dimensions,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withRepeat,
  withTiming,
  withSequence,
  interpolate,
  Extrapolate,
} from 'react-native-reanimated';
import { useLoadingAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

const { width: screenWidth } = Dimensions.get('window');

interface LoadingSpinnerProps {
  size?: 'small' | 'medium' | 'large';
  variant?: 'spinner' | 'dots' | 'pulse' | 'wave' | 'bounce';
  color?: string;
  text?: string;
  showText?: boolean;
  testID?: string;
}

export function LoadingSpinner({
  size = 'medium',
  variant = 'spinner',
  color,
  text,
  showText = true,
  testID,
}: LoadingSpinnerProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const spinnerColor = color || theme.colors.primary;

  const getSizeValue = () => {
    switch (size) {
      case 'small':
        return 20;
      case 'large':
        return 60;
      default:
        return 40;
    }
  };

  const sizeValue = getSizeValue();

  if (variant === 'spinner') {
    return <SpinnerVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'dots') {
    return <DotsVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'pulse') {
    return <PulseVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'wave') {
    return <WaveVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  if (variant === 'bounce') {
    return <BounceVariant size={sizeValue} color={spinnerColor} testID={testID} />;
  }

  return null;
}

// Spinner variant
function SpinnerVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const { animatedStyle, startLoading, stopLoading } = useLoadingAnimation();

  useEffect(() => {
    startLoading();
    return () => stopLoading();
  }, [startLoading, stopLoading]);

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.spinner,
          {
            width: size,
            height: size,
            borderColor: color,
            borderTopColor: 'transparent',
            borderWidth: size * 0.1,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

// Dots variant
function DotsVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const dot1 = useSharedValue(0);
  const dot2 = useSharedValue(0);
  const dot3 = useSharedValue(0);

  useEffect(() => {
    const animateDots = () => {
      dot1.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
      
      dot2.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 400 }),
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
      
      dot3.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 400 }),
          withTiming(0, { duration: 400 }),
          withTiming(1, { duration: 400 }),
          withTiming(0, { duration: 400 })
        ),
        -1,
        false
      );
    };

    animateDots();
  }, [dot1, dot2, dot3]);

  const dot1Style = useAnimatedStyle(() => ({
    opacity: dot1.value,
    transform: [{ scale: interpolate(dot1.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  const dot2Style = useAnimatedStyle(() => ({
    opacity: dot2.value,
    transform: [{ scale: interpolate(dot2.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  const dot3Style = useAnimatedStyle(() => ({
    opacity: dot3.value,
    transform: [{ scale: interpolate(dot3.value, [0, 1], [0.5, 1], Extrapolate.CLAMP) }],
  }));

  return (
    <View style={styles.container}>
      <View testID={testID} style={styles.dotsContainer}>
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot1Style,
          ]}
        />
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot2Style,
          ]}
        />
        <Animated.View
          style={[
            styles.dot,
            { width: size * 0.3, height: size * 0.3, backgroundColor: color },
            dot3Style,
          ]}
        />
      </View>
    </View>
  );
}

// Pulse variant
function PulseVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const scale = useSharedValue(1);
  const opacity = useSharedValue(1);

  useEffect(() => {
    scale.value = withRepeat(
      withSequence(
        withTiming(1.2, { duration: 600 }),
        withTiming(1, { duration: 600 })
      ),
      -1,
      true
    );
    
    opacity.value = withRepeat(
      withSequence(
        withTiming(0.3, { duration: 600 }),
        withTiming(1, { duration: 600 })
      ),
      -1,
      true
    );
  }, [scale, opacity]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
    opacity: opacity.value,
  }));

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.pulse,
          {
            width: size,
            height: size,
            backgroundColor: color,
            borderRadius: size / 2,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

// Wave variant
function WaveVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const wave1 = useSharedValue(0);
  const wave2 = useSharedValue(0);
  const wave3 = useSharedValue(0);
  const wave4 = useSharedValue(0);
  const wave5 = useSharedValue(0);

  useEffect(() => {
    const animateWave = () => {
      wave1.value = withRepeat(
        withSequence(
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave2.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave3.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave4.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
      
      wave5.value = withRepeat(
        withSequence(
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(0, { duration: 200 }),
          withTiming(1, { duration: 200 }),
          withTiming(0, { duration: 200 })
        ),
        -1,
        false
      );
    };

    animateWave();
  }, [wave1, wave2, wave3, wave4, wave5]);

  const getWaveStyle = (wave: Animated.SharedValue<number>) => {
    return useAnimatedStyle(() => ({
      height: interpolate(wave.value, [0, 1], [size * 0.2, size], Extrapolate.CLAMP),
      opacity: interpolate(wave.value, [0, 1], [0.3, 1], Extrapolate.CLAMP),
    }));
  };

  return (
    <View style={styles.container}>
      <View testID={testID} style={styles.waveContainer}>
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave1),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave2),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave3),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave4),
          ]}
        />
        <Animated.View
          style={[
            styles.wave,
            { width: size * 0.1, backgroundColor: color },
            getWaveStyle(wave5),
          ]}
        />
      </View>
    </View>
  );
}

// Bounce variant
function BounceVariant({ size, color, testID }: { size: number; color: string; testID?: string }) {
  const translateY = useSharedValue(0);

  useEffect(() => {
    translateY.value = withRepeat(
      withSequence(
        withTiming(-size * 0.5, { duration: 400 }),
        withTiming(0, { duration: 400 })
      ),
      -1,
      true
    );
  }, [translateY, size]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ translateY: translateY.value }],
  }));

  return (
    <View style={styles.container}>
      <Animated.View
        testID={testID}
        style={[
          styles.bounce,
          {
            width: size,
            height: size,
            backgroundColor: color,
            borderRadius: size / 2,
          },
          animatedStyle,
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    justifyContent: 'center',
    alignItems: 'center',
  },
  spinner: {
    borderRadius: 50,
  },
  dotsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  dot: {
    borderRadius: 50,
  },
  pulse: {
    // Styles defined inline
  },
  waveContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: 4,
  },
  wave: {
    borderRadius: 2,
  },
  bounce: {
    // Styles defined inline
  },
});


