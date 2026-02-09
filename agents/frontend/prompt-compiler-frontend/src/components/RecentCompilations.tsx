"use client";

import { type FC } from "react";
import type { RecentRecord } from "@/types/api";
import GradeBadge from "./GradeBadge";

interface RecentCompilationsProps {
    records: RecentRecord[];
}

const formatDate = (isoString: string): string => {
    const date = new Date(isoString);
    return date.toLocaleString("en-US", {
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
};

const truncatePrompt = (prompt: string, maxLength: number = 60): string => {
    if (prompt.length <= maxLength) return prompt;
    return prompt.slice(0, maxLength) + "...";
};

export const RecentCompilations: FC<RecentCompilationsProps> = ({ records }) => {
    if (!records || records.length === 0) {
        return (
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 text-center">
                <p className="text-slate-400">No recent compilations yet. Start compiling prompts!</p>
            </div>
        );
    }

    return (
        <div className="overflow-hidden rounded-2xl border border-slate-700/50">
            <div className="overflow-x-auto">
                <table className="w-full" role="table">
                    <thead>
                        <tr className="bg-slate-800/80 border-b border-slate-700/50">
                            <th className="px-4 py-3 text-left text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Prompt
                            </th>
                            <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Score
                            </th>
                            <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Grade
                            </th>
                            <th className="px-4 py-3 text-center text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Status
                            </th>
                            <th className="px-4 py-3 text-right text-xs font-semibold text-slate-400 uppercase tracking-wider">
                                Time
                            </th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-700/30">
                        {records.map((record, index) => (
                            <tr
                                key={record.id || index}
                                className="bg-slate-800/30 hover:bg-slate-800/60 transition-colors"
                            >
                                <td className="px-4 py-3 text-sm text-slate-300 max-w-xs">
                                    <span title={record.prompt}>
                                        {truncatePrompt(record.prompt)}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-center">
                                    <span className={`text-sm font-semibold ${record.score >= 0.7 ? "text-emerald-400" : record.score >= 0.5 ? "text-amber-400" : "text-red-400"
                                        }`}>
                                        {(record.score * 100).toFixed(0)}%
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-center">
                                    <GradeBadge grade={record.grade as "A" | "B" | "C" | "D" | "F"} size="sm" />
                                </td>
                                <td className="px-4 py-3 text-center">
                                    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${record.is_good
                                            ? "bg-emerald-500/20 text-emerald-400"
                                            : "bg-amber-500/20 text-amber-400"
                                        }`}>
                                        {record.is_good ? "✓ Good" : "⚠ Improve"}
                                    </span>
                                </td>
                                <td className="px-4 py-3 text-right text-xs text-slate-500">
                                    {formatDate(record.timestamp)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default RecentCompilations;
