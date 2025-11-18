'use client';

import React, { forwardRef, useState, useMemo, useCallback, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Input } from './input';
import { Label } from './label';
import { Badge } from './badge';
import { Eye, EyeOff, AlertCircle, CheckCircle, Info, X } from 'lucide-react';
import { usePerformanceMonitor } from '@/lib/stores/examples-store';

export interface ValidationRule {
  test: (value: string) => boolean;
  message: string;
  severity?: 'error' | 'warning' | 'info';
}

export interface AdvancedInputProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'onChange'> {
  label?: string;
  description?: string;
  error?: string;
  success?: string;
  warning?: string;
  info?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  validationRules?: ValidationRule[];
  showValidation?: boolean;
  showCharacterCount?: boolean;
  showPasswordToggle?: boolean;
  showClearButton?: boolean;
  maxLength?: number;
  minLength?: number;
  required?: boolean;
  variant?: 'default' | 'outline' | 'filled' | 'minimal';
  size?: 'sm' | 'default' | 'lg';
  rounded?: 'default' | 'full' | 'none';
  shadow?: 'none' | 'sm' | 'md' | 'lg';
  animation?: 'none' | 'pulse' | 'bounce' | 'shake';
  onChange?: (value: string, isValid: boolean, errors: string[]) => void;
  onValidationChange?: (isValid: boolean, errors: string[]) => void;
  className?: string;
  labelClassName?: string;
  inputClassName?: string;
}

const AdvancedInput = forwardRef<HTMLInputElement, AdvancedInputProps>(
  (
    {
      label,
      description,
      error,
      success,
      warning,
      info,
      leftIcon,
      rightIcon,
      validationRules = [],
      showValidation = true,
      showCharacterCount = false,
      showPasswordToggle = false,
      showClearButton = false,
      maxLength,
      minLength,
      required = false,
      variant = 'default',
      size = 'default',
      rounded = 'default',
      shadow = 'md',
      animation = 'none',
      onChange,
      onValidationChange,
      className,
      labelClassName,
      inputClassName,
      value: externalValue,
      defaultValue,
      type = 'text',
      ...props
    },
    ref
  ) => {
    // Performance monitoring
    const { measureRenderTime } = usePerformanceMonitor();

    // Local state
    const [value, setValue] = useState(externalValue || defaultValue || '');
    const [isFocused, setIsFocused] = useState(false);
    const [showPassword, setShowPassword] = useState(false);
    const [validationErrors, setValidationErrors] = useState<string[]>([]);
    const [isValidating, setIsValidating] = useState(false);

    // Memoized computed values
    const currentValue = externalValue !== undefined ? externalValue : value;
    const characterCount = String(currentValue).length;
    const isPasswordType = type === 'password';
    const displayType = isPasswordType && showPassword ? 'text' : type;
    const isOverLimit = maxLength ? characterCount > maxLength : false;

    // Memoized validation state
    const validationState = useMemo(() => {
      if (!showValidation || !validationRules.length) return { isValid: true, errors: [] };

      const errors: string[] = [];
      let isValid = true;

      // Required validation
      if (required && !currentValue) {
        errors.push('This field is required');
        isValid = false;
      }

      // Length validation
      if (minLength && characterCount < minLength) {
        errors.push(`Minimum ${minLength} characters required`);
        isValid = false;
      }

      if (maxLength && characterCount > maxLength) {
        errors.push(`Maximum ${maxLength} characters allowed`);
        isValid = false;
      }

      // Custom validation rules
      validationRules.forEach(rule => {
        if (currentValue && !rule.test(currentValue)) {
          errors.push(rule.message);
          if (rule.severity === 'error') {
            isValid = false;
          }
        }
      });

      return { isValid, errors };
    }, [showValidation, validationRules, required, currentValue, characterCount, minLength, maxLength]);

    // Memoized input classes
    const inputClasses = useMemo(() => {
      const baseClasses = cn(
        'transition-all duration-200',
        'focus:ring-2 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        {
          // Size variants
          'h-8 px-2 text-sm': size === 'sm',
          'h-10 px-3': size === 'default',
          'h-12 px-4 text-lg': size === 'lg',
          
          // Rounded variants
          'rounded-md': rounded === 'default',
          'rounded-full': rounded === 'full',
          'rounded-none': rounded === 'none',
          
          // Shadow variants
          'shadow-none': shadow === 'none',
          'shadow-sm': shadow === 'sm',
          'shadow-md': shadow === 'md',
          'shadow-lg': shadow === 'lg',
          
          // Animation variants
          'animate-none': animation === 'none',
          'animate-pulse': animation === 'pulse',
          'animate-bounce': animation === 'bounce',
          'shake': animation === 'shake',
        },
        inputClassName
      );

      // Variant-specific classes
      const variantClasses = {
        default: 'border border-input bg-background',
        outline: 'border-2 border-input bg-transparent',
        filled: 'border-0 bg-muted',
        minimal: 'border-0 bg-transparent border-b-2 border-input',
      };

      return cn(baseClasses, variantClasses[variant]);
    }, [size, rounded, shadow, animation, variant, inputClassName]);

    // Memoized status classes
    const statusClasses = useMemo(() => {
      if (error || (!validationState.isValid && validationState.errors.length > 0)) {
        return 'border-destructive focus:ring-destructive';
      }
      if (success) {
        return 'border-green-500 focus:ring-green-500';
      }
      if (warning) {
        return 'border-yellow-500 focus:ring-yellow-500';
      }
      if (info) {
        return 'border-blue-500 focus:ring-blue-500';
      }
      if (isFocused) {
        return 'border-primary focus:ring-primary';
      }
      return '';
    }, [error, success, warning, info, validationState.isValid, validationState.errors.length, isFocused]);

    // Validation effect
    useEffect(() => {
      if (showValidation && validationRules.length > 0) {
        setIsValidating(true);
        const timer = setTimeout(() => {
          setValidationErrors(validationState.errors);
          setIsValidating(false);
          
          if (onValidationChange) {
            onValidationChange(validationState.isValid, validationState.errors);
          }
        }, 300); // Debounce validation

        return () => clearTimeout(timer);
      }
    }, [currentValue, validationRules, showValidation, validationState, onValidationChange]);

    // Enhanced change handler
    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      setValue(newValue);
      
      if (onChange) {
        onChange(newValue, validationState.isValid, validationState.errors);
      }
    }, [onChange, validationState.isValid, validationState.errors]);

    // Enhanced focus handlers
    const handleFocus = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(true);
      if (props.onFocus) props.onFocus(e);
    }, [props]);

    const handleBlur = useCallback((e: React.FocusEvent<HTMLInputElement>) => {
      setIsFocused(false);
      if (props.onBlur) props.onBlur(e);
    }, [props]);

    // Clear input handler
    const handleClear = useCallback(() => {
      setValue('');
      if (onChange) {
        onChange('', true, []);
      }
    }, [onChange]);

    // Toggle password visibility
    const togglePasswordVisibility = useCallback(() => {
      setShowPassword(prev => !prev);
    }, []);

    // Memoized right icons
    const rightIcons = useMemo(() => {
      const icons: React.ReactNode[] = [];

      if (showClearButton && currentValue) {
        icons.push(
          <button
            key="clear"
            type="button"
            onClick={handleClear}
            className="p-1 hover:bg-muted rounded-full transition-colors"
            aria-label="Clear input"
          >
            <X className="h-4 w-4 text-muted-foreground" />
          </button>
        );
      }

      if (showPasswordToggle && isPasswordType) {
        icons.push(
          <button
            key="password-toggle"
            type="button"
            onClick={togglePasswordVisibility}
            className="p-1 hover:bg-muted rounded-full transition-colors"
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
          </button>
        );
      }

      if (rightIcon) {
        icons.push(rightIcon);
      }

      return icons;
    }, [showClearButton, showPasswordToggle, isPasswordType, currentValue, rightIcon, showPassword, handleClear, togglePasswordVisibility]);

    // Memoized status message
    const statusMessage = useMemo(() => {
      if (error) return { message: error, type: 'error', icon: AlertCircle };
      if (success) return { message: success, type: 'success', icon: CheckCircle };
      if (warning) return { message: warning, type: 'warning', icon: AlertCircle };
      if (info) return { message: info, type: 'info', icon: Info };
      if (validationErrors.length > 0) {
        return { message: validationErrors[0], type: 'error', icon: AlertCircle };
      }
      return null;
    }, [error, success, warning, info, validationErrors]);

    // Memoized character count
    const characterCountDisplay = useMemo(() => {
      if (!showCharacterCount || !maxLength) return null;

      return (
        <div className="flex items-center gap-2 text-xs">
          <span className={cn(
            'font-mono',
            isOverLimit ? 'text-destructive' : 'text-muted-foreground'
          )}>
            {characterCount}/{maxLength}
          </span>
          {isOverLimit && (
            <Badge variant="destructive" size="sm">Over limit</Badge>
          )}
        </div>
      );
    }, [showCharacterCount, maxLength, characterCount, isOverLimit]);

    // Performance monitoring effect
    useEffect(() => {
      const cleanup = measureRenderTime('AdvancedInput');
      return cleanup;
    }, [measureRenderTime]);

    return (
      <div className={cn('space-y-2', className)}>
        {/* Label */}
        {label && (
          <Label className={cn('text-sm font-medium', labelClassName)}>
            {label}
            {required && <span className="text-destructive ml-1">*</span>}
          </Label>
        )}

        {/* Description */}
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}

        {/* Input Container */}
        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground">
              {leftIcon}
            </div>
          )}

          {/* Input */}
          <Input
            ref={ref}
            type={displayType}
            value={currentValue}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            className={cn(
              inputClasses,
              statusClasses,
              leftIcon && 'pl-10',
              rightIcons.length > 0 && 'pr-10'
            )}
            {...props}
          />

          {/* Right Icons */}
          {rightIcons.length > 0 && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
              {rightIcons}
            </div>
          )}
        </div>

        {/* Status Message */}
        {statusMessage && (
          <div className={cn(
            'flex items-center gap-2 text-sm',
            {
              'text-destructive': statusMessage.type === 'error',
              'text-green-600': statusMessage.type === 'success',
              'text-yellow-600': statusMessage.type === 'warning',
              'text-blue-600': statusMessage.type === 'info',
            }
          )}>
            <statusMessage.icon className="h-4 w-4" />
            <span>{statusMessage.message}</span>
          </div>
        )}

        {/* Character Count */}
        {characterCountDisplay}

        {/* Validation Loading */}
        {isValidating && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-primary"></div>
            <span>Validating...</span>
          </div>
        )}
      </div>
    );
  }
);

AdvancedInput.displayName = 'AdvancedInput';

export { AdvancedInput };
export type { ValidationRule };
