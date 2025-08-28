import React, { forwardRef, useState, useCallback } from 'react';
import { View, TextInput, Text, StyleSheet, TouchableOpacity } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedInputProps {
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  label?: string;
  hasError?: boolean;
  errorMessage?: string;
  helperText?: string;
  isRequired?: boolean;
  isDisabled?: boolean;
  isSecureText?: boolean;
  hasLeftIcon?: boolean;
  leftIconName?: string;
  leftIconColor?: string;
  hasRightIcon?: boolean;
  rightIconName?: string;
  rightIconColor?: string;
  canShowPasswordToggle?: boolean;
  shouldShowCharacterCount?: boolean;
  maxLength?: number;
  keyboardType?: 'default' | 'email-address' | 'numeric' | 'phone-pad';
  autoCapitalize?: 'none' | 'sentences' | 'words' | 'characters';
  autoCorrect?: boolean;
  multiline?: boolean;
  numberOfLines?: number;
  style?: any;
  inputStyle?: any;
  labelStyle?: any;
  errorStyle?: any;
  helperStyle?: any;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const INPUT_STATES = {
  default: {
    borderColor: '#E5E5EA',
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
  },
  focused: {
    borderColor: '#007AFF',
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
  },
  error: {
    borderColor: '#FF3B30',
    backgroundColor: '#FFFFFF',
    textColor: '#000000',
  },
  disabled: {
    borderColor: '#E5E5EA',
    backgroundColor: '#F2F2F7',
    textColor: '#8E8E93',
  },
} as const;

const INPUT_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    fontSize: 14,
    borderRadius: 6,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    borderRadius: 8,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    fontSize: 18,
    borderRadius: 10,
  },
} as const;

// ============================================================================
// HELPERS
// ============================================================================

const getInputState = (props: OptimizedInputProps, isFocused: boolean) => {
  const { hasError, isDisabled } = props;
  
  if (isDisabled) return INPUT_STATES.disabled;
  if (hasError) return INPUT_STATES.error;
  if (isFocused) return INPUT_STATES.focused;
  return INPUT_STATES.default;
};

const getInputStyle = (props: OptimizedInputProps, isFocused: boolean) => {
  const { multiline, numberOfLines = 1 } = props;
  const state = getInputState(props, isFocused);
  const size = INPUT_SIZES.medium;
  
  return {
    ...state,
    ...size,
    minHeight: multiline ? numberOfLines * 24 : size.paddingVertical * 2 + 16,
  };
};

const getLabelStyle = (props: OptimizedInputProps) => {
  const { hasError, isDisabled } = props;
  
  return {
    fontSize: 14,
    fontWeight: '500',
    color: isDisabled ? '#8E8E93' : hasError ? '#FF3B30' : '#000000',
    marginBottom: 4,
  };
};

const getErrorStyle = () => ({
  fontSize: 12,
  color: '#FF3B30',
  marginTop: 4,
});

const getHelperStyle = () => ({
  fontSize: 12,
  color: '#8E8E93',
  marginTop: 4,
});

// ============================================================================
// SUBCOMPONENTS
// ============================================================================

const InputLabel: React.FC<{ props: OptimizedInputProps }> = ({ props }) => {
  const { label, isRequired } = props;
  
  if (!label) return null;
  
  return (
    <Text style={[styles.label, getLabelStyle(props)]}>
      {label}
      {isRequired && <Text style={styles.required}> *</Text>}
    </Text>
  );
};

const InputIcon: React.FC<{ 
  iconName: string; 
  color: string; 
  position: 'left' | 'right';
  onPress?: () => void;
}> = ({ iconName, color, position, onPress }) => {
  const iconStyle = position === 'left' ? styles.leftIcon : styles.rightIcon;
  
  if (onPress) {
    return (
      <TouchableOpacity onPress={onPress} style={iconStyle}>
        <Text style={[styles.iconText, { color }]}>{iconName}</Text>
      </TouchableOpacity>
    );
  }
  
  return (
    <Text style={[styles.iconText, iconStyle, { color }]}>
      {iconName}
    </Text>
  );
};

const InputError: React.FC<{ props: OptimizedInputProps }> = ({ props }) => {
  const { hasError, errorMessage } = props;
  
  if (!hasError || !errorMessage) return null;
  
  return (
    <Text style={[styles.errorText, getErrorStyle()]}>
      {errorMessage}
    </Text>
  );
};

const InputHelper: React.FC<{ props: OptimizedInputProps }> = ({ props }) => {
  const { helperText, shouldShowCharacterCount, value, maxLength } = props;
  
  if (!helperText && !shouldShowCharacterCount) return null;
  
  const characterCount = shouldShowCharacterCount && maxLength 
    ? `${value.length}/${maxLength}`
    : null;
  
  return (
    <Text style={[styles.helperText, getHelperStyle()]}>
      {helperText}
      {characterCount && ` • ${characterCount}`}
    </Text>
  );
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedInput = forwardRef<TextInput, OptimizedInputProps>(({
  value,
  onChangeText,
  placeholder,
  label,
  hasError = false,
  errorMessage,
  helperText,
  isRequired = false,
  isDisabled = false,
  isSecureText = false,
  hasLeftIcon = false,
  leftIconName,
  leftIconColor,
  hasRightIcon = false,
  rightIconName,
  rightIconColor,
  canShowPasswordToggle = false,
  shouldShowCharacterCount = false,
  maxLength,
  keyboardType = 'default',
  autoCapitalize = 'none',
  autoCorrect = false,
  multiline = false,
  numberOfLines = 1,
  style,
  inputStyle,
  labelStyle,
  errorStyle,
  helperStyle,
}, ref) => {
  const [isFocused, setIsFocused] = useState(false);
  const [isPasswordVisible, setIsPasswordVisible] = useState(!isSecureText);
  
  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);
  
  const handleBlur = useCallback(() => {
    setIsFocused(false);
  }, []);
  
  const handlePasswordToggle = useCallback(() => {
    setIsPasswordVisible(!isPasswordVisible);
  }, [isPasswordVisible]);
  
  const handleRightIconPress = useCallback(() => {
    if (canShowPasswordToggle) {
      handlePasswordToggle();
    }
  }, [canShowPasswordToggle, handlePasswordToggle]);
  
  const inputState = getInputState({ hasError, isDisabled }, isFocused);
  const inputStyles = getInputStyle({ hasError, isDisabled, multiline, numberOfLines }, isFocused);
  
  const shouldShowPasswordToggle = canShowPasswordToggle && isSecureText;
  const shouldShowRightIcon = hasRightIcon || shouldShowPasswordToggle;
  const rightIconToShow = shouldShowPasswordToggle 
    ? (isPasswordVisible ? 'eye-off' : 'eye') 
    : rightIconName;
  
  return (
    <View style={[styles.container, style]}>
      <InputLabel props={{ label, isRequired, hasError, isDisabled }} />
      
      <View style={[
        styles.inputContainer,
        {
          borderColor: inputState.borderColor,
          backgroundColor: inputState.backgroundColor,
          borderRadius: inputStyles.borderRadius,
        }
      ]}>
        {hasLeftIcon && leftIconName && (
          <InputIcon
            iconName={leftIconName}
            color={leftIconColor || inputState.textColor}
            position="left"
          />
        )}
        
        <TextInput
          ref={ref}
          value={value}
          onChangeText={onChangeText}
          placeholder={placeholder}
          placeholderTextColor="#8E8E93"
          secureTextEntry={isSecureText && !isPasswordVisible}
          editable={!isDisabled}
          maxLength={maxLength}
          keyboardType={keyboardType}
          autoCapitalize={autoCapitalize}
          autoCorrect={autoCorrect}
          multiline={multiline}
          numberOfLines={numberOfLines}
          style={[
            styles.input,
            {
              color: inputState.textColor,
              fontSize: inputStyles.fontSize,
              paddingVertical: inputStyles.paddingVertical,
              paddingHorizontal: inputStyles.paddingHorizontal,
              minHeight: inputStyles.minHeight,
            },
            inputStyle,
          ]}
          onFocus={handleFocus}
          onBlur={handleBlur}
        />
        
        {shouldShowRightIcon && rightIconToShow && (
          <InputIcon
            iconName={rightIconToShow}
            color={rightIconColor || inputState.textColor}
            position="right"
            onPress={shouldShowPasswordToggle ? handleRightIconPress : undefined}
          />
        )}
      </View>
      
      <InputError props={{ hasError, errorMessage }} />
      <InputHelper props={{ helperText, shouldShowCharacterCount, value, maxLength }} />
    </View>
  );
});

// ============================================================================
// STYLES
// ============================================================================

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontWeight: '500',
    marginBottom: 4,
  },
  required: {
    color: '#FF3B30',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
  },
  input: {
    flex: 1,
    fontWeight: '400',
  },
  leftIcon: {
    paddingLeft: 16,
    paddingRight: 8,
  },
  rightIcon: {
    paddingRight: 16,
    paddingLeft: 8,
  },
  iconText: {
    fontSize: 16,
  },
  errorText: {
    fontWeight: '400',
  },
  helperText: {
    fontWeight: '400',
  },
}); 