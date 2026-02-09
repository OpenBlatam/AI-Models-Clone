'use client';

import { forwardRef, type HTMLAttributes } from 'react';
import { motion } from 'framer-motion';

type CardVariant = 'default' | 'bordered' | 'elevated' | 'glass';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
    variant?: CardVariant;
    isHoverable?: boolean;
    isClickable?: boolean;
}

const variantClasses: Record<CardVariant, string> = {
    default: 'bg-card',
    bordered: 'bg-card border border-primary/20',
    elevated: 'bg-card shadow-xl shadow-black/20',
    glass: 'bg-card/80 backdrop-blur-xl border border-white/10',
};

export const Card = forwardRef<HTMLDivElement, CardProps>(
    (
        {
            className = '',
            variant = 'default',
            isHoverable = false,
            isClickable = false,
            children,
            ...props
        },
        ref
    ) => {
        const hoverClass = isHoverable ? 'hover:bg-card-hover transition-colors duration-300' : '';
        const clickableClass = isClickable ? 'cursor-pointer' : '';

        return (
            <motion.div
                ref={ref}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3 }}
                whileHover={isHoverable ? { scale: 1.01, y: -2 } : undefined}
                className={`
          rounded-2xl p-6
          ${variantClasses[variant]}
          ${hoverClass}
          ${clickableClass}
          ${className}
        `}
                tabIndex={isClickable ? 0 : undefined}
                role={isClickable ? 'button' : undefined}
                {...props}
            >
                {children}
            </motion.div>
        );
    }
);

Card.displayName = 'Card';

// Sub-components
export const CardHeader = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div
            ref={ref}
            className={`mb-4 ${className}`}
            {...props}
        >
            {children}
        </div>
    )
);

CardHeader.displayName = 'CardHeader';

export const CardTitle = forwardRef<HTMLHeadingElement, HTMLAttributes<HTMLHeadingElement>>(
    ({ className = '', children, ...props }, ref) => (
        <h3
            ref={ref}
            className={`text-xl font-bold text-text ${className}`}
            {...props}
        >
            {children}
        </h3>
    )
);

CardTitle.displayName = 'CardTitle';

export const CardDescription = forwardRef<HTMLParagraphElement, HTMLAttributes<HTMLParagraphElement>>(
    ({ className = '', children, ...props }, ref) => (
        <p
            ref={ref}
            className={`text-sm text-text-muted ${className}`}
            {...props}
        >
            {children}
        </p>
    )
);

CardDescription.displayName = 'CardDescription';

export const CardContent = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div
            ref={ref}
            className={`${className}`}
            {...props}
        >
            {children}
        </div>
    )
);

CardContent.displayName = 'CardContent';

export const CardFooter = forwardRef<HTMLDivElement, HTMLAttributes<HTMLDivElement>>(
    ({ className = '', children, ...props }, ref) => (
        <div
            ref={ref}
            className={`mt-4 pt-4 border-t border-white/10 ${className}`}
            {...props}
        >
            {children}
        </div>
    )
);

CardFooter.displayName = 'CardFooter';

export default Card;
