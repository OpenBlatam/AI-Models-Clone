import React, { memo, forwardRef } from 'react';
import { TextInput, View, Text, StyleSheet, TextInputProps } from 'react-native';
import { useTheme } from '@/contexts/theme-context';

interface InputProps extends TextInputProps {
  label?: string;
  error?: string;
  containerStyle?: object;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const InputComponent = forwardRef<TextInput, InputProps>(
  ({ label, error, containerStyle, style, leftIcon, rightIcon, ...props }, ref) => {
    const { theme } = useTheme();

    return (
      <View style={[styles.container, containerStyle]}>
        {label && (
          <Text
            style={[styles.label, { color: theme.colors.text }]}
            accessibilityRole="text"
            accessibilityLabel={label}
          >
            {label}
          </Text>
        )}
        <View
          style={[
            styles.inputContainer,
            {
              backgroundColor: theme.colors.surface,
              borderColor: error ? theme.colors.error : theme.colors.border,
            },
            error && styles.inputError,
          ]}
        >
          {leftIcon && <View style={styles.leftIcon}>{leftIcon}</View>}
          <TextInput
            ref={ref}
            style={[
              styles.input,
              {
                color: theme.colors.text,
              },
              leftIcon && styles.inputWithLeftIcon,
              rightIcon && styles.inputWithRightIcon,
              style,
            ]}
            placeholderTextColor={theme.colors.textSecondary}
            accessibilityLabel={label}
            accessibilityHint={error}
            accessibilityState={{ invalid: !!error }}
            {...props}
          />
          {rightIcon && <View style={styles.rightIcon}>{rightIcon}</View>}
        </View>
        {error && (
          <Text style={[styles.errorText, { color: theme.colors.error }]} accessibilityLiveRegion="polite">
            {error}
          </Text>
        )}
      </View>
    );
  }
);

InputComponent.displayName = 'Input';

export const Input = memo(InputComponent);

const styles = StyleSheet.create({
  container: {
    marginBottom: 16,
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderRadius: 12,
    paddingHorizontal: 16,
  },
  input: {
    flex: 1,
    paddingVertical: 12,
    fontSize: 16,
  },
  inputWithLeftIcon: {
    marginLeft: 8,
  },
  inputWithRightIcon: {
    marginRight: 8,
  },
  leftIcon: {
    marginRight: 8,
  },
  rightIcon: {
    marginLeft: 8,
  },
  inputError: {
    borderWidth: 1.5,
  },
  errorText: {
    fontSize: 12,
    marginTop: 4,
  },
});
