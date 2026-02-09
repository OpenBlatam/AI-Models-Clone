'use client';

import { forwardRef, type HTMLAttributes } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { AlertCircle, CheckCircle, AlertTriangle, Info, X } from 'lucide-react';

type AlertVariant = 'info' | 'success' | 'warning' | 'error';

interface AlertProps extends Omit<HTMLAttributes<HTMLDivElement>, 'title'> {
    variant?: AlertVariant;
    title?: string;
    description?: string;
    isClosable?: boolean;
    onClose?: () => void;
}

const variantConfig: Record<AlertVariant, {
    icon: typeof AlertCircle;
    containerClass: string;
    iconClass: string;
}> = {
    info: {
        icon: Info,
        containerClass: 'bg-secondary/10 border-secondary/30',
        iconClass: 'text-secondary',
    },
    success: {
        icon: CheckCircle,
        containerClass: 'bg-accent-success/10 border-accent-success/30',
        iconClass: 'text-accent-success',
    },
    warning: {
        icon: AlertTriangle,
        containerClass: 'bg-accent-warning/10 border-accent-warning/30',
        iconClass: 'text-accent-warning',
    },
    error: {
        icon: AlertCircle,
        containerClass: 'bg-accent-error/10 border-accent-error/30',
        iconClass: 'text-accent-error',
    },
};

export const Alert = forwardRef<HTMLDivElement, AlertProps>(
    (
        {
            className = '',
            variant = 'info',
            title,
            description,
            isClosable = false,
            onClose,
            children,
            ...props
        },
        ref
    ) => {
        const { icon: Icon, containerClass, iconClass } = variantConfig[variant];

        return (
            <AnimatePresence>
                <motion.div
                    ref={ref}
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    className={`
            flex items-start gap-3 p-4
            rounded-xl border
            ${containerClass}
            ${className}
          `}
                    role="alert"
                    aria-live="polite"
                    {...props}
                >
                    <Icon
                        className={`w-5 h-5 flex-shrink-0 mt-0.5 ${iconClass}`}
                        aria-hidden="true"
                    />
                    <div className="flex-1 min-w-0">
                        {title && (
                            <h4 className="font-semibold text-text mb-1">{title}</h4>
                        )}
                        {description && (
                            <p className="text-sm text-text-muted">{description}</p>
                        )}
                        {children}
                    </div>
                    {isClosable && onClose && (
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-shrink-0 p-1 rounded-lg hover:bg-white/10 transition-colors"
                            aria-label="Close alert"
                            tabIndex={0}
                        >
                            <X className="w-4 h-4 text-text-muted" aria-hidden="true" />
                        </button>
                    )}
                </motion.div>
            </AnimatePresence>
        );
    }
);

Alert.displayName = 'Alert';

export default Alert;
