'use client';

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import { cn } from '@/lib/utils';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { runtimeUtils } from '@/lib/runtime-profiler';

export interface OptimizedCardProps {
  title: string;
  description?: string;
  content?: React.ReactNode;
  footer?: React.ReactNode;
  tags?: string[];
  imageUrl?: string;
  imageAlt?: string;
  variant?: 'default' | 'elevated' | 'outlined' | 'minimal';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  interactive?: boolean;
  onAction?: () => void;
  actionLabel?: string;
  className?: string;
  children?: React.ReactNode;
}

export interface OptimizedCardState {
  isVisible: boolean;
  isLoaded: boolean;
  isHovered: boolean;
  isPressed: boolean;
}

const VARIANTS = {
  default: 'bg-background border border-border shadow-sm hover:shadow-md transition-shadow',
  elevated: 'bg-background border-0 shadow-lg hover:shadow-xl transition-shadow',
  outlined: 'bg-background border-2 border-border shadow-none hover:border-primary/50 transition-colors',
  minimal: 'bg-background/50 border-0 shadow-none backdrop-blur-sm hover:bg-background/80 transition-colors',
} as const;

const SIZES = {
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
} as const;

const OptimizedCard = React.memo<OptimizedCardProps>(({
  title,
  description,
  content,
  footer,
  tags = [],
  imageUrl,
  imageAlt,
  variant = 'default',
  size = 'md',
  loading = false,
  interactive = false,
  onAction,
  actionLabel,
  className,
  children,
}) => {
  // Performance profiling
  const stopProfiling = runtimeUtils.startProfiling('OptimizedCard');
  
  // State management with useReducer pattern for complex state
  const [state, setState] = useState<OptimizedCardState>({
    isVisible: false,
    isLoaded: false,
    isHovered: false,
    isPressed: false,
  });

  // Refs for intersection observer and performance optimization
  const cardRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);

  // Memoized values for performance
  const cardClasses = useMemo(() => {
    return cn(
      'group relative overflow-hidden rounded-lg transition-all duration-200',
      VARIANTS[variant],
      SIZES[size],
      interactive && 'cursor-pointer select-none',
      state.isHovered && interactive && 'scale-[1.02]',
      state.isPressed && interactive && 'scale-[0.98]',
      className
    );
  }, [variant, size, interactive, state.isHovered, state.isPressed, className]);

  const headerClasses = useMemo(() => {
    return cn(
      'space-y-2',
      size === 'sm' ? 'mb-3' : size === 'md' ? 'mb-4' : 'mb-6'
    );
  }, [size]);

  const contentClasses = useMemo(() => {
    return cn(
      'space-y-4',
      size === 'sm' ? 'mb-3' : size === 'md' ? 'mb-4' : 'mb-6'
    );
  }, [size]);

  // Memoized event handlers
  const handleMouseEnter = useCallback(() => {
    if (interactive) {
      setState(prev => ({ ...prev, isHovered: true }));
    }
  }, [interactive]);

  const handleMouseLeave = useCallback(() => {
    if (interactive) {
      setState(prev => ({ ...prev, isHovered: false, isPressed: false }));
    }
  }, [interactive]);

  const handleMouseDown = useCallback(() => {
    if (interactive) {
      setState(prev => ({ ...prev, isPressed: true }));
    }
  }, [interactive]);

  const handleMouseUp = useCallback(() => {
    if (interactive) {
      setState(prev => ({ ...prev, isPressed: false }));
    }
  }, [interactive]);

  const handleClick = useCallback(() => {
    if (interactive && onAction) {
      onAction();
    }
  }, [interactive, onAction]);

  const handleImageLoad = useCallback(() => {
    setState(prev => ({ ...prev, isLoaded: true }));
  }, []);

  // Intersection Observer for lazy loading and visibility tracking
  useEffect(() => {
    if (!cardRef.current) return;

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setState(prev => ({ ...prev, isVisible: true }));
            observer.unobserve(entry.target);
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
      }
    );

    observer.observe(cardRef.current);

    return () => {
      if (cardRef.current) {
        observer.unobserve(cardRef.current);
      }
    };
  }, []);

  // Memoized image component for performance
  const OptimizedImage = useMemo(() => {
    if (!imageUrl) return null;

    return (
      <div className="relative mb-4 overflow-hidden rounded-md">
        {!state.isLoaded && (
          <Skeleton className="h-48 w-full" />
        )}
        <img
          ref={imageRef}
          src={imageUrl}
          alt={imageAlt || title}
          className={cn(
            'h-48 w-full object-cover transition-opacity duration-300',
            state.isLoaded ? 'opacity-100' : 'opacity-0'
          )}
          loading="lazy"
          onLoad={handleImageLoad}
        />
      </div>
    );
  }, [imageUrl, imageAlt, title, state.isLoaded, handleImageLoad]);

  // Memoized tags component
  const OptimizedTags = useMemo(() => {
    if (tags.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-2">
        {tags.map((tag, index) => (
          <Badge
            key={`${tag}-${index}`}
            variant="secondary"
            className="text-xs"
          >
            {tag}
          </Badge>
        ))}
      </div>
    );
  }, [tags]);

  // Memoized action button
  const OptimizedActionButton = useMemo(() => {
    if (!onAction || !actionLabel) return null;

    return (
      <Button
        onClick={handleClick}
        size={size === 'sm' ? 'sm' : 'default'}
        className="w-full"
      >
        {actionLabel}
      </Button>
    );
  }, [onAction, actionLabel, handleClick, size]);

  // Cleanup profiling on unmount
  useEffect(() => {
    return () => {
      stopProfiling();
    };
  }, [stopProfiling]);

  // Loading state
  if (loading) {
    return (
      <Card className={cn('animate-pulse', className)}>
        <CardHeader>
          <Skeleton className="h-6 w-3/4" />
          <Skeleton className="h-4 w-1/2" />
        </CardHeader>
        <CardContent>
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-2/3" />
        </CardContent>
        <CardFooter>
          <Skeleton className="h-10 w-full" />
        </CardFooter>
      </Card>
    );
  }

  return (
    <Card
      ref={cardRef}
      className={cardClasses}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      onMouseDown={handleMouseDown}
      onMouseUp={handleMouseUp}
      onClick={handleClick}
      role={interactive ? 'button' : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-label={interactive ? title : undefined}
    >
      {OptimizedImage}
      
      <CardHeader className={headerClasses}>
        <CardTitle className="text-lg font-semibold leading-tight">
          {title}
        </CardTitle>
        {description && (
          <CardDescription className="text-sm text-muted-foreground">
            {description}
          </CardDescription>
        )}
        {OptimizedTags}
      </CardHeader>

      {(content || children) && (
        <CardContent className={contentClasses}>
          {content || children}
        </CardContent>
      )}

      {(footer || OptimizedActionButton) && (
        <CardFooter className="flex flex-col gap-3">
          {footer}
          {OptimizedActionButton}
        </CardFooter>
      )}
    </Card>
  );
});

OptimizedCard.displayName = 'OptimizedCard';

// Specialized card variants for common use cases
export const InfoCard = React.memo<Omit<OptimizedCardProps, 'variant' | 'interactive'>>((props) => (
  <OptimizedCard {...props} variant="outlined" />
));

export const ActionCard = React.memo<Omit<OptimizedCardProps, 'variant' | 'interactive'> & { onAction: () => void; actionLabel: string }>((props) => (
  <OptimizedCard {...props} variant="elevated" interactive />
));

export const MinimalCard = React.memo<Omit<OptimizedCardProps, 'variant'>>((props) => (
  <OptimizedCard {...props} variant="minimal" />
));

export const LoadingCard = React.memo<Omit<OptimizedCardProps, 'loading'>>((props) => (
  <OptimizedCard {...props} loading />
));

// Export the main component and variants
export { OptimizedCard };
export default OptimizedCard;
