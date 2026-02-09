export enum StoreType {
  RETAIL = 'retail',
  RESTAURANT = 'restaurant',
  CAFE = 'cafe',
  BOUTIQUE = 'boutique',
  SUPERMARKET = 'supermarket',
  PHARMACY = 'pharmacy',
  ELECTRONICS = 'electronics',
  CLOTHING = 'clothing',
  FURNITURE = 'furniture',
  OTHER = 'other',
}

export enum DesignStyle {
  MODERN = 'modern',
  CLASSIC = 'classic',
  MINIMALIST = 'minimalist',
  INDUSTRIAL = 'industrial',
  RUSTIC = 'rustic',
  LUXURY = 'luxury',
  ECO_FRIENDLY = 'eco_friendly',
  VINTAGE = 'vintage',
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
}

export interface ChatSession {
  session_id: string
  messages: ChatMessage[]
  store_info: Record<string, unknown>
  created_at?: string
  updated_at?: string
}

export interface StoreLayout {
  dimensions: {
    width: number
    length: number
    height: number
  }
  zones: Array<Record<string, unknown>>
  furniture_placement: Array<Record<string, unknown>>
  traffic_flow: Record<string, unknown>
  accessibility: Record<string, unknown>
}

export interface StoreVisualization {
  image_url?: string
  image_prompt: string
  view_type: 'exterior' | 'interior' | 'layout'
  style: DesignStyle
}

export interface MarketingPlan {
  target_audience: string
  marketing_strategy: string[]
  sales_tactics: string[]
  pricing_strategy: string
  promotion_ideas: string[]
  social_media_plan: Record<string, unknown>
  opening_strategy: string
}

export interface DecorationPlan {
  color_scheme: Record<string, string>
  lighting_plan: Record<string, unknown>
  furniture_recommendations: Array<Record<string, unknown>>
  decoration_elements: Array<Record<string, unknown>>
  materials: string[]
  budget_estimate: Record<string, number>
}

export interface StoreDesign {
  store_id: string
  store_name: string
  store_type: StoreType
  style: DesignStyle
  layout: StoreLayout
  visualizations: StoreVisualization[]
  marketing_plan: MarketingPlan
  decoration_plan: DecorationPlan
  description: string
  competitor_analysis?: Record<string, unknown>
  financial_analysis?: Record<string, unknown>
  inventory_recommendations?: Record<string, unknown>
  kpis?: Record<string, unknown>
  created_at: string
  updated_at: string
}

export interface StoreDesignRequest {
  store_name: string
  store_type: StoreType
  style_preference?: DesignStyle
  budget_range?: string
  location?: string
  target_audience?: string
  special_requirements?: string
  dimensions?: {
    width: number
    length: number
    height: number
  }
  additional_info?: string
}

export interface ApiResponse<T> {
  data?: T
  error?: string
  message?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}


