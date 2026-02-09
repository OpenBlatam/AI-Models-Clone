// Custom React hooks for the Prompt Compiler frontend

import { useState, useEffect, useCallback } from "react";
import { toast } from "sonner";
import {
    compilePrompt,
    getStatistics,
    getRecentCompilations,
    checkHealth,
    batchCompile,
} from "@/services/api";
import type {
    CompilationResult,
    StatisticsSummary,
    RecentRecord,
    HealthStatus
} from "@/types/api";
import { HEALTH_POLL_INTERVAL } from "@/constants";

// ═══════════════════════════════════════════════════════════════════════════
// usePromptCompiler - Handles single prompt compilation
// ═══════════════════════════════════════════════════════════════════════════

interface UsePromptCompilerReturn {
    result: CompilationResult | null;
    isLoading: boolean;
    error: string | null;
    compile: (prompt: string, autoImprove?: boolean) => Promise<void>;
    reset: () => void;
}

export const usePromptCompiler = (): UsePromptCompilerReturn => {
    const [result, setResult] = useState<CompilationResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const compile = useCallback(async (prompt: string, autoImprove = false) => {
        setIsLoading(true);
        setError(null);

        try {
            const response = await compilePrompt(prompt, { autoImprove });
            setResult(response.compilation);

            if (response.compilation.is_good) {
                toast.success("Great prompt!", {
                    description: `Score: ${Math.round(response.compilation.score * 100)}% - Grade: ${response.compilation.grade}`,
                });
            } else {
                toast.warning("Room for improvement", {
                    description: `Score: ${Math.round(response.compilation.score * 100)}% - Check recommendations`,
                });
            }
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to compile prompt";
            setError(message);
            toast.error("Compilation failed", { description: message });
            setResult(null);
        } finally {
            setIsLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResult(null);
        setError(null);
    }, []);

    return { result, isLoading, error, compile, reset };
};

// ═══════════════════════════════════════════════════════════════════════════
// useBatchCompiler - Handles batch prompt compilation
// ═══════════════════════════════════════════════════════════════════════════

interface UseBatchCompilerReturn {
    results: CompilationResult[] | null;
    isLoading: boolean;
    error: string | null;
    progress: number;
    compile: (prompts: string[], parallel?: boolean) => Promise<void>;
    reset: () => void;
}

export const useBatchCompiler = (): UseBatchCompilerReturn => {
    const [results, setResults] = useState<CompilationResult[] | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [progress, setProgress] = useState(0);

    const compile = useCallback(async (prompts: string[], parallel = true) => {
        setIsLoading(true);
        setError(null);
        setProgress(0);

        const progressInterval = setInterval(() => {
            setProgress((p) => Math.min(p + 10, 90));
        }, 200);

        try {
            const response = await batchCompile(prompts, parallel);
            setResults(response.data.compilations);
            setProgress(100);
            toast.success(`Compiled ${response.data.total} prompts`, {
                description: `${response.data.good_count} good, ${response.data.bad_count} need improvement`,
            });
        } catch (err) {
            const message = err instanceof Error ? err.message : "Batch compilation failed";
            setError(message);
            toast.error("Batch compilation failed", { description: message });
        } finally {
            clearInterval(progressInterval);
            setIsLoading(false);
        }
    }, []);

    const reset = useCallback(() => {
        setResults(null);
        setError(null);
        setProgress(0);
    }, []);

    return { results, isLoading, error, progress, compile, reset };
};

// ═══════════════════════════════════════════════════════════════════════════
// useStatistics - Fetches and manages statistics data
// ═══════════════════════════════════════════════════════════════════════════

interface UseStatisticsReturn {
    statistics: StatisticsSummary | null;
    recentRecords: RecentRecord[];
    isLoading: boolean;
    error: string | null;
    refresh: () => Promise<void>;
}

export const useStatistics = (recentCount = 20): UseStatisticsReturn => {
    const [statistics, setStatistics] = useState<StatisticsSummary | null>(null);
    const [recentRecords, setRecentRecords] = useState<RecentRecord[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const refresh = useCallback(async () => {
        setIsLoading(true);
        setError(null);

        try {
            const [statsResponse, recentResponse] = await Promise.all([
                getStatistics(),
                getRecentCompilations(recentCount),
            ]);

            setStatistics(statsResponse.statistics.summary);
            setRecentRecords(recentResponse.data.records);
        } catch (err) {
            const message = err instanceof Error ? err.message : "Failed to load statistics";
            setError(message);
        } finally {
            setIsLoading(false);
        }
    }, [recentCount]);

    useEffect(() => {
        refresh();
    }, [refresh]);

    return { statistics, recentRecords, isLoading, error, refresh };
};

// ═══════════════════════════════════════════════════════════════════════════
// useHealthCheck - Polls API health status
// ═══════════════════════════════════════════════════════════════════════════

interface UseHealthCheckReturn {
    health: HealthStatus | null;
    isLoading: boolean;
}

export const useHealthCheck = (pollInterval = HEALTH_POLL_INTERVAL): UseHealthCheckReturn => {
    const [health, setHealth] = useState<HealthStatus | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const fetchHealth = async () => {
            try {
                const status = await checkHealth();
                setHealth(status);
            } catch {
                setHealth({
                    status: "offline",
                    agent_running: false,
                    service: "prompt_compiler_ai_sam3",
                    version: "unknown",
                });
            } finally {
                setIsLoading(false);
            }
        };

        fetchHealth();
        const interval = setInterval(fetchHealth, pollInterval);
        return () => clearInterval(interval);
    }, [pollInterval]);

    return { health, isLoading };
};

// ═══════════════════════════════════════════════════════════════════════════
// useToggle - Simple toggle state hook
// ═══════════════════════════════════════════════════════════════════════════

export const useToggle = (initialValue = false): [boolean, () => void, (value: boolean) => void] => {
    const [value, setValue] = useState(initialValue);
    const toggle = useCallback(() => setValue((v) => !v), []);
    return [value, toggle, setValue];
};

// ═══════════════════════════════════════════════════════════════════════════
// useExpandable - Manages expandable item state
// ═══════════════════════════════════════════════════════════════════════════

export const useExpandable = (): [number | null, (index: number) => void] => {
    const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

    const toggle = useCallback((index: number) => {
        setExpandedIndex((current) => (current === index ? null : index));
    }, []);

    return [expandedIndex, toggle];
};
