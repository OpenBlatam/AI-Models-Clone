import React, { useCallback, useMemo } from 'react';
import { View, Text, StyleSheet, ViewStyle, TextStyle } from 'react-native';

interface OptimizedBadgeProps {
  text: string;
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'info';
  size?: 'small' | 'medium' | 'large';
  isRounded?: boolean;
  isOutlined?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
}

const variantStyles = {
  primary: { backgroundColor: '#007AFF', textColor: '#FFFFFF' },
  secondary: { backgroundColor: '#8E8E93', textColor: '#FFFFFF' },
  success: { backgroundColor: '#34C759', textColor: '#FFFFFF' },
  warning: { backgroundColor: '#FF9500', textColor: '#FFFFFF' },
  error: { backgroundColor: '#FF3B30', textColor: '#FFFFFF' },
  info: { backgroundColor: '#5AC8FA', textColor: '#FFFFFF' },
} as const;

const sizeStyles = {
  small: { paddingHorizontal: 6, paddingVertical: 2, fontSize: 10 },
  medium: { paddingHorizontal: 8, paddingVertical: 4, fontSize: 12 },
  large: { paddingHorizontal: 12, paddingVertical: 6, fontSize: 14 },
} as const;

export const OptimizedBadge: React.FC<OptimizedBadgeProps> = ({
  text,
  variant = 'primary',
  size = 'medium',
  isRounded = false,
  isOutlined = false,
  style,
  textStyle,
  accessibilityLabel,
}) => {
  const getBadgeStyle = useCallback((): ViewStyle => {
    const baseStyle: ViewStyle = {
      borderRadius: isRounded ? 20 : 4,
      alignItems: 'center',
      justifyContent: 'center',
      ...sizeStyles[size],
    };

    if (isOutlined) {
      return {
        ...baseStyle,
        backgroundColor: 'transparent',
        borderWidth: 1,
        borderColor: variantStyles[variant].backgroundColor,
      };
    }

    return {
      ...baseStyle,
      backgroundColor: variantStyles[variant].backgroundColor,
    };
  }, [variant, size, isRounded, isOutlined]);

  const getTextStyle = useCallback((): TextStyle => {
    const baseStyle: TextStyle = {
      fontSize: sizeStyles[size].fontSize,
      fontWeight: '600',
      textAlign: 'center',
    };

    if (isOutlined) {
      return {
        ...baseStyle,
        color: variantStyles[variant].backgroundColor,
      };
    }

    return {
      ...baseStyle,
      color: variantStyles[variant].textColor,
    };
  }, [variant, size, isOutlined]);

  const badgeStyle = useMemo(() => [getBadgeStyle(), style], [getBadgeStyle, style]);
  const textStyleMemo = useMemo(() => [getTextStyle(), textStyle], [getTextStyle, textStyle]);

  return (
    <View
      style={badgeStyle}
      accessible={true}
      accessibilityLabel={accessibilityLabel || `Badge: ${text}`}
      accessibilityRole="text"
    >
      <Text style={textStyleMemo}>{text}</Text>
    </View>
  );
}; 