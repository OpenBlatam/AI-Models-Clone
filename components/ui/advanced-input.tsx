'use client';

import React, { forwardRef, InputHTMLAttributes, useState, useMemo, useCallback, memo } from 'react';
import { cn } from '@/lib/utils';
import { Eye, EyeOff, AlertCircle, CheckCircle, Search, X } from 'lucide-react';

export interface AdvancedInputProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'size'> {
  label?: string;
  helperText?: string;
  error?: string;
  success?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'filled' | 'outlined';
  fullWidth?: boolean;
  clearable?: boolean;
  searchable?: boolean;
  password?: boolean;
  required?: boolean;
  disabled?: boolean;
  loading?: boolean;
  onClear?: () => void;
  onSearch?: (value: string) => void;
}

// Memoized style objects for better performance
const STYLES = {
  sizes: {
    sm: 'px-3 py-2 text-sm',
    md: 'px-4 py-3 text-base',
    lg: 'px-6 py-4 text-lg',
  },
  variants: {
    default: 'border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20',
    filled: 'border-0 bg-gray-100 focus:bg-white focus:ring-2 focus:ring-blue-500/20',
    outlined: 'border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20',
  },
} as const;

// Base input styles that don't change
const BASE_INPUT_STYLES = [
  'block w-full transition-all duration-200',
  'placeholder:text-gray-400',
  'disabled:opacity-50 disabled:cursor-not-allowed',
] as const;

export const AdvancedInput = memo(forwardRef<HTMLInputElement, AdvancedInputProps>(
  (
    {
      label,
      helperText,
      error,
      success,
      leftIcon,
      rightIcon,
      size = 'md',
      variant = 'default',
      fullWidth = false,
      clearable = false,
      searchable = false,
      password = false,
      required = false,
      disabled = false,
      loading = false,
      onClear,
      onSearch,
      className,
      value,
      onChange,
      ...props
    },
    ref
  ) => {
    const [showPassword, setShowPassword] = useState(false);
    const [inputValue, setInputValue] = useState(value || '');
    const [isFocused, setIsFocused] = useState(false);

    // Memoize computed values
    const isDisabled = useMemo(() => disabled || loading, [disabled, loading]);
    const hasRightIcons = useMemo(() => 
      Boolean(rightIcon || clearable || password || loading || error || success), 
      [rightIcon, clearable, password, loading, error, success]
    );

    // Memoize input classes
    const inputClasses = useMemo(() => {
      return cn(
        BASE_INPUT_STYLES,
        STYLES.sizes[size],
        STYLES.variants[variant],
        // Status colors
        error && 'border-red-500 focus:border-red-500 focus:ring-red-500/20',
        success && 'border-green-500 focus:border-green-500 focus:ring-green-500/20',
        // Icon padding
        leftIcon && 'pl-10',
        hasRightIcons && 'pr-10',
        // Focus state
        isFocused && 'ring-2 ring-blue-500/20',
        className
      );
    }, [size, variant, error, success, leftIcon, hasRightIcons, isFocused, className]);

    // Memoize input type
    const inputType = useMemo(() => {
      if (password && !showPassword) return 'password';
      return props.type || 'text';
    }, [password, showPassword, props.type]);

    // Memoize status icon
    const statusIcon = useMemo(() => {
      if (loading) {
        return (
          <div 
            className="animate-spin rounded-full h-4 w-4 border-2 border-blue-500 border-t-transparent" 
            aria-hidden="true"
          />
        );
      }
      if (error) return <AlertCircle className="h-4 w-4 text-red-500" aria-hidden="true" />;
      if (success) return <CheckCircle className="h-4 w-4 text-green-500" aria-hidden="true" />;
      return null;
    }, [loading, error, success]);

    // Memoize status color
    const statusColor = useMemo(() => {
      if (error) return 'border-red-500 focus:border-red-500 focus:ring-red-500/20';
      if (success) return 'border-green-500 focus:border-green-500 focus:ring-green-500/20';
      return '';
    }, [error, success]);

    // Memoize container classes
    const containerClasses = useMemo(() => {
      return cn('space-y-2', fullWidth && 'w-full');
    }, [fullWidth]);

    // Memoize label
    const labelElement = useMemo(() => {
      if (!label) return null;
      
      return (
        <label className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1" aria-label="required">*</span>}
        </label>
      );
    }, [label, required]);

    // Memoize helper text
    const helperTextElement = useMemo(() => {
      if (!helperText || error || success) return null;
      
      return (
        <p className="text-sm text-gray-500" id={`${props.id || 'input'}-helper`}>
          {helperText}
        </p>
      );
    }, [helperText, error, success, props.id]);

    // Memoize error message
    const errorElement = useMemo(() => {
      if (!error) return null;
      
      return (
        <p className="text-sm text-red-600 flex items-center" role="alert">
          <AlertCircle className="h-4 w-4 mr-1" aria-hidden="true" />
          {error}
        </p>
      );
    }, [error]);

    // Memoize success message
    const successElement = useMemo(() => {
      if (!success) return null;
      
      return (
        <p className="text-sm text-green-600 flex items-center">
          <CheckCircle className="h-4 w-4 mr-1" aria-hidden="true" />
          {success}
        </p>
      );
    }, [success]);

    // Event handlers
    const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
      const newValue = e.target.value;
      setInputValue(newValue);
      onChange?.(e);
      
      if (searchable && onSearch) {
        onSearch(newValue);
      }
    }, [onChange, searchable, onSearch]);

    const handleClear = useCallback(() => {
      setInputValue('');
      onClear?.();
      // Trigger onChange with empty value
      const event = {
        target: { value: '' }
      } as React.ChangeEvent<HTMLInputElement>;
      onChange?.(event);
    }, [onClear, onChange]);

    const handlePasswordToggle = useCallback(() => {
      setShowPassword(prev => !prev);
    }, []);

    const handleFocus = useCallback(() => {
      setIsFocused(true);
    }, []);

    const handleBlur = useCallback(() => {
      setIsFocused(false);
    }, []);

    return (
      <div className={containerClasses}>
        {labelElement}

        <div className="relative">
          {/* Left Icon */}
          {leftIcon && (
            <div 
              className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
              aria-hidden="true"
            >
              {leftIcon}
            </div>
          )}

          {/* Input Field */}
          <input
            ref={ref}
            type={inputType}
            value={inputValue}
            onChange={handleChange}
            onFocus={handleFocus}
            onBlur={handleBlur}
            disabled={isDisabled}
            className={inputClasses}
            aria-invalid={Boolean(error)}
            aria-describedby={
              [helperText && !error && !success ? `${props.id || 'input'}-helper` : null]
                .filter(Boolean)
                .join(' ') || undefined
            }
            {...props}
          />

          {/* Right Icons Container */}
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 flex items-center space-x-2">
            {/* Status Icon */}
            {statusIcon}
            
            {/* Search Icon */}
            {searchable && <Search className="h-4 w-4 text-gray-400" aria-hidden="true" />}
            
            {/* Password Toggle */}
            {password && (
              <button
                type="button"
                onClick={handlePasswordToggle}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label={showPassword ? 'Hide password' : 'Show password'}
                disabled={isDisabled}
              >
                {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            )}
            
            {/* Clear Button */}
            {clearable && inputValue && (
              <button
                type="button"
                onClick={handleClear}
                className="text-gray-400 hover:text-gray-600 transition-colors"
                aria-label="Clear input"
                disabled={isDisabled}
              >
                <X className="h-4 w-4" />
              </button>
            )}
            
            {/* Custom Right Icon */}
            {rightIcon && !clearable && !password && !statusIcon && (
              <span className="text-gray-400" aria-hidden="true">{rightIcon}</span>
            )}
          </div>
        </div>

        {helperTextElement}
        {errorElement}
        {successElement}
      </div>
    );
  }
));

AdvancedInput.displayName = 'AdvancedInput';

// Memoized specialized variants for better performance
export const SearchInput = memo(forwardRef<HTMLInputElement, Omit<AdvancedInputProps, 'searchable' | 'leftIcon'>>(
  (props, ref) => (
    <AdvancedInput
      ref={ref}
      searchable
      leftIcon={<Search className="h-4 w-4" />}
      placeholder="Search..."
      {...props}
    />
  )
));
SearchInput.displayName = 'SearchInput';

export const PasswordInput = memo(forwardRef<HTMLInputElement, Omit<AdvancedInputProps, 'password' | 'type'>>(
  (props, ref) => (
    <AdvancedInput
      ref={ref}
      password
      type="password"
      {...props}
    />
  )
));
PasswordInput.displayName = 'PasswordInput';

export const EmailInput = memo(forwardRef<HTMLInputElement, Omit<AdvancedInputProps, 'type'>>(
  (props, ref) => (
    <AdvancedInput
      ref={ref}
      type="email"
      {...props}
    />
  )
));
EmailInput.displayName = 'EmailInput';

export const NumberInput = memo(forwardRef<HTMLInputElement, Omit<AdvancedInputProps, 'type'>>(
  (props, ref) => (
    <AdvancedInput
      ref={ref}
      type="number"
      {...props}
    />
  )
));
NumberInput.displayName = 'NumberInput';
