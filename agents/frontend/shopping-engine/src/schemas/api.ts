// ═══════════════════════════════════════════════════════════════════════════════
// Zod Validation Schemas for Shopping Engine API
// ═══════════════════════════════════════════════════════════════════════════════

import { z } from 'zod';

// ── Base Schemas ─────────────────────────────────────────────────────────────

export const ProductInfoSchema = z.object({
    name: z.string().optional(),
    category: z.string().optional(),
    brand: z.string().optional(),
    model: z.string().optional(),
    description: z.string().optional(),
    features: z.array(z.string()).optional(),
    keywords: z.array(z.string()).optional(),
    estimated_price: z.number().optional(),
    currency: z.string().optional(),
}).passthrough();

export const UserPreferencesSchema = z.object({
    budget_min: z.number().optional(),
    budget_max: z.number().optional(),
    preferred_vendors: z.array(z.string()).optional(),
    preferred_brands: z.array(z.string()).optional(),
    condition: z.enum(['new', 'used', 'refurbished']).optional(),
}).passthrough();

// ── Response Schemas ─────────────────────────────────────────────────────────

export const TaskSubmittedResponseSchema = z.object({
    status: z.literal('submitted'),
    task_id: z.string(),
    message: z.string(),
});

export const ErrorResponseSchema = z.object({
    status: z.literal('error'),
    error: z.string(),
    status_code: z.number().optional(),
});

export const HealthCheckResponseSchema = z.object({
    status: z.enum(['healthy', 'ready']),
    agent_running: z.boolean(),
    service: z.string(),
});

// ── Product Analysis ─────────────────────────────────────────────────────────

export const ProductAnalysisResultSchema = z.object({
    analysis: z.string(),
    product_info: ProductInfoSchema.optional(),
    confidence: z.number().optional(),
    tokens_used: z.number(),
    model: z.string(),
    success: z.boolean(),
    timestamp: z.string(),
});

export const AnalyzeProductResponseSchema = z.discriminatedUnion('status', [
    z.object({
        status: z.literal('completed'),
        service_type: z.string(),
        result: ProductAnalysisResultSchema,
    }),
    TaskSubmittedResponseSchema,
    ErrorResponseSchema,
]);

// ── Purchase Options ─────────────────────────────────────────────────────────

export const PurchaseOptionSchema = z.object({
    vendor: z.string(),
    vendor_url: z.string(),
    price: z.number(),
    currency: z.string(),
    availability: z.enum(['in_stock', 'limited', 'out_of_stock']),
    shipping_cost: z.number().optional(),
    delivery_estimate: z.string().optional(),
    condition: z.enum(['new', 'used', 'refurbished']),
    rating: z.number().optional(),
    reviews_count: z.number().optional(),
    special_offer: z.string().optional(),
});

export const PurchaseOptionsResultSchema = z.object({
    purchase_options: z.string(),
    options: z.array(PurchaseOptionSchema).optional(),
    recommended_option: PurchaseOptionSchema.optional(),
    search_strategy: z.string().optional(),
    tokens_used: z.number(),
    model: z.string(),
    success: z.boolean(),
    timestamp: z.string(),
});

// ── Recommendations ──────────────────────────────────────────────────────────

export const RecommendationSchema = z.object({
    name: z.string(),
    brand: z.string().optional(),
    price: z.number().optional(),
    currency: z.string().optional(),
    reason: z.string(),
    rating: z.number().optional(),
    similarity_score: z.number().optional(),
    url: z.string().optional(),
    image_url: z.string().optional(),
});

export const RecommendationsResultSchema = z.object({
    recommendations: z.string(),
    items: z.array(RecommendationSchema).optional(),
    recommendation_type: z.enum(['alternatives', 'upgrades', 'accessories', 'bundle']),
    tokens_used: z.number(),
    model: z.string(),
    success: z.boolean(),
    timestamp: z.string(),
});

// ── Price Comparison ─────────────────────────────────────────────────────────

export const VendorPriceSchema = z.object({
    vendor: z.string(),
    vendor_url: z.string(),
    price: z.number(),
    original_price: z.number().optional(),
    currency: z.string(),
    discount_percentage: z.number().optional(),
    availability: z.string(),
    last_updated: z.string().optional(),
});

export const PriceComparisonResultSchema = z.object({
    price_comparison: z.string(),
    prices: z.array(VendorPriceSchema).optional(),
    best_deal: VendorPriceSchema.optional(),
    price_range: z.object({
        min: z.number(),
        max: z.number(),
        average: z.number(),
    }).optional(),
    tokens_used: z.number(),
    model: z.string(),
    success: z.boolean(),
    timestamp: z.string(),
});

// ── Product Details ──────────────────────────────────────────────────────────

export const ProductDetailsResultSchema = z.object({
    product_details: z.string(),
    specifications: z.record(z.string()).optional(),
    materials: z.array(z.string()).optional(),
    dimensions: z.object({
        width: z.number().optional(),
        height: z.number().optional(),
        depth: z.number().optional(),
        weight: z.number().optional(),
        unit: z.string().optional(),
    }).optional(),
    compatibility: z.array(z.string()).optional(),
    warranty: z.object({
        duration: z.string(),
        type: z.string(),
        coverage: z.array(z.string()).optional(),
    }).optional(),
    reviews_summary: z.object({
        average_rating: z.number(),
        total_reviews: z.number(),
        pros: z.array(z.string()).optional(),
        cons: z.array(z.string()).optional(),
    }).optional(),
    tokens_used: z.number(),
    model: z.string(),
    success: z.boolean(),
    timestamp: z.string(),
});

// ── Type Exports ─────────────────────────────────────────────────────────────

export type ProductInfo = z.infer<typeof ProductInfoSchema>;
export type PurchaseOption = z.infer<typeof PurchaseOptionSchema>;
export type Recommendation = z.infer<typeof RecommendationSchema>;
export type VendorPrice = z.infer<typeof VendorPriceSchema>;
export type ProductAnalysisResult = z.infer<typeof ProductAnalysisResultSchema>;
export type PurchaseOptionsResult = z.infer<typeof PurchaseOptionsResultSchema>;
export type RecommendationsResult = z.infer<typeof RecommendationsResultSchema>;
export type PriceComparisonResult = z.infer<typeof PriceComparisonResultSchema>;
export type ProductDetailsResult = z.infer<typeof ProductDetailsResultSchema>;
