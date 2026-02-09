"use client";

import { type FC } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ScoreGaugeProps {
    score: number;
    size?: "sm" | "md" | "lg";
    showPercentage?: boolean;
}

const getScoreColor = (score: number): string => {
    if (score >= 0.8) return "#10b981";
    if (score >= 0.6) return "#eab308";
    if (score >= 0.4) return "#f97316";
    return "#ef4444";
};

const sizes = {
    sm: { wrapper: "w-24 h-24", text: "text-xl", label: "text-xs", stroke: 6 },
    md: { wrapper: "w-36 h-36", text: "text-3xl", label: "text-sm", stroke: 8 },
    lg: { wrapper: "w-48 h-48", text: "text-4xl", label: "text-base", stroke: 10 },
};

export const ScoreGauge: FC<ScoreGaugeProps> = ({
    score,
    size = "md",
    showPercentage = true,
}) => {
    const percentage = Math.round(score * 100);
    const sizeStyles = sizes[size];
    const color = getScoreColor(score);

    // SVG circle calculations
    const radius = 45;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (score * circumference);

    return (
        <motion.div
            className={`relative ${sizeStyles.wrapper} flex items-center justify-center`}
            role="progressbar"
            aria-valuenow={percentage}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Score: ${percentage}%`}
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ type: "spring", stiffness: 200, damping: 20 }}
        >
            {/* Background glow */}
            <motion.div
                className="absolute inset-0 rounded-full blur-xl"
                style={{ backgroundColor: color }}
                initial={{ opacity: 0 }}
                animate={{ opacity: 0.2 }}
                transition={{ delay: 0.5 }}
            />

            <svg className="absolute inset-0 w-full h-full -rotate-90">
                {/* Background circle */}
                <circle
                    cx="50%"
                    cy="50%"
                    r={`${radius}%`}
                    fill="none"
                    stroke="currentColor"
                    strokeWidth={sizeStyles.stroke}
                    className="text-slate-700/50"
                />

                {/* Progress circle */}
                <motion.circle
                    cx="50%"
                    cy="50%"
                    r={`${radius}%`}
                    fill="none"
                    stroke={color}
                    strokeWidth={sizeStyles.stroke}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    initial={{ strokeDashoffset: circumference }}
                    animate={{ strokeDashoffset }}
                    transition={{ duration: 1.2, ease: "easeOut", delay: 0.2 }}
                    style={{ filter: `drop-shadow(0 0 8px ${color})` }}
                />
            </svg>

            {/* Center content */}
            <motion.div
                className="flex flex-col items-center z-10"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
            >
                {showPercentage && (
                    <motion.span
                        className={`font-bold ${sizeStyles.text}`}
                        style={{ color }}
                        key={percentage}
                        initial={{ scale: 0.5 }}
                        animate={{ scale: 1 }}
                        transition={{ type: "spring", stiffness: 300 }}
                    >
                        {percentage}
                    </motion.span>
                )}
                <span className={`text-slate-400 ${sizeStyles.label}`}>Score</span>
            </motion.div>
        </motion.div>
    );
};

export default ScoreGauge;
