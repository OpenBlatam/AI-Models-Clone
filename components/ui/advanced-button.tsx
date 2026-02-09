'use client';

import React, { forwardRef, ButtonHTMLAttributes, memo, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Loader2 } from 'lucide-react';

export interface AdvancedButtonProps extends Omit<ButtonHTMLAttributes<HTMLButtonElement>, 'size'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'destructive' | 'success' | 'warning';
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  loading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
  rounded?: 'none' | 'sm' | 'md' | 'lg' | 'full';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  animation?: 'none' | 'pulse' | 'bounce' | 'spin';
  disabled?: boolean;
  children: React.ReactNode;
}

// Memoized style objects for better performance
const STYLES = {
  variants: {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white shadow-lg hover:shadow-xl focus:ring-blue-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white shadow-md hover:shadow-lg focus:ring-gray-500',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus:ring-blue-500',
    ghost: 'text-gray-700 hover:bg-gray-100 hover:text-gray-900 focus:ring-gray-500',
    destructive: 'bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-xl focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-xl focus:ring-green-500',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white shadow-lg hover:shadow-xl focus:ring-yellow-500',
  },
  sizes: {
    xs: 'px-2 py-1 text-xs font-medium',
    sm: 'px-3 py-2 text-sm font-medium',
    md: 'px-4 py-2 text-sm font-medium',
    lg: 'px-6 py-3 text-base font-medium',
    xl: 'px-8 py-4 text-lg font-medium',
  },
  rounded: {
    none: 'rounded-none',
    sm: 'rounded-sm',
    md: 'rounded-md',
    lg: 'rounded-lg',
    full: 'rounded-full',
  },
  shadows: {
    none: 'shadow-none',
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  },
  animations: {
    none: '',
    pulse: 'animate-pulse',
    bounce: 'animate-bounce',
    spin: 'animate-spin',
  },
} as const;

// Base button styles that don't change
const BASE_STYLES = [
  'inline-flex items-center justify-center font-medium transition-all duration-200',
  'focus:outline-none focus:ring-2 focus:ring-offset-2',
  'disabled:opacity-50 disabled:cursor-not-allowed disabled:pointer-events-none',
  'hover:scale-105 active:scale-95',
] as const;

export const AdvancedButton = memo(forwardRef<HTMLButtonElement, AdvancedButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      loadingText,
      leftIcon,
      rightIcon,
      fullWidth = false,
      rounded = 'md',
      shadow = 'md',
      animation = 'none',
      disabled = false,
      className,
      children,
      ...props
    },
    ref
  ) => {
    // Memoize computed values to prevent unnecessary recalculations
    const isDisabled = useMemo(() => disabled || loading, [disabled, loading]);
    
    const buttonClasses = useMemo(() => {
      return cn(
        BASE_STYLES,
        STYLES.variants[variant],
        STYLES.sizes[size],
        STYLES.rounded[rounded],
        STYLES.shadows[shadow],
        STYLES.animations[animation],
        fullWidth && 'w-full',
        className
      );
    }, [variant, size, rounded, shadow, animation, fullWidth, className]);

    // Memoize loading content to prevent unnecessary re-renders
    const loadingContent = useMemo(() => {
      if (!loading) return null;
      
      return (
        <>
          <Loader2 className="mr-2 h-4 w-4 animate-spin" aria-hidden="true" />
          <span>{loadingText || 'Loading...'}</span>
        </>
      );
    }, [loading, loadingText]);

    // Memoize normal content
    const normalContent = useMemo(() => {
      if (loading) return null;
      
      return (
        <>
          {leftIcon && <span className="mr-2" aria-hidden="true">{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span className="ml-2" aria-hidden="true">{rightIcon}</span>}
        </>
      );
    }, [loading, leftIcon, rightIcon, children]);

    return (
      <button
        ref={ref}
        disabled={isDisabled}
        className={buttonClasses}
        aria-disabled={isDisabled}
        aria-busy={loading}
        {...props}
      >
        {loadingContent}
        {normalContent}
      </button>
    );
  }
));

AdvancedButton.displayName = 'AdvancedButton';

// Memoized variant components for better performance
export const PrimaryButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="primary" {...props} />
));
PrimaryButton.displayName = 'PrimaryButton';

export const SecondaryButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="secondary" {...props} />
));
SecondaryButton.displayName = 'SecondaryButton';

export const OutlineButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="outline" {...props} />
));
OutlineButton.displayName = 'OutlineButton';

export const GhostButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="ghost" {...props} />
));
GhostButton.displayName = 'GhostButton';

export const DestructiveButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="destructive" {...props} />
));
DestructiveButton.displayName = 'DestructiveButton';

export const SuccessButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="success" {...props} />
));
SuccessButton.displayName = 'SuccessButton';

export const WarningButton = memo(forwardRef<HTMLButtonElement, Omit<AdvancedButtonProps, 'variant'>>(
  (props, ref) => <AdvancedButton ref={ref} variant="warning" {...props} />
));
WarningButton.displayName = 'WarningButton';
