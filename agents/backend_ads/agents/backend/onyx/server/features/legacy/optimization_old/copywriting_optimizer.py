"""
Copywriting Optimizer - Advanced AI Content Enhancement.

Advanced optimization system for copywriting with A/B testing,
performance analytics, and automated content enhancement.
"""

import asyncio
import time
import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import numpy as np

import structlog
from .copywriting_model import (
    CopywritingModel, ContentRequest, GeneratedContent, 
    ContentType, ContentTone, ContentAnalyzer, create_copywriting_model
)
from .optimization import FastHasher, optimize_performance
from .performance_optimizers import ultra_optimize

logger = structlog.get_logger(__name__)


@dataclass
class OptimizationRule:
    """Rule for content optimization."""
    name: str
    condition: str
    action: str
    priority: int
    impact_score: float


@dataclass
class A_B_TestResult:
    """Result of A/B testing."""
    variant_a: GeneratedContent
    variant_b: GeneratedContent
    winner: str  # 'A', 'B', or 'tie'
    confidence: float
    improvement_percentage: float
    metrics_comparison: Dict[str, Any]


class ContentOptimizerEngine:
    """Advanced content optimization engine."""
    
    def __init__(self):
        self.optimization_rules = self._load_optimization_rules()
        self.analyzer = ContentAnalyzer()
        
    def _load_optimization_rules(self) -> List[OptimizationRule]:
        """Load predefined optimization rules."""
        return [
            OptimizationRule(
                name="Improve Readability",
                condition="readability_score < 60",
                action="simplify_language",
                priority=1,
                impact_score=0.8
            ),
            OptimizationRule(
                name="Strengthen CTA",
                condition="call_to_action_strength < 0.5",
                action="enhance_call_to_action",
                priority=2,
                impact_score=0.9
            ),
            OptimizationRule(
                name="Add Emotional Triggers",
                condition="len(emotional_triggers) < 2",
                action="add_emotional_words",
                priority=3,
                impact_score=0.7
            ),
            OptimizationRule(
                name="Optimize Length",
                condition="word_count > max_length * 1.2",
                action="reduce_length",
                priority=4,
                impact_score=0.6
            ),
            OptimizationRule(
                name="Enhance Engagement",
                condition="engagement_prediction < 0.7",
                action="add_engagement_elements",
                priority=5,
                impact_score=0.8
            )
        ]
    
    @ultra_optimize(enable_caching=True, monitor_performance=True)
    async def optimize_content(self, content: str, target_metrics: Dict[str, float] = None) -> str:
        """Optimize content based on rules and target metrics."""
        current_metrics = await self.analyzer.analyze_content(content)
        
        optimized_content = content
        applied_optimizations = []
        
        for rule in sorted(self.optimization_rules, key=lambda x: x.priority):
            if self._should_apply_rule(rule, current_metrics, target_metrics):
                optimized_content = await self._apply_optimization(optimized_content, rule)
                applied_optimizations.append(rule.name)
        
        if applied_optimizations:
            logger.info(f"Applied optimizations: {', '.join(applied_optimizations)}")
        
        return optimized_content
    
    def _should_apply_rule(self, rule: OptimizationRule, metrics, target_metrics) -> bool:
        """Check if optimization rule should be applied."""
        # Simplified rule evaluation (in production, this would be more sophisticated)
        if "readability_score" in rule.condition and metrics.readability_score < 60:
            return True
        elif "call_to_action_strength" in rule.condition and metrics.call_to_action_strength < 0.5:
            return True
        elif "emotional_triggers" in rule.condition and len(metrics.emotional_triggers) < 2:
            return True
        elif "engagement_prediction" in rule.condition and metrics.engagement_prediction < 0.7:
            return True
        
        return False
    
    async def _apply_optimization(self, content: str, rule: OptimizationRule) -> str:
        """Apply specific optimization rule."""
        if rule.action == "simplify_language":
            return self._simplify_language(content)
        elif rule.action == "enhance_call_to_action":
            return self._enhance_call_to_action(content)
        elif rule.action == "add_emotional_words":
            return self._add_emotional_words(content)
        elif rule.action == "reduce_length":
            return self._reduce_length(content)
        elif rule.action == "add_engagement_elements":
            return self._add_engagement_elements(content)
        
        return content
    
    def _simplify_language(self, content: str) -> str:
        """Simplify language for better readability."""
        # Replace complex words with simpler alternatives
        replacements = {
            "utilize": "use",
            "facilitate": "help",
            "implement": "do",
            "demonstrate": "show",
            "optimize": "improve",
            "enhance": "make better",
            "substantial": "large",
            "comprehensive": "complete"
        }
        
        simplified = content
        for complex_word, simple_word in replacements.items():
            simplified = re.sub(rf'\b{complex_word}\b', simple_word, simplified, flags=re.IGNORECASE)
        
        return simplified
    
    def _enhance_call_to_action(self, content: str) -> str:
        """Enhance call-to-action in content."""
        # Add stronger CTA verbs
        strong_ctas = [
            "Start now", "Get instant access", "Claim your spot", 
            "Take action today", "Don't miss out", "Join thousands"
        ]
        
        # Look for weak CTAs and strengthen them
        weak_patterns = [
            r'\blearn more\b',
            r'\bclick here\b',
            r'\bfind out\b',
            r'\bcheck it out\b'
        ]
        
        enhanced = content
        for pattern in weak_patterns:
            if re.search(pattern, enhanced, re.IGNORECASE):
                import random
                strong_cta = random.choice(strong_ctas)
                enhanced = re.sub(pattern, strong_cta, enhanced, flags=re.IGNORECASE, count=1)
                break
        
        return enhanced
    
    def _add_emotional_words(self, content: str) -> str:
        """Add emotional trigger words."""
        emotional_words = {
            'positive': ['amazing', 'incredible', 'breakthrough', 'revolutionary', 'exclusive'],
            'urgency': ['limited time', 'don\'t wait', 'act fast', 'hurry', 'expires soon'],
            'social_proof': ['proven', 'trusted by thousands', 'bestselling', 'award-winning']
        }
        
        # Add one emotional word if none present
        words_present = any(
            word.lower() in content.lower() 
            for category in emotional_words.values() 
            for word in category
        )
        
        if not words_present:
            import random
            category = random.choice(list(emotional_words.keys()))
            word = random.choice(emotional_words[category])
            
            # Insert at the beginning
            content = f"{word.title()} - {content}"
        
        return content
    
    def _reduce_length(self, content: str) -> str:
        """Reduce content length while preserving meaning."""
        # Remove unnecessary words
        unnecessary_words = [
            r'\bvery\b', r'\breally\b', r'\bquite\b', r'\bjust\b',
            r'\bthat\b(?=\s+is)', r'\bwhich\s+is\b'
        ]
        
        reduced = content
        for pattern in unnecessary_words:
            reduced = re.sub(pattern, '', reduced, flags=re.IGNORECASE)
        
        # Clean up extra spaces
        reduced = re.sub(r'\s+', ' ', reduced).strip()
        
        return reduced
    
    def _add_engagement_elements(self, content: str) -> str:
        """Add elements to increase engagement."""
        # Add question or direct address
        if '?' not in content and 'you' not in content.lower():
            # Add direct address
            content = f"You deserve {content.lower()}"
        
        return content


class AdvancedA_B_Tester:
    """Advanced A/B testing for copywriting."""
    
    def __init__(self):
        self.copywriting_model = create_copywriting_model()
        self.optimizer = ContentOptimizerEngine()
        
    @ultra_optimize(enable_caching=True, monitor_performance=True)
    async def run_ab_test(
        self, 
        request: ContentRequest, 
        test_variants: int = 2,
        optimization_strategies: List[str] = None
    ) -> A_B_TestResult:
        """Run advanced A/B test with multiple strategies."""
        
        # Generate base content (Variant A)
        variant_a = await self.copywriting_model.create_content(request)
        
        # Generate optimized variant (Variant B)
        optimized_request = self._create_optimized_request(request, optimization_strategies)
        variant_b = await self.copywriting_model.create_content(optimized_request)
        
        # If variant B is similar to A, apply manual optimization
        if self._calculate_content_similarity(variant_a.content, variant_b.content) > 0.9:
            variant_b.content = await self.optimizer.optimize_content(variant_a.content)
            # Re-analyze the optimized content
            variant_b.metrics = await self.optimizer.analyzer.analyze_content(variant_b.content)
        
        # Compare variants
        winner, confidence, improvement = self._compare_variants(variant_a, variant_b)
        
        return A_B_TestResult(
            variant_a=variant_a,
            variant_b=variant_b,
            winner=winner,
            confidence=confidence,
            improvement_percentage=improvement,
            metrics_comparison=self._create_metrics_comparison(variant_a, variant_b)
        )
    
    def _create_optimized_request(self, original_request: ContentRequest, strategies: List[str]) -> ContentRequest:
        """Create optimized request for variant B."""
        optimized_request = original_request.copy()
        
        strategies = strategies or ["tone_variation", "urgency_boost"]
        
        for strategy in strategies:
            if strategy == "tone_variation":
                # Try a different tone
                tone_alternatives = {
                    ContentTone.PROFESSIONAL: ContentTone.FRIENDLY,
                    ContentTone.CASUAL: ContentTone.PLAYFUL,
                    ContentTone.URGENT: ContentTone.EMOTIONAL,
                    ContentTone.FRIENDLY: ContentTone.AUTHORITATIVE
                }
                optimized_request.tone = tone_alternatives.get(original_request.tone, ContentTone.PROFESSIONAL)
            
            elif strategy == "urgency_boost":
                optimized_request.urgency_level = min(5, original_request.urgency_level + 1)
                if "limited" not in optimized_request.key_message.lower():
                    optimized_request.key_message = f"Limited time: {optimized_request.key_message}"
            
            elif strategy == "personalization":
                if "you" not in optimized_request.key_message.lower():
                    optimized_request.key_message = f"You can {optimized_request.key_message.lower()}"
        
        return optimized_request
    
    def _calculate_content_similarity(self, content_a: str, content_b: str) -> float:
        """Calculate similarity between two content pieces."""
        # Simple word-based similarity
        words_a = set(content_a.lower().split())
        words_b = set(content_b.lower().split())
        
        intersection = words_a.intersection(words_b)
        union = words_a.union(words_b)
        
        return len(intersection) / len(union) if union else 0
    
    def _compare_variants(self, variant_a: GeneratedContent, variant_b: GeneratedContent) -> Tuple[str, float, float]:
        """Compare variants and determine winner."""
        if not variant_a.metrics or not variant_b.metrics:
            return "tie", 0.5, 0.0
        
        # Calculate composite score for each variant
        score_a = self._calculate_composite_score(variant_a.metrics)
        score_b = self._calculate_composite_score(variant_b.metrics)
        
        # Determine winner
        if score_b > score_a * 1.05:  # 5% improvement threshold
            winner = "B"
            confidence = min(0.95, (score_b - score_a) / score_a + 0.6)
            improvement = ((score_b - score_a) / score_a) * 100
        elif score_a > score_b * 1.05:
            winner = "A"
            confidence = min(0.95, (score_a - score_b) / score_b + 0.6)
            improvement = ((score_a - score_b) / score_b) * 100
        else:
            winner = "tie"
            confidence = 0.5
            improvement = 0.0
        
        return winner, confidence, improvement
    
    def _calculate_composite_score(self, metrics) -> float:
        """Calculate composite score from metrics."""
        # Weighted combination of different metrics
        weights = {
            'readability_score': 0.2,
            'engagement_prediction': 0.4,
            'call_to_action_strength': 0.25,
            'sentiment_score': 0.15
        }
        
        score = 0.0
        score += (metrics.readability_score / 100) * weights['readability_score']
        score += metrics.engagement_prediction * weights['engagement_prediction']
        score += metrics.call_to_action_strength * weights['call_to_action_strength']
        score += ((metrics.sentiment_score + 1) / 2) * weights['sentiment_score']  # Normalize sentiment
        
        return score
    
    def _create_metrics_comparison(self, variant_a: GeneratedContent, variant_b: GeneratedContent) -> Dict[str, Any]:
        """Create detailed metrics comparison."""
        if not variant_a.metrics or not variant_b.metrics:
            return {}
        
        return {
            "readability": {
                "variant_a": variant_a.metrics.readability_score,
                "variant_b": variant_b.metrics.readability_score,
                "improvement": variant_b.metrics.readability_score - variant_a.metrics.readability_score
            },
            "engagement": {
                "variant_a": variant_a.metrics.engagement_prediction,
                "variant_b": variant_b.metrics.engagement_prediction,
                "improvement": variant_b.metrics.engagement_prediction - variant_a.metrics.engagement_prediction
            },
            "cta_strength": {
                "variant_a": variant_a.metrics.call_to_action_strength,
                "variant_b": variant_b.metrics.call_to_action_strength,
                "improvement": variant_b.metrics.call_to_action_strength - variant_a.metrics.call_to_action_strength
            },
            "content_length": {
                "variant_a": variant_a.metrics.word_count,
                "variant_b": variant_b.metrics.word_count,
                "difference": variant_b.metrics.word_count - variant_a.metrics.word_count
            }
        }


class CopywritingPerformanceAnalyzer:
    """Analyze copywriting performance and provide insights."""
    
    def __init__(self):
        self.performance_history = []
        
    async def analyze_performance_trends(self, generated_contents: List[GeneratedContent]) -> Dict[str, Any]:
        """Analyze performance trends from generated content."""
        if not generated_contents:
            return {"error": "No content provided for analysis"}
        
        # Group by content type and tone
        performance_by_type = {}
        performance_by_tone = {}
        
        for content in generated_contents:
            content_type = content.content_type.value
            tone = content.tone.value
            
            if content_type not in performance_by_type:
                performance_by_type[content_type] = []
            if tone not in performance_by_tone:
                performance_by_tone[tone] = []
            
            if content.metrics:
                metrics_dict = {
                    'generation_time': content.generation_time_ms,
                    'readability': content.metrics.readability_score,
                    'engagement': content.metrics.engagement_prediction,
                    'cta_strength': content.metrics.call_to_action_strength,
                    'word_count': content.metrics.word_count
                }
                
                performance_by_type[content_type].append(metrics_dict)
                performance_by_tone[tone].append(metrics_dict)
        
        # Calculate averages and trends
        type_analysis = {}
        for content_type, metrics_list in performance_by_type.items():
            if metrics_list:
                type_analysis[content_type] = {
                    'avg_generation_time': np.mean([m['generation_time'] for m in metrics_list]),
                    'avg_readability': np.mean([m['readability'] for m in metrics_list]),
                    'avg_engagement': np.mean([m['engagement'] for m in metrics_list]),
                    'avg_cta_strength': np.mean([m['cta_strength'] for m in metrics_list]),
                    'avg_word_count': np.mean([m['word_count'] for m in metrics_list]),
                    'total_generated': len(metrics_list)
                }
        
        tone_analysis = {}
        for tone, metrics_list in performance_by_tone.items():
            if metrics_list:
                tone_analysis[tone] = {
                    'avg_generation_time': np.mean([m['generation_time'] for m in metrics_list]),
                    'avg_readability': np.mean([m['readability'] for m in metrics_list]),
                    'avg_engagement': np.mean([m['engagement'] for m in metrics_list]),
                    'avg_cta_strength': np.mean([m['cta_strength'] for m in metrics_list]),
                    'total_generated': len(metrics_list)
                }
        
        # Identify best performers
        best_type = max(type_analysis.items(), key=lambda x: x[1]['avg_engagement']) if type_analysis else None
        best_tone = max(tone_analysis.items(), key=lambda x: x[1]['avg_engagement']) if tone_analysis else None
        
        return {
            "summary": {
                "total_content_analyzed": len(generated_contents),
                "avg_generation_time": np.mean([c.generation_time_ms for c in generated_contents]),
                "best_performing_type": best_type[0] if best_type else None,
                "best_performing_tone": best_tone[0] if best_tone else None
            },
            "performance_by_type": type_analysis,
            "performance_by_tone": tone_analysis,
            "recommendations": self._generate_recommendations(type_analysis, tone_analysis)
        }
    
    def _generate_recommendations(self, type_analysis: Dict, tone_analysis: Dict) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        
        if type_analysis:
            # Find fastest generating content type
            fastest_type = min(type_analysis.items(), key=lambda x: x[1]['avg_generation_time'])
            recommendations.append(f"Fastest generation: {fastest_type[0]} content type")
            
            # Find most engaging content type
            most_engaging = max(type_analysis.items(), key=lambda x: x[1]['avg_engagement'])
            recommendations.append(f"Highest engagement: {most_engaging[0]} content type")
        
        if tone_analysis:
            # Find most effective tone
            best_tone = max(tone_analysis.items(), key=lambda x: x[1]['avg_engagement'])
            recommendations.append(f"Most effective tone: {best_tone[0]}")
        
        return recommendations


# Factory function
def create_copywriting_optimizer() -> ContentOptimizerEngine:
    """Create copywriting optimizer instance."""
    return ContentOptimizerEngine()


def create_ab_tester() -> AdvancedA_B_Tester:
    """Create A/B tester instance."""
    return AdvancedA_B_Tester()


def create_performance_analyzer() -> CopywritingPerformanceAnalyzer:
    """Create performance analyzer instance."""
    return CopywritingPerformanceAnalyzer()


# Export components
__all__ = [
    "ContentOptimizerEngine",
    "AdvancedA_B_Tester",
    "CopywritingPerformanceAnalyzer",
    "OptimizationRule",
    "A_B_TestResult",
    "create_copywriting_optimizer",
    "create_ab_tester", 
    "create_performance_analyzer"
] 