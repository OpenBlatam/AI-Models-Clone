"use client";

import { type FC } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { STAGGER_ITEM } from "@/constants";
import { limitArray } from "@/utils";

interface IssuesListProps {
    issues: string[];
    maxItems?: number;
}

export const IssuesList: FC<IssuesListProps> = ({ issues, maxItems }) => {
    if (!issues || issues.length === 0) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="flex items-center gap-3 p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20"
            >
                <span className="text-2xl">✨</span>
                <span className="text-emerald-400 font-medium">No issues detected! Great job!</span>
            </motion.div>
        );
    }

    const { items: displayedIssues, remaining } = maxItems
        ? limitArray(issues, maxItems)
        : { items: issues, remaining: 0 };

    return (
        <motion.div
            className="space-y-2"
            role="list"
            aria-label="Detected issues"
            initial="hidden"
            animate="visible"
        >
            <AnimatePresence>
                {displayedIssues.map((issue, index) => (
                    <motion.div
                        key={index}
                        variants={STAGGER_ITEM}
                        initial="hidden"
                        animate="visible"
                        custom={index}
                        transition={{ delay: index * 0.05 }}
                        whileHover={{ scale: 1.01, x: 4 }}
                        className="group flex items-start gap-3 p-3 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800/80 hover:border-amber-500/30 transition-colors duration-200"
                        role="listitem"
                    >
                        <motion.span
                            whileHover={{ scale: 1.1, rotate: 10 }}
                            className="flex-shrink-0 w-6 h-6 flex items-center justify-center rounded-full bg-amber-500/20 text-amber-400 text-sm"
                            aria-hidden="true"
                        >
                            ⚠
                        </motion.span>
                        <span className="text-slate-300 text-sm leading-relaxed group-hover:text-slate-100 transition-colors">
                            {issue}
                        </span>
                    </motion.div>
                ))}
            </AnimatePresence>

            {remaining > 0 && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-center py-2"
                >
                    <span className="text-slate-500 text-sm">
                        +{remaining} more issue{remaining > 1 ? "s" : ""}
                    </span>
                </motion.div>
            )}
        </motion.div>
    );
};

export default IssuesList;
