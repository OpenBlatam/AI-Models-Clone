import React, { memo } from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator, ViewStyle, TextStyle } from 'react-native';
import Animated, { useAnimatedStyle, useSharedValue, withSpring } from 'react-native-reanimated';
import { useTheme } from '@/contexts/theme-context';

interface ButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}

const AnimatedTouchableOpacity = Animated.createAnimatedComponent(TouchableOpacity);

function ButtonComponent({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  disabled = false,
  loading = false,
  style,
  textStyle,
  accessibilityLabel,
  accessibilityHint,
}: ButtonProps) {
  const { theme } = useTheme();
  const scale = useSharedValue(1);

  const animatedStyle = useAnimatedStyle(() => ({
    transform: [{ scale: scale.value }],
  }));

  function handlePressIn() {
    scale.value = withSpring(0.95);
  }

  function handlePressOut() {
    scale.value = withSpring(1);
  }

  function handlePress() {
    if (!disabled && !loading) {
      onPress();
    }
  }

  const buttonStyles = [
    styles.button,
    {
      backgroundColor: getBackgroundColor(variant, theme),
      borderColor: getBorderColor(variant, theme),
    },
    variant === 'outline' && styles.outline,
    styles[size],
    (disabled || loading) && { opacity: 0.5 },
    style,
  ];

  const textStyles = [
    styles.text,
    {
      color: getTextColor(variant, theme),
    },
    styles[`${size}Text`],
    textStyle,
  ];

  return (
    <AnimatedTouchableOpacity
      style={[buttonStyles, animatedStyle]}
      onPress={handlePress}
      onPressIn={handlePressIn}
      onPressOut={handlePressOut}
      disabled={disabled || loading}
      activeOpacity={1}
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityState={{ disabled: disabled || loading }}
    >
      {loading ? (
        <ActivityIndicator color={getTextColor(variant, theme)} size="small" />
      ) : (
        <Text style={textStyles}>{title}</Text>
      )}
    </AnimatedTouchableOpacity>
  );
}

function getBackgroundColor(variant: string, theme: ReturnType<typeof useTheme>['theme']): string {
  if (variant === 'outline') return 'transparent';
  return theme.colors[variant as keyof typeof theme.colors] || theme.colors.primary;
}

function getBorderColor(variant: string, theme: ReturnType<typeof useTheme>['theme']): string {
  if (variant === 'outline') return theme.colors.primary;
  return 'transparent';
}

function getTextColor(variant: string, theme: ReturnType<typeof useTheme>['theme']): string {
  if (variant === 'outline') return theme.colors.primary;
  if (variant === 'primary' || variant === 'secondary' || variant === 'danger') return '#FFFFFF';
  return theme.colors.text;
}

export const Button = memo(ButtonComponent);

const styles = StyleSheet.create({
  button: {
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    flexDirection: 'row',
    borderWidth: 1,
  },
  outline: {
    borderWidth: 1.5,
  },
  small: {
    paddingHorizontal: 16,
    paddingVertical: 10,
    minHeight: 36,
  },
  medium: {
    paddingHorizontal: 20,
    paddingVertical: 12,
    minHeight: 44,
  },
  large: {
    paddingHorizontal: 24,
    paddingVertical: 16,
    minHeight: 52,
  },
  text: {
    fontWeight: '600',
  },
  smallText: {
    fontSize: 14,
  },
  mediumText: {
    fontSize: 16,
  },
  largeText: {
    fontSize: 18,
  },
});
