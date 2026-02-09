"use client";

import { motion } from "framer-motion";
import { useStatistics } from "@/hooks";
import { FADE_IN_UP, SCALE_IN } from "@/constants";
import { StatisticsCard, GradeDistributionChart, ScoreTrendChart, RecentCompilations } from "@/components";

export default function StatisticsPage() {
    const { statistics, recentRecords, isLoading, error } = useStatistics(20);

    if (isLoading) {
        return (
            <div className="space-y-6">
                <div className="text-center py-12">
                    <div className="inline-flex items-center gap-3 text-slate-400">
                        <motion.div
                            className="w-6 h-6 border-2 border-violet-500 border-t-transparent rounded-full"
                            animate={{ rotate: 360 }}
                            transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        />
                        <span>Loading statistics...</span>
                    </div>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <motion.div
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="p-6 rounded-2xl bg-red-500/10 border border-red-500/30 text-center"
            >
                <span className="text-2xl mb-2 block">❌</span>
                <p className="text-red-400 font-semibold">Failed to Load Statistics</p>
                <p className="text-red-300/80 text-sm mt-1">{error}</p>
                <p className="text-slate-500 text-xs mt-4">Make sure the backend API is running on port 8051</p>
            </motion.div>
        );
    }

    if (!statistics) {
        return (
            <motion.div initial={FADE_IN_UP.hidden} animate={FADE_IN_UP.visible} className="text-center py-12">
                <span className="text-4xl mb-4 block">📊</span>
                <p className="text-slate-400">No statistics available yet.</p>
                <p className="text-slate-500 text-sm mt-1">Start compiling prompts to see analytics!</p>
            </motion.div>
        );
    }

    return (
        <motion.div className="space-y-8" initial="hidden" animate="visible">
            {/* Page Header */}
            <motion.section variants={FADE_IN_UP} className="text-center space-y-2">
                <h1 className="text-3xl font-bold text-slate-100">Statistics Dashboard</h1>
                <p className="text-slate-400">Analytics from your prompt compilations</p>
            </motion.section>

            {/* Summary Cards */}
            <motion.section variants={SCALE_IN}>
                <StatisticsCard statistics={statistics} />
            </motion.section>

            {/* Charts Row */}
            <div className="grid md:grid-cols-2 gap-6">
                <GradeDistributionChart distribution={statistics.grade_distribution} />
                <ScoreTrendChart trend={statistics.score_trend} />
            </div>

            {/* Common Issues */}
            {statistics.common_issues?.length > 0 && (
                <motion.section variants={SCALE_IN} className="glass-card rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                        <span>🔍</span> Most Common Issues
                    </h3>
                    <div className="space-y-2">
                        {statistics.common_issues.slice(0, 5).map((item, index) => (
                            <motion.div
                                key={index}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: index * 0.05 }}
                                className="flex items-center justify-between p-3 rounded-xl bg-slate-800/40 border border-slate-700/30"
                            >
                                <span className="text-sm text-slate-300">{item.issue}</span>
                                <span className="px-2 py-1 rounded-full bg-amber-500/20 text-amber-400 text-xs font-medium">
                                    {item.count}x
                                </span>
                            </motion.div>
                        ))}
                    </div>
                </motion.section>
            )}

            {/* Category Averages */}
            {statistics.average_category_scores && (
                <motion.section variants={SCALE_IN} className="glass-card rounded-2xl p-6">
                    <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                        <span>📈</span> Average Category Scores
                    </h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                        {Object.entries(statistics.average_category_scores).map(([category, score]) => (
                            <motion.div
                                key={category}
                                whileHover={{ scale: 1.02 }}
                                className="text-center p-4 rounded-xl bg-slate-800/40 border border-slate-700/30"
                            >
                                <p className="text-2xl font-bold text-slate-200">{(score * 100).toFixed(0)}%</p>
                                <p className="text-xs text-slate-500 capitalize mt-1">{category}</p>
                            </motion.div>
                        ))}
                    </div>
                </motion.section>
            )}

            {/* Recent Compilations */}
            <section>
                <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                    <span>🕐</span> Recent Compilations
                </h3>
                <RecentCompilations records={recentRecords} />
            </section>
        </motion.div>
    );
}
