'use client';

import React, { forwardRef, useMemo } from 'react';
import { cn } from '@/lib/utils';
import { Button } from './button';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from './tooltip';
import { Loader2, AlertCircle, CheckCircle, Info } from 'lucide-react';
import { usePerformanceMonitor } from '@/lib/stores/examples-store';

export interface AdvancedButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' | 'gradient';
  size?: 'default' | 'sm' | 'lg' | 'xl';
  loading?: boolean;
  success?: boolean;
  error?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  tooltip?: string;
  tooltipPosition?: 'top' | 'bottom' | 'left' | 'right';
  badge?: string;
  badgeVariant?: 'default' | 'secondary' | 'destructive' | 'outline';
  gradient?: 'blue' | 'green' | 'purple' | 'orange' | 'red';
  rounded?: 'default' | 'full' | 'none';
  shadow?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  animation?: 'none' | 'pulse' | 'bounce' | 'spin' | 'ping';
  disabled?: boolean;
  children: React.ReactNode;
}

const AdvancedButton = forwardRef<HTMLButtonElement, AdvancedButtonProps>(
  (
    {
      className,
      variant = 'default',
      size = 'default',
      loading = false,
      success = false,
      error = false,
      icon,
      iconPosition = 'left',
      tooltip,
      tooltipPosition = 'top',
      badge,
      badgeVariant = 'default',
      gradient = 'blue',
      rounded = 'default',
      shadow = 'md',
      animation = 'none',
      disabled = false,
      children,
      onClick,
      ...props
    },
    ref
  ) => {
    // Performance monitoring
    const { measureRenderTime } = usePerformanceMonitor();

    // Memoized classes for performance
    const buttonClasses = useMemo(() => {
      const baseClasses = cn(
        'relative inline-flex items-center justify-center font-medium transition-all duration-200',
        'focus:outline-none focus:ring-2 focus:ring-offset-2',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        'hover:scale-105 active:scale-95',
        {
          // Size variants
          'h-9 px-3 text-sm': size === 'sm',
          'h-10 px-4 py-2': size === 'default',
          'h-11 px-8': size === 'lg',
          'h-12 px-10 text-lg': size === 'xl',
          
          // Rounded variants
          'rounded-md': rounded === 'default',
          'rounded-full': rounded === 'full',
          'rounded-none': rounded === 'none',
          
          // Shadow variants
          'shadow-none': shadow === 'none',
          'shadow-sm': shadow === 'sm',
          'shadow-md': shadow === 'md',
          'shadow-lg': shadow === 'lg',
          'shadow-xl': shadow === 'xl',
          
          // Animation variants
          'animate-none': animation === 'none',
          'animate-pulse': animation === 'pulse',
          'animate-bounce': animation === 'bounce',
          'animate-spin': animation === 'spin',
          'animate-ping': animation === 'ping',
        },
        className
      );

      // Gradient variants
      if (variant === 'gradient') {
        const gradientClasses = {
          blue: 'bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white',
          green: 'bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 text-white',
          purple: 'bg-gradient-to-r from-purple-500 to-purple-600 hover:from-purple-600 hover:to-purple-700 text-white',
          orange: 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white',
          red: 'bg-gradient-to-r from-red-500 to-red-600 hover:from-red-600 hover:to-red-700 text-white',
        };
        return cn(baseClasses, gradientClasses[gradient]);
      }

      return baseClasses;
    }, [variant, size, rounded, shadow, animation, gradient, className]);

    // Memoized icon classes
    const iconClasses = useMemo(() => {
      return cn('transition-all duration-200', {
        'mr-2': iconPosition === 'left' && !loading,
        'ml-2': iconPosition === 'right' && !loading,
        'mr-2 animate-spin': loading && iconPosition === 'left',
        'ml-2 animate-spin': loading && iconPosition === 'right',
      });
    }, [iconPosition, loading]);

    // Memoized status icon
    const statusIcon = useMemo(() => {
      if (loading) return <Loader2 className="h-4 w-4" />;
      if (success) return <CheckCircle className="h-4 w-4 text-green-500" />;
      if (error) return <AlertCircle className="h-4 w-4 text-red-500" />;
      return icon;
    }, [loading, success, error, icon]);

    // Enhanced click handler with performance monitoring
    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
      const cleanup = measureRenderTime('AdvancedButton');
      
      if (onClick) {
        onClick(event);
      }
      
      cleanup();
    };

    // Button content
    const buttonContent = (
      <>
        {statusIcon && iconPosition === 'left' && (
          <span className={iconClasses}>{statusIcon}</span>
        )}
        
        <span className="relative">
          {children}
          {badge && (
            <span className={cn(
              'absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-medium rounded-full',
              'bg-primary text-primary-foreground',
              {
                'bg-secondary text-secondary-foreground': badgeVariant === 'secondary',
                'bg-destructive text-destructive-foreground': badgeVariant === 'destructive',
                'border border-input bg-background': badgeVariant === 'outline',
              }
            )}>
              {badge}
            </span>
          )}
        </span>
        
        {statusIcon && iconPosition === 'right' && (
          <span className={iconClasses}>{statusIcon}</span>
        )}
      </>
    );

    // If tooltip is provided, wrap with tooltip
    if (tooltip) {
      return (
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button
                ref={ref}
                variant={variant === 'gradient' ? 'default' : variant}
                size={size}
                disabled={disabled || loading}
                className={buttonClasses}
                onClick={handleClick}
                {...props}
              >
                {buttonContent}
              </Button>
            </TooltipTrigger>
            <TooltipContent side={tooltipPosition}>
              <p>{tooltip}</p>
            </TooltipContent>
          </Tooltip>
        </TooltipProvider>
      );
    }

    // Return regular button
    return (
      <Button
        ref={ref}
        variant={variant === 'gradient' ? 'default' : variant}
        size={size}
        disabled={disabled || loading}
        className={buttonClasses}
        onClick={handleClick}
        {...props}
      >
        {buttonContent}
      </Button>
    );
  }
);

AdvancedButton.displayName = 'AdvancedButton';

export { AdvancedButton };





