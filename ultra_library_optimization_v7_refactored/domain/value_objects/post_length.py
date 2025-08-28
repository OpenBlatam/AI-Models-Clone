#!/usr/bin/env python3
"""
Post Length Value Object - Domain Layer
======================================

Immutable value object representing the length of a LinkedIn post.
"""

from enum import Enum
from typing import Tuple


class PostLength(Enum):
    """
    Immutable value object for post length.
    
    This value object encapsulates the length of a LinkedIn post and provides
    domain-specific logic for length validation and processing.
    """
    
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTENDED = "extended"
    
    @classmethod
    def get_all_lengths(cls) -> list['PostLength']:
        """Get all available lengths"""
        return list(cls)
    
    def get_character_range(self) -> Tuple[int, int]:
        """Get character range for this length"""
        ranges = {
            self.SHORT: (50, 200),
            self.MEDIUM: (200, 800),
            self.LONG: (800, 1500),
            self.EXTENDED: (1500, 3000)
        }
        return ranges.get(self, (0, 0))
    
    def get_min_characters(self) -> int:
        """Get minimum characters for this length"""
        return self.get_character_range()[0]
    
    def get_max_characters(self) -> int:
        """Get maximum characters for this length"""
        return self.get_character_range()[1]
    
    def get_optimal_characters(self) -> int:
        """Get optimal character count for this length"""
        min_chars, max_chars = self.get_character_range()
        return (min_chars + max_chars) // 2
    
    def is_within_range(self, character_count: int) -> bool:
        """Check if character count is within range for this length"""
        min_chars, max_chars = self.get_character_range()
        return min_chars <= character_count <= max_chars
    
    def get_engagement_optimization(self) -> float:
        """Get engagement optimization factor for this length"""
        optimizations = {
            self.SHORT: 1.2,    # Short posts often get higher engagement
            self.MEDIUM: 1.0,   # Medium is baseline
            self.LONG: 0.9,     # Long posts may have lower engagement
            self.EXTENDED: 0.8   # Extended posts have lowest engagement
        }
        return optimizations.get(self, 1.0)
    
    def get_read_time_minutes(self) -> float:
        """Get estimated read time in minutes"""
        read_times = {
            self.SHORT: 0.5,
            self.MEDIUM: 1.5,
            self.LONG: 3.0,
            self.EXTENDED: 5.0
        }
        return read_times.get(self, 1.0)
    
    def get_complexity_score(self) -> float:
        """Get complexity score for this length"""
        complexity_scores = {
            self.SHORT: 0.3,
            self.MEDIUM: 0.6,
            self.LONG: 0.8,
            self.EXTENDED: 1.0
        }
        return complexity_scores.get(self, 0.5)
    
    def get_usage_recommendations(self) -> list[str]:
        """Get usage recommendations for this length"""
        recommendations = {
            self.SHORT: [
                "Perfect for quick updates and announcements",
                "Great for sharing links with brief commentary",
                "Ideal for engaging questions and polls",
                "Best for high-frequency posting"
            ],
            self.MEDIUM: [
                "Optimal for sharing insights and tips",
                "Great for storytelling and case studies",
                "Perfect for educational content",
                "Ideal for thought leadership posts"
            ],
            self.LONG: [
                "Best for in-depth analysis and tutorials",
                "Great for comprehensive case studies",
                "Perfect for detailed industry insights",
                "Ideal for educational series"
            ],
            self.EXTENDED: [
                "Best for comprehensive guides and tutorials",
                "Great for detailed industry analysis",
                "Perfect for educational content series",
                "Ideal for thought leadership deep-dives"
            ]
        }
        return recommendations.get(self, [])
    
    def get_formatting_tips(self) -> list[str]:
        """Get formatting tips for this length"""
        tips = {
            self.SHORT: [
                "Use bullet points for clarity",
                "Keep sentences concise",
                "Use emojis sparingly",
                "Focus on one key message"
            ],
            self.MEDIUM: [
                "Use paragraphs for readability",
                "Include subheadings if needed",
                "Use bullet points for lists",
                "Balance text with white space"
            ],
            self.LONG: [
                "Use clear section breaks",
                "Include subheadings throughout",
                "Use bullet points and numbered lists",
                "Add visual breaks with emojis or symbols"
            ],
            self.EXTENDED: [
                "Use clear section headers",
                "Break content into digestible chunks",
                "Use bullet points and numbered lists extensively",
                "Include call-to-action sections"
            ]
        }
        return tips.get(self, [])
    
    def get_hashtag_recommendations(self) -> int:
        """Get recommended number of hashtags for this length"""
        hashtag_counts = {
            self.SHORT: 2,
            self.MEDIUM: 5,
            self.LONG: 8,
            self.EXTENDED: 12
        }
        return hashtag_counts.get(self, 3)
    
    def get_optimal_structure(self) -> dict[str, any]:
        """Get optimal content structure for this length"""
        structures = {
            self.SHORT: {
                "intro": "10%",
                "main_content": "70%",
                "conclusion": "20%",
                "hashtags": "inline"
            },
            self.MEDIUM: {
                "intro": "15%",
                "main_content": "60%",
                "conclusion": "25%",
                "hashtags": "end"
            },
            self.LONG: {
                "intro": "20%",
                "main_content": "55%",
                "conclusion": "25%",
                "hashtags": "end"
            },
            self.EXTENDED: {
                "intro": "25%",
                "main_content": "50%",
                "conclusion": "25%",
                "hashtags": "end"
            }
        }
        return structures.get(self, {})
    
    def __str__(self) -> str:
        """String representation"""
        return self.value
    
    def __repr__(self) -> str:
        """Detailed representation"""
        return f"PostLength.{self.name}"
    
    def __eq__(self, other: object) -> bool:
        """Compare lengths"""
        if not isinstance(other, PostLength):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash based on value"""
        return hash(self.value) 