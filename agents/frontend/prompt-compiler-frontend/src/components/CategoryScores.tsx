"use client";

import { type FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type { CategoryScores as CategoryScoresType } from "@/types/api";
import { Progress } from "@/components/ui/progress";

interface CategoryScoresProps {
    scores: CategoryScoresType;
    showLabels?: boolean;
}

const categoryMeta: Record<keyof CategoryScoresType, { label: string; icon: string; color: string }> = {
    clarity: { label: "Clarity", icon: "💡", color: "bg-violet-500" },
    specificity: { label: "Specificity", icon: "🎯", color: "bg-blue-500" },
    structure: { label: "Structure", icon: "📐", color: "bg-emerald-500" },
    context: { label: "Context", icon: "📚", color: "bg-amber-500" },
    actionability: { label: "Actionability", icon: "⚡", color: "bg-pink-500" },
};

const getScoreLabel = (score: number): string => {
    if (score >= 0.9) return "Excellent";
    if (score >= 0.7) return "Good";
    if (score >= 0.5) return "Fair";
    if (score >= 0.3) return "Poor";
    return "Very Poor";
};

const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: (i: number) => ({
        opacity: 1,
        x: 0,
        transition: { delay: i * 0.1, duration: 0.4 },
    }),
};

export const CategoryScores: FC<CategoryScoresProps> = ({
    scores,
    showLabels = true,
}) => {
    const categories = Object.entries(categoryMeta) as [keyof CategoryScoresType, typeof categoryMeta.clarity][];

    return (
        <motion.div
            className="space-y-4"
            role="list"
            aria-label="Category scores"
            initial="hidden"
            animate="visible"
        >
            <AnimatePresence>
                {categories.map(([key, meta], index) => {
                    const score = scores[key] ?? 0;
                    const percentage = Math.round(score * 100);

                    return (
                        <motion.div
                            key={key}
                            custom={index}
                            variants={itemVariants}
                            initial="hidden"
                            animate="visible"
                            className="group"
                            role="listitem"
                            aria-label={`${meta.label}: ${percentage}%`}
                            whileHover={{ scale: 1.01 }}
                        >
                            {/* Label row */}
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <motion.span
                                        className="text-lg"
                                        aria-hidden="true"
                                        whileHover={{ scale: 1.2, rotate: 10 }}
                                    >
                                        {meta.icon}
                                    </motion.span>
                                    <span className="text-sm font-medium text-slate-200">{meta.label}</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    {showLabels && (
                                        <span className="text-xs text-slate-400">{getScoreLabel(score)}</span>
                                    )}
                                    <motion.span
                                        className="text-sm font-bold text-slate-100"
                                        initial={{ opacity: 0 }}
                                        animate={{ opacity: 1 }}
                                        transition={{ delay: 0.5 + index * 0.1 }}
                                    >
                                        {percentage}%
                                    </motion.span>
                                </div>
                            </div>

                            {/* Progress bar */}
                            <div className="relative h-2.5 bg-slate-700/50 rounded-full overflow-hidden">
                                <motion.div
                                    className={`absolute inset-y-0 left-0 ${meta.color} rounded-full`}
                                    initial={{ width: 0 }}
                                    animate={{ width: `${percentage}%` }}
                                    transition={{ duration: 0.8, delay: index * 0.1, ease: "easeOut" }}
                                />
                            </div>
                        </motion.div>
                    );
                })}
            </AnimatePresence>
        </motion.div>
    );
};

export default CategoryScores;
