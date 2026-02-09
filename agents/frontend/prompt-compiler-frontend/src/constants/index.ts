// Shared constants for the Prompt Compiler frontend

// ═══════════════════════════════════════════════════════════════════════════
// GRADE CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const GRADE_STYLES = {
    A: { bg: "bg-emerald-500 hover:bg-emerald-400", glow: "#10b981", label: "Excellent" },
    B: { bg: "bg-blue-500 hover:bg-blue-400", glow: "#3b82f6", label: "Good" },
    C: { bg: "bg-yellow-500 hover:bg-yellow-400", glow: "#eab308", label: "Acceptable" },
    D: { bg: "bg-orange-500 hover:bg-orange-400", glow: "#f97316", label: "Below Average" },
    F: { bg: "bg-red-500 hover:bg-red-400", glow: "#ef4444", label: "Needs Improvement" },
} as const;

export const GRADE_COLORS = {
    A: "#10b981",
    B: "#3b82f6",
    C: "#eab308",
    D: "#f97316",
    F: "#ef4444",
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// CATEGORY CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const CATEGORY_META = {
    clarity: { label: "Clarity", icon: "💡", color: "bg-violet-500" },
    specificity: { label: "Specificity", icon: "🎯", color: "bg-blue-500" },
    structure: { label: "Structure", icon: "📐", color: "bg-emerald-500" },
    context: { label: "Context", icon: "📚", color: "bg-amber-500" },
    actionability: { label: "Actionability", icon: "⚡", color: "bg-pink-500" },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// PRIORITY CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const PRIORITY_STYLES = {
    high: { bg: "bg-red-500/20", text: "text-red-400", icon: "🔴" },
    medium: { bg: "bg-amber-500/20", text: "text-amber-400", icon: "🟡" },
    low: { bg: "bg-blue-500/20", text: "text-blue-400", icon: "🔵" },
} as const;

// ═══════════════════════════════════════════════════════════════════════════
// ANIMATION VARIANTS (Framer Motion)
// ═══════════════════════════════════════════════════════════════════════════

export const FADE_IN_UP = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0 },
};

export const FADE_IN_LEFT = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0 },
};

export const FADE_IN_RIGHT = {
    hidden: { opacity: 0, x: 20 },
    visible: { opacity: 1, x: 0 },
};

export const SCALE_IN = {
    hidden: { opacity: 0, scale: 0.95 },
    visible: { opacity: 1, scale: 1 },
};

export const STAGGER_CONTAINER = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: { staggerChildren: 0.1 },
    },
};

export const STAGGER_ITEM = {
    hidden: { opacity: 0, y: 10 },
    visible: { opacity: 1, y: 0 },
};

// ═══════════════════════════════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════════════════════════════

export const NAV_ITEMS = [
    { href: "/", label: "Compiler", icon: "⚡" },
    { href: "/statistics", label: "Statistics", icon: "📊" },
    { href: "/batch", label: "Batch", icon: "📦" },
] as const;

// ═══════════════════════════════════════════════════════════════════════════
// API CONFIGURATION
// ═══════════════════════════════════════════════════════════════════════════

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8051";
export const HEALTH_POLL_INTERVAL = 30000; // 30 seconds
export const MAX_PROMPT_LENGTH = 10000;
export const MAX_BATCH_PROMPTS = 100;
