'use client';

import { useState, useCallback } from 'react';
import apiClient from '@/src/api/client';
import { useTaskPolling } from './useTaskPolling';
import type {
    ProductDetailsRequest,
    ProductDetailsResult,
    DirectResultResponse,
    TaskSubmittedResponse,
} from '@/src/types/api';

interface UseProductDetailsReturn {
    getDetails: (request: ProductDetailsRequest) => Promise<void>;
    result: ProductDetailsResult | null;
    isLoading: boolean;
    isPolling: boolean;
    error: string | null;
    reset: () => void;
}

export const useProductDetails = (): UseProductDetailsReturn => {
    const [result, setResult] = useState<ProductDetailsResult | null>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const { isPolling, startPolling, stopPolling } = useTaskPolling<ProductDetailsResult>({
        onComplete: (taskResult) => {
            setResult(taskResult);
            setIsLoading(false);
        },
        onError: (err) => {
            setError(err);
            setIsLoading(false);
        },
    });

    const getDetails = useCallback(async (request: ProductDetailsRequest) => {
        setIsLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await apiClient.getProductDetails(request);

            if (response.status === 'completed') {
                const directResponse = response as DirectResultResponse<ProductDetailsResult>;
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
            const errorMessage = err instanceof Error ? err.message : 'Getting product details failed';
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
        getDetails,
        result,
        isLoading,
        isPolling,
        error,
        reset,
    };
};

export default useProductDetails;
