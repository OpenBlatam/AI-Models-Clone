"""
Servidor principal para Addiction Recovery AI
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

try:
    from api.recovery_api import router
    from config.settings import settings
    from middleware.logging_middleware import LoggingMiddleware
    from middleware.error_handler import ErrorHandlerMiddleware
    from middleware.performance import PerformanceMonitoringMiddleware
    from core.lifespan import lifespan
    from middleware.rate_limit import RateLimitMiddleware
    from config.app_config import get_config
    from utils.logging_config import setup_logging
except ImportError:
    # Para imports relativos
    from .api.recovery_api import router
    from .config.settings import settings
    from .middleware.logging_middleware import LoggingMiddleware
    from .middleware.error_handler import ErrorHandlerMiddleware
    from .middleware.performance import PerformanceMonitoringMiddleware
    from .core.lifespan import lifespan
    from .middleware.rate_limit import RateLimitMiddleware
    from .config.app_config import get_config
    from .utils.logging_config import setup_logging

# Get configuration first
config = get_config()

# Setup logging
setup_logging(
    level=config.log_level,
    format_string=config.log_format
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Addiction Recovery AI API",
    description="Sistema de IA para ayudar a dejar adicciones (cigarrillos, alcohol, drogas y otras dependencias)",
    version="3.3.0",
    lifespan=lifespan  # Use lifespan context manager instead of @app.on_event
)

# Customize OpenAPI schema
try:
    from api.openapi_customization import customize_openapi_schema
    app.openapi = lambda: customize_openapi_schema(app)
except ImportError:
    from .api.openapi_customization import customize_openapi_schema
    app.openapi = lambda: customize_openapi_schema(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=config.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add middleware in order (last added = first executed)
# Error handler should be first to catch all errors
app.add_middleware(ErrorHandlerMiddleware)

# Performance Optimizations (always enabled first)
try:
    from performance.async_optimizer import get_async_optimizer
    from performance.memory_optimizer import get_memory_optimizer
    from middleware.speed_middleware import SpeedMiddleware
    from middleware.ultra_speed_middleware import UltraSpeedMiddleware
    
    # Initialize async optimizer (enable uvloop)
    async_optimizer = get_async_optimizer()
    async_optimizer.enable_uvloop()
    
    # Initialize memory optimizer
    memory_optimizer = get_memory_optimizer()
    
    # Performance Integrator (integrates all optimizations)
    try:
        from middleware.performance_integrator import PerformanceIntegratorMiddleware
        redis_url = None
        try:
            redis_url = config.redis_url if hasattr(config, 'redis_url') else None
        except:
            pass
        
        app.add_middleware(
            PerformanceIntegratorMiddleware,
            enable_all=True,
            redis_url=redis_url
        )
        logger.info("✅ Performance integrator middleware enabled")
    except ImportError:
        pass
    
    # Ultra-speed middleware (highest priority - maximum performance)
    # Get Redis URL from config if available
    redis_url = None
    try:
        redis_url = config.redis_url if hasattr(config, 'redis_url') else None
    except:
        pass
    
    try:
        app.add_middleware(
            UltraSpeedMiddleware,
            redis_url=redis_url,
            enable_brotli=True,
            enable_coalescing=True,
            enable_prefetch=True
        )
        
        # Speed middleware (fallback optimizations)
        app.add_middleware(SpeedMiddleware)
    except ImportError:
        pass
except ImportError:
    pass

# AWS Observability (if running in AWS)
try:
    from config.aws_settings import get_aws_settings
    from middleware.aws_observability import AWSObservabilityMiddleware
    from middleware.opentelemetry_middleware import OpenTelemetryMiddleware
    from middleware.oauth2_middleware import OAuth2Middleware
    from middleware.performance_middleware import PerformanceMiddleware, ConnectionPoolMiddleware
    from middleware.security_advanced import SecurityHeadersMiddleware, DDoSProtectionMiddleware, InputValidationMiddleware
    from aws.prometheus_metrics import PrometheusMetricsMiddleware, get_metrics_endpoint
    from optimization.cold_start import init_cold_start
    from performance.warmup import initialize_warmup
    
    aws_settings = get_aws_settings()
    
    # Initialize cold start optimizations
    if aws_settings.is_lambda:
        init_cold_start()
    
    # Security middleware (always enabled)
    app.add_middleware(SecurityHeadersMiddleware, strict_csp=True)
    app.add_middleware(InputValidationMiddleware)
    app.add_middleware(DDoSProtectionMiddleware, requests_per_minute=60, requests_per_hour=1000)
    
    if aws_settings.is_lambda:
        # OpenTelemetry for distributed tracing
        app.add_middleware(OpenTelemetryMiddleware)
        # AWS CloudWatch observability
        app.add_middleware(AWSObservabilityMiddleware)
        # Prometheus metrics
        app.add_middleware(PrometheusMetricsMiddleware)
        # Performance optimizations
        app.add_middleware(PerformanceMiddleware, enable_compression=True)
        app.add_middleware(ConnectionPoolMiddleware)
        # OAuth2 authentication
        app.add_middleware(OAuth2Middleware, public_paths=[
            "/", "/docs", "/redoc", "/openapi.json",
            "/health", "/metrics",
            "/recovery/health",
            "/recovery/auth/login",
            "/recovery/auth/register"
        ])
        
        # Add Prometheus metrics endpoint
        from fastapi import APIRouter
        metrics_router = APIRouter()
        metrics_router.add_api_route("/metrics", get_metrics_endpoint(), methods=["GET"])
        app.include_router(metrics_router)
    else:
        # Performance middleware for non-Lambda deployments
        app.add_middleware(PerformanceMiddleware, enable_compression=True)
        app.add_middleware(ConnectionPoolMiddleware)
        
except ImportError:
    pass  # AWS middleware not available

# Warmup optimization (integrated in lifespan)
try:
    from performance.warmup import initialize_warmup
    # Will be called in lifespan startup
except ImportError:
    pass

# Intelligent Throttling (advanced rate limiting)
try:
    from middleware.throttling_middleware import ThrottlingMiddleware
    app.add_middleware(ThrottlingMiddleware)
except ImportError:
    # Fallback to basic rate limiting
    app.add_middleware(
        RateLimitMiddleware,
        requests_per_minute=config.rate_limit_per_minute,
        requests_per_hour=config.rate_limit_per_hour
    )
# Performance monitoring
app.add_middleware(PerformanceMonitoringMiddleware)
# Logging
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(router, prefix="/recovery", tags=["Recovery"])

# Include health check routers
try:
    from api.health import router as health_router
    from api.health_advanced import router as health_advanced_router
except ImportError:
    from .api.health import router as health_router
    from .api.health_advanced import router as health_advanced_router

app.include_router(health_router)
app.include_router(health_advanced_router)


@app.get("/")
async def root():
    """Endpoint raíz"""
    return {
        "service": "Addiction Recovery AI",
        "version": "1.0.0",
        "status": "running",
        "description": "Sistema de IA para ayudar a dejar adicciones",
        "endpoints": {
            "assessment": {
                "assess": "POST /recovery/assess",
                "profile": "GET /recovery/profile/{user_id}",
                "update_profile": "POST /recovery/update-profile"
            },
            "recovery_plans": {
                "create": "POST /recovery/create-plan",
                "get": "GET /recovery/plan/{user_id}",
                "update": "POST /recovery/update-plan",
                "strategies": "GET /recovery/strategies/{addiction_type}"
            },
            "progress": {
                "log_entry": "POST /recovery/log-entry",
                "get_progress": "GET /recovery/progress/{user_id}",
                "stats": "GET /recovery/stats/{user_id}",
                "timeline": "GET /recovery/timeline/{user_id}"
            },
            "relapse_prevention": {
                "check_risk": "POST /recovery/check-relapse-risk",
                "triggers": "GET /recovery/triggers/{user_id}",
                "coping_strategies": "POST /recovery/coping-strategies",
                "emergency_plan": "POST /recovery/emergency-plan"
            },
            "support": {
                "coaching": "POST /recovery/coaching-session",
                "motivation": "GET /recovery/motivation/{user_id}",
                "celebrate": "POST /recovery/celebrate-milestone",
                "achievements": "GET /recovery/achievements/{user_id}"
            },
            "analytics": {
                "analytics": "GET /recovery/analytics/{user_id}",
                "advanced_analytics": "GET /recovery/analytics/advanced/{user_id}",
                "report": "POST /recovery/generate-report",
                "insights": "GET /recovery/insights/{user_id}"
            },
            "notifications": {
                "get": "GET /recovery/notifications/{user_id}",
                "mark_read": "POST /recovery/notifications/{notification_id}/read",
                "reminders": "GET /recovery/reminders/{user_id}"
            },
            "users": {
                "create": "POST /recovery/users/create",
                "get": "GET /recovery/users/{user_id}"
            },
            "export": {
                "export_data": "GET /recovery/export/{user_id}?format=json|csv"
            },
            "auth": {
                "register": "POST /recovery/auth/register",
                "login": "POST /recovery/auth/login"
            },
            "reports": {
                "pdf": "GET /recovery/reports/pdf/{user_id}"
            },
            "gamification": {
                "points": "GET /recovery/gamification/points/{user_id}",
                "achievements": "GET /recovery/gamification/achievements/{user_id}",
                "leaderboard": "GET /recovery/gamification/leaderboard"
            },
            "emergency": {
                "create_contact": "POST /recovery/emergency/contact",
                "get_contacts": "GET /recovery/emergency/contacts/{user_id}",
                "trigger": "POST /recovery/emergency/trigger",
                "resources": "GET /recovery/emergency/resources"
            },
            "dashboard": {
                "get": "GET /recovery/dashboard/{user_id}"
            },
            "calendar": {
                "create_event": "POST /recovery/calendar/event",
                "upcoming": "GET /recovery/calendar/upcoming/{user_id}",
                "daily_reminders": "POST /recovery/calendar/daily-reminders/{user_id}"
            },
            "chatbot": {
                "message": "POST /recovery/chatbot/message",
                "start": "POST /recovery/chatbot/start",
                "history": "GET /recovery/chatbot/history/{user_id}"
            },
            "community": {
                "create_post": "POST /recovery/community/post",
                "get_posts": "GET /recovery/community/posts"
            },
            "predictive": {
                "relapse_risk": "POST /recovery/predictive/relapse-risk"
            },
            "health": {
                "record_metric": "POST /recovery/health/metric",
                "summary": "GET /recovery/health/summary/{user_id}"
            },
            "goals": {
                "create": "POST /recovery/goals/create",
                "get": "GET /recovery/goals/{user_id}"
            },
            "wearable": {
                "register": "POST /recovery/wearable/register"
            },
            "sentiment": {
                "analyze": "POST /recovery/sentiment/analyze",
                "journal_entry": "POST /recovery/sentiment/journal-entry",
                "trend": "GET /recovery/sentiment/trend/{user_id}"
            },
            "mentorship": {
                "request": "POST /recovery/mentorship/request",
                "available": "GET /recovery/mentorship/available"
            },
            "medication": {
                "add": "POST /recovery/medication/add",
                "schedule": "GET /recovery/medication/schedule/{user_id}"
            },
            "health_app": {
                "connect": "POST /recovery/health-app/connect",
                "sync": "POST /recovery/health-app/sync"
            },
            "push": {
                "register_device": "POST /recovery/push/register-device",
                "send": "POST /recovery/push/send"
            },
            "voice": {
                "analyze": "POST /recovery/voice/analyze"
            },
            "family": {
                "add_member": "POST /recovery/family/add-member",
                "dashboard": "GET /recovery/family/dashboard/{user_id}"
            },
            "alerts": {
                "evaluate": "POST /recovery/alerts/evaluate",
                "active": "GET /recovery/alerts/active/{user_id}"
            },
            "therapy": {
                "schedule": "POST /recovery/therapy/schedule",
                "therapists": "GET /recovery/therapy/therapists"
            },
            "visualization": {
                "progress_chart": "POST /recovery/visualization/progress-chart",
                "radar": "POST /recovery/visualization/radar"
            },
            "economy": {
                "earn_points": "POST /recovery/economy/earn-points",
                "balance": "GET /recovery/economy/balance/{user_id}",
                "rewards": "GET /recovery/economy/rewards"
            },
            "emergency": {
                "services": "GET /recovery/emergency/services",
                "crisis_resources": "GET /recovery/emergency/crisis-resources"
            },
            "withdrawal": {
                "record_symptom": "POST /recovery/withdrawal/record-symptom",
                "timeline": "GET /recovery/withdrawal/timeline/{user_id}"
            },
            "sleep": {
                "analyze_patterns": "POST /recovery/sleep/analyze-patterns",
                "correlate": "POST /recovery/sleep/correlate"
            },
            "challenges": {
                "create": "POST /recovery/challenges/create",
                "available": "GET /recovery/challenges/available/{user_id}"
            },
            "webhooks": {
                "register": "POST /recovery/webhooks/register",
                "get_user_webhooks": "GET /recovery/webhooks/{user_id}"
            },
            "certificates": {
                "generate": "POST /recovery/certificates/generate",
                "get_user_certificates": "GET /recovery/certificates/{user_id}"
            },
            "backup": {
                "create": "POST /recovery/backup/create",
                "restore": "POST /recovery/backup/restore"
            },
            "social": {
                "connect": "POST /recovery/social/connect",
                "share_milestone": "POST /recovery/social/share-milestone"
            },
            "nlp": {
                "analyze_text": "POST /recovery/nlp/analyze-text",
                "extract_insights": "POST /recovery/nlp/extract-insights"
            },
            "support_groups": {
                "create": "POST /recovery/support-groups/create",
                "search": "GET /recovery/support-groups/search"
            },
            "reports": {
                "comprehensive": "POST /recovery/reports/comprehensive",
                "export": "POST /recovery/reports/export"
            },
            "predictive": {
                "success_probability": "POST /recovery/predictive/success-probability",
                "relapse_window": "POST /recovery/predictive/relapse-window"
            },
            "recommendations": {
                "personalized": "POST /recovery/recommendations/personalized",
                "resources": "GET /recovery/recommendations/resources/{user_id}"
            },
            "habits": {
                "create": "POST /recovery/habits/create",
                "log_completion": "POST /recovery/habits/log-completion"
            },
            "mindfulness": {
                "start_session": "POST /recovery/mindfulness/start-session",
                "programs": "GET /recovery/mindfulness/programs/{user_id}"
            },
            "resources": {
                "library": "GET /recovery/resources/library",
                "search": "GET /recovery/resources/search"
            },
            "patterns": {
                "daily": "POST /recovery/patterns/daily",
                "weekly": "POST /recovery/patterns/weekly"
            },
            "financial": {
                "calculate_savings": "POST /recovery/financial/calculate-savings",
                "summary": "GET /recovery/financial/summary/{user_id}"
            },
            "reminders": {
                "create": "POST /recovery/reminders/create",
                "upcoming": "GET /recovery/reminders/upcoming/{user_id}"
            },
            "wellness": {
                "calculate_score": "POST /recovery/wellness/calculate-score",
                "trends": "POST /recovery/wellness/trends"
            },
            "relationships": {
                "add": "POST /recovery/relationships/add",
                "network": "GET /recovery/relationships/network/{user_id}"
            },
            "coaching": {
                "start_session": "POST /recovery/coaching/start-session",
                "send_message": "POST /recovery/coaching/send-message"
            },
            "integrations": {
                "connect": "POST /recovery/integrations/connect",
                "available": "GET /recovery/integrations/available"
            },
            "progress_advanced": {
                "visualization": "POST /recovery/progress/visualization",
                "comparison": "POST /recovery/progress/comparison"
            },
            "gamification_advanced": {
                "award_achievement": "POST /recovery/gamification/award-achievement",
                "user_level": "GET /recovery/gamification/user-level/{user_id}"
            },
            "analysis_advanced": {
                "comprehensive": "POST /recovery/analysis/comprehensive",
                "behavioral_patterns": "POST /recovery/analysis/behavioral-patterns"
            },
            "long_term_goals": {
                "create": "POST /recovery/long-term-goals/create",
                "update_progress": "POST /recovery/long-term-goals/update-progress"
            },
            "risk_advanced": {
                "assessment": "POST /recovery/risk/assessment",
                "predict_relapse": "POST /recovery/risk/predict-relapse"
            },
            "metrics_advanced": {
                "kpis": "POST /recovery/metrics/kpis",
                "dashboard": "GET /recovery/metrics/dashboard/{user_id}"
            },
            "notifications_intelligent": {
                "create": "POST /recovery/notifications/intelligent",
                "preferences": "GET /recovery/notifications/preferences/{user_id}"
            },
            "medication_advanced": {
                "add": "POST /recovery/medication/advanced/add",
                "adherence": "GET /recovery/medication/advanced/adherence/{medication_id}"
            },
            "iot": {
                "register_device": "POST /recovery/iot/register-device",
                "health_metrics": "GET /recovery/iot/health-metrics/{user_id}"
            },
            "voice_advanced": {
                "analyze": "POST /recovery/voice/advanced/analyze",
                "detect_stress": "POST /recovery/voice/advanced/detect-stress"
            },
            "location": {
                "add": "POST /recovery/location/add",
                "check_proximity": "POST /recovery/location/check-proximity"
            },
            "image": {
                "analyze_emotions": "POST /recovery/image/analyze-emotions"
            },
            "sleep_advanced": {
                "record": "POST /recovery/sleep/advanced/record",
                "analyze_patterns": "POST /recovery/sleep/advanced/analyze-patterns"
            },
            "ml_learning": {
                "train_model": "POST /recovery/ml/train-model",
                "predict": "POST /recovery/ml/predict"
            },
            "predictive_ml": {
                "recovery_trajectory": "POST /recovery/predictive-ml/recovery-trajectory",
                "long_term_outcome": "POST /recovery/predictive-ml/long-term-outcome"
            },
            "blockchain": {
                "mint_nft": "POST /recovery/blockchain/mint-nft",
                "create_certificate": "POST /recovery/blockchain/create-certificate"
            },
            "realtime_events": {
                "log": "POST /recovery/events/log",
                "recent": "GET /recovery/events/recent/{user_id}"
            },
            "social_media": {
                "analyze": "POST /recovery/social-media/analyze",
                "detect_triggers": "POST /recovery/social-media/detect-triggers"
            },
            "ml_recommendations": {
                "get": "POST /recovery/ml-recommendations/get",
                "collaborative": "POST /recovery/ml-recommendations/collaborative"
            },
            "vr_ar_therapy": {
                "create_session": "POST /recovery/vr-ar/create-session",
                "scenarios": "GET /recovery/vr-ar/scenarios"
            },
            "biometrics": {
                "record": "POST /recovery/biometrics/record",
                "analyze_trends": "POST /recovery/biometrics/analyze-trends"
            },
            "voice_assistant": {
                "register": "POST /recovery/voice-assistant/register",
                "process_command": "POST /recovery/voice-assistant/process-command"
            },
            "purchases": {
                "record": "POST /recovery/purchases/record",
                "analyze_patterns": "POST /recovery/purchases/analyze-patterns"
            },
            "relationships": {
                "add": "POST /recovery/relationships/add",
                "analyze_network": "POST /recovery/relationships/analyze-network"
            },
            "productivity": {
                "record_work": "POST /recovery/productivity/record-work",
                "analyze_work_patterns": "POST /recovery/productivity/analyze-work-patterns"
            },
            "nutrition": {
                "record_meal": "POST /recovery/nutrition/record-meal",
                "analyze_patterns": "POST /recovery/nutrition/analyze-patterns"
            },
            "exercise": {
                "record_session": "POST /recovery/exercise/record-session",
                "analyze_patterns": "POST /recovery/exercise/analyze-patterns"
            },
            "meditation": {
                "connect_app": "POST /recovery/meditation/connect-app",
                "analyze_impact": "POST /recovery/meditation/analyze-impact"
            },
            "environment": {
                "record_context": "POST /recovery/environment/record-context",
                "predict_risk": "POST /recovery/environment/predict-risk"
            },
            "habits": {
                "create": "POST /recovery/habits/create",
                "analyze_performance": "POST /recovery/habits/analyze-performance"
            },
            "temporal": {
                "analyze_daily_patterns": "POST /recovery/temporal/analyze-daily-patterns",
                "analyze_weekly_patterns": "POST /recovery/temporal/analyze-weekly-patterns"
            },
            "genetic": {
                "analyze": "POST /recovery/genetic/analyze",
                "predict_risk": "POST /recovery/genetic/predict-risk"
            },
            "medical_devices": {
                "register": "POST /recovery/medical-devices/register",
                "analyze_data": "POST /recovery/medical-devices/analyze-data"
            },
            "visual_progress": {
                "generate": "POST /recovery/visual-progress/generate",
                "create_timeline": "POST /recovery/visual-progress/create-timeline"
            },
            "ehr": {
                "connect": "POST /recovery/ehr/connect",
                "medical_history": "GET /recovery/ehr/medical-history/{user_id}"
            },
            "correlations": {
                "analyze_multivariate": "POST /recovery/correlations/analyze-multivariate"
            },
            "prediction": {
                "long_term_success": "POST /recovery/prediction/long-term-success",
                "milestone_achievement": "POST /recovery/prediction/milestone-achievement"
            },
            "behavioral": {
                "analyze_patterns": "POST /recovery/behavioral/analyze-patterns",
                "detect_anomalies": "POST /recovery/behavioral/detect-anomalies"
            },
            "telemedicine": {
                "schedule_session": "POST /recovery/telemedicine/schedule-session",
                "available_providers": "GET /recovery/telemedicine/available-providers/{user_id}"
            },
            "alerts": {
                "create": "POST /recovery/alerts/create",
                "evaluate_conditions": "POST /recovery/alerts/evaluate-conditions"
            },
            "adherence": {
                "calculate_rate": "POST /recovery/adherence/calculate-rate",
                "predict_risk": "POST /recovery/adherence/predict-risk"
            },
            "symptoms": {
                "record": "POST /recovery/symptoms/record",
                "analyze_patterns": "POST /recovery/symptoms/analyze-patterns"
            },
            "quality_of_life": {
                "assess": "POST /recovery/quality-of-life/assess",
                "analyze_trends": "POST /recovery/quality-of-life/analyze-trends"
            },
            "neural_network": {
                "train": "POST /recovery/neural-network/train",
                "predict": "POST /recovery/neural-network/predict"
            },
            "monitoring": {
                "start_continuous": "POST /recovery/monitoring/start-continuous",
                "realtime_metrics": "GET /recovery/monitoring/realtime-metrics/{user_id}"
            },
            "ai_sleep": {
                "analyze": "POST /recovery/ai-sleep/analyze",
                "predict_quality": "POST /recovery/ai-sleep/predict-quality"
            },
            "emotions": {
                "record": "POST /recovery/emotions/record",
                "analyze_patterns": "POST /recovery/emotions/analyze-patterns"
            },
            "voice_emotion": {
                "analyze": "POST /recovery/voice-emotion/analyze",
                "detect_risk": "POST /recovery/voice-emotion/detect-risk"
            },
            "wellness": {
                "connect_app": "POST /recovery/wellness/connect-app",
                "analyze_impact": "POST /recovery/wellness/analyze-impact"
            },
            "activity_patterns": {
                "analyze": "POST /recovery/activity-patterns/analyze",
                "predict_outcome": "POST /recovery/activity-patterns/predict-outcome"
            },
            "health_devices": {
                "register": "POST /recovery/health-devices/register",
                "record_reading": "POST /recovery/health-devices/record-reading"
            },
            "coaching": {
                "create_plan": "POST /recovery/coaching/create-plan",
                "provide_session": "POST /recovery/coaching/provide-session"
            },
            "social_network": {
                "analyze": "POST /recovery/social-network/analyze",
                "predict_influence": "POST /recovery/social-network/predict-influence"
            },
            "goals": {
                "create_advanced": "POST /recovery/goals/create-advanced",
                "analyze_performance": "POST /recovery/goals/analyze-performance"
            },
            "comparative": {
                "compare_periods": "POST /recovery/comparative/compare-periods",
                "compare_with_baseline": "POST /recovery/comparative/compare-with-baseline"
            },
            "resilience": {
                "assess": "POST /recovery/resilience/assess",
                "predict_outcome": "POST /recovery/resilience/predict-outcome"
            },
            "rewards": {
                "award": "POST /recovery/rewards/award",
                "analyze_impact": "POST /recovery/rewards/analyze-impact"
            },
            "alternative_therapy": {
                "recommend": "POST /recovery/alternative-therapy/recommend",
                "track_session": "POST /recovery/alternative-therapy/track-session"
            },
            "motivation": {
                "assess": "POST /recovery/motivation/assess",
                "predict_drop": "POST /recovery/motivation/predict-drop"
            },
            "relapse": {
                "record": "POST /recovery/relapse/record",
                "predict_risk": "POST /recovery/relapse/predict-risk"
            },
            "barriers": {
                "identify": "POST /recovery/barriers/identify",
                "suggest_solutions": "POST /recovery/barriers/suggest-solutions"
            },
            "stress": {
                "assess": "POST /recovery/stress/assess",
                "predict_episode": "POST /recovery/stress/predict-episode"
            },
            "social_support": {
                "assess": "POST /recovery/social-support/assess",
                "recommend_resources": "POST /recovery/social-support/recommend-resources"
            },
            "emergency": {
                "trigger": "POST /recovery/emergency/trigger",
                "resources": "POST /recovery/emergency/resources"
            },
            "visual_progress": {
                "generate_timeline": "POST /recovery/visual-progress/generate-timeline",
                "create_chart": "POST /recovery/visual-progress/create-chart"
            },
            "medications": {
                "register": "POST /recovery/medications/register",
                "analyze_adherence": "POST /recovery/medications/analyze-adherence"
            },
            "sleep_patterns": {
                "analyze": "POST /recovery/sleep-patterns/analyze",
                "correlate_with_recovery": "POST /recovery/sleep-patterns/correlate-with-recovery"
            },
            "wellness": {
                "assess_comprehensive": "POST /recovery/wellness/assess-comprehensive"
            },
            "reminders": {
                "create_intelligent": "POST /recovery/reminders/create-intelligent",
                "optimize_timing": "POST /recovery/reminders/optimize-timing"
            },
            "health_devices_advanced": {
                "register": "POST /recovery/health-devices-advanced/register",
                "analyze_data": "POST /recovery/health-devices-advanced/analyze-data"
            },
            "habits": {
                "analyze": "POST /recovery/habits/analyze"
            },
            "exercise": {
                "analyze_patterns": "POST /recovery/exercise/analyze-patterns"
            },
            "nutrition": {
                "analyze_patterns": "POST /recovery/nutrition/analyze-patterns",
                "assess_adequacy": "POST /recovery/nutrition/assess-adequacy"
            },
            "long_term_progress": {
                "analyze": "POST /recovery/long-term-progress/analyze",
                "predict_outcome": "POST /recovery/long-term-progress/predict-outcome"
            },
            "achievements": {
                "award": "POST /recovery/achievements/award",
                "check_eligibility": "POST /recovery/achievements/check-eligibility"
            },
            "group_therapy": {
                "find_groups": "POST /recovery/group-therapy/find-groups",
                "track_participation": "POST /recovery/group-therapy/track-participation"
            },
            "mood": {
                "analyze_patterns": "POST /recovery/mood/analyze-patterns",
                "predict_episode": "POST /recovery/mood/predict-episode"
            },
            "therapy": {
                "track_session": "POST /recovery/therapy/track-session",
                "recommend_adjustments": "POST /recovery/therapy/recommend-adjustments"
            },
            "relationships": {
                "analyze": "POST /recovery/relationships/analyze",
                "assess_impact": "POST /recovery/relationships/assess-impact"
            },
            "health_check": "GET /recovery/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/recovery/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Addiction Recovery AI",
        "version": "3.3.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8018)

