// API Client for Prompt Compiler AI SAM3

import type {
    CompilePromptRequest,
    CompileResponse,
    AnalyzePromptRequest,
    AnalyzeResponse,
    BatchCompileRequest,
    BatchCompileResponse,
    StatisticsResponse,
    RecentCompilationsResponse,
    HealthStatus,
} from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8051";

// ═══════════════════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

const handleResponse = async <T>(response: Response): Promise<T> => {
    if (!response.ok) {
        const error = await response.json().catch(() => ({ message: "Unknown error" }));
        throw new Error(error.error?.message || error.message || `HTTP ${response.status}`);
    }
    return response.json();
};

// ═══════════════════════════════════════════════════════════════════════════
// API FUNCTIONS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Compile and analyze a prompt with statistics recording.
 */
export const compilePrompt = async (
    prompt: string,
    options?: { context?: Record<string, unknown>; autoImprove?: boolean }
): Promise<CompileResponse> => {
    const request: CompilePromptRequest = {
        prompt,
        context: options?.context,
        auto_improve: options?.autoImprove ?? false,
    };

    const response = await fetch(`${API_BASE_URL}/compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });

    return handleResponse<CompileResponse>(response);
};

/**
 * Analyze a prompt without recording statistics.
 */
export const analyzePrompt = async (prompt: string): Promise<AnalyzeResponse> => {
    const request: AnalyzePromptRequest = { prompt };

    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });

    return handleResponse<AnalyzeResponse>(response);
};

/**
 * Compile multiple prompts at once.
 */
export const batchCompile = async (
    prompts: string[],
    parallel: boolean = true
): Promise<BatchCompileResponse> => {
    const request: BatchCompileRequest = { prompts, parallel };

    const response = await fetch(`${API_BASE_URL}/batch-compile`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
    });

    return handleResponse<BatchCompileResponse>(response);
};

/**
 * Get compilation statistics.
 */
export const getStatistics = async (sessionOnly: boolean = false): Promise<StatisticsResponse> => {
    const url = new URL(`${API_BASE_URL}/statistics`);
    if (sessionOnly) {
        url.searchParams.set("session_only", "true");
    }

    const response = await fetch(url.toString());
    return handleResponse<StatisticsResponse>(response);
};

/**
 * Get recent compilation records.
 */
export const getRecentCompilations = async (n: number = 10): Promise<RecentCompilationsResponse> => {
    const url = new URL(`${API_BASE_URL}/statistics/recent`);
    url.searchParams.set("n", n.toString());

    const response = await fetch(url.toString());
    return handleResponse<RecentCompilationsResponse>(response);
};

/**
 * Check service health.
 */
export const checkHealth = async (): Promise<HealthStatus> => {
    try {
        const response = await fetch(`${API_BASE_URL}/health`, {
            signal: AbortSignal.timeout(5000),
        });
        return handleResponse<HealthStatus>(response);
    } catch {
        return {
            status: "offline",
            agent_running: false,
            service: "prompt_compiler_ai_sam3",
            version: "unknown",
        };
    }
};
