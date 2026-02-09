"use client";

import { type FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { PRIORITY_STYLES, STAGGER_ITEM } from "@/constants";
import { useExpandable } from "@/hooks";
import type { Recommendation } from "@/types/api";

interface RecommendationsPanelProps {
    recommendations: Recommendation[];
    quickTip?: string;
}

export const RecommendationsPanel: FC<RecommendationsPanelProps> = ({
    recommendations,
    quickTip,
}) => {
    const [expandedIndex, toggleExpanded] = useExpandable();

    const handleKeyDown = (e: React.KeyboardEvent, index: number) => {
        if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            toggleExpanded(index);
        }
    };

    return (
        <div className="space-y-4">
            {/* Quick Tip */}
            {quickTip && (
                <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-4 rounded-xl bg-gradient-to-r from-violet-500/20 to-purple-500/20 border border-violet-500/30"
                >
                    <div className="flex items-start gap-3">
                        <span className="text-2xl">💡</span>
                        <div>
                            <p className="text-sm font-semibold text-violet-300 mb-1">Quick Tip</p>
                            <p className="text-slate-300 text-sm">{quickTip}</p>
                        </div>
                    </div>
                </motion.div>
            )}

            {/* Recommendations list */}
            {recommendations && recommendations.length > 0 ? (
                <motion.div
                    className="space-y-2"
                    role="list"
                    aria-label="Recommendations"
                    initial="hidden"
                    animate="visible"
                >
                    <AnimatePresence>
                        {recommendations.map((rec, index) => {
                            const priority = PRIORITY_STYLES[rec.priority as keyof typeof PRIORITY_STYLES] || PRIORITY_STYLES.medium;
                            const isExpanded = expandedIndex === index;

                            return (
                                <motion.div
                                    key={index}
                                    variants={STAGGER_ITEM}
                                    className={`rounded-xl border transition-all duration-200 ${isExpanded
                                            ? "bg-slate-800/80 border-slate-600"
                                            : "bg-slate-800/40 border-slate-700/50 hover:bg-slate-800/60"
                                        }`}
                                    role="listitem"
                                >
                                    <button
                                        onClick={() => toggleExpanded(index)}
                                        onKeyDown={(e) => handleKeyDown(e, index)}
                                        className="w-full p-4 flex items-start gap-3 text-left"
                                        aria-expanded={isExpanded}
                                        tabIndex={0}
                                    >
                                        <span className="flex-shrink-0 text-lg" aria-hidden="true">
                                            {priority.icon}
                                        </span>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-2 mb-1">
                                                <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${priority.bg} ${priority.text}`}>
                                                    {rec.priority.toUpperCase()}
                                                </span>
                                                <span className="text-xs text-slate-500 capitalize">{rec.category}</span>
                                            </div>
                                            <p className="text-slate-200 text-sm">{rec.suggestion}</p>
                                        </div>
                                        <motion.span
                                            className="flex-shrink-0 text-slate-400"
                                            animate={{ rotate: isExpanded ? 180 : 0 }}
                                            transition={{ duration: 0.2 }}
                                            aria-hidden="true"
                                        >
                                            ▼
                                        </motion.span>
                                    </button>

                                    {/* Expanded content */}
                                    <AnimatePresence>
                                        {isExpanded && rec.example && (
                                            <motion.div
                                                initial={{ height: 0, opacity: 0 }}
                                                animate={{ height: "auto", opacity: 1 }}
                                                exit={{ height: 0, opacity: 0 }}
                                                className="px-4 pb-4 pt-0 ml-9 overflow-hidden"
                                            >
                                                <div className="p-3 rounded-lg bg-slate-900/50 border border-slate-700/30">
                                                    <p className="text-xs text-slate-500 mb-1">Example:</p>
                                                    <p className="text-sm text-slate-300 italic">&ldquo;{rec.example}&rdquo;</p>
                                                </div>
                                            </motion.div>
                                        )}
                                    </AnimatePresence>
                                </motion.div>
                            );
                        })}
                    </AnimatePresence>
                </motion.div>
            ) : (
                !quickTip && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20"
                    >
                        <span className="text-2xl">🎉</span>
                        <span className="text-emerald-400 font-medium">Your prompt looks great! No recommendations needed.</span>
                    </motion.div>
                )
            )}
        </div>
    );
};

export default RecommendationsPanel;
