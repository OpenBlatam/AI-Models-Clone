'use client';

import { useState, useCallback } from 'react';
import apiClient from '@/src/api/client';
import { useTaskPolling } from './useTaskPolling';
import type {
    FindPurchaseOptionsRequest,
    PurchaseOptionsResult,
    DirectResultResponse,
    TaskSubmittedResponse,
} from '@/src/types/api';

interface UsePurchaseOptionsReturn {
    findOptions: (request: FindPurchaseOptionsRequest) => Promise<void>;
    result: PurchaseOptionsResult | null;
    isLoading: boolean;
    isPolling: boolean;
    error: string | null;
    reset: () => void;
}

export const usePurchaseOptions = (): UsePurchaseOptionsReturn => {
    const [result, setResult] = useState<PurchaseOptionsResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { isPolling, startPolling, stopPolling } = useTaskPolling<PurchaseOptionsResult>({
        onComplete: (taskResult) => {
            setResult(taskResult);
            setIsLoading(false);
        },
        onError: (err) => {
            setError(err);
            setIsLoading(false);
        },
    });

    const findOptions = useCallback(async (request: FindPurchaseOptionsRequest) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await apiClient.findPurchaseOptions(request);

            if (response.status === 'completed') {
                const directResponse = response as DirectResultResponse<PurchaseOptionsResult>;
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
            const errorMessage = err instanceof Error ? err.message : 'Finding purchase options failed';
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
        findOptions,
        result,
        isLoading,
        isPolling,
        error,
        reset,
    };
};

export default usePurchaseOptions;
