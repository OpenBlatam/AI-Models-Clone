import React, { useMemo, useCallback, memo } from 'react';
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  AccessibilityInfo,
  Platform,
  useWindowDimensions,
} from 'react-native';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from '../../lib/i18n/i18n-config';

// ============================================================================
// TYPES
// ============================================================================

interface AccessibleButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large' | 'xl';
  isLoading?: boolean;
  isDisabled?: boolean;
  hasIcon?: boolean;
  iconName?: keyof typeof Ionicons.glyphMap;
  iconPosition?: 'left' | 'right';
  isFullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  // Accessibility props
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'link' | 'menuitem' | 'tab' | 'switch' | 'checkbox' | 'radio';
  accessibilityState?: {
    disabled?: boolean;
    selected?: boolean;
    checked?: boolean | 'mixed';
    busy?: boolean;
    expanded?: boolean;
  };
  accessibilityActions?: Array<{
    name: string;
    label?: string;
  }>;
  onAccessibilityAction?: (event: { nativeEvent: { actionName: string } }) => void;
  testID?: string;
  // Advanced accessibility
  accessibilityLiveRegion?: 'none' | 'polite' | 'assertive';
  accessibilityElementsHidden?: boolean;
  importantForAccessibility?: 'auto' | 'yes' | 'no' | 'no-hide-descendants';
}

// ============================================================================
// STYLE CONFIGURATIONS
// ============================================================================

const BUTTON_VARIANTS = {
  primary: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
    textColor: '#FFFFFF',
    pressedColor: '#0056CC',
  },
  secondary: {
    backgroundColor: '#8E8E93',
    borderColor: '#8E8E93',
    textColor: '#FFFFFF',
    pressedColor: '#6C6C70',
  },
  outline: {
    backgroundColor: 'transparent',
    borderColor: '#007AFF',
    textColor: '#007AFF',
    pressedColor: '#F0F8FF',
  },
  ghost: {
    backgroundColor: 'transparent',
    borderColor: 'transparent',
    textColor: '#007AFF',
    pressedColor: '#F0F8FF',
  },
  danger: {
    backgroundColor: '#FF3B30',
    borderColor: '#FF3B30',
    textColor: '#FFFFFF',
    pressedColor: '#CC2E24',
  },
  success: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
    textColor: '#FFFFFF',
    pressedColor: '#2AA44F',
  },
  warning: {
    backgroundColor: '#FF9500',
    borderColor: '#FF9500',
    textColor: '#FFFFFF',
    pressedColor: '#CC7700',
  },
};

const BUTTON_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    fontSize: 14,
    minHeight: 32,
    iconSize: 16,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    fontSize: 16,
    minHeight: 44,
    iconSize: 20,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    fontSize: 18,
    minHeight: 52,
    iconSize: 24,
  },
  xl: {
    paddingVertical: 20,
    paddingHorizontal: 32,
    fontSize: 20,
    minHeight: 60,
    iconSize: 28,
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getButtonStyle(
  variant: keyof typeof BUTTON_VARIANTS,
  size: keyof typeof BUTTON_SIZES,
  isDisabled: boolean,
  isFullWidth: boolean,
  isDark: boolean,
  width: number
): ViewStyle {
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  const baseStyle: ViewStyle = {
    backgroundColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.backgroundColor,
    borderColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.borderColor,
    borderWidth: variant === 'outline' || variant === 'ghost' ? 1 : 0,
    borderRadius: 12,
    paddingVertical: sizeStyle.paddingVertical,
    paddingHorizontal: sizeStyle.paddingHorizontal,
    minHeight: sizeStyle.minHeight,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    opacity: isDisabled ? 0.6 : 1,
    width: isFullWidth ? '100%' : 'auto',
    maxWidth: width * 0.9,
    shadowColor: isDark ? '#000000' : '#000000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: isDisabled ? 0 : 0.1,
    shadowRadius: 4,
    elevation: isDisabled ? 0 : 2,
  };

  return baseStyle;
}

function getTextStyle(
  variant: keyof typeof BUTTON_VARIANTS,
  size: keyof typeof BUTTON_SIZES,
  isDisabled: boolean,
  isDark: boolean
): TextStyle {
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  return {
    color: isDisabled ? (isDark ? '#8E8E93' : '#6C6C70') : variantStyle.textColor,
    fontSize: sizeStyle.fontSize,
    fontWeight: '600',
    textAlign: 'center',
    includeFontPadding: false,
    textAlignVertical: 'center',
  };
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const AccessibleButton = memo<AccessibleButtonProps>(({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  isDisabled = false,
  hasIcon = false,
  iconName,
  iconPosition = 'left',
  isFullWidth = false,
  style,
  textStyle,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  accessibilityState,
  accessibilityActions,
  onAccessibilityAction,
  testID,
  accessibilityLiveRegion = 'polite',
  accessibilityElementsHidden = false,
  importantForAccessibility = 'auto',
}) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const { t } = useTranslation();
  
  const isDark = colorScheme === 'dark';
  const isButtonDisabled = isDisabled || isLoading;

  // Memoized styles
  const buttonStyle = useMemo(() =>
    getButtonStyle(variant, size, isButtonDisabled, isFullWidth, isDark, width),
    [variant, size, isButtonDisabled, isFullWidth, isDark, width]
  );

  const textStyleMemo = useMemo(() =>
    getTextStyle(variant, size, isButtonDisabled, isDark),
    [variant, size, isButtonDisabled, isDark]
  );

  // Accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || title,
    accessibilityHint: accessibilityHint || t('accessibility.button'),
    accessibilityRole,
    accessibilityState: {
      disabled: isButtonDisabled,
      busy: isLoading,
      ...accessibilityState,
    },
    accessibilityActions: accessibilityActions || [
      { name: 'activate', label: t('common.ok') },
    ],
    onAccessibilityAction: onAccessibilityAction || ((event) => {
      if (event.nativeEvent.actionName === 'activate' && !isButtonDisabled) {
        onPress();
      }
    }),
    accessibilityLiveRegion,
    accessibilityElementsHidden,
    importantForAccessibility,
  }), [
    accessibilityLabel,
    accessibilityHint,
    title,
    accessibilityRole,
    isButtonDisabled,
    isLoading,
    accessibilityState,
    accessibilityActions,
    onAccessibilityAction,
    accessibilityLiveRegion,
    accessibilityElementsHidden,
    importantForAccessibility,
    t,
  ]);

  // Event handlers
  const handlePress = useCallback(() => {
    if (!isButtonDisabled) {
      // Announce the action for screen readers
      AccessibilityInfo.announceForAccessibility(`${title} ${t('common.ok')}`);
      onPress();
    }
  }, [isButtonDisabled, title, onPress, t]);

  const handleLongPress = useCallback(() => {
    if (!isButtonDisabled) {
      AccessibilityInfo.announceForAccessibility(`${title} ${t('accessibility.button')} long pressed`);
    }
  }, [isButtonDisabled, title, t]);

  // Icon component
  const IconComponent = useMemo(() => {
    if (!hasIcon || !iconName) return null;
    
    const sizeStyle = BUTTON_SIZES[size];
    const variantStyle = BUTTON_VARIANTS[variant];
    
    return (
      <Ionicons
        name={iconName}
        size={sizeStyle.iconSize}
        color={isButtonDisabled ? (isDark ? '#8E8E93' : '#6C6C70') : variantStyle.textColor}
        style={[
          styles.icon,
          iconPosition === 'left' ? styles.iconLeft : styles.iconRight,
        ]}
      />
    );
  }, [hasIcon, iconName, size, variant, isButtonDisabled, isDark, iconPosition]);

  return (
    <TouchableOpacity
      style={[styles.button, buttonStyle, style]}
      onPress={handlePress}
      onLongPress={handleLongPress}
      disabled={isButtonDisabled}
      activeOpacity={0.8}
      testID={testID}
      {...accessibilityProps}
    >
      {iconPosition === 'left' && IconComponent}
      
      <Text style={[styles.text, textStyleMemo, textStyle]}>
        {isLoading ? t('common.loading') : title}
      </Text>
      
      {iconPosition === 'right' && IconComponent}
    </TouchableOpacity>
  );
});

AccessibleButton.displayName = 'AccessibleButton';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  button: {
    // Base styles are applied via getButtonStyle
  },
  text: {
    // Base styles are applied via getTextStyle
  },
  icon: {
    // Base icon styles
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
});
import {
  TouchableOpacity,
  Text,
  StyleSheet,
  ViewStyle,
  TextStyle,
  AccessibilityInfo,
  Platform,
  useWindowDimensions,
} from 'react-native';
import { useColorScheme } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTranslation } from '../../lib/i18n/i18n-config';

// ============================================================================
// TYPES
// ============================================================================

interface AccessibleButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'success' | 'warning';
  size?: 'small' | 'medium' | 'large' | 'xl';
  isLoading?: boolean;
  isDisabled?: boolean;
  hasIcon?: boolean;
  iconName?: keyof typeof Ionicons.glyphMap;
  iconPosition?: 'left' | 'right';
  isFullWidth?: boolean;
  style?: ViewStyle;
  textStyle?: TextStyle;
  // Accessibility props
  accessibilityLabel?: string;
  accessibilityHint?: string;
  accessibilityRole?: 'button' | 'link' | 'menuitem' | 'tab' | 'switch' | 'checkbox' | 'radio';
  accessibilityState?: {
    disabled?: boolean;
    selected?: boolean;
    checked?: boolean | 'mixed';
    busy?: boolean;
    expanded?: boolean;
  };
  accessibilityActions?: Array<{
    name: string;
    label?: string;
  }>;
  onAccessibilityAction?: (event: { nativeEvent: { actionName: string } }) => void;
  testID?: string;
  // Advanced accessibility
  accessibilityLiveRegion?: 'none' | 'polite' | 'assertive';
  accessibilityElementsHidden?: boolean;
  importantForAccessibility?: 'auto' | 'yes' | 'no' | 'no-hide-descendants';
}

// ============================================================================
// STYLE CONFIGURATIONS
// ============================================================================

const BUTTON_VARIANTS = {
  primary: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
    textColor: '#FFFFFF',
    pressedColor: '#0056CC',
  },
  secondary: {
    backgroundColor: '#8E8E93',
    borderColor: '#8E8E93',
    textColor: '#FFFFFF',
    pressedColor: '#6C6C70',
  },
  outline: {
    backgroundColor: 'transparent',
    borderColor: '#007AFF',
    textColor: '#007AFF',
    pressedColor: '#F0F8FF',
  },
  ghost: {
    backgroundColor: 'transparent',
    borderColor: 'transparent',
    textColor: '#007AFF',
    pressedColor: '#F0F8FF',
  },
  danger: {
    backgroundColor: '#FF3B30',
    borderColor: '#FF3B30',
    textColor: '#FFFFFF',
    pressedColor: '#CC2E24',
  },
  success: {
    backgroundColor: '#34C759',
    borderColor: '#34C759',
    textColor: '#FFFFFF',
    pressedColor: '#2AA44F',
  },
  warning: {
    backgroundColor: '#FF9500',
    borderColor: '#FF9500',
    textColor: '#FFFFFF',
    pressedColor: '#CC7700',
  },
};

const BUTTON_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    fontSize: 14,
    minHeight: 32,
    iconSize: 16,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    fontSize: 16,
    minHeight: 44,
    iconSize: 20,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 24,
    fontSize: 18,
    minHeight: 52,
    iconSize: 24,
  },
  xl: {
    paddingVertical: 20,
    paddingHorizontal: 32,
    fontSize: 20,
    minHeight: 60,
    iconSize: 28,
  },
};

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

function getButtonStyle(
  variant: keyof typeof BUTTON_VARIANTS,
  size: keyof typeof BUTTON_SIZES,
  isDisabled: boolean,
  isFullWidth: boolean,
  isDark: boolean,
  width: number
): ViewStyle {
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  const baseStyle: ViewStyle = {
    backgroundColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.backgroundColor,
    borderColor: isDisabled ? (isDark ? '#3A3A3C' : '#E5E5EA') : variantStyle.borderColor,
    borderWidth: variant === 'outline' || variant === 'ghost' ? 1 : 0,
    borderRadius: 12,
    paddingVertical: sizeStyle.paddingVertical,
    paddingHorizontal: sizeStyle.paddingHorizontal,
    minHeight: sizeStyle.minHeight,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    opacity: isDisabled ? 0.6 : 1,
    width: isFullWidth ? '100%' : 'auto',
    maxWidth: width * 0.9,
    shadowColor: isDark ? '#000000' : '#000000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: isDisabled ? 0 : 0.1,
    shadowRadius: 4,
    elevation: isDisabled ? 0 : 2,
  };

  return baseStyle;
}

function getTextStyle(
  variant: keyof typeof BUTTON_VARIANTS,
  size: keyof typeof BUTTON_SIZES,
  isDisabled: boolean,
  isDark: boolean
): TextStyle {
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  return {
    color: isDisabled ? (isDark ? '#8E8E93' : '#6C6C70') : variantStyle.textColor,
    fontSize: sizeStyle.fontSize,
    fontWeight: '600',
    textAlign: 'center',
    includeFontPadding: false,
    textAlignVertical: 'center',
  };
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export const AccessibleButton = memo<AccessibleButtonProps>(({
  title,
  onPress,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  isDisabled = false,
  hasIcon = false,
  iconName,
  iconPosition = 'left',
  isFullWidth = false,
  style,
  textStyle,
  accessibilityLabel,
  accessibilityHint,
  accessibilityRole = 'button',
  accessibilityState,
  accessibilityActions,
  onAccessibilityAction,
  testID,
  accessibilityLiveRegion = 'polite',
  accessibilityElementsHidden = false,
  importantForAccessibility = 'auto',
}) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const { t } = useTranslation();
  
  const isDark = colorScheme === 'dark';
  const isButtonDisabled = isDisabled || isLoading;

  // Memoized styles
  const buttonStyle = useMemo(() =>
    getButtonStyle(variant, size, isButtonDisabled, isFullWidth, isDark, width),
    [variant, size, isButtonDisabled, isFullWidth, isDark, width]
  );

  const textStyleMemo = useMemo(() =>
    getTextStyle(variant, size, isButtonDisabled, isDark),
    [variant, size, isButtonDisabled, isDark]
  );

  // Accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || title,
    accessibilityHint: accessibilityHint || t('accessibility.button'),
    accessibilityRole,
    accessibilityState: {
      disabled: isButtonDisabled,
      busy: isLoading,
      ...accessibilityState,
    },
    accessibilityActions: accessibilityActions || [
      { name: 'activate', label: t('common.ok') },
    ],
    onAccessibilityAction: onAccessibilityAction || ((event) => {
      if (event.nativeEvent.actionName === 'activate' && !isButtonDisabled) {
        onPress();
      }
    }),
    accessibilityLiveRegion,
    accessibilityElementsHidden,
    importantForAccessibility,
  }), [
    accessibilityLabel,
    accessibilityHint,
    title,
    accessibilityRole,
    isButtonDisabled,
    isLoading,
    accessibilityState,
    accessibilityActions,
    onAccessibilityAction,
    accessibilityLiveRegion,
    accessibilityElementsHidden,
    importantForAccessibility,
    t,
  ]);

  // Event handlers
  const handlePress = useCallback(() => {
    if (!isButtonDisabled) {
      // Announce the action for screen readers
      AccessibilityInfo.announceForAccessibility(`${title} ${t('common.ok')}`);
      onPress();
    }
  }, [isButtonDisabled, title, onPress, t]);

  const handleLongPress = useCallback(() => {
    if (!isButtonDisabled) {
      AccessibilityInfo.announceForAccessibility(`${title} ${t('accessibility.button')} long pressed`);
    }
  }, [isButtonDisabled, title, t]);

  // Icon component
  const IconComponent = useMemo(() => {
    if (!hasIcon || !iconName) return null;
    
    const sizeStyle = BUTTON_SIZES[size];
    const variantStyle = BUTTON_VARIANTS[variant];
    
    return (
      <Ionicons
        name={iconName}
        size={sizeStyle.iconSize}
        color={isButtonDisabled ? (isDark ? '#8E8E93' : '#6C6C70') : variantStyle.textColor}
        style={[
          styles.icon,
          iconPosition === 'left' ? styles.iconLeft : styles.iconRight,
        ]}
      />
    );
  }, [hasIcon, iconName, size, variant, isButtonDisabled, isDark, iconPosition]);

  return (
    <TouchableOpacity
      style={[styles.button, buttonStyle, style]}
      onPress={handlePress}
      onLongPress={handleLongPress}
      disabled={isButtonDisabled}
      activeOpacity={0.8}
      testID={testID}
      {...accessibilityProps}
    >
      {iconPosition === 'left' && IconComponent}
      
      <Text style={[styles.text, textStyleMemo, textStyle]}>
        {isLoading ? t('common.loading') : title}
      </Text>
      
      {iconPosition === 'right' && IconComponent}
    </TouchableOpacity>
  );
});

AccessibleButton.displayName = 'AccessibleButton';

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  button: {
    // Base styles are applied via getButtonStyle
  },
  text: {
    // Base styles are applied via getTextStyle
  },
  icon: {
    // Base icon styles
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
});


