"use client";

import { type FC } from "react";
import { motion } from "framer-motion";
import { Badge } from "@/components/ui/badge";

interface GradeBadgeProps {
    grade: "A" | "B" | "C" | "D" | "F" | string;
    size?: "sm" | "md" | "lg";
    showGlow?: boolean;
}

const gradeStyles: Record<string, { bg: string; glow: string }> = {
    A: { bg: "bg-emerald-500 hover:bg-emerald-400", glow: "#10b981" },
    B: { bg: "bg-blue-500 hover:bg-blue-400", glow: "#3b82f6" },
    C: { bg: "bg-yellow-500 hover:bg-yellow-400", glow: "#eab308" },
    D: { bg: "bg-orange-500 hover:bg-orange-400", glow: "#f97316" },
    F: { bg: "bg-red-500 hover:bg-red-400", glow: "#ef4444" },
};

const sizes = {
    sm: "w-8 h-8 text-lg",
    md: "w-12 h-12 text-2xl",
    lg: "w-16 h-16 text-3xl",
};

const gradeLabels: Record<string, string> = {
    A: "Excellent",
    B: "Good",
    C: "Acceptable",
    D: "Below Average",
    F: "Needs Improvement",
};

export const GradeBadge: FC<GradeBadgeProps> = ({
    grade,
    size = "md",
    showGlow = true,
}) => {
    const style = gradeStyles[grade] || gradeStyles.F;
    const sizeClass = sizes[size];
    const label = gradeLabels[grade] || "Unknown";

    return (
        <motion.div
            className={`
        relative inline-flex items-center justify-center rounded-xl font-bold text-white
        ${style.bg} ${sizeClass}
      `}
            role="status"
            aria-label={`Grade: ${grade} - ${label}`}
            title={label}
            initial={{ scale: 0, rotate: -180 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: "spring", stiffness: 200, damping: 15 }}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            style={showGlow ? { boxShadow: `0 0 20px ${style.glow}60` } : undefined}
        >
            {grade}

            {/* Shimmer effect */}
            <motion.div
                className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <motion.div
                    className="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent"
                    initial={{ x: "-100%" }}
                    animate={{ x: "100%" }}
                    transition={{ duration: 1.5, delay: 0.5 }}
                />
            </motion.div>
        </motion.div>
    );
};

export default GradeBadge;
