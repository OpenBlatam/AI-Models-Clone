import React from 'react';
import { TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedButtonProps {
  title: string;
  onPress: () => void;
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
  isDisabled?: boolean;
  hasIcon?: boolean;
  iconName?: string;
  iconPosition?: 'left' | 'right';
  canShowLoading?: boolean;
  shouldShowSpinner?: boolean;
  hasRoundedCorners?: boolean;
  isFullWidth?: boolean;
  style?: any;
  textStyle?: any;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const BUTTON_VARIANTS = {
  primary: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
    textColor: '#FFFFFF',
  },
  secondary: {
    backgroundColor: '#F2F2F7',
    borderColor: '#F2F2F7',
    textColor: '#000000',
  },
  outline: {
    backgroundColor: 'transparent',
    borderColor: '#007AFF',
    textColor: '#007AFF',
  },
  ghost: {
    backgroundColor: 'transparent',
    borderColor: 'transparent',
    textColor: '#007AFF',
  },
  danger: {
    backgroundColor: '#FF3B30',
    borderColor: '#FF3B30',
    textColor: '#FFFFFF',
  },
} as const;

const BUTTON_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    fontSize: 14,
    borderRadius: 6,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 24,
    fontSize: 16,
    borderRadius: 8,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 32,
    fontSize: 18,
    borderRadius: 10,
  },
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const getButtonStyle = (props: OptimizedButtonProps) => {
  const { variant = 'primary', size = 'medium', isDisabled, hasRoundedCorners, isFullWidth } = props;
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  return {
    backgroundColor: isDisabled ? '#E5E5EA' : variantStyle.backgroundColor,
    borderColor: isDisabled ? '#E5E5EA' : variantStyle.borderColor,
    paddingVertical: sizeStyle.paddingVertical,
    paddingHorizontal: sizeStyle.paddingHorizontal,
    borderRadius: hasRoundedCorners ? 25 : sizeStyle.borderRadius,
    width: isFullWidth ? '100%' : 'auto',
    opacity: isDisabled ? 0.6 : 1,
  };
};

const getTextStyle = (props: OptimizedButtonProps) => {
  const { variant = 'primary', size = 'medium', isDisabled } = props;
  const variantStyle = BUTTON_VARIANTS[variant];
  const sizeStyle = BUTTON_SIZES[size];
  
  return {
    color: isDisabled ? '#8E8E93' : variantStyle.textColor,
    fontSize: sizeStyle.fontSize,
    fontWeight: '600',
    textAlign: 'center',
  };
};

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const ButtonContent: React.FC<{ props: OptimizedButtonProps }> = ({ props }) => {
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
        color={getTextStyle(props).color} 
      />
    );
  }

  return (
    <>
      {hasIcon && iconName && iconPosition === 'left' && (
        <Text style={[styles.icon, { color: getTextStyle(props).color }]}>
          {iconName}
        </Text>
      )}
      <Text style={[styles.buttonText, getTextStyle(props)]}>
        {title}
      </Text>
      {hasIcon && iconName && iconPosition === 'right' && (
        <Text style={[styles.icon, { color: getTextStyle(props).color }]}>
          {iconName}
        </Text>
      )}
    </>
  );
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedButton: React.FC<OptimizedButtonProps> = ({
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
}) => {
  const isButtonDisabled = isDisabled || isLoading;
  const shouldHandlePress = !isButtonDisabled;

  const handlePress = () => {
    if (shouldHandlePress) {
      onPress();
    }
  };

  return (
    <TouchableOpacity
      style={[
        styles.button,
        getButtonStyle({ 
          variant, 
          size, 
          isDisabled: isButtonDisabled, 
          hasRoundedCorners, 
          isFullWidth 
        }),
        style,
      ]}
      onPress={handlePress}
      disabled={isButtonDisabled}
      activeOpacity={0.8}
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
      />
    </TouchableOpacity>
  );
};

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
  },
  icon: {
    fontSize: 16,
    marginHorizontal: 4,
  },
}); 