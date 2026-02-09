"use client";

import BatchCompiler from "@/components/BatchCompiler";

export default function BatchPage() {
    return (
        <div className="space-y-8">
            {/* Page Header */}
            <section className="text-center space-y-2">
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-300 text-sm">
                    <span>📦</span>
                    <span>Batch Processing</span>
                </div>
                <h1 className="text-3xl font-bold text-slate-100">Batch Compile</h1>
                <p className="text-slate-400 max-w-2xl mx-auto">
                    Compile multiple prompts at once. Enter one prompt per line and get aggregate results for your entire batch.
                </p>
            </section>

            {/* Instructions */}
            <section className="glass-card rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3">
                    How it works
                </h3>
                <div className="grid md:grid-cols-3 gap-4">
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                            1
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-200">Enter Prompts</p>
                            <p className="text-xs text-slate-500">One prompt per line, up to 100 prompts</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                            2
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-200">Choose Mode</p>
                            <p className="text-xs text-slate-500">Parallel (faster) or sequential processing</p>
                        </div>
                    </div>
                    <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                            3
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-200">Review Results</p>
                            <p className="text-xs text-slate-500">Get scores, grades, and aggregate statistics</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* Batch Compiler */}
            <section className="glass-card rounded-3xl p-6 md:p-8">
                <BatchCompiler />
            </section>

            {/* Tips */}
            <section className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/30">
                <h4 className="text-sm font-semibold text-slate-300 mb-2 flex items-center gap-2">
                    <span>💡</span>
                    Tips for batch processing
                </h4>
                <ul className="text-sm text-slate-400 space-y-1 list-disc list-inside">
                    <li>Use parallel mode for faster processing when prompts are independent</li>
                    <li>Sequential mode is better for seeing results in order</li>
                    <li>Each compilation is recorded in your statistics</li>
                    <li>Empty lines are automatically ignored</li>
                </ul>
            </section>
        </div>
    );
}
