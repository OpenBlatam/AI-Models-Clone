'use client';

// ═══════════════════════════════════════════════════════════════════════════════
// React Query Hooks for Shopping Engine API
// ═══════════════════════════════════════════════════════════════════════════════

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/src/api/client';
import { showToast } from '@/src/providers/ToastProvider';
import { useProductStore } from '@/src/stores';
import type {
    AnalyzeProductRequest,
    FindPurchaseOptionsRequest,
    GetRecommendationsRequest,
    ComparePricesRequest,
    ProductDetailsRequest,
    ProductAnalysisResult,
    PurchaseOptionsResult,
    RecommendationsResult,
    PriceComparisonResult,
    ProductDetailsResult,
    DirectResultResponse,
    TaskSubmittedResponse,
} from '@/src/types/api';

// ── Query Keys ───────────────────────────────────────────────────────────────

export const queryKeys = {
    health: ['health'] as const,
    taskStatus: (taskId: string) => ['task', taskId, 'status'] as const,
    taskResult: (taskId: string) => ['task', taskId, 'result'] as const,
};

// ── Health Check Hook ────────────────────────────────────────────────────────

export const useHealthCheck = () => {
    return useQuery({
        queryKey: queryKeys.health,
        queryFn: () => apiClient.healthCheck(),
        refetchInterval: 30000, // Check every 30 seconds
        staleTime: 10000,
    });
};

// ── Analyze Product Hook ─────────────────────────────────────────────────────

export const useAnalyzeProductMutation = () => {
    const queryClient = useQueryClient();
    const setCurrentProduct = useProductStore((s) => s.setCurrentProduct);

    return useMutation({
        mutationFn: async (request: AnalyzeProductRequest) => {
            const response = await apiClient.analyzeProduct({ ...request, direct: true });

            if (response.status === 'completed') {
                return (response as DirectResultResponse<ProductAnalysisResult>).result;
            }

            if (response.status === 'submitted') {
                // For async tasks, poll until completion
                const taskId = (response as TaskSubmittedResponse).task_id;
                return pollTaskResult<ProductAnalysisResult>(taskId, apiClient);
            }

            throw new Error('Unexpected response');
        },
        onSuccess: (data) => {
            showToast.success('Product analyzed successfully!');
            if (data.product_info) {
                setCurrentProduct(data.product_info);
            }
            queryClient.invalidateQueries({ queryKey: queryKeys.health });
        },
        onError: (error: Error) => {
            showToast.error(error.message || 'Analysis failed');
        },
    });
};

// ── Purchase Options Hook ────────────────────────────────────────────────────

export const usePurchaseOptionsMutation = () => {
    return useMutation({
        mutationFn: async (request: FindPurchaseOptionsRequest) => {
            const response = await apiClient.findPurchaseOptions({ ...request, direct: true });

            if (response.status === 'completed') {
                return (response as DirectResultResponse<PurchaseOptionsResult>).result;
            }

            if (response.status === 'submitted') {
                const taskId = (response as TaskSubmittedResponse).task_id;
                return pollTaskResult<PurchaseOptionsResult>(taskId, apiClient);
            }

            throw new Error('Unexpected response');
        },
        onSuccess: () => {
            showToast.success('Purchase options found!');
        },
        onError: (error: Error) => {
            showToast.error(error.message || 'Failed to find purchase options');
        },
    });
};

// ── Recommendations Hook ─────────────────────────────────────────────────────

export const useRecommendationsMutation = () => {
    return useMutation({
        mutationFn: async (request: GetRecommendationsRequest) => {
            const response = await apiClient.getRecommendations({ ...request, direct: true });

            if (response.status === 'completed') {
                return (response as DirectResultResponse<RecommendationsResult>).result;
            }

            if (response.status === 'submitted') {
                const taskId = (response as TaskSubmittedResponse).task_id;
                return pollTaskResult<RecommendationsResult>(taskId, apiClient);
            }

            throw new Error('Unexpected response');
        },
        onSuccess: () => {
            showToast.success('Recommendations ready!');
        },
        onError: (error: Error) => {
            showToast.error(error.message || 'Failed to get recommendations');
        },
    });
};

// ── Compare Prices Hook ──────────────────────────────────────────────────────

export const useComparePricesMutation = () => {
    return useMutation({
        mutationFn: async (request: ComparePricesRequest) => {
            const response = await apiClient.comparePrices({ ...request, direct: true });

            if (response.status === 'completed') {
                return (response as DirectResultResponse<PriceComparisonResult>).result;
            }

            if (response.status === 'submitted') {
                const taskId = (response as TaskSubmittedResponse).task_id;
                return pollTaskResult<PriceComparisonResult>(taskId, apiClient);
            }

            throw new Error('Unexpected response');
        },
        onSuccess: () => {
            showToast.success('Price comparison complete!');
        },
        onError: (error: Error) => {
            showToast.error(error.message || 'Price comparison failed');
        },
    });
};

// ── Product Details Hook ─────────────────────────────────────────────────────

export const useProductDetailsMutation = () => {
    return useMutation({
        mutationFn: async (request: ProductDetailsRequest) => {
            const response = await apiClient.getProductDetails({ ...request, direct: true });

            if (response.status === 'completed') {
                return (response as DirectResultResponse<ProductDetailsResult>).result;
            }

            if (response.status === 'submitted') {
                const taskId = (response as TaskSubmittedResponse).task_id;
                return pollTaskResult<ProductDetailsResult>(taskId, apiClient);
            }

            throw new Error('Unexpected response');
        },
        onSuccess: () => {
            showToast.success('Product details loaded!');
        },
        onError: (error: Error) => {
            showToast.error(error.message || 'Failed to get product details');
        },
    });
};

// ── Task Polling Helper ──────────────────────────────────────────────────────

async function pollTaskResult<T>(
    taskId: string,
    client: typeof apiClient,
    maxAttempts = 60,
    interval = 2000
): Promise<T> {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
        const status = await client.getTaskStatus(taskId);

        if (status.status === 'completed') {
            return client.getTaskResult<T>(taskId);
        }

        if (status.status === 'failed') {
            throw new Error(status.error || 'Task failed');
        }

        await new Promise((resolve) => setTimeout(resolve, interval));
    }

    throw new Error('Task polling timeout');
}
