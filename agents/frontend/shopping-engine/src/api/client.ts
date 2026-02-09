// ═══════════════════════════════════════════════════════════════════════════════
// API Client for Shopping Engine AI
// ═══════════════════════════════════════════════════════════════════════════════

import type {
    AnalyzeProductRequest,
    AnalyzeProductResponse,
    FindPurchaseOptionsRequest,
    FindPurchaseOptionsResponse,
    GetRecommendationsRequest,
    GetRecommendationsResponse,
    ComparePricesRequest,
    ComparePricesResponse,
    ProductDetailsRequest,
    ProductDetailsResponse,
    TaskStatusResponse,
    HealthCheckResponse,
    ErrorResponse,
} from '@/src/types/api';

// ── Configuration ────────────────────────────────────────────────────────────

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8060';

// ── API Client Class ─────────────────────────────────────────────────────────

class ApiClient {
    private baseUrl: string;

    constructor(baseUrl: string = API_BASE_URL) {
        this.baseUrl = baseUrl;
    }

    private async request<T>(
        endpoint: string,
        options: RequestInit = {}
    ): Promise<T> {
        const url = `${this.baseUrl}${endpoint}`;

        const defaultHeaders: HeadersInit = {
            'Content-Type': 'application/json',
        };

        const response = await fetch(url, {
            ...options,
            headers: {
                ...defaultHeaders,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorResponse: ErrorResponse = {
                status: 'error',
                error: errorData.detail || errorData.error || `HTTP ${response.status}`,
                status_code: response.status,
            };
            throw errorResponse;
        }

        return response.json();
    }

    // ── Product Analysis ─────────────────────────────────────────────────────

    async analyzeProduct(data: AnalyzeProductRequest): Promise<AnalyzeProductResponse> {
        return this.request<AnalyzeProductResponse>('/analyze-product', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ── Purchase Options ─────────────────────────────────────────────────────

    async findPurchaseOptions(data: FindPurchaseOptionsRequest): Promise<FindPurchaseOptionsResponse> {
        return this.request<FindPurchaseOptionsResponse>('/find-purchase-options', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ── Recommendations ──────────────────────────────────────────────────────

    async getRecommendations(data: GetRecommendationsRequest): Promise<GetRecommendationsResponse> {
        return this.request<GetRecommendationsResponse>('/get-recommendations', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ── Price Comparison ─────────────────────────────────────────────────────

    async comparePrices(data: ComparePricesRequest): Promise<ComparePricesResponse> {
        return this.request<ComparePricesResponse>('/compare-prices', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ── Product Details ──────────────────────────────────────────────────────

    async getProductDetails(data: ProductDetailsRequest): Promise<ProductDetailsResponse> {
        return this.request<ProductDetailsResponse>('/product-details', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    // ── Task Status ──────────────────────────────────────────────────────────

    async getTaskStatus(taskId: string): Promise<TaskStatusResponse> {
        return this.request<TaskStatusResponse>(`/task/${taskId}/status`);
    }

    async getTaskResult<T>(taskId: string): Promise<T> {
        return this.request<T>(`/task/${taskId}/result`);
    }

    // ── Health Check ─────────────────────────────────────────────────────────

    async healthCheck(): Promise<HealthCheckResponse> {
        return this.request<HealthCheckResponse>('/health');
    }
}

// ── Singleton Export ─────────────────────────────────────────────────────────

export const apiClient = new ApiClient();
export default apiClient;
