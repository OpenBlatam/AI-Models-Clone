import React, { useMemo, useCallback, memo } from 'react';
import { 
  TouchableOpacity, 
  Text, 
  StyleSheet, 
  ActivityIndicator, 
  ViewStyle, 
  TextStyle,
  AccessibilityInfo,
  Platform 
} from 'react-native';
import { useWindowDimensions } from 'react-native';
import { useColorScheme } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large' | 'xl';
  isLoading?: boolean;
  isDisabled?: boolean;
  hasIcon?: boolean;
  iconName?: string;
  iconPosition?: 'left' | 'right';
  canShowLoading?: boolean;
  shouldShowSpinner?: boolean;
  hasRoundedCorners?: boolean;
  isFullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  testID?: string;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const BUTTON_VARIANTS = {
  primary: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
    textColor: '#FFFFFF',
    pressedColor: '#0056CC',
  },
  secondary: {
    backgroundColor: '#F2F2F7',
    borderColor: '#F2F2F7',
    textColor: '#000000',
    pressedColor: '#E5E5EA',
  },
  outline: {
    backgroundColor: 'transparent',
    borderColor: '#007AFF',
    textColor: '#007AFF',
    pressedColor: '#E3F2FD',
  },
  ghost: {
    backgroundColor: 'transparent',
    borderColor: 'transparent',
    textColor: '#007AFF',
    pressedColor: '#F2F2F7',
  },
  danger: {
    backgroundColor: '#FF3B30',
    borderColor: '#FF3B30',
    textColor: '#FFFFFF',
    pressedColor: '#D70015',
  },
  success: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
    textColor: '#FFFFFF',
    pressedColor: '#28A745',
  },
  warning: {
    backgroundColor: '#FF9500',
    borderColor: '#FF9500',
    textColor: '#FFFFFF',
    pressedColor: '#E6850E',
  },
} as const;

const BUTTON_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    fontSize: 14,
    borderRadius: 6,
    minHeight: 36,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    fontSize: 16,
    borderRadius: 8,
    minHeight: 44,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    fontSize: 18,
    borderRadius: 10,
    minHeight: 52,
  },
  xl: {
    paddingVertical: 20,
    paddingHorizontal: 40,
    fontSize: 20,
    borderRadius: 12,
    minHeight: 60,
  },
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const getButtonStyle = (props: OptimizedButtonProps, isDark: boolean, width: number): ViewStyle => {
  const { variant = 'primary', size = 'medium', isDisabled, hasRoundedCorners, isFullWidth } = props;
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  // Responsive adjustments
  const responsivePadding = width < 375 ? sizeStyle.paddingHorizontal * 0.8 : sizeStyle.paddingHorizontal;
  const responsiveFontSize = width < 375 ? sizeStyle.fontSize * 0.9 : sizeStyle.fontSize;
  
  return {
    backgroundColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.backgroundColor,
    borderColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.borderColor,
    paddingVertical: sizeStyle.paddingVertical,
    paddingHorizontal: responsivePadding,
    borderRadius: hasRoundedCorners ? 25 : sizeStyle.borderRadius,
    width: isFullWidth ? '100%' : 'auto',
    opacity: isDisabled ? 0.6 : 1,
    minHeight: sizeStyle.minHeight,
    shadowColor: isDark ? '#000000' : '#000000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: isDisabled ? 0 : 0.1,
    shadowRadius: 4,
    elevation: isDisabled ? 0 : 2,
  };
};

const getTextStyle = (props: OptimizedButtonProps, isDark: boolean, width: number): TextStyle => {
  const { variant = 'primary', size = 'medium', isDisabled } = props;
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  // Responsive font size
  const responsiveFontSize = width < 375 ? sizeStyle.fontSize * 0.9 : sizeStyle.fontSize;
  
  return {
    color: isDisabled 
      ? (isDark ? '#8E8E93' : '#8E8E93') 
      : variantStyle.textColor,
    fontSize: responsiveFontSize,
    fontWeight: '600' as const,
    textAlign: 'center' as const,
    includeFontPadding: false,
    textAlignVertical: 'center',
  };
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const ButtonContent = memo<{ props: OptimizedButtonProps; isDark: boolean; width: number }>(({ props, isDark, width }) => {
  const { 
    title, 
    isLoading, 
    hasIcon, 
    iconName, 
    iconPosition = 'left',
    canShowLoading = true,
    shouldShowSpinner = true 
  } = props;

  const isShowingLoading = isLoading && canShowLoading && shouldShowSpinner;

  if (isShowingLoading) {
    return (
      <ActivityIndicator 
        size="small" 
        color={getTextStyle(props, isDark, width).color} 
      />
    );
  }

  return (
    <>
      {hasIcon && iconName && iconPosition === 'left' && (
        <Text style={[styles.icon, { color: getTextStyle(props, isDark, width).color }]}>
          {iconName}
        </Text>
      )}
      <Text style={[styles.buttonText, getTextStyle(props, isDark, width)]}>
        {title}
      </Text>
      {hasIcon && iconName && iconPosition === 'right' && (
        <Text style={[styles.icon, { color: getTextStyle(props, isDark, width).color }]}>
          {iconName}
        </Text>
      )}
    </>
  );
});

ButtonContent.displayName = 'ButtonContent';

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedButton = memo<OptimizedButtonProps>(({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  isDisabled = false,
  hasIcon = false,
  iconName,
  iconPosition = 'left',
  canShowLoading = true,
  shouldShowSpinner = true,
  hasRoundedCorners = false,
  isFullWidth = false,
  style,
  textStyle,
  accessibilityLabel,
  accessibilityHint,
  testID,
}) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';

  const isButtonDisabled = isDisabled || isLoading;
  const shouldHandlePress = !isButtonDisabled;

  // Memoized styles for performance
  const buttonStyle = useMemo(() => 
    getButtonStyle({ variant, size, isDisabled: isButtonDisabled, hasRoundedCorners, isFullWidth }, isDark, width), 
    [variant, size, isButtonDisabled, hasRoundedCorners, isFullWidth, isDark, width]
  );

  const textStyleMemo = useMemo(() => 
    getTextStyle({ variant, size, isDisabled: isButtonDisabled }, isDark, width), 
    [variant, size, isButtonDisabled, isDark, width]
  );

  // Memoized accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || `${title} button`,
    accessibilityHint: accessibilityHint || `Tap to ${title.toLowerCase()}`,
    accessibilityRole: 'button' as const,
    accessibilityState: { 
      disabled: isButtonDisabled,
      busy: isLoading 
    },
    accessibilityActions: [{ name: 'activate', label: `Activate ${title}` }],
  }), [accessibilityLabel, accessibilityHint, title, isButtonDisabled, isLoading]);

  // Memoized press handler
  const handlePress = useCallback(() => {
    if (shouldHandlePress) {
      // Haptic feedback for iOS
      if (Platform.OS === 'ios') {
        const { HapticFeedback } = require('expo-haptics');
        HapticFeedback.impactAsync(HapticFeedback.ImpactFeedbackStyle.Light);
      }
      onPress();
    }
  }, [shouldHandlePress, onPress]);

  // Memoized long press handler for accessibility
  const handleLongPress = useCallback(() => {
    if (shouldHandlePress) {
      AccessibilityInfo.announceForAccessibility(`${title} button long pressed`);
    }
  }, [shouldHandlePress, title]);

  return (
    <TouchableOpacity
      style={[
        styles.button,
        buttonStyle,
        style,
      ]}
      onPress={handlePress}
      onLongPress={handleLongPress}
      disabled={isButtonDisabled}
      activeOpacity={0.8}
      testID={testID}
      {...accessibilityProps}
    >
      <ButtonContent 
        props={{ 
          title, 
          isLoading, 
          hasIcon, 
          iconName, 
          iconPosition, 
          canShowLoading, 
          shouldShowSpinner,
          variant,
          size,
          isDisabled: isButtonDisabled 
        }} 
        isDark={isDark}
        width={width}
      />
    </TouchableOpacity>
  );
});

OptimizedButton.displayName = 'OptimizedButton';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    minHeight: 44,
  },
  buttonText: {
    fontWeight: '600',
    textAlign: 'center',
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  icon: {
    fontSize: 16,
    marginHorizontal: 4,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
}); 
  const isDark = colorScheme === 'dark';

  const isButtonDisabled = isDisabled || isLoading;
  const shouldHandlePress = !isButtonDisabled;

  // Memoized styles for performance
  const buttonStyle = useMemo(() => 
    getButtonStyle({ variant, size, isDisabled: isButtonDisabled, hasRoundedCorners, isFullWidth }, isDark, width), 
    [variant, size, isButtonDisabled, hasRoundedCorners, isFullWidth, isDark, width]
  );

  const textStyleMemo = useMemo(() => 
    getTextStyle({ variant, size, isDisabled: isButtonDisabled }, isDark, width), 
    [variant, size, isButtonDisabled, isDark, width]
  );

  // Memoized accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || `${title} button`,
    accessibilityHint: accessibilityHint || `Tap to ${title.toLowerCase()}`,
    accessibilityRole: 'button' as const,
    accessibilityState: { 
      disabled: isButtonDisabled,
      busy: isLoading 
    },
    accessibilityActions: [{ name: 'activate', label: `Activate ${title}` }],
  }), [accessibilityLabel, accessibilityHint, title, isButtonDisabled, isLoading]);

  // Memoized press handler
  const handlePress = useCallback(() => {
    if (shouldHandlePress) {
      // Haptic feedback for iOS
      if (Platform.OS === 'ios') {
        const { HapticFeedback } = require('expo-haptics');
        HapticFeedback.impactAsync(HapticFeedback.ImpactFeedbackStyle.Light);
      }
      onPress();
    }
  }, [shouldHandlePress, onPress]);

  // Memoized long press handler for accessibility
  const handleLongPress = useCallback(() => {
    if (shouldHandlePress) {
      AccessibilityInfo.announceForAccessibility(`${title} button long pressed`);
    }
  }, [shouldHandlePress, title]);

  return (
    <TouchableOpacity
      style={[
        styles.button,
        buttonStyle,
        style,
      ]}
      onPress={handlePress}
      onLongPress={handleLongPress}
      disabled={isButtonDisabled}
      activeOpacity={0.8}
      testID={testID}
      {...accessibilityProps}
    >
      <ButtonContent 
        props={{ 
          title, 
          isLoading, 
          hasIcon, 
          iconName, 
          iconPosition, 
          canShowLoading, 
          shouldShowSpinner,
          variant,
          size,
          isDisabled: isButtonDisabled 
        }} 
        isDark={isDark}
        width={width}
      />
    </TouchableOpacity>
  );
});

OptimizedButton.displayName = 'OptimizedButton';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  button: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 1,
    minHeight: 44,
  },
  buttonText: {
    fontWeight: '600',
    textAlign: 'center',
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  icon: {
    fontSize: 16,
    marginHorizontal: 4,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
}); 