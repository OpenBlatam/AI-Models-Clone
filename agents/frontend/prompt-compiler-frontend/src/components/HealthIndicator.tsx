"use client";

import { type FC } from "react";
import { motion } from "framer-motion";
import { useHealthCheck } from "@/hooks";

const STATUS_STYLES = {
    healthy: { dot: "bg-emerald-500 shadow-emerald-500/50", text: "text-emerald-400", label: "Online" },
    degraded: { dot: "bg-amber-500 shadow-amber-500/50", text: "text-amber-400", label: "Degraded" },
    offline: { dot: "bg-red-500 shadow-red-500/50", text: "text-red-400", label: "Offline" },
} as const;

export const HealthIndicator: FC = () => {
    const { health, isLoading } = useHealthCheck();

    const status = health?.status || "offline";
    const style = STATUS_STYLES[status] || STATUS_STYLES.offline;

    return (
        <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            className="group relative flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-800/60 border border-slate-700/50 hover:bg-slate-800/80 transition-colors cursor-default"
            role="status"
            aria-label={`API Status: ${style.label}`}
        >
            {/* Pulsing dot */}
            <span className="relative flex h-2.5 w-2.5">
                {status === "healthy" && (
                    <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${style.dot}`} />
                )}
                <span className={`relative inline-flex rounded-full h-2.5 w-2.5 shadow-lg ${style.dot}`} />
            </span>

            <span className={`text-xs font-medium ${style.text}`}>
                {isLoading ? "Checking..." : style.label}
            </span>

            {/* Tooltip */}
            {health && (
                <motion.div
                    initial={{ opacity: 0, y: 5 }}
                    whileHover={{ opacity: 1, y: 0 }}
                    className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-50 whitespace-nowrap"
                >
                    <p className="text-xs text-slate-400">
                        Service: <span className="text-slate-200">{health.service}</span>
                    </p>
                    <p className="text-xs text-slate-400">
                        Version: <span className="text-slate-200">{health.version}</span>
                    </p>
                    <p className="text-xs text-slate-400">
                        Agent: <span className={health.agent_running ? "text-emerald-400" : "text-red-400"}>
                            {health.agent_running ? "Running" : "Stopped"}
                        </span>
                    </p>
                    {/* Tooltip arrow */}
                    <div className="absolute top-full left-1/2 -translate-x-1/2 border-4 border-transparent border-t-slate-700" />
                </motion.div>
            )}
        </motion.div>
    );
};

export default HealthIndicator;
