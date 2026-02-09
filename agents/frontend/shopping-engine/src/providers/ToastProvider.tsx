'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// Toast Notifications Provider
// ═══════════════════════════════════════════════════════════════════════════════

import { Toaster, toast } from 'react-hot-toast';

export const ToastProvider = () => {
    return (
        <Toaster
            position="top-right"
            toastOptions={{
                duration: 4000,
                style: {
                    background: 'hsl(240, 10%, 10%)',
                    color: 'hsl(0, 0%, 95%)',
                    border: '1px solid hsl(258, 90%, 66%, 0.3)',
                    borderRadius: '12px',
                    padding: '16px',
                    fontSize: '14px',
                    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3)',
                },
                success: {
                    iconTheme: {
                        primary: 'hsl(142, 76%, 55%)',
                        secondary: 'hsl(240, 10%, 10%)',
                    },
                    style: {
                        border: '1px solid hsl(142, 76%, 55%, 0.3)',
                    },
                },
                error: {
                    iconTheme: {
                        primary: 'hsl(0, 84%, 60%)',
                        secondary: 'hsl(240, 10%, 10%)',
                    },
                    style: {
                        border: '1px solid hsl(0, 84%, 60%, 0.3)',
                    },
                },
                loading: {
                    iconTheme: {
                        primary: 'hsl(258, 90%, 66%)',
                        secondary: 'hsl(240, 10%, 10%)',
                    },
                },
            }}
        />
    );
};

// ── Toast Helpers ────────────────────────────────────────────────────────────

export const showToast = {
    success: (message: string) => {
        toast.success(message);
    },

    error: (message: string) => {
        toast.error(message);
    },

    loading: (message: string) => {
        return toast.loading(message);
    },

    dismiss: (toastId?: string) => {
        if (toastId) {
            toast.dismiss(toastId);
        } else {
            toast.dismiss();
        }
    },

    promise: <T,>(
        promise: Promise<T>,
        messages: {
            loading: string;
            success: string;
            error: string;
        }
    ) => {
        return toast.promise(promise, messages);
    },

    custom: (message: string, options?: { icon?: string; duration?: number }) => {
        toast(message, {
            icon: options?.icon || '💡',
            duration: options?.duration || 4000,
        });
    },
};

export default ToastProvider;
