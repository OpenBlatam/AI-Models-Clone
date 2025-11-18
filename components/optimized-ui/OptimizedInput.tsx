import React, { useState, useCallback, useMemo, forwardRef, useImperativeHandle } from 'react';
import {
  View,
  TextInput,
  Text,
  StyleSheet,
  TouchableOpacity,
  ViewStyle,
  TextStyle,
  TextInputProps,
  AccessibilityInfo,
  Platform,
  Animated,
} from 'react-native';
import { useWindowDimensions } from 'react-native';
import { useColorScheme } from 'react-native';

// ============================================================================
// TYPES
// ============================================================================

interface OptimizedInputProps extends Omit<TextInputProps, 'style'> {
  label?: string;
  placeholder?: string;
  value: string;
  onChangeText: (text: string) => void;
  error?: string;
  helperText?: string;
  isRequired?: boolean;
  isDisabled?: boolean;
  isReadOnly?: boolean;
  hasIcon?: boolean;
  iconName?: string;
  iconPosition?: 'left' | 'right';
  onIconPress?: () => void;
  variant?: 'outlined' | 'filled' | 'underlined';
  size?: 'small' | 'medium' | 'large';
  isFullWidth?: boolean;
  containerStyle?: ViewStyle;
  inputStyle?: TextStyle;
  labelStyle?: TextStyle;
  errorStyle?: TextStyle;
  helperStyle?: TextStyle;
  testID?: string;
  accessibilityLabel?: string;
  accessibilityHint?: string;
  validationRules?: ValidationRule[];
  onValidationChange?: (isValid: boolean, errors: string[]) => void;
}

interface ValidationRule {
  test: (value: string) => boolean;
  message: string;
}

interface InputRef {
  focus: () => void;
  blur: () => void;
  clear: () => void;
  validate: () => boolean;
}

// ============================================================================
// STATIC CONTENT
// ============================================================================

const INPUT_VARIANTS = {
  outlined: {
    borderWidth: 1,
    borderRadius: 8,
    backgroundColor: 'transparent',
  },
  filled: {
    borderWidth: 0,
    borderRadius: 8,
    backgroundColor: '#F2F2F7',
  },
  underlined: {
    borderWidth: 0,
    borderBottomWidth: 1,
    borderRadius: 0,
    backgroundColor: 'transparent',
  },
} as const;

const INPUT_SIZES = {
  small: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    fontSize: 14,
    minHeight: 36,
  },
  medium: {
    paddingVertical: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    minHeight: 44,
  },
  large: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    fontSize: 18,
    minHeight: 52,
  },
} as const;

// Default validation rules
const DEFAULT_VALIDATION_RULES: ValidationRule[] = [
  {
    test: (value: string) => value.length > 0,
    message: 'This field is required',
  },
];

// ============================================================================
// HELPERS
// ============================================================================

const getInputStyle = (
  props: OptimizedInputProps,
  isDark: boolean,
  width: number,
  isFocused: boolean,
  hasError: boolean
): ViewStyle => {
  const { variant = 'outlined', size = 'medium', isDisabled, isFullWidth } = props;
  const variantStyle = INPUT_VARIANTS[variant];
  const sizeStyle = INPUT_SIZES[size];

  // Responsive adjustments
  const responsivePadding = width < 375 ? sizeStyle.paddingHorizontal * 0.8 : sizeStyle.paddingHorizontal;
  const responsiveFontSize = width < 375 ? sizeStyle.fontSize * 0.9 : sizeStyle.fontSize;

  const baseColor = isDark ? '#3A3A3C' : '#E5E5EA';
  const focusColor = isDark ? '#0A84FF' : '#007AFF';
  const errorColor = isDark ? '#FF453A' : '#FF3B30';

  return {
    ...variantStyle,
    paddingVertical: sizeStyle.paddingVertical,
    paddingHorizontal: responsivePadding,
    fontSize: responsiveFontSize,
    minHeight: sizeStyle.minHeight,
    width: isFullWidth ? '100%' : 'auto',
    borderColor: hasError ? errorColor : (isFocused ? focusColor : baseColor),
    backgroundColor: variant === 'filled' ? (isDark ? '#2C2C2E' : '#F2F2F7') : 'transparent',
    color: isDark ? '#FFFFFF' : '#000000',
    opacity: isDisabled ? 0.6 : 1,
    shadowColor: isDark ? '#000000' : '#000000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: isFocused ? 0.1 : 0,
    shadowRadius: 2,
    elevation: isFocused ? 1 : 0,
  };
};

const getLabelStyle = (props: OptimizedInputProps, isDark: boolean, width: number): TextStyle => {
  const { size = 'medium' } = props;
  const sizeStyle = INPUT_SIZES[size];
  
  // Responsive font size
  const responsiveFontSize = width < 375 ? sizeStyle.fontSize * 0.8 : sizeStyle.fontSize * 0.9;
  
  return {
    fontSize: responsiveFontSize,
    fontWeight: '500' as const,
    color: isDark ? '#FFFFFF' : '#000000',
    marginBottom: 4,
    includeFontPadding: false,
  };
};

// ============================================================================
// MAIN EXPORTED COMPONENT
// ============================================================================

export const OptimizedInput = forwardRef<InputRef, OptimizedInputProps>(({
  label,
  placeholder,
  value,
  onChangeText,
  error,
  helperText,
  isRequired = false,
  isDisabled = false,
  isReadOnly = false,
  hasIcon = false,
  iconName,
  iconPosition = 'right',
  onIconPress,
  variant = 'outlined',
  size = 'medium',
  isFullWidth = false,
  containerStyle,
  inputStyle,
  labelStyle,
  errorStyle,
  helperStyle,
  testID,
  accessibilityLabel,
  accessibilityHint,
  validationRules = DEFAULT_VALIDATION_RULES,
  onValidationChange,
  ...textInputProps
}, ref) => {
  const colorScheme = useColorScheme();
  const { width } = useWindowDimensions();
  const isDark = colorScheme === 'dark';
  
  const [isFocused, setIsFocused] = useState(false);
  const [internalError, setInternalError] = useState<string | undefined>(error);
  const [isValid, setIsValid] = useState(true);

  // Memoized styles for performance
  const inputStyleMemo = useMemo(() => 
    getInputStyle({ variant, size, isDisabled, isFullWidth }, isDark, width, isFocused, !!internalError), 
    [variant, size, isDisabled, isFullWidth, isDark, width, isFocused, internalError]
  );

  const labelStyleMemo = useMemo(() => 
    getLabelStyle({ size }, isDark, width), 
    [size, isDark, width]
  );

  // Validation function
  const validateInput = useCallback((inputValue: string): boolean => {
    if (validationRules.length === 0) return true;
    
    const errors: string[] = [];
    
    validationRules.forEach(rule => {
      if (!rule.test(inputValue)) {
        errors.push(rule.message);
      }
    });
    
    const isValidInput = errors.length === 0;
    setIsValid(isValidInput);
    setInternalError(errors[0] || undefined);
    
    onValidationChange?.(isValidInput, errors);
    return isValidInput;
  }, [validationRules, onValidationChange]);

  // Handle text change with validation
  const handleChangeText = useCallback((text: string) => {
    onChangeText(text);
    if (validationRules.length > 0) {
      validateInput(text);
    }
  }, [onChangeText, validateInput]);

  // Focus handlers
  const handleFocus = useCallback(() => {
    setIsFocused(true);
    textInputProps.onFocus?.(undefined as any);
  }, [textInputProps]);

  const handleBlur = useCallback(() => {
    setIsFocused(false);
    textInputProps.onBlur?.(undefined as any);
  }, [textInputProps]);

  // Expose methods via ref
  useImperativeHandle(ref, () => ({
    focus: () => {
      // Focus will be handled by the TextInput ref
    },
    blur: () => {
      // Blur will be handled by the TextInput ref
    },
    clear: () => {
      onChangeText('');
      setInternalError(undefined);
      setIsValid(true);
    },
    validate: () => {
      return validateInput(value);
    },
  }), [onChangeText, validateInput, value]);

  // Memoized accessibility props
  const accessibilityProps = useMemo(() => ({
    accessible: true,
    accessibilityLabel: accessibilityLabel || `${label || 'Input'} field`,
    accessibilityHint: accessibilityHint || `Enter ${label || 'text'} in this field`,
    accessibilityRole: 'text' as const,
    accessibilityState: { 
      disabled: isDisabled,
      busy: false 
    },
  }), [accessibilityLabel, accessibilityHint, label, isDisabled]);

  // Memoized icon component
  const IconComponent = useMemo(() => {
    if (!hasIcon || !iconName) return null;
    
    return (
      <TouchableOpacity
        style={[
          styles.iconContainer,
          iconPosition === 'left' ? styles.iconLeft : styles.iconRight,
        ]}
        onPress={onIconPress}
        disabled={!onIconPress}
        accessible={true}
        accessibilityLabel={`${iconName} icon`}
        accessibilityRole="button"
      >
        <Text style={[styles.icon, { color: isDark ? '#FFFFFF' : '#000000' }]}>
          {iconName}
        </Text>
      </TouchableOpacity>
    );
  }, [hasIcon, iconName, iconPosition, onIconPress, isDark]);

  const displayError = internalError || error;
  const displayHelperText = helperText || (isRequired ? 'This field is required' : '');

  return (
    <View style={[styles.container, containerStyle]} testID={testID}>
      {label && (
        <Text style={[styles.label, labelStyleMemo, labelStyle]}>
          {label}
          {isRequired && <Text style={styles.required}> *</Text>}
        </Text>
      )}
      
      <View style={styles.inputContainer}>
        {iconPosition === 'left' && IconComponent}
        
        <TextInput
          style={[styles.input, inputStyleMemo, inputStyle]}
          value={value}
          onChangeText={handleChangeText}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          placeholderTextColor={isDark ? '#8E8E93' : '#8E8E93'}
          editable={!isDisabled && !isReadOnly}
          selectTextOnFocus={!isReadOnly}
          {...textInputProps}
          {...accessibilityProps}
        />
        
        {iconPosition === 'right' && IconComponent}
      </View>
      
      {(displayError || displayHelperText) && (
        <View style={styles.messageContainer}>
          {displayError && (
            <Text style={[styles.errorText, errorStyle]}>
              {displayError}
            </Text>
          )}
          {displayHelperText && !displayError && (
            <Text style={[styles.helperText, helperStyle]}>
              {displayHelperText}
            </Text>
          )}
        </View>
      )}
    </View>
  );
});

OptimizedInput.displayName = 'OptimizedInput';

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
    includeFontPadding: false,
  },
  required: {
    color: '#FF3B30',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  iconContainer: {
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
  icon: {
    fontSize: 18,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  messageContainer: {
    marginTop: 4,
    minHeight: 20,
  },
  errorText: {
    fontSize: 12,
    color: '#FF3B30',
    includeFontPadding: false,
  },
  helperText: {
    fontSize: 12,
    color: '#8E8E93',
    includeFontPadding: false,
  },
}); 
  label: {
    fontWeight: '500',
    marginBottom: 4,
    includeFontPadding: false,
  },
  required: {
    color: '#FF3B30',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  iconContainer: {
    padding: 8,
    justifyContent: 'center',
    alignItems: 'center',
  },
  iconLeft: {
    marginRight: 8,
  },
  iconRight: {
    marginLeft: 8,
  },
  icon: {
    fontSize: 18,
    includeFontPadding: false,
    textAlignVertical: 'center',
  },
  messageContainer: {
    marginTop: 4,
    minHeight: 20,
  },
  errorText: {
    fontSize: 12,
    color: '#FF3B30',
    includeFontPadding: false,
  },
  helperText: {
    fontSize: 12,
    color: '#8E8E93',
    includeFontPadding: false,
  },
}); 