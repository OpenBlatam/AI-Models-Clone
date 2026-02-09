// API Types for Prompt Compiler AI SAM3 Frontend

// ═══════════════════════════════════════════════════════════════════════════
// REQUEST TYPES
// ═══════════════════════════════════════════════════════════════════════════

export interface CompilePromptRequest {
    prompt: string;
    context?: Record<string, unknown>;
    auto_improve?: boolean;
}

export interface AnalyzePromptRequest {
    prompt: string;
}

export interface BatchCompileRequest {
    prompts: string[];
    parallel?: boolean;
}

// ═══════════════════════════════════════════════════════════════════════════
// RESPONSE TYPES
// ═══════════════════════════════════════════════════════════════════════════

export interface CategoryScores {
    clarity: number;
    specificity: number;
    structure: number;
    context: number;
    actionability: number;
}

export interface Recommendation {
    category: string;
    priority: "high" | "medium" | "low";
    suggestion: string;
    example?: string;
}

export interface CompilationResult {
    original_prompt: string;
    compiled_prompt: string;
    score: number;
    is_good: boolean;
    grade: "A" | "B" | "C" | "D" | "F";
    issues: string[];
    recommendations: Recommendation[];
    category_scores: CategoryScores;
    quick_tip: string;
    compilation_id: string;
    timestamp: string;
}

export interface CompileResponse {
    success: boolean;
    compilation: CompilationResult;
}

export interface AnalyzeResponse {
    success: boolean;
    data: {
        analysis: {
            clarity_score: number;
            specificity_score: number;
            structure_score: number;
            context_score: number;
            actionability_score: number;
            issues: string[];
            details: Record<string, unknown>;
        };
        score: {
            overall_score: number;
            is_good: boolean;
            category_scores: CategoryScores;
            grade: string;
        };
        is_good: boolean;
    };
}

export interface BatchCompileResponse {
    success: boolean;
    data: {
        compilations: CompilationResult[];
        total: number;
        good_count: number;
        bad_count: number;
    };
}

export interface CommonIssue {
    issue: string;
    count: number;
}

export interface StatisticsSummary {
    total_prompts: number;
    good_prompts: number;
    bad_prompts: number;
    good_percentage: number;
    average_score: number;
    grade_distribution: Record<string, number>;
    common_issues: CommonIssue[];
    average_category_scores: CategoryScores;
    score_trend: number[];
}

export interface StatisticsResponse {
    success: boolean;
    statistics: {
        summary: StatisticsSummary;
        session_id: string;
        compilation_count: number;
    };
}

export interface RecentRecord {
    id: string;
    prompt: string;
    score: number;
    is_good: boolean;
    grade: string;
    issues: string[];
    timestamp: string;
    session_id: string | null;
    category_scores: CategoryScores;
}

export interface RecentCompilationsResponse {
    success: boolean;
    data: {
        records: RecentRecord[];
        count: number;
    };
}

export interface HealthStatus {
    status: "healthy" | "degraded" | "offline";
    agent_running: boolean;
    service: string;
    version: string;
}

export interface ApiError {
    success: false;
    error: {
        message: string;
        code?: string;
        details?: Record<string, unknown>;
    };
}
