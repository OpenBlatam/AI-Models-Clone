// ═══════════════════════════════════════════════════════════════════════════════
// Utility Functions
// ═══════════════════════════════════════════════════════════════════════════════

import clsx, { type ClassValue } from 'clsx';
import { format, formatDistanceToNow, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';

// ── Class Name Utility ───────────────────────────────────────────────────────

/**
 * Merge class names conditionally
 */
export const cn = (...inputs: ClassValue[]): string => {
    return clsx(inputs);
};

// ── Date Formatting ──────────────────────────────────────────────────────────

/**
 * Format a date string to a readable format
 */
export const formatDate = (dateString: string, formatStr = 'PPP'): string => {
    try {
        const date = parseISO(dateString);
        return format(date, formatStr, { locale: es });
    } catch {
        return dateString;
    }
};

/**
 * Format a date as relative time (e.g., "hace 2 horas")
 */
export const formatRelativeTime = (dateString: string): string => {
    try {
        const date = parseISO(dateString);
        return formatDistanceToNow(date, { addSuffix: true, locale: es });
    } catch {
        return dateString;
    }
};

/**
 * Format a date for display in UI
 */
export const formatDateTime = (dateString: string): string => {
    try {
        const date = parseISO(dateString);
        return format(date, "d 'de' MMMM 'a las' HH:mm", { locale: es });
    } catch {
        return dateString;
    }
};

// ── Currency Formatting ──────────────────────────────────────────────────────

/**
 * Format a number as currency
 */
export const formatCurrency = (
    amount: number,
    currency = 'MXN',
    locale = 'es-MX'
): string => {
    return new Intl.NumberFormat(locale, {
        style: 'currency',
        currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(amount);
};

/**
 * Format a number with thousands separator
 */
export const formatNumber = (num: number, locale = 'es-MX'): string => {
    return new Intl.NumberFormat(locale).format(num);
};

// ── String Utilities ─────────────────────────────────────────────────────────

/**
 * Truncate a string with ellipsis
 */
export const truncate = (str: string, maxLength: number): string => {
    if (str.length <= maxLength) return str;
    return str.slice(0, maxLength - 3) + '...';
};

/**
 * Capitalize first letter
 */
export const capitalize = (str: string): string => {
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

/**
 * Convert snake_case to Title Case
 */
export const snakeToTitle = (str: string): string => {
    return str
        .split('_')
        .map((word) => capitalize(word))
        .join(' ');
};

// ── Validation Utilities ─────────────────────────────────────────────────────

/**
 * Check if a string is a valid URL
 */
export const isValidUrl = (str: string): boolean => {
    try {
        new URL(str);
        return true;
    } catch {
        return false;
    }
};

/**
 * Check if a string is a valid email
 */
export const isValidEmail = (email: string): boolean => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
};

// ── File Utilities ───────────────────────────────────────────────────────────

/**
 * Convert file size to human readable format
 */
export const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

/**
 * Get file extension from filename
 */
export const getFileExtension = (filename: string): string => {
    return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
};

// ── Async Utilities ──────────────────────────────────────────────────────────

/**
 * Delay execution for a specified time
 */
export const delay = (ms: number): Promise<void> => {
    return new Promise((resolve) => setTimeout(resolve, ms));
};

/**
 * Retry a function with exponential backoff
 */
export const retryWithBackoff = async <T>(
    fn: () => Promise<T>,
    maxRetries = 3,
    baseDelay = 1000
): Promise<T> => {
    let lastError: Error | undefined;

    for (let attempt = 0; attempt < maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            lastError = error as Error;
            if (attempt < maxRetries - 1) {
                await delay(baseDelay * Math.pow(2, attempt));
            }
        }
    }

    throw lastError;
};

// ── Object Utilities ─────────────────────────────────────────────────────────

/**
 * Deep clone an object
 */
export const deepClone = <T>(obj: T): T => {
    return JSON.parse(JSON.stringify(obj));
};

/**
 * Check if an object is empty
 */
export const isEmpty = (obj: object): boolean => {
    return Object.keys(obj).length === 0;
};

/**
 * Omit keys from an object
 */
export const omit = <T extends object, K extends keyof T>(
    obj: T,
    keys: K[]
): Omit<T, K> => {
    const result = { ...obj };
    keys.forEach((key) => delete result[key]);
    return result;
};

/**
 * Pick keys from an object
 */
export const pick = <T extends object, K extends keyof T>(
    obj: T,
    keys: K[]
): Pick<T, K> => {
    const result = {} as Pick<T, K>;
    keys.forEach((key) => {
        if (key in obj) {
            result[key] = obj[key];
        }
    });
    return result;
};
