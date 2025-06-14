"""
Model mapping between backend_ads and main backend models.
This file provides adapters to convert between the two model systems.
"""
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

# Import backend_ads models
from models import (
    AdsIaRequest,
    AdsResponse,
    BrandKitResponse,
    BrandVoice as AdsBrandVoice,
    AudienceProfile as AdsAudienceProfile,
    ProjectContext as AdsProjectContext,
    ContentSource as AdsContentSource,
    EmailTemplate as AdsEmailTemplate,
    EmailSequenceRequest as AdsEmailSequenceRequest,
    EmailSequenceResponse as AdsEmailSequenceResponse,
    EmailSequenceMetrics as AdsEmailSequenceMetrics,
    EmailSequenceSettings as AdsEmailSequenceSettings
)

# Import main backend models
from onyx.server.features.ads.api import (
    AdsRequest as MainAdsRequest,
    AdsResponse as MainAdsResponse,
    BrandVoice as MainBrandVoice,
    AudienceProfile as MainAudienceProfile,
    ProjectContext as MainProjectContext,
    ContentSource as MainContentSource,
    AdsGenerationRequest as MainAdsGenerationRequest,
    BackgroundRemovalRequest as MainBackgroundRemovalRequest,
    EmailSequenceMetrics as MainEmailSequenceMetrics,
    EmailSequenceSettings as MainEmailSequenceSettings
)

class ModelAdapter:
    """Adapter class to convert between backend_ads and main backend models."""
    
    @staticmethod
    def to_main_ads_request(ads_request: AdsIaRequest) -> MainAdsRequest:
        """Convert backend_ads AdsIaRequest to main backend AdsRequest."""
        return MainAdsRequest(
            url=ads_request.url,
            type=ads_request.type,
            prompt=ads_request.prompt
        )
    
    @staticmethod
    def to_ads_request(ads_request: MainAdsRequest) -> AdsIaRequest:
        """Convert main backend AdsRequest to backend_ads AdsIaRequest."""
        return AdsIaRequest(
            url=ads_request.url,
            type=ads_request.type,
            prompt=ads_request.prompt
        )
    
    @staticmethod
    def to_main_brand_voice(brand_voice: AdsBrandVoice) -> MainBrandVoice:
        """Convert backend_ads BrandVoice to main backend BrandVoice."""
        return MainBrandVoice(
            tone=brand_voice.tone,
            style=brand_voice.style,
            personality_traits=brand_voice.personality_traits,
            industry_specific_terms=brand_voice.industry_specific_terms,
            brand_guidelines=brand_voice.brand_guidelines
        )
    
    @staticmethod
    def to_brand_voice(brand_voice: MainBrandVoice) -> AdsBrandVoice:
        """Convert main backend BrandVoice to backend_ads BrandVoice."""
        return AdsBrandVoice(
            tone=brand_voice.tone,
            style=brand_voice.style,
            personality_traits=brand_voice.personality_traits,
            industry_specific_terms=brand_voice.industry_specific_terms,
            brand_guidelines=brand_voice.brand_guidelines
        )
    
    @staticmethod
    def to_main_audience_profile(profile: AdsAudienceProfile) -> MainAudienceProfile:
        """Convert backend_ads AudienceProfile to main backend AudienceProfile."""
        return MainAudienceProfile(
            demographics=profile.demographics,
            interests=profile.interests,
            pain_points=profile.pain_points,
            goals=profile.goals,
            buying_behavior=profile.buying_behavior,
            customer_stage=profile.customer_stage
        )
    
    @staticmethod
    def to_audience_profile(profile: MainAudienceProfile) -> AdsAudienceProfile:
        """Convert main backend AudienceProfile to backend_ads AudienceProfile."""
        return AdsAudienceProfile(
            demographics=profile.demographics,
            interests=profile.interests,
            pain_points=profile.pain_points,
            goals=profile.goals,
            buying_behavior=profile.buying_behavior,
            customer_stage=profile.customer_stage
        )
    
    @staticmethod
    def to_main_project_context(context: AdsProjectContext) -> MainProjectContext:
        """Convert backend_ads ProjectContext to main backend ProjectContext."""
        return MainProjectContext(
            project_name=context.project_name,
            project_description=context.project_description,
            industry=context.industry,
            key_messages=context.key_messages,
            brand_assets=context.brand_assets,
            content_sources=[
                ModelAdapter.to_main_content_source(cs)
                for cs in context.content_sources
            ],
            custom_variables=context.custom_variables
        )
    
    @staticmethod
    def to_project_context(context: MainProjectContext) -> AdsProjectContext:
        """Convert main backend ProjectContext to backend_ads ProjectContext."""
        return AdsProjectContext(
            project_name=context.project_name,
            project_description=context.project_description,
            industry=context.industry,
            key_messages=context.key_messages,
            brand_assets=context.brand_assets,
            content_sources=[
                ModelAdapter.to_content_source(cs)
                for cs in context.content_sources
            ],
            custom_variables=context.custom_variables
        )
    
    @staticmethod
    def to_main_content_source(source: AdsContentSource) -> MainContentSource:
        """Convert backend_ads ContentSource to main backend ContentSource."""
        return MainContentSource(
            type=source.type,
            content=source.content,
            priority=source.priority,
            relevance_score=source.relevance_score
        )
    
    @staticmethod
    def to_content_source(source: MainContentSource) -> AdsContentSource:
        """Convert main backend ContentSource to backend_ads ContentSource."""
        return AdsContentSource(
            type=source.type,
            content=source.content,
            priority=source.priority,
            relevance_score=source.relevance_score
        )
    
    @staticmethod
    def to_main_email_sequence_metrics(metrics: AdsEmailSequenceMetrics) -> MainEmailSequenceMetrics:
        """Convert backend_ads EmailSequenceMetrics to main backend EmailSequenceMetrics."""
        return MainEmailSequenceMetrics(
            sequence_id=metrics.sequence_id,
            total_sent=metrics.total_sent,
            opens=metrics.opens,
            clicks=metrics.clicks,
            conversions=metrics.conversions,
            bounces=metrics.bounces,
            unsubscribes=metrics.unsubscribes,
            revenue=metrics.revenue,
            last_updated=metrics.last_updated,
            engagement_score=metrics.engagement_score,
            delivery_rate=metrics.delivery_rate,
            spam_complaints=metrics.spam_complaints,
            device_stats=metrics.device_stats,
            location_stats=metrics.location_stats,
            time_stats=metrics.time_stats
        )
    
    @staticmethod
    def to_email_sequence_metrics(metrics: MainEmailSequenceMetrics) -> AdsEmailSequenceMetrics:
        """Convert main backend EmailSequenceMetrics to backend_ads EmailSequenceMetrics."""
        return AdsEmailSequenceMetrics(
            sequence_id=metrics.sequence_id,
            total_sent=metrics.total_sent,
            opens=metrics.opens,
            clicks=metrics.clicks,
            conversions=metrics.conversions,
            bounces=metrics.bounces,
            unsubscribes=metrics.unsubscribes,
            revenue=metrics.revenue,
            last_updated=metrics.last_updated,
            engagement_score=metrics.engagement_score,
            delivery_rate=metrics.delivery_rate,
            spam_complaints=metrics.spam_complaints,
            device_stats=metrics.device_stats,
            location_stats=metrics.location_stats,
            time_stats=metrics.time_stats
        )
    
    @staticmethod
    def to_main_email_sequence_settings(settings: AdsEmailSequenceSettings) -> MainEmailSequenceSettings:
        """Convert backend_ads EmailSequenceSettings to main backend EmailSequenceSettings."""
        return MainEmailSequenceSettings(
            sequence_id=settings.sequence_id,
            sender_name=settings.sender_name,
            reply_to_email=settings.reply_to_email,
            unsubscribe_link=settings.unsubscribe_link,
            double_opt_in=settings.double_opt_in,
            resend_failed_emails=settings.resend_failed_emails,
            max_retry_attempts=settings.max_retry_attempts,
            retry_delay_minutes=settings.retry_delay_minutes,
            custom_tracking_domain=settings.custom_tracking_domain,
            custom_branding=settings.custom_branding,
            compliance_settings=settings.compliance_settings
        )
    
    @staticmethod
    def to_email_sequence_settings(settings: MainEmailSequenceSettings) -> AdsEmailSequenceSettings:
        """Convert main backend EmailSequenceSettings to backend_ads EmailSequenceSettings."""
        return AdsEmailSequenceSettings(
            sequence_id=settings.sequence_id,
            sender_name=settings.sender_name,
            reply_to_email=settings.reply_to_email,
            unsubscribe_link=settings.unsubscribe_link,
            double_opt_in=settings.double_opt_in,
            resend_failed_emails=settings.resend_failed_emails,
            max_retry_attempts=settings.max_retry_attempts,
            retry_delay_minutes=settings.retry_delay_minutes,
            custom_tracking_domain=settings.custom_tracking_domain,
            custom_branding=settings.custom_branding,
            compliance_settings=settings.compliance_settings
        ) 