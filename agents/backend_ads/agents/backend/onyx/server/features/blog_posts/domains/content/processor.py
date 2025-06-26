"""
Content Processing Service.

Handles content formatting, sanitization, and enhancement operations.
"""

import re
import html
import math
from typing import Dict, Any
import structlog

try:
    import bleach
except ImportError:
    bleach = None

from ...interfaces.content_interfaces import IContentProcessor
from ...config import BlogPostConfig

logger = structlog.get_logger(__name__)


class ContentProcessorService:
    """Service for content processing operations."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="content_processor")
        
        # HTML sanitization settings
        self.allowed_tags = [
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'p', 'br', 'strong', 'em', 'u', 'i', 'b',
            'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
            'a', 'img', 'div', 'span', 'table', 'tr', 'td', 'th'
        ]
        
        self.allowed_attributes = {
            'a': ['href', 'title', 'target'],
            'img': ['src', 'alt', 'width', 'height', 'title'],
            'div': ['class', 'id'],
            'span': ['class', 'id'],
            'table': ['class'],
            'tr': ['class'],
            'td': ['class', 'colspan', 'rowspan'],
            'th': ['class', 'colspan', 'rowspan']
        }
    
    def sanitize_html(self, content: str) -> str:
        """
        Sanitize HTML content to remove potentially harmful elements.
        
        Args:
            content: The HTML content to sanitize
            
        Returns:
            Sanitized HTML content
        """
        try:
            if bleach is None:
                self.logger.warning("Bleach not available, using basic HTML escaping")
                return html.escape(content)
            
            sanitized = bleach.clean(
                content,
                tags=self.allowed_tags,
                attributes=self.allowed_attributes,
                strip=True
            )
            
            self.logger.debug("HTML content sanitized", 
                            original_length=len(content),
                            sanitized_length=len(sanitized))
            
            return sanitized
            
        except Exception as e:
            self.logger.error("HTML sanitization failed", error=str(e))
            return html.escape(content)
    
    def format_content(self, content: str) -> str:
        """
        Auto-format content for better readability.
        
        Args:
            content: The content to format
            
        Returns:
            Formatted content
        """
        if not self.config.enable_auto_formatting:
            return content
        
        try:
            formatted = content
            
            # Add proper spacing around headings
            formatted = re.sub(r'([^\n])(#{1,6}\s)', r'\1\n\n\2', formatted)
            formatted = re.sub(r'(#{1,6}[^\n]+)([^\n])', r'\1\n\n\2', formatted)
            
            # Add spacing around lists
            formatted = re.sub(r'([^\n])(\n[-*+]\s)', r'\1\n\2', formatted)
            formatted = re.sub(r'([-*+][^\n]+)([^\n])', r'\1\n\2', formatted)
            
            # Fix multiple consecutive newlines
            formatted = re.sub(r'\n{3,}', '\n\n', formatted)
            
            # Fix spacing around paragraphs
            formatted = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', formatted)
            
            # Remove trailing whitespace from lines
            formatted = '\n'.join(line.rstrip() for line in formatted.split('\n'))
            
            # Ensure proper spacing after punctuation
            formatted = re.sub(r'([.!?])([A-Z])', r'\1 \2', formatted)
            
            # Fix spacing around em dashes
            formatted = re.sub(r'\s*—\s*', ' — ', formatted)
            
            self.logger.debug("Content formatted", 
                            original_length=len(content),
                            formatted_length=len(formatted))
            
            return formatted.strip()
            
        except Exception as e:
            self.logger.error("Content formatting failed", error=str(e))
            return content
    
    def generate_excerpt(self, content: str, max_length: int = 200) -> str:
        """
        Generate an excerpt from content.
        
        Args:
            content: The content to excerpt
            max_length: Maximum length of excerpt
            
        Returns:
            Generated excerpt
        """
        try:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', content)
            
            # Remove markdown headers
            text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
            
            # Get first paragraph or sentences
            sentences = re.split(r'[.!?]+', text)
            excerpt = ""
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if len(excerpt + sentence) <= max_length - 3:
                    excerpt += sentence + ". "
                else:
                    break
            
            excerpt = excerpt.strip()
            if len(excerpt) < len(text) and not excerpt.endswith('...'):
                excerpt += "..."
            
            self.logger.debug("Excerpt generated", 
                            original_length=len(content),
                            excerpt_length=len(excerpt))
            
            return excerpt
            
        except Exception as e:
            self.logger.error("Excerpt generation failed", error=str(e))
            return content[:max_length] + "..." if len(content) > max_length else content
    
    def calculate_reading_time(self, content: str, words_per_minute: int = 200) -> int:
        """
        Calculate estimated reading time for content.
        
        Args:
            content: The content to analyze
            words_per_minute: Average reading speed
            
        Returns:
            Estimated reading time in minutes
        """
        try:
            # Remove HTML tags for word count
            text_content = re.sub(r'<[^>]+>', '', content)
            
            # Remove markdown formatting
            text_content = re.sub(r'[#*_`]', '', text_content)
            
            word_count = len(text_content.split())
            reading_time = math.ceil(word_count / words_per_minute)
            
            self.logger.debug("Reading time calculated", 
                            word_count=word_count,
                            reading_time_minutes=reading_time)
            
            return max(1, reading_time)  # Minimum 1 minute
            
        except Exception as e:
            self.logger.error("Reading time calculation failed", error=str(e))
            return 1
    
    def calculate_readability_score(self, content: str) -> float:
        """
        Calculate a simplified readability score (similar to Flesch Reading Ease).
        
        Args:
            content: The content to analyze
            
        Returns:
            Readability score (0-100, higher is better)
        """
        try:
            # Remove HTML tags
            text = re.sub(r'<[^>]+>', '', content)
            
            # Count sentences (simple approach)
            sentences = re.split(r'[.!?]+', text)
            sentences = [s.strip() for s in sentences if s.strip()]
            sentence_count = len(sentences)
            
            if sentence_count == 0:
                return 0.0
            
            # Count words and syllables (simplified)
            words = text.split()
            word_count = len(words)
            
            if word_count == 0:
                return 0.0
            
            # Estimate syllables (very simplified)
            syllable_count = 0
            for word in words:
                syllable_count += max(1, len(re.findall(r'[aeiouAEIOU]', word)))
            
            # Calculate average sentence length and syllables per word
            avg_sentence_length = word_count / sentence_count
            avg_syllables_per_word = syllable_count / word_count
            
            # Simplified Flesch Reading Ease formula
            score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
            
            # Normalize to 0-100 range
            normalized_score = max(0, min(100, score))
            
            self.logger.debug("Readability score calculated", 
                            score=normalized_score,
                            sentence_count=sentence_count,
                            word_count=word_count,
                            avg_sentence_length=avg_sentence_length)
            
            return normalized_score
            
        except Exception as e:
            self.logger.error("Readability score calculation failed", error=str(e))
            return 50.0  # Default middle score
    
    def generate_slug(self, title: str) -> str:
        """
        Generate a URL-friendly slug from a title.
        
        Args:
            title: The title to convert
            
        Returns:
            URL-friendly slug
        """
        try:
            # Convert to lowercase
            slug = title.lower()
            
            # Replace spaces and special characters with hyphens
            slug = re.sub(r'[^\w\s-]', '', slug)
            slug = re.sub(r'[-\s]+', '-', slug)
            
            # Remove leading/trailing hyphens
            slug = slug.strip('-')
            
            # Limit length
            if len(slug) > 50:
                slug = slug[:50].rstrip('-')
            
            self.logger.debug("Slug generated", 
                            original_title=title,
                            generated_slug=slug)
            
            return slug
            
        except Exception as e:
            self.logger.error("Slug generation failed", error=str(e))
            # Fallback to simple conversion
            return re.sub(r'[^a-zA-Z0-9]', '-', title.lower())[:50].strip('-')
    
    def enhance_content_structure(self, content: str) -> str:
        """
        Enhance content structure by adding proper formatting.
        
        Args:
            content: The content to enhance
            
        Returns:
            Enhanced content with better structure
        """
        try:
            enhanced = content
            
            # Ensure proper heading hierarchy
            enhanced = self._fix_heading_hierarchy(enhanced)
            
            # Add table of contents markers if content is long
            if len(enhanced.split()) > 1000:
                enhanced = self._add_table_of_contents_markers(enhanced)
            
            # Improve list formatting
            enhanced = self._improve_list_formatting(enhanced)
            
            # Add proper paragraph breaks
            enhanced = self._improve_paragraph_structure(enhanced)
            
            self.logger.debug("Content structure enhanced")
            
            return enhanced
            
        except Exception as e:
            self.logger.error("Content structure enhancement failed", error=str(e))
            return content
    
    def _fix_heading_hierarchy(self, content: str) -> str:
        """Fix heading hierarchy to ensure proper structure."""
        lines = content.split('\n')
        fixed_lines = []
        current_level = 0
        
        for line in lines:
            if line.strip().startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level > current_level + 1:
                    level = current_level + 1
                current_level = level
                fixed_lines.append('#' * level + line.lstrip('#'))
            else:
                fixed_lines.append(line)
        
        return '\n'.join(fixed_lines)
    
    def _add_table_of_contents_markers(self, content: str) -> str:
        """Add markers for table of contents generation."""
        lines = content.split('\n')
        enhanced_lines = []
        
        for line in lines:
            if line.strip().startswith('##') and not line.strip().startswith('###'):
                enhanced_lines.append(f"<!-- TOC_ENTRY: {line.strip()} -->")
            enhanced_lines.append(line)
        
        return '\n'.join(enhanced_lines)
    
    def _improve_list_formatting(self, content: str) -> str:
        """Improve formatting of lists."""
        # Ensure consistent list markers
        content = re.sub(r'^[\s]*[-*+]\s+', '- ', content, flags=re.MULTILINE)
        
        # Add spacing around lists
        content = re.sub(r'\n(- [^\n]+(?:\n- [^\n]+)*)', r'\n\n\1\n', content)
        
        return content
    
    def _improve_paragraph_structure(self, content: str) -> str:
        """Improve paragraph structure and spacing."""
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        
        improved_paragraphs = []
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Ensure sentences end with proper punctuation
                if not paragraph.endswith(('.', '!', '?', ':', ';')):
                    paragraph += '.'
                improved_paragraphs.append(paragraph)
        
        return '\n\n'.join(improved_paragraphs) 