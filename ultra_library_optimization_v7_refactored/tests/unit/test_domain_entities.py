#!/usr/bin/env python3
"""
Unit Tests for Domain Entities
==============================

Comprehensive unit tests for domain entities and value objects.
"""

import pytest
import asyncio
from datetime import datetime
from uuid import uuid4

from domain.entities.linkedin_post import LinkedInPost
from domain.value_objects.post_tone import PostTone
from domain.value_objects.post_length import PostLength
from domain.value_objects.optimization_strategy import OptimizationStrategy


class TestPostTone:
    """Test cases for PostTone value object."""
    
    def test_post_tone_creation(self):
        """Test creating PostTone instances."""
        tone = PostTone.PROFESSIONAL
        assert tone.value == "professional"
        assert str(tone) == "professional"
    
    def test_post_tone_equality(self):
        """Test PostTone equality."""
        tone1 = PostTone.PROFESSIONAL
        tone2 = PostTone.PROFESSIONAL
        tone3 = PostTone.CASUAL
        
        assert tone1 == tone2
        assert tone1 != tone3
        assert hash(tone1) == hash(tone2)
    
    def test_post_tone_classification(self):
        """Test PostTone classification methods."""
        professional = PostTone.PROFESSIONAL
        casual = PostTone.CASUAL
        inspirational = PostTone.INSPIRATIONAL
        
        assert professional.is_formal()
        assert not casual.is_formal()
        assert inspirational.is_engaging()
    
    def test_post_tone_engagement_multiplier(self):
        """Test PostTone engagement multiplier."""
        professional = PostTone.PROFESSIONAL
        humorous = PostTone.HUMOROUS
        
        assert professional.get_engagement_multiplier() == 1.0
        assert humorous.get_engagement_multiplier() == 1.6
    
    def test_post_tone_characteristics(self):
        """Test PostTone characteristics."""
        professional = PostTone.PROFESSIONAL
        characteristics = professional.get_characteristics()
        
        assert "formal" in characteristics
        assert "business-like" in characteristics
        assert len(characteristics) > 0
    
    def test_post_tone_usage_tips(self):
        """Test PostTone usage tips."""
        professional = PostTone.PROFESSIONAL
        tips = professional.get_usage_tips()
        
        assert len(tips) > 0
        assert all(isinstance(tip, str) for tip in tips)
    
    def test_get_all_tones(self):
        """Test getting all available tones."""
        all_tones = PostTone.get_all_tones()
        assert len(all_tones) > 0
        assert all(isinstance(tone, PostTone) for tone in all_tones)
    
    def test_get_formal_tones(self):
        """Test getting formal tones."""
        formal_tones = PostTone.get_formal_tones()
        assert len(formal_tones) > 0
        assert all(tone.is_formal() for tone in formal_tones)
    
    def test_get_casual_tones(self):
        """Test getting casual tones."""
        casual_tones = PostTone.get_casual_tones()
        assert len(casual_tones) > 0
        assert all(tone.is_casual() for tone in casual_tones)
    
    def test_get_engaging_tones(self):
        """Test getting engaging tones."""
        engaging_tones = PostTone.get_engaging_tones()
        assert len(engaging_tones) > 0
        assert all(tone.is_engaging() for tone in engaging_tones)


class TestPostLength:
    """Test cases for PostLength value object."""
    
    def test_post_length_creation(self):
        """Test creating PostLength instances."""
        length = PostLength.MEDIUM
        assert length.value == "medium"
        assert str(length) == "medium"
    
    def test_post_length_equality(self):
        """Test PostLength equality."""
        length1 = PostLength.MEDIUM
        length2 = PostLength.MEDIUM
        length3 = PostLength.LONG
        
        assert length1 == length2
        assert length1 != length3
        assert hash(length1) == hash(length2)
    
    def test_post_length_character_range(self):
        """Test PostLength character range."""
        short = PostLength.SHORT
        medium = PostLength.MEDIUM
        long = PostLength.LONG
        extended = PostLength.EXTENDED
        
        assert short.get_character_range() == (50, 200)
        assert medium.get_character_range() == (200, 800)
        assert long.get_character_range() == (800, 1500)
        assert extended.get_character_range() == (1500, 3000)
    
    def test_post_length_within_range(self):
        """Test PostLength range validation."""
        medium = PostLength.MEDIUM
        min_chars, max_chars = medium.get_character_range()
        
        assert medium.is_within_range(min_chars)
        assert medium.is_within_range(max_chars)
        assert medium.is_within_range((min_chars + max_chars) // 2)
        assert not medium.is_within_range(min_chars - 1)
        assert not medium.is_within_range(max_chars + 1)
    
    def test_post_length_engagement_optimization(self):
        """Test PostLength engagement optimization."""
        short = PostLength.SHORT
        medium = PostLength.MEDIUM
        long = PostLength.LONG
        
        assert short.get_engagement_optimization() == 1.2
        assert medium.get_engagement_optimization() == 1.0
        assert long.get_engagement_optimization() == 0.9
    
    def test_post_length_read_time(self):
        """Test PostLength read time."""
        short = PostLength.SHORT
        medium = PostLength.MEDIUM
        long = PostLength.LONG
        
        assert short.get_read_time_minutes() == 0.5
        assert medium.get_read_time_minutes() == 1.5
        assert long.get_read_time_minutes() == 3.0
    
    def test_post_length_complexity_score(self):
        """Test PostLength complexity score."""
        short = PostLength.SHORT
        medium = PostLength.MEDIUM
        long = PostLength.LONG
        
        assert short.get_complexity_score() == 0.3
        assert medium.get_complexity_score() == 0.6
        assert long.get_complexity_score() == 0.8
    
    def test_post_length_usage_recommendations(self):
        """Test PostLength usage recommendations."""
        medium = PostLength.MEDIUM
        recommendations = medium.get_usage_recommendations()
        
        assert len(recommendations) > 0
        assert all(isinstance(rec, str) for rec in recommendations)
    
    def test_post_length_formatting_tips(self):
        """Test PostLength formatting tips."""
        medium = PostLength.MEDIUM
        tips = medium.get_formatting_tips()
        
        assert len(tips) > 0
        assert all(isinstance(tip, str) for tip in tips)
    
    def test_post_length_hashtag_recommendations(self):
        """Test PostLength hashtag recommendations."""
        short = PostLength.SHORT
        medium = PostLength.MEDIUM
        long = PostLength.LONG
        
        assert short.get_hashtag_recommendations() == 2
        assert medium.get_hashtag_recommendations() == 5
        assert long.get_hashtag_recommendations() == 8
    
    def test_post_length_optimal_structure(self):
        """Test PostLength optimal structure."""
        medium = PostLength.MEDIUM
        structure = medium.get_optimal_structure()
        
        assert "intro" in structure
        assert "main_content" in structure
        assert "conclusion" in structure
        assert "hashtags" in structure
    
    def test_get_all_lengths(self):
        """Test getting all available lengths."""
        all_lengths = PostLength.get_all_lengths()
        assert len(all_lengths) > 0
        assert all(isinstance(length, PostLength) for length in all_lengths)


class TestOptimizationStrategy:
    """Test cases for OptimizationStrategy value object."""
    
    def test_optimization_strategy_creation(self):
        """Test creating OptimizationStrategy instances."""
        strategy = OptimizationStrategy.QUANTUM
        assert strategy.value == "quantum"
        assert str(strategy) == "quantum"
    
    def test_optimization_strategy_equality(self):
        """Test OptimizationStrategy equality."""
        strategy1 = OptimizationStrategy.QUANTUM
        strategy2 = OptimizationStrategy.QUANTUM
        strategy3 = OptimizationStrategy.NEUROMORPHIC
        
        assert strategy1 == strategy2
        assert strategy1 != strategy3
        assert hash(strategy1) == hash(strategy2)
    
    def test_optimization_strategy_classification(self):
        """Test OptimizationStrategy classification methods."""
        quantum = OptimizationStrategy.QUANTUM
        neuromorphic = OptimizationStrategy.NEUROMORPHIC
        ai_self_healing = OptimizationStrategy.AI_SELF_HEALING
        
        assert quantum.is_quantum_based()
        assert neuromorphic.is_neuromorphic_based()
        assert ai_self_healing.is_ai_based()
        assert quantum.is_advanced()
    
    def test_optimization_strategy_performance_multiplier(self):
        """Test OptimizationStrategy performance multiplier."""
        default = OptimizationStrategy.DEFAULT
        quantum = OptimizationStrategy.QUANTUM
        hybrid = OptimizationStrategy.HYBRID
        
        assert default.get_performance_multiplier() == 1.0
        assert quantum.get_performance_multiplier() == 1.5
        assert hybrid.get_performance_multiplier() == 2.0
    
    def test_optimization_strategy_complexity_score(self):
        """Test OptimizationStrategy complexity score."""
        default = OptimizationStrategy.DEFAULT
        quantum = OptimizationStrategy.QUANTUM
        quantum_internet = OptimizationStrategy.QUANTUM_INTERNET
        
        assert default.get_complexity_score() == 0.1
        assert quantum.get_complexity_score() == 0.8
        assert quantum_internet.get_complexity_score() == 1.0
    
    def test_optimization_strategy_resource_requirements(self):
        """Test OptimizationStrategy resource requirements."""
        default = OptimizationStrategy.DEFAULT
        quantum = OptimizationStrategy.QUANTUM
        
        default_reqs = default.get_resource_requirements()
        quantum_reqs = quantum.get_resource_requirements()
        
        assert "cpu" in default_reqs
        assert "memory" in default_reqs
        assert "gpu" in default_reqs
        assert "quantum" in default_reqs
        assert "neuromorphic" in default_reqs
        
        assert default_reqs["cpu"] == "low"
        assert quantum_reqs["cpu"] == "medium"
    
    def test_optimization_strategy_processing_time_estimate(self):
        """Test OptimizationStrategy processing time estimate."""
        default = OptimizationStrategy.DEFAULT
        quantum = OptimizationStrategy.QUANTUM
        
        assert default.get_processing_time_estimate() == 100.0
        assert quantum.get_processing_time_estimate() == 500.0
    
    def test_optimization_strategy_accuracy_estimate(self):
        """Test OptimizationStrategy accuracy estimate."""
        default = OptimizationStrategy.DEFAULT
        quantum = OptimizationStrategy.QUANTUM
        
        assert default.get_accuracy_estimate() == 0.7
        assert quantum.get_accuracy_estimate() == 0.85
    
    def test_optimization_strategy_description(self):
        """Test OptimizationStrategy description."""
        quantum = OptimizationStrategy.QUANTUM
        description = quantum.get_description()
        
        assert isinstance(description, str)
        assert len(description) > 0
        assert "quantum" in description.lower()
    
    def test_optimization_strategy_use_cases(self):
        """Test OptimizationStrategy use cases."""
        quantum = OptimizationStrategy.QUANTUM
        use_cases = quantum.get_use_cases()
        
        assert len(use_cases) > 0
        assert all(isinstance(use_case, str) for use_case in use_cases)
    
    def test_get_all_strategies(self):
        """Test getting all available strategies."""
        all_strategies = OptimizationStrategy.get_all_strategies()
        assert len(all_strategies) > 0
        assert all(isinstance(strategy, OptimizationStrategy) for strategy in all_strategies)
    
    def test_get_quantum_strategies(self):
        """Test getting quantum-based strategies."""
        quantum_strategies = OptimizationStrategy.get_quantum_strategies()
        assert len(quantum_strategies) > 0
        assert all(strategy.is_quantum_based() for strategy in quantum_strategies)
    
    def test_get_neuromorphic_strategies(self):
        """Test getting neuromorphic-based strategies."""
        neuromorphic_strategies = OptimizationStrategy.get_neuromorphic_strategies()
        assert len(neuromorphic_strategies) > 0
        assert all(strategy.is_neuromorphic_based() for strategy in neuromorphic_strategies)
    
    def test_get_ai_strategies(self):
        """Test getting AI-based strategies."""
        ai_strategies = OptimizationStrategy.get_ai_strategies()
        assert len(ai_strategies) > 0
        assert all(strategy.is_ai_based() for strategy in ai_strategies)
    
    def test_get_advanced_strategies(self):
        """Test getting advanced strategies."""
        advanced_strategies = OptimizationStrategy.get_advanced_strategies()
        assert len(advanced_strategies) > 0
        assert all(strategy.is_advanced() for strategy in advanced_strategies)


class TestLinkedInPost:
    """Test cases for LinkedInPost entity."""
    
    def test_linkedin_post_creation(self):
        """Test creating LinkedInPost instances."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content for LinkedIn post.",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        assert post.topic == "Test Topic"
        assert post.content == "Test content for LinkedIn post."
        assert post.tone == PostTone.PROFESSIONAL
        assert post.length == PostLength.MEDIUM
        assert post.optimization_strategy == OptimizationStrategy.DEFAULT
        assert post.optimization_score == 0.0
        assert len(post.hashtags) == 0
        assert post.call_to_action is None
    
    def test_linkedin_post_validation(self):
        """Test LinkedInPost validation."""
        # Test empty topic
        with pytest.raises(ValueError, match="Topic cannot be empty"):
            LinkedInPost(
                topic="",
                content="Test content",
                tone=PostTone.PROFESSIONAL,
                length=PostLength.MEDIUM
            )
        
        # Test empty content
        with pytest.raises(ValueError, match="Content cannot be empty"):
            LinkedInPost(
                topic="Test Topic",
                content="",
                tone=PostTone.PROFESSIONAL,
                length=PostLength.MEDIUM
            )
        
        # Test content too long
        long_content = "x" * 3001
        with pytest.raises(ValueError, match="Content exceeds LinkedIn character limit"):
            LinkedInPost(
                topic="Test Topic",
                content=long_content,
                tone=PostTone.PROFESSIONAL,
                length=PostLength.MEDIUM
            )
    
    def test_linkedin_post_hashtag_operations(self):
        """Test LinkedInPost hashtag operations."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        # Add hashtags
        post.add_hashtag("AI")
        post.add_hashtag("Business")
        post.add_hashtag("Innovation")
        
        assert len(post.hashtags) == 3
        assert "#AI" in post.hashtags
        assert "#Business" in post.hashtags
        assert "#Innovation" in post.hashtags
        
        # Remove hashtag
        post.remove_hashtag("#AI")
        assert len(post.hashtags) == 2
        assert "#AI" not in post.hashtags
    
    def test_linkedin_post_call_to_action(self):
        """Test LinkedInPost call to action."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.set_call_to_action("What do you think?")
        assert post.call_to_action == "What do you think?"
    
    def test_linkedin_post_content_update(self):
        """Test LinkedInPost content update."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Original content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.update_content("Updated content")
        assert post.content == "Updated content"
        
        # Test validation
        with pytest.raises(ValueError, match="Content cannot be empty"):
            post.update_content("")
        
        with pytest.raises(ValueError, match="Content exceeds LinkedIn character limit"):
            post.update_content("x" * 3001)
    
    def test_linkedin_post_optimization(self):
        """Test LinkedInPost optimization application."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        metadata = {"strategy": "quantum", "score": 0.85}
        post.apply_optimization(OptimizationStrategy.QUANTUM, 0.85, metadata)
        
        assert post.optimization_strategy == OptimizationStrategy.QUANTUM
        assert post.optimization_score == 0.85
        assert post.optimization_metadata["strategy"] == "quantum"
    
    def test_linkedin_post_performance_metrics(self):
        """Test LinkedInPost performance metrics."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.set_performance_metrics(100.0, 200.0, True)
        
        assert post.generation_time_ms == 100.0
        assert post.optimization_time_ms == 200.0
        assert post.cache_hit is True
    
    def test_linkedin_post_total_length(self):
        """Test LinkedInPost total length calculation."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.add_hashtag("AI")
        post.set_call_to_action("What do you think?")
        
        total_length = post.get_total_length()
        expected_length = len("Test content") + len("#AI") + len("What do you think?")
        assert total_length == expected_length
    
    def test_linkedin_post_engagement_score(self):
        """Test LinkedInPost engagement score calculation."""
        post = LinkedInPost(
            topic="Test Topic",
            content="This is a medium-length post with good content for engagement testing.",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.add_hashtag("AI")
        post.add_hashtag("Business")
        post.add_hashtag("Innovation")
        post.set_call_to_action("What do you think?")
        post.apply_optimization(OptimizationStrategy.QUANTUM, 0.8, {})
        
        score = post.get_engagement_score()
        assert 0.0 <= score <= 1.0
    
    def test_linkedin_post_ready_for_posting(self):
        """Test LinkedInPost ready for posting check."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        # Should not be ready initially (low optimization score)
        assert not post.is_ready_for_posting()
        
        # Apply optimization to make it ready
        post.apply_optimization(OptimizationStrategy.QUANTUM, 0.8, {})
        assert post.is_ready_for_posting()
    
    def test_linkedin_post_serialization(self):
        """Test LinkedInPost serialization."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post.add_hashtag("AI")
        post.set_call_to_action("What do you think?")
        post.apply_optimization(OptimizationStrategy.QUANTUM, 0.8, {"test": "data"})
        
        # Test to_dict
        post_dict = post.to_dict()
        assert post_dict["topic"] == "Test Topic"
        assert post_dict["tone"] == "professional"
        assert post_dict["hashtags"] == ["#AI"]
        assert post_dict["call_to_action"] == "What do you think?"
        assert post_dict["optimization_score"] == 0.8
        assert post_dict["ready_for_posting"] is True
        
        # Test to_json
        post_json = post.to_json()
        assert isinstance(post_json, str)
        assert "Test Topic" in post_json
    
    def test_linkedin_post_deserialization(self):
        """Test LinkedInPost deserialization."""
        original_post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        original_post.add_hashtag("AI")
        original_post.set_call_to_action("What do you think?")
        original_post.apply_optimization(OptimizationStrategy.QUANTUM, 0.8, {"test": "data"})
        
        # Convert to dict and back
        post_dict = original_post.to_dict()
        restored_post = LinkedInPost.from_dict(post_dict)
        
        assert restored_post.topic == original_post.topic
        assert restored_post.content == original_post.content
        assert restored_post.tone == original_post.tone
        assert restored_post.length == original_post.length
        assert restored_post.hashtags == original_post.hashtags
        assert restored_post.call_to_action == original_post.call_to_action
        assert restored_post.optimization_strategy == original_post.optimization_strategy
        assert restored_post.optimization_score == original_post.optimization_score
    
    def test_linkedin_post_equality(self):
        """Test LinkedInPost equality."""
        post1 = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        post2 = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        # Different IDs, so not equal
        assert post1 != post2
        assert hash(post1) != hash(post2)
    
    def test_linkedin_post_string_representation(self):
        """Test LinkedInPost string representation."""
        post = LinkedInPost(
            topic="Test Topic",
            content="Test content",
            tone=PostTone.PROFESSIONAL,
            length=PostLength.MEDIUM
        )
        
        str_repr = str(post)
        repr_repr = repr(post)
        
        assert "LinkedInPost" in str_repr
        assert "Test Topic" in str_repr
        assert "LinkedInPost" in repr_repr
        assert "Test Topic" in repr_repr


if __name__ == "__main__":
    pytest.main([__file__]) 