#!/usr/bin/env python3
"""
Post Tone Value Object - Domain Layer
=====================================

Immutable value object representing the tone of a LinkedIn post.
"""

from enum import Enum
from typing import List


class PostTone(Enum):
    """
    Immutable value object for post tone.
    
    This value object encapsulates the tone of a LinkedIn post and provides
    domain-specific logic for tone validation and processing.
    """
    
    PROFESSIONAL = "professional"
    CASUAL = "casual"
    FRIENDLY = "friendly"
    AUTHORITATIVE = "authoritative"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    CONVERSATIONAL = "conversational"
    HUMOROUS = "humorous"
    MOTIVATIONAL = "motivational"
    ANALYTICAL = "analytical"
    
    @classmethod
    def get_all_tones(cls) -> List['PostTone']:
        """Get all available tones"""
        return list(cls)
    
    @classmethod
    def get_formal_tones(cls) -> List['PostTone']:
        """Get formal tones suitable for business context"""
        return [
            cls.PROFESSIONAL,
            cls.AUTHORITATIVE,
            cls.EDUCATIONAL,
            cls.ANALYTICAL
        ]
    
    @classmethod
    def get_casual_tones(cls) -> List['PostTone']:
        """Get casual tones suitable for personal branding"""
        return [
            cls.CASUAL,
            cls.FRIENDLY,
            cls.CONVERSATIONAL,
            cls.HUMOROUS
        ]
    
    @classmethod
    def get_engaging_tones(cls) -> List['PostTone']:
        """Get tones that drive engagement"""
        return [
            cls.INSPIRATIONAL,
            cls.MOTIVATIONAL,
            cls.CONVERSATIONAL,
            cls.FRIENDLY
        ]
    
    def is_formal(self) -> bool:
        """Check if tone is formal"""
        return self in self.get_formal_tones()
    
    def is_casual(self) -> bool:
        """Check if tone is casual"""
        return self in self.get_casual_tones()
    
    def is_engaging(self) -> bool:
        """Check if tone is engaging"""
        return self in self.get_engaging_tones()
    
    def get_engagement_multiplier(self) -> float:
        """Get engagement multiplier for this tone"""
        multipliers = {
            self.PROFESSIONAL: 1.0,
            self.CASUAL: 1.2,
            self.FRIENDLY: 1.3,
            self.AUTHORITATIVE: 1.1,
            self.INSPIRATIONAL: 1.5,
            self.EDUCATIONAL: 1.2,
            self.CONVERSATIONAL: 1.4,
            self.HUMOROUS: 1.6,
            self.MOTIVATIONAL: 1.4,
            self.ANALYTICAL: 0.9
        }
        return multipliers.get(self, 1.0)
    
    def get_characteristics(self) -> List[str]:
        """Get characteristics of this tone"""
        characteristics = {
            self.PROFESSIONAL: ["formal", "business-like", "credible", "trustworthy"],
            self.CASUAL: ["relaxed", "approachable", "conversational", "friendly"],
            self.FRIENDLY: ["warm", "welcoming", "supportive", "encouraging"],
            self.AUTHORITATIVE: ["confident", "expert", "knowledgeable", "leadership"],
            self.INSPIRATIONAL: ["motivating", "uplifting", "visionary", "aspirational"],
            self.EDUCATIONAL: ["informative", "helpful", "teaching", "enlightening"],
            self.CONVERSATIONAL: ["natural", "dialogue-like", "interactive", "engaging"],
            self.HUMOROUS: ["funny", "entertaining", "light-hearted", "memorable"],
            self.MOTIVATIONAL: ["encouraging", "energizing", "action-oriented", "empowering"],
            self.ANALYTICAL: ["data-driven", "logical", "systematic", "evidence-based"]
        }
        return characteristics.get(self, [])
    
    def get_usage_tips(self) -> List[str]:
        """Get usage tips for this tone"""
        tips = {
            self.PROFESSIONAL: [
                "Use industry-specific terminology",
                "Maintain formal language",
                "Focus on expertise and credibility",
                "Avoid slang or colloquialisms"
            ],
            self.CASUAL: [
                "Use conversational language",
                "Include personal anecdotes",
                "Keep it light and approachable",
                "Use contractions naturally"
            ],
            self.FRIENDLY: [
                "Show genuine interest in others",
                "Use inclusive language",
                "Offer support and encouragement",
                "Be warm and welcoming"
            ],
            self.AUTHORITATIVE: [
                "Demonstrate expertise clearly",
                "Use confident language",
                "Provide actionable insights",
                "Establish thought leadership"
            ],
            self.INSPIRATIONAL: [
                "Share compelling stories",
                "Use powerful, uplifting language",
                "Focus on possibilities and growth",
                "Connect emotionally with audience"
            ],
            self.EDUCATIONAL: [
                "Break down complex concepts",
                "Provide practical examples",
                "Use clear, accessible language",
                "Focus on learning and growth"
            ],
            self.CONVERSATIONAL: [
                "Write as you speak",
                "Ask questions to engage readers",
                "Use natural dialogue flow",
                "Encourage interaction"
            ],
            self.HUMOROUS: [
                "Use wit and cleverness",
                "Share relatable experiences",
                "Keep humor professional",
                "Make content memorable"
            ],
            self.MOTIVATIONAL: [
                "Focus on action and results",
                "Use energizing language",
                "Provide clear next steps",
                "Inspire confidence and determination"
            ],
            self.ANALYTICAL: [
                "Present data and facts clearly",
                "Use logical structure",
                "Provide evidence-based insights",
                "Focus on objective analysis"
            ]
        }
        return tips.get(self, [])
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"PostTone.{self.name}"
    
    def __eq__(self, other: object) -> bool:
        """Compare tones"""
        if not isinstance(other, PostTone):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash based on value"""
        return hash(self.value) 