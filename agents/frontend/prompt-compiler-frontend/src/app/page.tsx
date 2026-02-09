"use client";

import { motion, AnimatePresence } from "framer-motion";
import { usePromptCompiler } from "@/hooks";
import { FADE_IN_UP } from "@/constants";
import {
  PromptInput,
  ScoreGauge,
  GradeBadge,
  CategoryScores,
  IssuesList,
  RecommendationsPanel,
} from "@/components";

export default function HomePage() {
  const { result, isLoading, compile } = usePromptCompiler();

  const handleCompile = async (prompt: string, autoImprove: boolean) => {
    await compile(prompt, autoImprove);
  };

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <motion.section
        className="text-center space-y-4 mb-12"
        initial="hidden"
        animate="visible"
        variants={FADE_IN_UP}
      >
        <motion.div
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-violet-500/10 border border-violet-500/20 text-violet-300 text-sm"
          whileHover={{ scale: 1.05 }}
        >
          <span>⚡</span>
          <span>AI-Powered Prompt Analysis</span>
        </motion.div>
        <h1 className="text-4xl md:text-5xl font-bold">
          <span className="text-gradient">Prompt Compiler</span>
        </h1>
        <p className="text-lg text-slate-400 max-w-2xl mx-auto">
          Analyze your prompts for quality, get multi-dimensional scores, and receive actionable recommendations.
        </p>
      </motion.section>

      {/* Input Section */}
      <motion.section
        className="glass-card rounded-3xl p-6 md:p-8"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <PromptInput onSubmit={handleCompile} isLoading={isLoading} />
      </motion.section>

      {/* Results Section */}
      <AnimatePresence mode="wait">
        {result && (
          <motion.section
            className="space-y-6"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            key={result.compilation_id}
          >
            {/* Score Overview */}
            <motion.div
              className="glass-card rounded-3xl p-6 md:p-8"
              initial={{ scale: 0.95 }}
              animate={{ scale: 1 }}
            >
              <div className="flex flex-col md:flex-row items-center gap-8">
                <ScoreGauge score={result.score} size="lg" />

                <div className="flex-1 text-center md:text-left space-y-4">
                  <div className="flex flex-col md:flex-row items-center gap-4">
                    <GradeBadge grade={result.grade} size="lg" />
                    <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}>
                      <h2 className="text-2xl font-bold text-slate-100">
                        {result.is_good ? "Great Prompt! ✨" : "Room for Improvement"}
                      </h2>
                      <p className="text-slate-400">
                        {result.is_good ? "Your prompt meets quality standards" : "Follow the recommendations below"}
                      </p>
                    </motion.div>
                  </div>

                  {result.compiled_prompt !== result.original_prompt && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: 0.5 }}
                      className="p-4 rounded-xl bg-violet-500/10 border border-violet-500/20"
                    >
                      <p className="text-xs text-violet-400 uppercase tracking-wider mb-2">✨ Auto-Improved</p>
                      <p className="text-slate-200">{result.compiled_prompt}</p>
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Two Column Layout */}
            <div className="grid md:grid-cols-2 gap-6">
              <motion.div
                className="glass-card rounded-3xl p-6"
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.2 }}
              >
                <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <span>📊</span> Dimension Analysis
                </h3>
                <CategoryScores scores={result.category_scores} />
              </motion.div>

              <motion.div
                className="glass-card rounded-3xl p-6"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
              >
                <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                  <span>⚠️</span> Issues ({result.issues.length})
                </h3>
                <IssuesList issues={result.issues} maxItems={5} />
              </motion.div>
            </div>

            {/* Recommendations */}
            <motion.div
              className="glass-card rounded-3xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h3 className="text-lg font-semibold text-slate-200 mb-4 flex items-center gap-2">
                <span>💡</span> Recommendations
              </h3>
              <RecommendationsPanel recommendations={result.recommendations} quickTip={result.quick_tip} />
            </motion.div>

            {/* Metadata */}
            <motion.div
              className="flex flex-wrap items-center justify-center gap-4 text-xs text-slate-500"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
            >
              <span>ID: {result.compilation_id}</span>
              <span>•</span>
              <span>Time: {new Date(result.timestamp).toLocaleString()}</span>
            </motion.div>
          </motion.section>
        )}
      </AnimatePresence>
    </div>
  );
}
