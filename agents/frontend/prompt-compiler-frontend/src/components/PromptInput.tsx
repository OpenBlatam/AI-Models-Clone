"use client";

import { type FC, useState, type FormEvent, type ChangeEvent } from "react";
import { motion } from "framer-motion";
import { toast } from "sonner";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";

const promptSchema = z.object({
    prompt: z.string().min(1, "Prompt is required").max(10000, "Prompt too long"),
    autoImprove: z.boolean().default(false),
});

type PromptFormData = z.infer<typeof promptSchema>;

interface PromptInputProps {
    onSubmit: (prompt: string, autoImprove: boolean) => void;
    isLoading?: boolean;
    placeholder?: string;
    maxLength?: number;
}

export const PromptInput: FC<PromptInputProps> = ({
    onSubmit,
    isLoading = false,
    placeholder = "Enter your prompt here... (e.g., 'Write a function to validate email addresses')",
    maxLength = 10000,
}) => {
    const [autoImprove, setAutoImprove] = useState(false);

    const {
        register,
        handleSubmit,
        watch,
        formState: { errors },
    } = useForm<PromptFormData>({
        resolver: zodResolver(promptSchema),
        defaultValues: { prompt: "", autoImprove: false },
    });

    const promptValue = watch("prompt");
    const charCount = promptValue?.length || 0;
    const isNearLimit = charCount > maxLength * 0.9;

    const onFormSubmit = (data: PromptFormData) => {
        if (isLoading) return;
        onSubmit(data.prompt.trim(), autoImprove);
        toast.info("Compiling prompt...", { duration: 1500 });
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            handleSubmit(onFormSubmit)();
        }
    };

    return (
        <motion.form
            onSubmit={handleSubmit(onFormSubmit)}
            className="space-y-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            {/* Textarea container */}
            <motion.div
                className="relative group"
                whileHover={{ scale: 1.005 }}
                transition={{ type: "spring", stiffness: 300 }}
            >
                <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-purple-600 rounded-2xl blur opacity-20 group-hover:opacity-30 transition duration-300" />
                <div className="relative">
                    <Textarea
                        {...register("prompt")}
                        onKeyDown={handleKeyDown}
                        placeholder={placeholder}
                        rows={6}
                        disabled={isLoading}
                        className={`
              w-full px-5 py-4 rounded-2xl resize-none
              bg-slate-800/90 border border-slate-700/50
              text-slate-100 placeholder-slate-500
              focus:outline-none focus:ring-2 focus:ring-violet-500/50 focus:border-violet-500/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            `}
                        aria-label="Enter your prompt"
                    />

                    {/* Character count */}
                    <div className="absolute bottom-3 right-4 flex items-center gap-2">
                        <span className={`text-xs ${isNearLimit ? "text-amber-400" : "text-slate-500"}`}>
                            {charCount.toLocaleString()}/{maxLength.toLocaleString()}
                        </span>
                    </div>
                </div>

                {errors.prompt && (
                    <motion.p
                        className="text-red-400 text-sm mt-2"
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                    >
                        {errors.prompt.message}
                    </motion.p>
                )}
            </motion.div>

            {/* Options and submit */}
            <div className="flex items-center justify-between gap-4">
                {/* Auto-improve toggle */}
                <label className="flex items-center gap-3 cursor-pointer group/toggle">
                    <div className="relative">
                        <input
                            type="checkbox"
                            checked={autoImprove}
                            onChange={(e) => setAutoImprove(e.target.checked)}
                            className="sr-only peer"
                            disabled={isLoading}
                        />
                        <motion.div
                            className={`w-11 h-6 rounded-full transition-colors ${autoImprove ? "bg-violet-600" : "bg-slate-700"}`}
                            whileTap={{ scale: 0.95 }}
                        />
                        <motion.div
                            className="absolute left-1 top-1 w-4 h-4 bg-white rounded-full"
                            animate={{ x: autoImprove ? 20 : 0 }}
                            transition={{ type: "spring", stiffness: 500, damping: 30 }}
                        />
                    </div>
                    <div>
                        <span className="text-sm text-slate-300 group-hover/toggle:text-slate-100 transition-colors">
                            Auto-improve
                        </span>
                        <p className="text-xs text-slate-500">Automatically enhance low-scoring prompts</p>
                    </div>
                </label>

                {/* Submit button */}
                <Button
                    type="submit"
                    disabled={!promptValue?.trim() || isLoading}
                    className="relative inline-flex items-center gap-2 px-6 py-3 rounded-xl font-semibold text-white bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-500 hover:to-purple-500 disabled:opacity-50"
                    aria-label="Compile prompt"
                >
                    <motion.div
                        className="flex items-center gap-2"
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                    >
                        {isLoading ? (
                            <>
                                <motion.div
                                    className="w-5 h-5 border-2 border-white border-t-transparent rounded-full"
                                    animate={{ rotate: 360 }}
                                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                                />
                                <span>Compiling...</span>
                            </>
                        ) : (
                            <>
                                <span>⚡</span>
                                <span>Compile</span>
                                <span className="text-xs opacity-60 hidden sm:inline">(⌘+Enter)</span>
                            </>
                        )}
                    </motion.div>
                </Button>
            </div>
        </motion.form>
    );
};

export default PromptInput;
