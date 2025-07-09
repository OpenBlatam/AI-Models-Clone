"""
Email Sequence Models

This module contains all the data models for the email sequence system.
"""

from .sequence import EmailSequence, SequenceStep, SequenceTrigger
from .template import EmailTemplate, TemplateVariable
from .campaign import EmailCampaign, CampaignMetrics
from .subscriber import Subscriber, SubscriberSegment

__all__ = [
    "EmailSequence",
    "SequenceStep", 
    "SequenceTrigger",
    "EmailTemplate",
    "TemplateVariable",
    "EmailCampaign",
    "CampaignMetrics",
    "Subscriber",
    "SubscriberSegment"
] 