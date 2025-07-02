"""
⚙️ ULTRA LANDING PAGE CONFIG - SETTINGS
======================================

Configuración completa para landing pages ultra-optimizadas
con integración LangChain y configuraciones de performance.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseSettings, Field
import os


class UltraLandingPageSettings(BaseSettings):
    """Configuración principal para landing pages."""
    
    # === CONFIGURACIÓN GENERAL ===
    app_name: str = "Ultra Landing Page Generator"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = Field(default="production", description="Environment (dev, staging, production)")
    
    # === API CONFIGURATION ===
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_workers: int = 4
    api_timeout: int = 300
    
    # === BASE URLS ===
    base_url: str = "https://example.com"
    preview_base_url: str = "https://preview.example.com"
    admin_base_url: str = "https://admin.example.com"
    cdn_base_url: str = "https://cdn.example.com"
    
    # === LANGCHAIN CONFIGURATION ===
    langchain_model: str = "gpt-4"
    langchain_api_key: Optional[str] = None
    langchain_max_tokens: int = 2000
    langchain_temperature: float = 0.7
    langchain_timeout: int = 30
    
    # === SEO CONFIGURATION ===
    seo_min_title_length: int = 30
    seo_max_title_length: int = 60
    seo_min_meta_desc_length: int = 120
    seo_max_meta_desc_length: int = 160
    seo_target_keyword_density: float = 2.5
    seo_min_score_threshold: float = 70.0
    
    # === CONVERSION OPTIMIZATION ===
    conversion_min_score_threshold: float = 75.0
    conversion_cta_max_words: int = 3
    conversion_headline_max_length: int = 100
    conversion_min_testimonials: int = 3
    conversion_ab_test_enabled: bool = True
    
    # === PERFORMANCE CONFIG ===
    performance_min_score_threshold: float = 85.0
    performance_max_response_time_ms: int = 2000
    performance_cache_ttl_seconds: int = 3600
    performance_max_concurrent_generations: int = 10
    
    # === DATABASE CONFIG ===
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    cache_enabled: bool = True
    cache_default_ttl: int = 3600
    
    # === MONITORING CONFIG ===
    monitoring_enabled: bool = True
    metrics_enabled: bool = True
    logging_level: str = "INFO"
    sentry_dsn: Optional[str] = None
    
    # === ANALYTICS CONFIG ===
    google_analytics_id: Optional[str] = None
    google_tag_manager_id: Optional[str] = None
    facebook_pixel_id: Optional[str] = None
    analytics_tracking_enabled: bool = True
    
    # === SECURITY CONFIG ===
    cors_allowed_origins: List[str] = ["*"]
    rate_limit_enabled: bool = True
    rate_limit_requests_per_minute: int = 100
    api_key_required: bool = False
    allowed_file_types: List[str] = ["jpg", "jpeg", "png", "webp", "svg"]
    max_file_size_mb: int = 10
    
    class Config:
        env_file = ".env"
        env_prefix = "LANDING_PAGE_"


class LangChainPromptTemplates:
    """Templates de prompts ultra-optimizados para LangChain."""
    
    # === HEADLINE GENERATION ===
    HEADLINE_TEMPLATE = """
    Generate a high-converting headline for a {page_type} landing page.
    
    Context:
    - Target audience: {target_audience}
    - Primary keyword: {primary_keyword}
    - Main benefit: {main_benefit}
    - Tone: {tone}
    
    Requirements:
    - 10-15 words maximum
    - Include primary keyword naturally
    - Create urgency and desire
    - Focus on transformation/outcome
    - Use power words that convert
    
    Power words to consider: Revolutionary, Ultimate, Secret, Proven, Exclusive, Advanced, Premium
    
    Generate 3 headline variations:
    """
    
    # === META DESCRIPTION ===
    META_DESCRIPTION_TEMPLATE = """
    Write a compelling meta description for a {page_type} landing page.
    
    Context:
    - Target audience: {target_audience}
    - Primary keyword: {primary_keyword}
    - Main benefit: {main_benefit}
    - Call-to-action: {cta_text}
    
    Requirements:
    - Exactly 150-160 characters
    - Include primary keyword naturally
    - Clear value proposition
    - Strong call-to-action
    - Create urgency or curiosity
    
    Write a meta description that maximizes CTR:
    """
    
    # === HERO SECTION ===
    HERO_SECTION_TEMPLATE = """
    Create a high-converting hero section for a {page_type} landing page.
    
    Context:
    - Target audience: {target_audience}
    - Primary keyword: {primary_keyword}
    - Main benefit: {main_benefit}
    - Pain points: {pain_points}
    - Social proof: {social_proof}
    - Tone: {tone}
    
    Structure:
    1. Hook (attention-grabbing opening)
    2. Problem identification
    3. Solution with main benefit
    4. Social proof element
    5. Clear call-to-action
    
    Write persuasive copy optimized for conversion:
    """
    
    # === FEATURE DESCRIPTIONS ===
    FEATURE_TEMPLATE = """
    Create a benefit-focused feature description for {feature_name}.
    
    Context:
    - Target audience: {target_audience}
    - Page type: {page_type}
    - Tone: {tone}
    
    Structure:
    - Benefit-focused title (not feature-focused)
    - 2-3 sentences explaining the benefit
    - Specific pain point this solves
    - Quantifiable result when possible
    
    Focus on "what's in it for them" not "what it does":
    """
    
    # === TESTIMONIALS ===
    TESTIMONIAL_TEMPLATE = """
    Generate a credible testimonial for a {page_type} offering.
    
    Context:
    - Product/service: {product_name}
    - Main benefit: {main_benefit}
    - Target audience: {target_audience}
    - Result type: {result_type}
    
    Requirements:
    - Sound authentic and specific
    - Mention concrete result/benefit
    - Include emotional language
    - 2-3 sentences long
    - Include realistic author details
    
    Create a testimonial that builds trust:
    """


class SEOOptimizationConfig:
    """Configuración para optimización SEO ultra-avanzada."""
    
    # === KEYWORD RESEARCH ===
    PRIMARY_KEYWORD_WEIGHT = 1.0
    SECONDARY_KEYWORD_WEIGHT = 0.6
    LONG_TAIL_KEYWORD_WEIGHT = 0.4
    
    # === ON-PAGE SEO ===
    TITLE_TAG_SCORING = {
        "length_optimal": (50, 60),
        "keyword_present": 25,
        "power_words_bonus": 10,
        "brand_inclusion": 5
    }
    
    META_DESCRIPTION_SCORING = {
        "length_optimal": (150, 160),
        "keyword_present": 20,
        "cta_present": 15,
        "benefit_mentioned": 10
    }
    
    CONTENT_SCORING = {
        "keyword_density_optimal": (2.0, 3.0),
        "readability_target": 65,
        "word_count_minimum": 300,
        "header_structure_bonus": 10
    }
    
    # === TECHNICAL SEO ===
    SCHEMA_MARKUP_TYPES = [
        "Organization",
        "WebPage", 
        "Product",
        "Service",
        "Review",
        "FAQPage",
        "BreadcrumbList"
    ]
    
    OPEN_GRAPH_REQUIRED = [
        "og:title",
        "og:description", 
        "og:image",
        "og:url",
        "og:type"
    ]
    
    TWITTER_CARD_REQUIRED = [
        "twitter:card",
        "twitter:title",
        "twitter:description",
        "twitter:image"
    ]


class ConversionOptimizationConfig:
    """Configuración para optimización de conversión."""
    
    # === CTA OPTIMIZATION ===
    CTA_POWER_WORDS = [
        "Get", "Start", "Try", "Claim", "Download", "Access",
        "Unlock", "Discover", "Join", "Begin", "Create", "Build"
    ]
    
    CTA_URGENCY_WORDS = [
        "Now", "Today", "Instantly", "Immediately", "Free",
        "Limited", "Exclusive", "Only", "Fast", "Quick"
    ]
    
    CTA_COLOR_PSYCHOLOGY = {
        "orange": "urgency_action",
        "red": "urgency_high", 
        "green": "safety_go",
        "blue": "trust_professional",
        "purple": "premium_luxury"
    }
    
    # === PSYCHOLOGICAL TRIGGERS ===
    PERSUASION_PRINCIPLES = [
        "social_proof",
        "scarcity",
        "authority",
        "reciprocity",
        "commitment_consistency",
        "liking"
    ]
    
    URGENCY_TECHNIQUES = [
        "time_limited_offer",
        "quantity_scarcity",
        "exclusive_access",
        "price_increase_warning",
        "bonus_expiration"
    ]
    
    # === A/B TESTING CONFIG ===
    AB_TEST_ELEMENTS = [
        "headline",
        "cta_text",
        "cta_color",
        "hero_image",
        "value_proposition",
        "social_proof_placement"
    ]
    
    AB_TEST_CONFIDENCE_THRESHOLD = 95.0
    AB_TEST_MIN_SAMPLE_SIZE = 100
    AB_TEST_MAX_DURATION_DAYS = 30


class PerformanceConfig:
    """Configuración de performance y optimización."""
    
    # === RESPONSE TIMES ===
    TARGET_RESPONSE_TIMES = {
        "api_endpoint": 200,  # ms
        "page_generation": 2000,  # ms
        "ai_content_generation": 5000,  # ms
        "seo_analysis": 1000,  # ms
        "optimization": 3000  # ms
    }
    
    # === CACHING STRATEGIES ===
    CACHE_STRATEGIES = {
        "landing_page_data": 3600,  # 1 hour
        "seo_analysis": 1800,  # 30 minutes
        "ai_generated_content": 7200,  # 2 hours
        "analytics_data": 600,  # 10 minutes
        "optimization_suggestions": 1800  # 30 minutes
    }
    
    # === RATE LIMITING ===
    RATE_LIMITS = {
        "create_landing_page": "10/minute",
        "optimize_page": "5/minute", 
        "generate_content": "20/minute",
        "analytics_request": "50/minute",
        "general_api": "100/minute"
    }
    
    # === MONITORING THRESHOLDS ===
    ALERT_THRESHOLDS = {
        "response_time_ms": 5000,
        "error_rate_percent": 5.0,
        "memory_usage_percent": 85.0,
        "cpu_usage_percent": 80.0,
        "disk_usage_percent": 90.0
    }


class IntegrationConfig:
    """Configuración de integraciones externas."""
    
    # === LANGCHAIN MODELS ===
    AVAILABLE_MODELS = {
        "gpt-4": {
            "provider": "openai",
            "max_tokens": 4000,
            "cost_per_1k_tokens": 0.03,
            "quality_score": 95
        },
        "gpt-3.5-turbo": {
            "provider": "openai", 
            "max_tokens": 4000,
            "cost_per_1k_tokens": 0.002,
            "quality_score": 85
        },
        "claude-3": {
            "provider": "anthropic",
            "max_tokens": 4000,
            "cost_per_1k_tokens": 0.025,
            "quality_score": 90
        }
    }
    
    # === ANALYTICS PLATFORMS ===
    ANALYTICS_INTEGRATIONS = [
        "google_analytics",
        "google_tag_manager",
        "facebook_pixel",
        "hotjar",
        "mixpanel",
        "amplitude"
    ]
    
    # === A/B TESTING PLATFORMS ===
    AB_TEST_PLATFORMS = [
        "optimizely",
        "vwo",
        "google_optimize", 
        "unbounce",
        "custom_implementation"
    ]


# === INSTANCE GLOBAL ===
settings = UltraLandingPageSettings()
prompts = LangChainPromptTemplates()
seo_config = SEOOptimizationConfig()
conversion_config = ConversionOptimizationConfig()
performance_config = PerformanceConfig()
integration_config = IntegrationConfig()


def get_settings() -> UltraLandingPageSettings:
    """Obtiene configuración global."""
    return settings


def get_langchain_config() -> Dict[str, Any]:
    """Obtiene configuración de LangChain."""
    return {
        "model": settings.langchain_model,
        "api_key": settings.langchain_api_key,
        "max_tokens": settings.langchain_max_tokens,
        "temperature": settings.langchain_temperature,
        "timeout": settings.langchain_timeout,
        "available_models": integration_config.AVAILABLE_MODELS
    }


def get_seo_config() -> Dict[str, Any]:
    """Obtiene configuración SEO."""
    return {
        "title_length": (settings.seo_min_title_length, settings.seo_max_title_length),
        "meta_desc_length": (settings.seo_min_meta_desc_length, settings.seo_max_meta_desc_length),
        "target_keyword_density": settings.seo_target_keyword_density,
        "min_score_threshold": settings.seo_min_score_threshold,
        "scoring": {
            "title": seo_config.TITLE_TAG_SCORING,
            "meta_description": seo_config.META_DESCRIPTION_SCORING,
            "content": seo_config.CONTENT_SCORING
        }
    }


def get_conversion_config() -> Dict[str, Any]:
    """Obtiene configuración de conversión."""
    return {
        "min_score_threshold": settings.conversion_min_score_threshold,
        "cta_max_words": settings.conversion_cta_max_words,
        "headline_max_length": settings.conversion_headline_max_length,
        "min_testimonials": settings.conversion_min_testimonials,
        "ab_test_enabled": settings.conversion_ab_test_enabled,
        "power_words": conversion_config.CTA_POWER_WORDS,
        "urgency_words": conversion_config.CTA_URGENCY_WORDS,
        "psychological_triggers": conversion_config.PERSUASION_PRINCIPLES
    }


def get_performance_config() -> Dict[str, Any]:
    """Obtiene configuración de performance."""
    return {
        "min_score_threshold": settings.performance_min_score_threshold,
        "max_response_time_ms": settings.performance_max_response_time_ms,
        "cache_ttl": settings.performance_cache_ttl_seconds,
        "max_concurrent": settings.performance_max_concurrent_generations,
        "target_times": performance_config.TARGET_RESPONSE_TIMES,
        "cache_strategies": performance_config.CACHE_STRATEGIES,
        "rate_limits": performance_config.RATE_LIMITS
    }


if __name__ == "__main__":
    print("⚙️ ULTRA LANDING PAGE CONFIG LOADED")
    print("=" * 50)
    print(f"🌍 Environment: {settings.environment}")
    print(f"🤖 LangChain Model: {settings.langchain_model}")
    print(f"🔍 SEO Min Score: {settings.seo_min_score_threshold}")
    print(f"🎯 Conversion Min Score: {settings.conversion_min_score_threshold}")
    print(f"⚡ Performance Min Score: {settings.performance_min_score_threshold}")
    print(f"📊 Cache TTL: {settings.performance_cache_ttl_seconds}s")
    print(f"🚀 Ready for ultra-optimized landing pages!") 