// ═══════════════════════════════════════════════════════════════════════════════
// API Types for Shopping Engine AI
// ═══════════════════════════════════════════════════════════════════════════════

// ── Request Types ────────────────────────────────────────────────────────────

export interface AnalyzeProductRequest {
    image_data?: string;
    image_url?: string;
    additional_context?: string;
    priority?: number;
    direct?: boolean;
}

export interface FindPurchaseOptionsRequest {
    product_info: ProductInfo;
    country?: string;
    preferences?: UserPreferences;
    priority?: number;
    direct?: boolean;
}

export interface GetRecommendationsRequest {
    product_info: ProductInfo;
    recommendation_type?: RecommendationType;
    budget?: number;
    priority?: number;
    direct?: boolean;
}

export interface ComparePricesRequest {
    product_info: ProductInfo;
    vendors?: string[];
    priority?: number;
    direct?: boolean;
}

export interface ProductDetailsRequest {
    product_info: ProductInfo;
    detail_level?: DetailLevel;
    priority?: number;
    direct?: boolean;
}

// ── Response Types ───────────────────────────────────────────────────────────

export interface TaskSubmittedResponse {
    status: 'submitted';
    task_id: string;
    message: string;
}

export interface DirectResultResponse<T> {
    status: 'completed';
    service_type: string;
    result: T;
}

export interface TaskStatusResponse {
    task_id: string;
    status: TaskStatus;
    created_at?: string;
    completed_at?: string;
    error?: string;
}

export interface HealthCheckResponse {
    status: 'healthy' | 'ready';
    agent_running: boolean;
    service: string;
}

export interface ErrorResponse {
    status: 'error';
    error: string;
    status_code?: number;
}

// ── Domain Types ─────────────────────────────────────────────────────────────

export interface ProductInfo {
    name?: string;
    category?: string;
    brand?: string;
    model?: string;
    description?: string;
    features?: string[];
    keywords?: string[];
    estimated_price?: number;
    currency?: string;
    [key: string]: unknown;
}

export interface UserPreferences {
    budget_min?: number;
    budget_max?: number;
    preferred_vendors?: string[];
    preferred_brands?: string[];
    condition?: 'new' | 'used' | 'refurbished';
    shipping_preferences?: ShippingPreferences;
    [key: string]: unknown;
}

export interface ShippingPreferences {
    express?: boolean;
    free_shipping_only?: boolean;
    max_delivery_days?: number;
}

export interface ProductAnalysisResult {
    analysis: string;
    product_info: ProductInfo;
    confidence: number;
    tokens_used: number;
    model: string;
    success: boolean;
    timestamp: string;
}

export interface PurchaseOption {
    vendor: string;
    vendor_url: string;
    price: number;
    currency: string;
    availability: 'in_stock' | 'limited' | 'out_of_stock';
    shipping_cost?: number;
    delivery_estimate?: string;
    condition: 'new' | 'used' | 'refurbished';
    rating?: number;
    reviews_count?: number;
    special_offer?: string;
}

export interface PurchaseOptionsResult {
    purchase_options: string;
    options: PurchaseOption[];
    recommended_option?: PurchaseOption;
    search_strategy: string;
    tokens_used: number;
    model: string;
    success: boolean;
    timestamp: string;
}

export interface Recommendation {
    name: string;
    brand?: string;
    price?: number;
    currency?: string;
    reason: string;
    rating?: number;
    similarity_score?: number;
    url?: string;
    image_url?: string;
}

export interface RecommendationsResult {
    recommendations: string;
    items: Recommendation[];
    recommendation_type: RecommendationType;
    tokens_used: number;
    model: string;
    success: boolean;
    timestamp: string;
}

export interface VendorPrice {
    vendor: string;
    vendor_url: string;
    price: number;
    original_price?: number;
    currency: string;
    discount_percentage?: number;
    availability: string;
    last_updated?: string;
}

export interface PriceComparisonResult {
    price_comparison: string;
    prices: VendorPrice[];
    best_deal?: VendorPrice;
    price_range: {
        min: number;
        max: number;
        average: number;
    };
    tokens_used: number;
    model: string;
    success: boolean;
    timestamp: string;
}

export interface ProductDetailsResult {
    product_details: string;
    specifications: Record<string, string>;
    materials?: string[];
    dimensions?: {
        width?: number;
        height?: number;
        depth?: number;
        weight?: number;
        unit?: string;
    };
    compatibility?: string[];
    warranty?: {
        duration: string;
        type: string;
        coverage: string[];
    };
    reviews_summary?: {
        average_rating: number;
        total_reviews: number;
        pros: string[];
        cons: string[];
    };
    tokens_used: number;
    model: string;
    success: boolean;
    timestamp: string;
}

// ── Enums ────────────────────────────────────────────────────────────────────

export type TaskStatus = 'pending' | 'running' | 'completed' | 'failed';

export type RecommendationType = 'alternatives' | 'upgrades' | 'accessories' | 'bundle';

export type DetailLevel = 'basic' | 'complete' | 'technical';

// ── API Response Union Types ─────────────────────────────────────────────────

export type ApiResponse<T> = DirectResultResponse<T> | TaskSubmittedResponse | ErrorResponse;

export type AnalyzeProductResponse = ApiResponse<ProductAnalysisResult>;
export type FindPurchaseOptionsResponse = ApiResponse<PurchaseOptionsResult>;
export type GetRecommendationsResponse = ApiResponse<RecommendationsResult>;
export type ComparePricesResponse = ApiResponse<PriceComparisonResult>;
export type ProductDetailsResponse = ApiResponse<ProductDetailsResult>;
