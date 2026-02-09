// Utility functions for the Prompt Compiler frontend

import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

// ═══════════════════════════════════════════════════════════════════════════
// CLASS NAME UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const cn = (...inputs: ClassValue[]) => twMerge(clsx(inputs));

// ═══════════════════════════════════════════════════════════════════════════
// SCORE UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const getScoreColor = (score: number): string => {
    if (score >= 0.8) return "#10b981";
    if (score >= 0.6) return "#eab308";
    if (score >= 0.4) return "#f97316";
    return "#ef4444";
};

export const getScoreLabel = (score: number): string => {
    if (score >= 0.9) return "Excellent";
    if (score >= 0.7) return "Good";
    if (score >= 0.5) return "Fair";
    if (score >= 0.3) return "Poor";
    return "Very Poor";
};

export const getScorePercentage = (score: number): number => Math.round(score * 100);

// ═══════════════════════════════════════════════════════════════════════════
// STRING UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const truncateText = (text: string, maxLength: number = 60): string => {
    if (text.length <= maxLength) return text;
    return `${text.slice(0, maxLength)}...`;
};

export const pluralize = (count: number, singular: string, plural?: string): string => {
    return count === 1 ? singular : (plural || `${singular}s`);
};

// ═══════════════════════════════════════════════════════════════════════════
// DATE UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const formatDate = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

export const formatRelativeTime = (isoString: string): string => {
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;

    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays}d ago`;
};

// ═══════════════════════════════════════════════════════════════════════════
// VALIDATION UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const isValidPrompt = (prompt: string, maxLength: number = 10000): boolean => {
    const trimmed = prompt.trim();
    return trimmed.length > 0 && trimmed.length <= maxLength;
};

export const countPrompts = (input: string): number => {
    return input.split("\n").filter((line) => line.trim().length > 0).length;
};

// ═══════════════════════════════════════════════════════════════════════════
// ARRAY UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

export const limitArray = <T>(arr: T[], max: number): { items: T[]; remaining: number } => ({
    items: arr.slice(0, max),
    remaining: Math.max(0, arr.length - max),
});
