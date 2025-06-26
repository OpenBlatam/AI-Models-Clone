"""
Utility Functions for Blog Posts Module.

Contains helper functions for content validation, processing, and optimization.
"""

import re
import html
import math
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import bleach
import structlog

logger = structlog.get_logger(__name__)


def validate_content(content: str) -> Dict[str, Any]:
    """
    Validate blog post content.
    
    Args:
        content: The content to validate
        
    Returns:
        Dict containing validation results
    """
    errors = []
    warnings = []
    
    # Check minimum length
    if len(content.strip()) < 100:
        errors.append("Content must be at least 100 characters long")
    
    # Check word count
    word_count = len(content.split())
    if word_count < 50:
        errors.append("Content must have at least 50 words")
    elif word_count < 200:
        warnings.append("Content is quite short, consider adding more detail")
    
    # Check for basic structure
    if not any(marker in content for marker in ['#', '<h', '<p', '\n\n']):
        warnings.append("Content lacks clear structure (headings, paragraphs)")
    
    # Check for HTML issues
    if '<script' in content.lower():
        errors.append("Script tags are not allowed in content")
    
    # Check for empty paragraphs
    if re.search(r'<p>\s*</p>', content):
        warnings.append("Empty paragraphs found in content")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
        "word_count": word_count,
        "character_count": len(content)
    }


def sanitize_html(content: str) -> str:
    """
    Sanitize HTML content to remove potentially harmful elements.
    
    Args:
        content: The HTML content to sanitize
        
    Returns:
        Sanitized HTML content
    """
    allowed_tags = [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'strong', 'em', 'u', 'i', 'b',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
        'a', 'img', 'div', 'span', 'table', 'tr', 'td', 'th'
    ]
    
    allowed_attributes = {
        'a': ['href', 'title', 'target'],
        'img': ['src', 'alt', 'width', 'height', 'title'],
        'div': ['class', 'id'],
        'span': ['class', 'id'],
        'table': ['class'],
        'tr': ['class'],
        'td': ['class', 'colspan', 'rowspan'],
        'th': ['class', 'colspan', 'rowspan']
    }
    
    try:
        sanitized = bleach.clean(
            content,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True
        )
        return sanitized
    except Exception as e:
        logger.error("HTML sanitization failed", error=str(e))
        return html.escape(content)


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """
    Calculate estimated reading time for content.
    
    Args:
        content: The content to analyze
        words_per_minute: Average reading speed
        
    Returns:
        Estimated reading time in minutes
    """
    # Remove HTML tags for word count
    text_content = re.sub(r'<[^>]+>', '', content)
    word_count = len(text_content.split())
    
    reading_time = math.ceil(word_count / words_per_minute)
    return max(1, reading_time)  # Minimum 1 minute


def generate_slug(title: str) -> str:
    """
    Generate a URL-friendly slug from a title.
    
    Args:
        title: The title to convert
        
    Returns:
        URL-friendly slug
    """
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
    
    return slug


def extract_keywords(content: str, max_keywords: int = 10) -> List[str]:
    """
    Extract keywords from content using simple frequency analysis.
    
    Args:
        content: The content to analyze
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of extracted keywords
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', content.lower())
    
    # Remove punctuation and split into words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    
    # Common stop words to exclude
    stop_words = {
        'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with',
        'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before',
        'after', 'above', 'below', 'between', 'among', 'this', 'that', 'these',
        'those', 'you', 'your', 'they', 'their', 'them', 'she', 'her', 'his',
        'him', 'are', 'was', 'were', 'been', 'have', 'has', 'had', 'will',
        'would', 'could', 'should', 'may', 'might', 'can', 'must', 'shall'
    }
    
    # Filter out stop words and count frequency
    word_freq = {}
    for word in words:
        if word not in stop_words and len(word) > 3:
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency and return top keywords
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    return [word for word, freq in sorted_words[:max_keywords]]


def calculate_keyword_density(content: str, keywords: List[str]) -> float:
    """
    Calculate keyword density for given keywords in content.
    
    Args:
        content: The content to analyze
        keywords: List of keywords to check
        
    Returns:
        Keyword density as percentage
    """
    if not keywords:
        return 0.0
    
    # Remove HTML tags and convert to lowercase
    text = re.sub(r'<[^>]+>', '', content.lower())
    words = text.split()
    total_words = len(words)
    
    if total_words == 0:
        return 0.0
    
    # Count keyword occurrences
    keyword_count = 0
    for keyword in keywords:
        keyword_lower = keyword.lower()
        # Count both exact matches and partial matches
        keyword_count += text.count(keyword_lower)
    
    # Calculate density as percentage
    density = (keyword_count / total_words) * 100
    return round(density, 2)


def format_content(content: str) -> str:
    """
    Auto-format content for better readability.
    
    Args:
        content: The content to format
        
    Returns:
        Formatted content
    """
    # Add proper spacing around headings
    content = re.sub(r'([^\n])(#{1,6}\s)', r'\1\n\n\2', content)
    content = re.sub(r'(#{1,6}[^\n]+)([^\n])', r'\1\n\n\2', content)
    
    # Add spacing around lists
    content = re.sub(r'([^\n])(\n[-*+]\s)', r'\1\n\2', content)
    content = re.sub(r'([-*+][^\n]+)([^\n])', r'\1\n\2', content)
    
    # Fix multiple consecutive newlines
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # Fix spacing around paragraphs
    content = re.sub(r'([.!?])\s*\n\s*([A-Z])', r'\1\n\n\2', content)
    
    return content.strip()


def calculate_readability_score(content: str) -> float:
    """
    Calculate a simplified readability score (similar to Flesch Reading Ease).
    
    Args:
        content: The content to analyze
        
    Returns:
        Readability score (0-100, higher is better)
    """
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
    return max(0, min(100, score))


def generate_excerpt(content: str, max_length: int = 200) -> str:
    """
    Generate an excerpt from content.
    
    Args:
        content: The content to excerpt
        max_length: Maximum length of excerpt
        
    Returns:
        Generated excerpt
    """
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', content)
    
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
    if len(excerpt) < len(text):
        excerpt += "..."
    
    return excerpt


def validate_seo_data(title: str, description: str, keywords: List[str]) -> Dict[str, Any]:
    """
    Validate SEO data.
    
    Args:
        title: SEO title
        description: Meta description
        keywords: List of keywords
        
    Returns:
        Validation results
    """
    errors = []
    warnings = []
    
    # Validate title
    if len(title) < 10:
        errors.append("SEO title must be at least 10 characters")
    elif len(title) > 60:
        warnings.append("SEO title is longer than 60 characters")
    
    # Validate description
    if len(description) < 50:
        errors.append("Meta description must be at least 50 characters")
    elif len(description) > 160:
        warnings.append("Meta description is longer than 160 characters")
    
    # Validate keywords
    if len(keywords) > 10:
        warnings.append("Too many keywords, consider reducing to 5-10")
    elif len(keywords) == 0:
        warnings.append("No keywords specified")
    
    return {
        "is_valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


# Export all utility functions
__all__ = [
    "validate_content",
    "sanitize_html",
    "calculate_reading_time",
    "generate_slug",
    "extract_keywords",
    "calculate_keyword_density",
    "format_content",
    "calculate_readability_score",
    "generate_excerpt",
    "validate_seo_data"
] 