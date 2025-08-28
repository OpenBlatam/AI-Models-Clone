import React, { useCallback, useMemo } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  ViewStyle,
  TextStyle,
} from 'react-native';
import { LinearGradient } from 'react-native-linear-gradient';
import { BlurView } from 'react-native-blur';

interface OptimizedCardProps {
  title?: string;
  subtitle?: string;
  content?: React.ReactNode;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  onPress?: () => void;
  variant?: 'default' | 'elevated' | 'outlined' | 'gradient';
  size?: 'small' | 'medium' | 'large';
  isPressable?: boolean;
  isDisabled?: boolean;
  style?: ViewStyle;
  contentStyle?: ViewStyle;
  titleStyle?: TextStyle;
  subtitleStyle?: TextStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
}

export const OptimizedCard: React.FC<OptimizedCardProps> = ({
  title,
  subtitle,
  content,
  leftIcon,
  rightIcon,
  onPress,
  variant = 'default',
  size = 'medium',
  isPressable = false,
  isDisabled = false,
  style,
  contentStyle,
  titleStyle,
  subtitleStyle,
  accessibilityLabel,
  accessibilityHint,
}) => {
  const handlePress = useCallback(() => {
    if (!isDisabled && isPressable && onPress) {
      onPress();
    }
  }, [isDisabled, isPressable, onPress]);

  const getCardStyle = useCallback((): ViewStyle => {
    const baseStyle: ViewStyle = {
      borderRadius: 12,
      overflow: 'hidden',
      ...style,
    };

    const sizeStyles: Record<string, ViewStyle> = {
      small: { padding: 12 },
      medium: { padding: 16 },
      large: { padding: 20 },
    };

    const variantStyles: Record<string, ViewStyle> = {
      default: {
        backgroundColor: '#FFFFFF',
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 3,
      },
      elevated: {
        backgroundColor: '#FFFFFF',
        shadowColor: '#000000',
        shadowOffset: { width: 0, height: 8 },
        shadowOpacity: 0.15,
        shadowRadius: 12,
        elevation: 8,
      },
      outlined: {
        backgroundColor: '#FFFFFF',
        borderWidth: 1,
        borderColor: '#E5E5EA',
      },
      gradient: {
        backgroundColor: 'transparent',
      },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
      ...variantStyles[variant],
      opacity: isDisabled ? 0.6 : 1,
    };
  }, [variant, size, isDisabled, style]);

  const getTitleStyle = useCallback((): TextStyle => {
    const baseStyle: TextStyle = {
      fontSize: 16,
      fontWeight: '600',
      color: '#000000',
      marginBottom: 4,
      ...titleStyle,
    };

    const sizeStyles: Record<string, TextStyle> = {
      small: { fontSize: 14 },
      medium: { fontSize: 16 },
      large: { fontSize: 18 },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
    };
  }, [size, titleStyle]);

  const getSubtitleStyle = useCallback((): TextStyle => {
    const baseStyle: TextStyle = {
      fontSize: 14,
      color: '#8E8E93',
      marginBottom: 8,
      ...subtitleStyle,
    };

    const sizeStyles: Record<string, TextStyle> = {
      small: { fontSize: 12 },
      medium: { fontSize: 14 },
      large: { fontSize: 16 },
    };

    return {
      ...baseStyle,
      ...sizeStyles[size],
    };
  }, [size, subtitleStyle]);

  const renderHeader = useMemo(() => {
    if (!title && !subtitle && !leftIcon && !rightIcon) {
      return null;
    }

    return (
      <View style={styles.header}>
        {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
        <View style={styles.headerContent}>
          {title && <Text style={getTitleStyle()}>{title}</Text>}
          {subtitle && <Text style={getSubtitleStyle()}>{subtitle}</Text>}
        </View>
        {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
      </View>
    );
  }, [title, subtitle, leftIcon, rightIcon, getTitleStyle, getSubtitleStyle]);

  const renderContent = useMemo(() => {
    if (!content) return null;
    return <View style={[styles.content, contentStyle]}>{content}</View>;
  }, [content, contentStyle]);

  const renderGradientBackground = useMemo(() => {
    if (variant !== 'gradient') return null;
    
    return (
      <LinearGradient
        colors={['#667eea', '#764ba2']}
        style={StyleSheet.absoluteFillObject}
      />
    );
  }, [variant]);

  const CardContainer = isPressable ? TouchableOpacity : View;

  return (
    <CardContainer
      style={getCardStyle()}
      onPress={handlePress}
      disabled={isDisabled}
      accessible={true}
      accessibilityLabel={accessibilityLabel || title}
      accessibilityHint={accessibilityHint}
      accessibilityRole={isPressable ? 'button' : undefined}
      accessibilityState={{ disabled: isDisabled }}
    >
      {renderGradientBackground}
      {renderHeader}
      {renderContent}
    </CardContainer>
  );
};

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  leftIcon: {
    marginRight: 12,
    marginTop: 2,
  },
  headerContent: {
    flex: 1,
  },
  rightIcon: {
    marginLeft: 12,
    marginTop: 2,
  },
  content: {
    flex: 1,
  },
}); 