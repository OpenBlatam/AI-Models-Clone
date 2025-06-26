"""
NLP-Enhanced Blog Engine - Ultra High Quality with Advanced NLP.

This module enhances the existing ultra blog engine with advanced NLP
techniques to achieve maximum content quality and engagement.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio

from .nlp_integration import NLPIntegration, NLPAnalysisResult
from .ultra_blog_engine import UltraBlogEngine
from .quality_optimizer import QualityOptimizer
from .speed_optimizer import SpeedOptimizer

logger = logging.getLogger(__name__)

class NLPEnhancedBlogEngine:
    """
    Ultra-fast blog engine enhanced with advanced NLP capabilities.
    
    Combines the speed of the ultra blog engine with comprehensive
    NLP analysis to produce the highest quality content possible.
    """
    
    def __init__(self, enable_nlp: bool = True, enable_auto_enhancement: bool = True):
        """
        Initialize the NLP-enhanced blog engine.
        
        Args:
            enable_nlp: Enable NLP analysis and enhancements
            enable_auto_enhancement: Automatically enhance content based on NLP analysis
        """
        self.enable_nlp = enable_nlp
        self.enable_auto_enhancement = enable_auto_enhancement
        
        # Initialize core engines
        self.ultra_engine = UltraBlogEngine()
        self.quality_optimizer = QualityOptimizer()
        self.speed_optimizer = SpeedOptimizer()
        
        # Initialize NLP components
        if self.enable_nlp:
            self.nlp_integration = NLPIntegration()
        else:
            self.nlp_integration = None
        
        logger.info(
            f"NLP-Enhanced Blog Engine initialized. "
            f"NLP enabled: {enable_nlp}, "
            f"Auto-enhancement: {enable_auto_enhancement}"
        )
    
    async def generate_ultra_nlp_blog(
        self,
        topic: str,
        target_keywords: Optional[List[str]] = None,
        content_type: str = "blog_post",
        quality_target: float = 95.0,
        max_iterations: int = 3
    ) -> Dict[str, Any]:
        """
        Generate ultra-high quality blog with NLP optimization.
        
        Args:
            topic: Blog topic
            target_keywords: Target SEO keywords
            content_type: Type of content to generate
            quality_target: Target quality score (0-100)
            max_iterations: Maximum optimization iterations
            
        Returns:
            Dict with blog content and comprehensive analysis
        """
        start_time = datetime.now()
        
        logger.info(
            f"Starting ultra-NLP blog generation for topic: '{topic}'. "
            f"Quality target: {quality_target}/100"
        )
        
        # Initial blog generation using ultra engine
        initial_result = await self.ultra_engine.generate_blog_ultra_mode(
            topic=topic,
            mode="PREMIUM"  # Start with high quality
        )
        
        # Extract initial content
        content = initial_result.get('content', '')
        title = initial_result.get('title', '')
        meta_description = initial_result.get('meta_description', '')
        
        # NLP analysis and enhancement loop
        final_content = content
        final_title = title
        final_meta = meta_description
        nlp_analysis = None
        enhancement_history = []
        
        if self.enable_nlp and self.nlp_integration:
            for iteration in range(max_iterations):
                logger.info(f"NLP enhancement iteration {iteration + 1}/{max_iterations}")
                
                # Analyze current content
                nlp_analysis = self.nlp_integration.analyze_content(
                    content=final_content,
                    title=final_title,
                    keywords=target_keywords
                )
                
                # Check if quality target is met
                if nlp_analysis.overall_quality >= quality_target:
                    logger.info(f"Quality target reached: {nlp_analysis.overall_quality:.1f}/100")
                    break
                
                # Auto-enhance if enabled
                if self.enable_auto_enhancement:
                    enhanced_result = await self._enhance_content_with_nlp(
                        content=final_content,
                        title=final_title,
                        meta_description=final_meta,
                        nlp_analysis=nlp_analysis,
                        target_keywords=target_keywords
                    )
                    
                    if enhanced_result['improved']:
                        final_content = enhanced_result['content']
                        final_title = enhanced_result.get('title', final_title)
                        final_meta = enhanced_result.get('meta_description', final_meta)
                        enhancement_history.append(enhanced_result['improvements'])
                    else:
                        break
                else:
                    break
        
        # Final analysis
        if self.nlp_integration:
            final_nlp_analysis = self.nlp_integration.analyze_content(
                content=final_content,
                title=final_title,
                keywords=target_keywords
            )
        else:
            final_nlp_analysis = None
        
        # Calculate performance metrics
        generation_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Compile final result
        result = {
            'content': final_content,
            'title': final_title,
            'meta_description': final_meta,
            'generation_time_ms': generation_time,
            'nlp_analysis': final_nlp_analysis,
            'quality_score': final_nlp_analysis.overall_quality if final_nlp_analysis else 85.0,
            'enhancements_applied': len(enhancement_history),
            'enhancement_history': enhancement_history,
            'target_keywords': target_keywords,
            'ultra_engine_result': initial_result,
            'mode': 'NLP_ENHANCED_ULTRA'
        }
        
        logger.info(
            f"Ultra-NLP blog generation completed in {generation_time:.2f}ms. "
            f"Final quality: {result['quality_score']:.1f}/100. "
            f"Enhancements: {result['enhancements_applied']}"
        )
        
        return result
    
    async def _enhance_content_with_nlp(
        self,
        content: str,
        title: str,
        meta_description: str,
        nlp_analysis: NLPAnalysisResult,
        target_keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Enhance content based on NLP analysis recommendations.
        
        Args:
            content: Current content
            title: Current title
            meta_description: Current meta description
            nlp_analysis: NLP analysis results
            target_keywords: Target keywords
            
        Returns:
            Dict with enhanced content and improvement details
        """
        enhanced_content = content
        enhanced_title = title
        enhanced_meta = meta_description
        improvements = []
        improved = False
        
        try:
            # Readability improvements
            if nlp_analysis.readability_score < 70:
                enhanced_content = self._improve_readability(enhanced_content)
                improvements.append("Improved readability")
                improved = True
            
            # Sentiment improvements
            if nlp_analysis.sentiment_score < 60:
                enhanced_content = self._improve_sentiment(enhanced_content)
                improvements.append("Enhanced positive sentiment")
                improved = True
            
            # SEO improvements
            if nlp_analysis.seo_score < 70 and target_keywords:
                seo_result = self._improve_seo(enhanced_content, enhanced_title, target_keywords)
                enhanced_content = seo_result['content']
                enhanced_title = seo_result['title']
                improvements.extend(seo_result['improvements'])
                improved = True
            
            # Structure improvements
            if len(enhanced_content.split()) > 500 and enhanced_content.count('\n\n') < 3:
                enhanced_content = self._improve_structure(enhanced_content)
                improvements.append("Improved content structure")
                improved = True
            
        except Exception as e:
            logger.error(f"Error during content enhancement: {e}")
        
        return {
            'content': enhanced_content,
            'title': enhanced_title,
            'meta_description': enhanced_meta,
            'improvements': improvements,
            'improved': improved
        }
    
    def _improve_readability(self, content: str) -> str:
        """Improve content readability."""
        try:
            # Split long sentences
            sentences = content.split('. ')
            improved_sentences = []
            
            for sentence in sentences:
                words = sentence.split()
                if len(words) > 25:  # Long sentence
                    # Simple split at conjunction or comma
                    if ', ' in sentence:
                        parts = sentence.split(', ', 1)
                        improved_sentences.extend(parts)
                    elif ' and ' in sentence:
                        parts = sentence.split(' and ', 1)
                        if len(parts) == 2:
                            improved_sentences.append(parts[0] + '.')
                            improved_sentences.append('Additionally, ' + parts[1])
                        else:
                            improved_sentences.append(sentence)
                    else:
                        improved_sentences.append(sentence)
                else:
                    improved_sentences.append(sentence)
            
            return '. '.join(improved_sentences)
        except:
            return content
    
    def _improve_sentiment(self, content: str) -> str:
        """Improve content sentiment."""
        try:
            # Simple sentiment enhancement
            positive_replacements = {
                'problem': 'challenge',
                'difficult': 'interesting',
                'can\'t': 'haven\'t yet',
                'impossible': 'challenging',
                'failure': 'learning opportunity'
            }
            
            enhanced_content = content
            for negative, positive in positive_replacements.items():
                enhanced_content = enhanced_content.replace(negative, positive)
            
            return enhanced_content
        except:
            return content
    
    def _improve_seo(self, content: str, title: str, keywords: List[str]) -> Dict[str, Any]:
        """Improve SEO aspects."""
        enhanced_content = content
        enhanced_title = title
        improvements = []
        
        try:
            for keyword in keywords[:3]:  # Focus on top 3 keywords
                keyword_lower = keyword.lower()
                content_lower = enhanced_content.lower()
                
                # Check keyword density
                keyword_count = content_lower.count(keyword_lower)
                total_words = len(enhanced_content.split())
                current_density = (keyword_count / total_words) * 100 if total_words > 0 else 0
                
                # Add keyword if density is too low
                if current_density < 0.5:
                    # Add keyword naturally in conclusion
                    if not enhanced_content.endswith('\n\n'):
                        enhanced_content += '\n\n'
                    enhanced_content += f"In conclusion, {keyword} represents an important consideration for your strategy."
                    improvements.append(f"Added keyword: {keyword}")
                
                # Add keyword to title if not present
                if keyword_lower not in enhanced_title.lower():
                    enhanced_title = f"{keyword}: {enhanced_title}"
                    improvements.append(f"Added keyword to title: {keyword}")
        
        except Exception as e:
            logger.warning(f"SEO improvement failed: {e}")
        
        return {
            'content': enhanced_content,
            'title': enhanced_title,
            'improvements': improvements
        }
    
    def _improve_structure(self, content: str) -> str:
        """Improve content structure."""
        try:
            # Add paragraph breaks for better readability
            sentences = content.split('. ')
            paragraphs = []
            current_paragraph = []
            
            for i, sentence in enumerate(sentences):
                current_paragraph.append(sentence)
                
                # Create paragraph break every 3-4 sentences
                if len(current_paragraph) >= 3 and (i + 1) % 3 == 0:
                    paragraphs.append('. '.join(current_paragraph) + '.')
                    current_paragraph = []
            
            # Add remaining sentences
            if current_paragraph:
                paragraphs.append('. '.join(current_paragraph))
            
            return '\n\n'.join(paragraphs)
        except:
            return content
    
    def get_nlp_status(self) -> Dict[str, Any]:
        """Get NLP integration status."""
        if self.nlp_integration:
            from ..nlp import get_nlp_status
            return get_nlp_status()
        else:
            return {'nlp_enabled': False}
    
    async def analyze_existing_content(self, content: str, title: str = "", keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        """Analyze existing content with NLP."""
        if not self.nlp_integration:
            return {'error': 'NLP not enabled'}
        
        analysis = self.nlp_integration.analyze_content(content, title, keywords)
        
        return {
            'analysis': analysis,
            'grade': self._get_content_grade(analysis.overall_quality),
            'improvement_suggestions': analysis.recommendations
        }
    
    def _get_content_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "B+"
        elif score >= 80:
            return "B"
        elif score >= 75:
            return "C+"
        elif score >= 70:
            return "C"
        else:
            return "D" 