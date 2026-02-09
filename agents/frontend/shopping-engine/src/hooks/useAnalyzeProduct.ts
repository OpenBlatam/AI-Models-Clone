'use client';

import { useState, useCallback } from 'react';
import apiClient from '@/src/api/client';
import { useTaskPolling } from './useTaskPolling';
import type {
    AnalyzeProductRequest,
    ProductAnalysisResult,
    DirectResultResponse,
    TaskSubmittedResponse,
} from '@/src/types/api';

interface UseAnalyzeProductReturn {
    analyze: (request: AnalyzeProductRequest) => Promise<void>;
    result: ProductAnalysisResult | null;
    isLoading: boolean;
    isPolling: boolean;
    error: string | null;
    reset: () => void;
}

export const useAnalyzeProduct = (): UseAnalyzeProductReturn => {
    const [result, setResult] = useState<ProductAnalysisResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { isPolling, startPolling, stopPolling } = useTaskPolling<ProductAnalysisResult>({
        onComplete: (taskResult) => {
            setResult(taskResult);
            setIsLoading(false);
        },
        onError: (err) => {
            setError(err);
            setIsLoading(false);
        },
    });

    const analyze = useCallback(async (request: AnalyzeProductRequest) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await apiClient.analyzeProduct(request);

            if (response.status === 'completed') {
                const directResponse = response as DirectResultResponse<ProductAnalysisResult>;
                setResult(directResponse.result);
                setIsLoading(false);
                return;
            }

            if (response.status === 'submitted') {
                const taskResponse = response as TaskSubmittedResponse;
                startPolling(taskResponse.task_id);
                return;
            }

            throw new Error('Unexpected response status');
        } catch (err) {
            const errorMessage = err instanceof Error ? err.message : 'Analysis failed';
            setError(errorMessage);
            setIsLoading(false);
        }
    }, [startPolling]);

    const reset = useCallback(() => {
        setResult(null);
        setError(null);
        setIsLoading(false);
        stopPolling();
    }, [stopPolling]);

    return {
        analyze,
        result,
        isLoading,
        isPolling,
        error,
        reset,
    };
};

export default useAnalyzeProduct;
