'use client';

import React, { useEffect, useState } from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@/lib/utils';
import { 
  CheckCircle, 
  XCircle, 
  AlertTriangle, 
  Info, 
  X,
  AlertCircle 
} from 'lucide-react';
import { useToastNotifications, useAppActions } from '@/stores/app-store';

export interface ToastProps {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  onClose?: () => void;
}

const toastIcons = {
  success: CheckCircle,
  error: XCircle,
  warning: AlertTriangle,
  info: Info,
};

const toastStyles = {
  success: 'bg-green-50 border-green-200 text-green-800',
  error: 'bg-red-50 border-red-200 text-red-800',
  warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
  info: 'bg-blue-50 border-blue-200 text-blue-800',
};

const iconStyles = {
  success: 'text-green-500',
  error: 'text-red-500',
  warning: 'text-yellow-500',
  info: 'text-blue-500',
};

export function Toast({ 
  id, 
  type, 
  title, 
  message, 
  duration = 5000, 
  action, 
  onClose 
}: ToastProps) {
  const [isVisible, setIsVisible] = useState(false);
  const [isExiting, setIsExiting] = useState(false);
  const { removeToast } = useAppActions();

  useEffect(() => {
    // Animate in
    const timer = setTimeout(() => setIsVisible(true), 100);
    
    // Auto-dismiss
    if (duration > 0) {
      const dismissTimer = setTimeout(() => {
        handleClose();
      }, duration);
      
      return () => clearTimeout(dismissTimer);
    }
    
    return () => clearTimeout(timer);
  }, [duration]);

  const handleClose = () => {
    setIsExiting(true);
    setTimeout(() => {
      removeToast(id);
      onClose?.();
    }, 300);
  };

  const handleAction = () => {
    action?.onClick();
    handleClose();
  };

  const IconComponent = toastIcons[type];

  return (
    <div
      className={cn(
        'relative w-full max-w-sm bg-white border rounded-lg shadow-lg p-4 transition-all duration-300 ease-in-out',
        'transform transition-all duration-300',
        isVisible && !isExiting ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0',
        isExiting && 'translate-x-full opacity-0 scale-95',
        toastStyles[type]
      )}
      role="alert"
      aria-live="assertive"
      aria-atomic="true"
    >
      {/* Close button */}
      <button
        onClick={handleClose}
        className="absolute top-2 right-2 p-1 rounded-full hover:bg-black/5 transition-colors"
        aria-label="Close notification"
      >
        <X className="h-4 w-4" />
      </button>

      {/* Content */}
      <div className="flex items-start space-x-3">
        {/* Icon */}
        <div className={cn('flex-shrink-0', iconStyles[type])}>
          <IconComponent className="h-5 w-5" />
        </div>

        {/* Text content */}
        <div className="flex-1 min-w-0">
          <h4 className="text-sm font-medium">{title}</h4>
          {message && (
            <p className="mt-1 text-sm opacity-90">{message}</p>
          )}
          
          {/* Action button */}
          {action && (
            <button
              onClick={handleAction}
              className="mt-2 text-sm font-medium underline hover:no-underline transition-all"
            >
              {action.label}
            </button>
          )}
        </div>
      </div>

      {/* Progress bar */}
      {duration > 0 && (
        <div className="absolute bottom-0 left-0 h-1 bg-current opacity-20 rounded-b-lg">
          <div
            className="h-full bg-current transition-all duration-300 ease-linear"
            style={{
              width: isExiting ? '0%' : '100%',
              transitionDuration: `${duration}ms`,
            }}
          />
        </div>
      )}
    </div>
  );
}

export function ToastContainer() {
  const notifications = useToastNotifications();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return createPortal(
    <div className="fixed top-4 right-4 z-50 space-y-3 max-w-sm">
      {notifications.map((notification) => (
        <Toast
          key={notification.id}
          {...notification}
        />
      ))}
    </div>,
    document.body
  );
}

// Toast hook for easy usage
export function useToast() {
  const { addToast, removeToast } = useAppActions();

  const toast = {
    success: (title: string, message?: string, options?: Partial<ToastProps>) => {
      addToast({
        type: 'success',
        title,
        message,
        ...options,
      });
    },
    
    error: (title: string, message?: string, options?: Partial<ToastProps>) => {
      addToast({
        type: 'error',
        title,
        message,
        ...options,
      });
    },
    
    warning: (title: string, message?: string, options?: Partial<ToastProps>) => {
      addToast({
        type: 'warning',
        title,
        message,
        ...options,
      });
    },
    
    info: (title: string, message?: string, options?: Partial<ToastProps>) => {
      addToast({
        type: 'info',
        title,
        message,
        ...options,
      });
    },
    
    remove: removeToast,
  };

  return toast;
}

// Toast variants for different use cases
export const showSuccessToast = (title: string, message?: string) => {
  // This would be used in server components or outside React context
  if (typeof window !== 'undefined') {
    // Dispatch custom event for toast
    window.dispatchEvent(
      new CustomEvent('show-toast', {
        detail: { type: 'success', title, message }
      })
    );
  }
};

export const showErrorToast = (title: string, message?: string) => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('show-toast', {
        detail: { type: 'error', title, message }
      })
    );
  }
};

export const showWarningToast = (title: string, message?: string) => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('show-toast', {
        detail: { type: 'warning', title, message }
      })
    );
  }
};

export const showInfoToast = (title: string, message?: string) => {
  if (typeof window !== 'undefined') {
    window.dispatchEvent(
      new CustomEvent('show-toast', {
        detail: { type: 'info', title, message }
      })
    );
  }
};

// Global toast listener
if (typeof window !== 'undefined') {
  window.addEventListener('show-toast', ((event: CustomEvent) => {
    const { type, title, message } = event.detail;
    // This would integrate with your toast system
    console.log('Global toast event:', { type, title, message });
  }) as EventListener);
}
