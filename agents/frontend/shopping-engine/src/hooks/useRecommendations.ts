'use client';

import { useState, useCallback } from 'react';
import apiClient from '@/src/api/client';
import { useTaskPolling } from './useTaskPolling';
import type {
    GetRecommendationsRequest,
    RecommendationsResult,
    DirectResultResponse,
    TaskSubmittedResponse,
} from '@/src/types/api';

interface UseRecommendationsReturn {
    getRecommendations: (request: GetRecommendationsRequest) => Promise<void>;
    result: RecommendationsResult | null;
    isLoading: boolean;
    isPolling: boolean;
    error: string | null;
    reset: () => void;
}

export const useRecommendations = (): UseRecommendationsReturn => {
    const [result, setResult] = useState<RecommendationsResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { isPolling, startPolling, stopPolling } = useTaskPolling<RecommendationsResult>({
        onComplete: (taskResult) => {
            setResult(taskResult);
            setIsLoading(false);
        },
        onError: (err) => {
            setError(err);
            setIsLoading(false);
        },
    });

    const getRecommendations = useCallback(async (request: GetRecommendationsRequest) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await apiClient.getRecommendations(request);

            if (response.status === 'completed') {
                const directResponse = response as DirectResultResponse<RecommendationsResult>;
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
            const errorMessage = err instanceof Error ? err.message : 'Getting recommendations failed';
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
        getRecommendations,
        result,
        isLoading,
        isPolling,
        error,
        reset,
    };
};

export default useRecommendations;
