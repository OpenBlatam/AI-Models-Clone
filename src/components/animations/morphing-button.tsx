import React, { useCallback, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  withSequence,
  interpolate,
  Extrapolate,
  runOnJS,
} from 'react-native-reanimated';
import { useMorphingAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

interface MorphingButtonProps {
  title: string;
  onPress?: () => void;
  onPressAsync?: () => Promise<void>;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'small' | 'medium' | 'large';
  shape?: 'rectangle' | 'rounded' | 'pill' | 'circle';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  testID?: string;
}

export function MorphingButton({
  title,
  onPress,
  onPressAsync,
  variant = 'primary',
  size = 'medium',
  shape = 'rounded',
  disabled = false,
  loading = false,
  icon,
  testID,
}: MorphingButtonProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isPressed, setIsPressed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Animation values
  const scale = useSharedValue(1);
  const rotation = useSharedValue(0);
  const opacity = useSharedValue(1);
  const { animatedStyle: morphStyle, morphTo, progress } = useMorphingAnimation();

  const handlePressIn = useCallback(() => {
    if (disabled || loading || isLoading) return;
    
    setIsPressed(true);
    scale.value = withSpring(0.95, { damping: 15, stiffness: 300 });
    rotation.value = withTiming(2, { duration: 100 });
  }, [disabled, loading, isLoading, scale, rotation]);

  const handlePressOut = useCallback(() => {
    if (disabled || loading || isLoading) return;
    
    setIsPressed(false);
    scale.value = withSpring(1, { damping: 15, stiffness: 300 });
    rotation.value = withTiming(0, { duration: 100 });
  }, [disabled, loading, isLoading, scale, rotation]);

  const handlePress = useCallback(async () => {
    if (disabled || loading || isLoading) return;

    // Morph to loading state
    morphTo(1);
    scale.value = withSequence(
      withTiming(1.05, { duration: 150 }),
      withTiming(1, { duration: 150 })
    );

    if (onPressAsync) {
      setIsLoading(true);
      try {
        await onPressAsync();
      } catch (error) {
        // Handle error with shake animation
        rotation.value = withSequence(
          withTiming(-5, { duration: 50 }),
          withTiming(5, { duration: 50 }),
          withTiming(-5, { duration: 50 }),
          withTiming(5, { duration: 50 }),
          withTiming(0, { duration: 50 })
        );
      } finally {
        setIsLoading(false);
        morphTo(0);
      }
    } else if (onPress) {
      onPress();
      // Quick morph animation for regular press
      morphTo(0.5);
      setTimeout(() => morphTo(0), 200);
    }
  }, [disabled, loading, isLoading, onPress, onPressAsync, morphTo, scale, rotation]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` },
    ],
    opacity: disabled ? 0.5 : opacity.value,
  }));

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: theme.colors.primary,
          borderColor: theme.colors.primary,
          textColor: 'white',
        };
      case 'secondary':
        return {
          backgroundColor: theme.colors.secondary,
          borderColor: theme.colors.secondary,
          textColor: 'white',
        };
      case 'success':
        return {
          backgroundColor: theme.colors.success,
          borderColor: theme.colors.success,
          textColor: 'white',
        };
      case 'warning':
        return {
          backgroundColor: theme.colors.warning,
          borderColor: theme.colors.warning,
          textColor: 'white',
        };
      case 'error':
        return {
          backgroundColor: theme.colors.error,
          borderColor: theme.colors.error,
          textColor: 'white',
        };
      default:
        return {
          backgroundColor: theme.colors.primary,
          borderColor: theme.colors.primary,
          textColor: 'white',
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          paddingHorizontal: 12,
          paddingVertical: 8,
          fontSize: 14,
          minHeight: 32,
        };
      case 'large':
        return {
          paddingHorizontal: 24,
          paddingVertical: 16,
          fontSize: 18,
          minHeight: 56,
        };
      default:
        return {
          paddingHorizontal: 16,
          paddingVertical: 12,
          fontSize: 16,
          minHeight: 44,
        };
    }
  };

  const getShapeStyles = () => {
    switch (shape) {
      case 'rectangle':
        return { borderRadius: 4 };
      case 'pill':
        return { borderRadius: 50 };
      case 'circle':
        return { 
          borderRadius: 50,
          width: getSizeStyles().minHeight,
          height: getSizeStyles().minHeight,
          paddingHorizontal: 0,
        };
      default:
        return { borderRadius: 8 };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();
  const shapeStyles = getShapeStyles();

  const buttonStyle = [
    styles.button,
    {
      backgroundColor: variantStyles.backgroundColor,
      borderColor: variantStyles.borderColor,
      borderWidth: 1,
      ...sizeStyles,
      ...shapeStyles,
    },
    isPressed && styles.pressed,
  ];

  const textStyle = [
    styles.text,
    {
      color: variantStyles.textColor,
      fontSize: sizeStyles.fontSize,
    },
    shape === 'circle' && styles.circleText,
  ];

  const showLoading = loading || isLoading;

  return (
    <Animated.View style={[animatedStyle, morphStyle]}>
      <TouchableOpacity
        testID={testID}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={handlePress}
        disabled={disabled || showLoading}
        activeOpacity={1}
        style={buttonStyle}
      >
        <View style={styles.content}>
          {showLoading ? (
            <ActivityIndicator 
              size="small" 
              color={variantStyles.textColor}
              style={styles.loader}
            />
          ) : (
            <>
              {icon && <View style={styles.icon}>{icon}</View>}
              <Text style={textStyle} numberOfLines={1}>
                {title}
              </Text>
            </>
          )}
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  pressed: {
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  circleText: {
    fontSize: 12,
  },
  icon: {
    marginRight: 8,
  },
  loader: {
    marginRight: 8,
  },
});
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import Animated, {
  useAnimatedStyle,
  useSharedValue,
  withSpring,
  withTiming,
  withSequence,
  interpolate,
  Extrapolate,
  runOnJS,
} from 'react-native-reanimated';
import { useMorphingAnimation } from '../../lib/animations/advanced-animations';
import { useAppStore } from '../../store/app-store';
import { useI18n } from '../../lib/i18n/i18n-config';

interface MorphingButtonProps {
  title: string;
  onPress?: () => void;
  onPressAsync?: () => Promise<void>;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error';
  size?: 'small' | 'medium' | 'large';
  shape?: 'rectangle' | 'rounded' | 'pill' | 'circle';
  disabled?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  testID?: string;
}

export function MorphingButton({
  title,
  onPress,
  onPressAsync,
  variant = 'primary',
  size = 'medium',
  shape = 'rounded',
  disabled = false,
  loading = false,
  icon,
  testID,
}: MorphingButtonProps) {
  const { theme } = useAppStore();
  const { t } = useI18n();
  const [isPressed, setIsPressed] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  // Animation values
  const scale = useSharedValue(1);
  const rotation = useSharedValue(0);
  const opacity = useSharedValue(1);
  const { animatedStyle: morphStyle, morphTo, progress } = useMorphingAnimation();

  const handlePressIn = useCallback(() => {
    if (disabled || loading || isLoading) return;
    
    setIsPressed(true);
    scale.value = withSpring(0.95, { damping: 15, stiffness: 300 });
    rotation.value = withTiming(2, { duration: 100 });
  }, [disabled, loading, isLoading, scale, rotation]);

  const handlePressOut = useCallback(() => {
    if (disabled || loading || isLoading) return;
    
    setIsPressed(false);
    scale.value = withSpring(1, { damping: 15, stiffness: 300 });
    rotation.value = withTiming(0, { duration: 100 });
  }, [disabled, loading, isLoading, scale, rotation]);

  const handlePress = useCallback(async () => {
    if (disabled || loading || isLoading) return;

    // Morph to loading state
    morphTo(1);
    scale.value = withSequence(
      withTiming(1.05, { duration: 150 }),
      withTiming(1, { duration: 150 })
    );

    if (onPressAsync) {
      setIsLoading(true);
      try {
        await onPressAsync();
      } catch (error) {
        // Handle error with shake animation
        rotation.value = withSequence(
          withTiming(-5, { duration: 50 }),
          withTiming(5, { duration: 50 }),
          withTiming(-5, { duration: 50 }),
          withTiming(5, { duration: 50 }),
          withTiming(0, { duration: 50 })
        );
      } finally {
        setIsLoading(false);
        morphTo(0);
      }
    } else if (onPress) {
      onPress();
      // Quick morph animation for regular press
      morphTo(0.5);
      setTimeout(() => morphTo(0), 200);
    }
  }, [disabled, loading, isLoading, onPress, onPressAsync, morphTo, scale, rotation]);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [
      { scale: scale.value },
      { rotate: `${rotation.value}deg` },
    ],
    opacity: disabled ? 0.5 : opacity.value,
  }));

  const getVariantStyles = () => {
    switch (variant) {
      case 'primary':
        return {
          backgroundColor: theme.colors.primary,
          borderColor: theme.colors.primary,
          textColor: 'white',
        };
      case 'secondary':
        return {
          backgroundColor: theme.colors.secondary,
          borderColor: theme.colors.secondary,
          textColor: 'white',
        };
      case 'success':
        return {
          backgroundColor: theme.colors.success,
          borderColor: theme.colors.success,
          textColor: 'white',
        };
      case 'warning':
        return {
          backgroundColor: theme.colors.warning,
          borderColor: theme.colors.warning,
          textColor: 'white',
        };
      case 'error':
        return {
          backgroundColor: theme.colors.error,
          borderColor: theme.colors.error,
          textColor: 'white',
        };
      default:
        return {
          backgroundColor: theme.colors.primary,
          borderColor: theme.colors.primary,
          textColor: 'white',
        };
    }
  };

  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          paddingHorizontal: 12,
          paddingVertical: 8,
          fontSize: 14,
          minHeight: 32,
        };
      case 'large':
        return {
          paddingHorizontal: 24,
          paddingVertical: 16,
          fontSize: 18,
          minHeight: 56,
        };
      default:
        return {
          paddingHorizontal: 16,
          paddingVertical: 12,
          fontSize: 16,
          minHeight: 44,
        };
    }
  };

  const getShapeStyles = () => {
    switch (shape) {
      case 'rectangle':
        return { borderRadius: 4 };
      case 'pill':
        return { borderRadius: 50 };
      case 'circle':
        return { 
          borderRadius: 50,
          width: getSizeStyles().minHeight,
          height: getSizeStyles().minHeight,
          paddingHorizontal: 0,
        };
      default:
        return { borderRadius: 8 };
    }
  };

  const variantStyles = getVariantStyles();
  const sizeStyles = getSizeStyles();
  const shapeStyles = getShapeStyles();

  const buttonStyle = [
    styles.button,
    {
      backgroundColor: variantStyles.backgroundColor,
      borderColor: variantStyles.borderColor,
      borderWidth: 1,
      ...sizeStyles,
      ...shapeStyles,
    },
    isPressed && styles.pressed,
  ];

  const textStyle = [
    styles.text,
    {
      color: variantStyles.textColor,
      fontSize: sizeStyles.fontSize,
    },
    shape === 'circle' && styles.circleText,
  ];

  const showLoading = loading || isLoading;

  return (
    <Animated.View style={[animatedStyle, morphStyle]}>
      <TouchableOpacity
        testID={testID}
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={handlePress}
        disabled={disabled || showLoading}
        activeOpacity={1}
        style={buttonStyle}
      >
        <View style={styles.content}>
          {showLoading ? (
            <ActivityIndicator 
              size="small" 
              color={variantStyles.textColor}
              style={styles.loader}
            />
          ) : (
            <>
              {icon && <View style={styles.icon}>{icon}</View>}
              <Text style={textStyle} numberOfLines={1}>
                {title}
              </Text>
            </>
          )}
        </View>
      </TouchableOpacity>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  button: {
    justifyContent: 'center',
    alignItems: 'center',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  pressed: {
    shadowOpacity: 0.2,
    shadowRadius: 6,
    elevation: 4,
  },
  content: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
  },
  text: {
    fontWeight: '600',
    textAlign: 'center',
  },
  circleText: {
    fontSize: 12,
  },
  icon: {
    marginRight: 8,
  },
  loader: {
    marginRight: 8,
  },
});


