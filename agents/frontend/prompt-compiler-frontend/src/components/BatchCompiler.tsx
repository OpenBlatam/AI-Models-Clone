"use client";

import { type FC, useState, type FormEvent, type ChangeEvent } from "react";
import { batchCompile } from "@/services/api";
import type { CompilationResult } from "@/types/api";
import GradeBadge from "./GradeBadge";

interface BatchCompilerProps {
    onComplete?: (results: CompilationResult[]) => void;
}

export const BatchCompiler: FC<BatchCompilerProps> = ({ onComplete }) => {
    const [prompts, setPrompts] = useState("");
    const [parallel, setParallel] = useState(true);
    const [isLoading, setIsLoading] = useState(false);
    const [results, setResults] = useState<CompilationResult[] | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [progress, setProgress] = useState(0);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError(null);
        setResults(null);

        const promptList = prompts
            .split("\n")
            .map((p) => p.trim())
            .filter((p) => p.length > 0);

        if (promptList.length === 0) {
            setError("Please enter at least one prompt");
            return;
        }

        if (promptList.length > 100) {
            setError("Maximum 100 prompts allowed");
            return;
        }

        setIsLoading(true);
        setProgress(0);

        // Simulate progress for better UX
        const progressInterval = setInterval(() => {
            setProgress((p) => Math.min(p + 10, 90));
        }, 200);

        try {
            const response = await batchCompile(promptList, parallel);
            setResults(response.data.compilations);
            setProgress(100);
            onComplete?.(response.data.compilations);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Batch compilation failed");
        } finally {
            clearInterval(progressInterval);
            setIsLoading(false);
        }
    };

    const handleChange = (e: ChangeEvent<HTMLTextAreaElement>) => {
        setPrompts(e.target.value);
        setResults(null);
        setError(null);
    };

    const promptCount = prompts
        .split("\n")
        .filter((p) => p.trim().length > 0).length;

    const aggregateStats = results
        ? {
            total: results.length,
            good: results.filter((r) => r.is_good).length,
            avgScore: results.reduce((sum, r) => sum + r.score, 0) / results.length,
        }
        : null;

    return (
        <div className="space-y-6">
            {/* Input form */}
            <form onSubmit={handleSubmit} className="space-y-4">
                <div className="relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-cyan-600 to-blue-600 rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300" />
                    <div className="relative">
                        <textarea
                            value={prompts}
                            onChange={handleChange}
                            placeholder="Enter prompts, one per line...&#10;Example:&#10;Tell me about AI&#10;Write a Python function for sorting&#10;Explain machine learning"
                            rows={8}
                            disabled={isLoading}
                            className={`
                w-full px-5 py-4 rounded-2xl resize-none font-mono text-sm
                bg-slate-800/90 border border-slate-700/50
                text-slate-100 placeholder-slate-500
                focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50
                disabled:opacity-50 disabled:cursor-not-allowed
                transition-all duration-200
              `}
                            aria-label="Enter prompts, one per line"
                        />
                        <div className="absolute bottom-3 right-4 text-xs text-slate-500">
                            {promptCount} prompt{promptCount !== 1 ? "s" : ""}
                        </div>
                    </div>
                </div>

                {/* Options */}
                <div className="flex items-center justify-between gap-4">
                    <label className="flex items-center gap-3 cursor-pointer group/toggle">
                        <div className="relative">
                            <input
                                type="checkbox"
                                checked={parallel}
                                onChange={(e) => setParallel(e.target.checked)}
                                className="sr-only peer"
                                disabled={isLoading}
                            />
                            <div className="w-11 h-6 bg-slate-700 rounded-full peer peer-checked:bg-cyan-600 transition-colors" />
                            <div className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full transition-transform peer-checked:translate-x-5" />
                        </div>
                        <div>
                            <span className="text-sm text-slate-300 group-hover/toggle:text-slate-100 transition-colors">
                                Parallel Processing
                            </span>
                            <p className="text-xs text-slate-500">Process all prompts simultaneously</p>
                        </div>
                    </label>

                    <button
                        type="submit"
                        disabled={promptCount === 0 || isLoading}
                        className={`
              relative inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white
              bg-gradient-to-r from-cyan-600 to-blue-600
              hover:from-cyan-500 hover:to-blue-500
              focus:outline-none focus:ring-2 focus:ring-cyan-500/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200 hover:shadow-lg hover:shadow-cyan-500/25
            `}
                    >
                        {isLoading ? (
                            <>
                                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                                </svg>
                                <span>Processing...</span>
                            </>
                        ) : (
                            <>
                                <span>📦</span>
                                <span>Batch Compile</span>
                            </>
                        )}
                    </button>
                </div>
            </form>

            {/* Progress bar */}
            {isLoading && (
                <div className="space-y-2">
                    <div className="flex items-center justify-between text-sm">
                        <span className="text-slate-400">Processing prompts...</span>
                        <span className="text-cyan-400 font-medium">{progress}%</span>
                    </div>
                    <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-300"
                            style={{ width: `${progress}%` }}
                        />
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-start gap-3">
                    <span className="text-xl">❌</span>
                    <div>
                        <p className="text-red-400 font-semibold">Error</p>
                        <p className="text-red-300/80 text-sm">{error}</p>
                    </div>
                </div>
            )}

            {/* Results summary */}
            {aggregateStats && (
                <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-200">Batch Results</h3>

                    {/* Summary cards */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="p-4 rounded-xl bg-slate-800/50 border border-slate-700/50 text-center">
                            <p className="text-2xl font-bold text-slate-200">{aggregateStats.total}</p>
                            <p className="text-xs text-slate-500 uppercase">Total</p>
                        </div>
                        <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-center">
                            <p className="text-2xl font-bold text-emerald-400">{aggregateStats.good}</p>
                            <p className="text-xs text-slate-500 uppercase">Good</p>
                        </div>
                        <div className="p-4 rounded-xl bg-blue-500/10 border border-blue-500/20 text-center">
                            <p className="text-2xl font-bold text-blue-400">
                                {(aggregateStats.avgScore * 100).toFixed(0)}%
                            </p>
                            <p className="text-xs text-slate-500 uppercase">Avg Score</p>
                        </div>
                    </div>

                    {/* Results list */}
                    <div className="space-y-2 max-h-96 overflow-y-auto pr-2">
                        {results?.map((result, index) => (
                            <div
                                key={result.compilation_id}
                                className="flex items-center gap-4 p-3 rounded-xl bg-slate-800/40 border border-slate-700/30"
                            >
                                <span className="text-slate-500 text-sm w-6">#{index + 1}</span>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm text-slate-300 truncate" title={result.original_prompt}>
                                        {result.original_prompt}
                                    </p>
                                </div>
                                <span className={`text-sm font-medium ${result.score >= 0.7 ? "text-emerald-400" : result.score >= 0.5 ? "text-amber-400" : "text-red-400"
                                    }`}>
                                    {(result.score * 100).toFixed(0)}%
                                </span>
                                <GradeBadge grade={result.grade} size="sm" />
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
};

export default BatchCompiler;
