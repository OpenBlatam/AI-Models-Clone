"use client";

import { type FC } from "react";
import { motion } from "framer-motion";
import {
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    BarChart,
    Bar,
    Cell,
} from "recharts";
import type { StatisticsSummary } from "@/types/api";

interface StatisticsCardProps {
    statistics: StatisticsSummary;
}

const cardVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: { delay: i * 0.1, duration: 0.5 },
    }),
};

export const StatisticsCard: FC<StatisticsCardProps> = ({ statistics }) => {
    const goodPercentage = statistics.good_percentage || 0;

    const cards = [
        {
            label: "Total Prompts",
            value: statistics.total_prompts.toLocaleString(),
            gradient: "from-slate-800/80 to-slate-900/80",
            border: "border-slate-700/50",
            textColor: "from-violet-400 to-purple-400",
        },
        {
            label: "Good Prompts",
            value: statistics.good_prompts.toLocaleString(),
            sub: `(${goodPercentage.toFixed(1)}%)`,
            gradient: "from-emerald-900/30 to-slate-900/80",
            border: "border-emerald-500/20",
            textColor: "text-emerald-400",
            subColor: "text-emerald-500/80",
        },
        {
            label: "Needs Improvement",
            value: statistics.bad_prompts.toLocaleString(),
            sub: `(${(100 - goodPercentage).toFixed(1)}%)`,
            gradient: "from-red-900/20 to-slate-900/80",
            border: "border-red-500/20",
            textColor: "text-red-400",
            subColor: "text-red-500/80",
        },
        {
            label: "Average Score",
            value: `${(statistics.average_score * 100).toFixed(0)}%`,
            gradient: "from-blue-900/20 to-slate-900/80",
            border: "border-blue-500/20",
            textColor: "text-blue-400",
        },
    ];

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {cards.map((card, index) => (
                <motion.div
                    key={card.label}
                    custom={index}
                    variants={cardVariants}
                    initial="hidden"
                    animate="visible"
                    whileHover={{ scale: 1.02, y: -4 }}
                    className={`p-4 rounded-2xl bg-gradient-to-br ${card.gradient} border ${card.border} transition-colors cursor-default`}
                >
                    <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">{card.label}</p>
                    <div className="flex items-end gap-2">
                        <p className={`text-3xl font-bold ${card.textColor.includes("from-") ? `bg-gradient-to-r ${card.textColor} bg-clip-text text-transparent` : card.textColor}`}>
                            {card.value}
                        </p>
                        {card.sub && <p className={`text-sm mb-1 ${card.subColor}`}>{card.sub}</p>}
                    </div>
                </motion.div>
            ))}
        </div>
    );
};

interface GradeDistributionChartProps {
    distribution: Record<string, number>;
}

const gradeColors: Record<string, string> = {
    A: "#10b981",
    B: "#3b82f6",
    C: "#eab308",
    D: "#f97316",
    F: "#ef4444",
};

export const GradeDistributionChart: FC<GradeDistributionChartProps> = ({ distribution }) => {
    const grades = ["A", "B", "C", "D", "F"];
    const data = grades.map((grade) => ({
        grade,
        count: distribution[grade] || 0,
        fill: gradeColors[grade],
    }));

    return (
        <motion.div
            className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
        >
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Grade Distribution</h3>
            <div className="h-48">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={data}>
                        <XAxis dataKey="grade" stroke="#64748b" fontSize={12} />
                        <YAxis stroke="#64748b" fontSize={12} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#1e293b",
                                border: "1px solid #475569",
                                borderRadius: "8px",
                            }}
                            labelStyle={{ color: "#e2e8f0" }}
                        />
                        <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                            {data.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.fill} />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
    );
};

interface ScoreTrendChartProps {
    trend: number[];
}

export const ScoreTrendChart: FC<ScoreTrendChartProps> = ({ trend }) => {
    if (!trend || trend.length === 0) {
        return (
            <motion.div
                className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
            >
                <h3 className="text-lg font-semibold text-slate-200 mb-4">Score Trend</h3>
                <p className="text-slate-400 text-center py-8">No data yet</p>
            </motion.div>
        );
    }

    const data = trend.map((score, index) => ({
        index: index + 1,
        score: Math.round(score * 100),
    }));

    return (
        <motion.div
            className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, delay: 0.2 }}
        >
            <h3 className="text-lg font-semibold text-slate-200 mb-4">Score Trend (Last {trend.length})</h3>
            <div className="h-32">
                <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={data}>
                        <defs>
                            <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                            </linearGradient>
                        </defs>
                        <XAxis dataKey="index" stroke="#64748b" fontSize={10} />
                        <YAxis domain={[0, 100]} stroke="#64748b" fontSize={10} />
                        <Tooltip
                            contentStyle={{
                                backgroundColor: "#1e293b",
                                border: "1px solid #475569",
                                borderRadius: "8px",
                            }}
                            formatter={(value: number) => [`${value}%`, "Score"]}
                        />
                        <Area
                            type="monotone"
                            dataKey="score"
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            fillOpacity={1}
                            fill="url(#scoreGradient)"
                        />
                    </AreaChart>
                </ResponsiveContainer>
            </div>
        </motion.div>
    );
};

export default StatisticsCard;
