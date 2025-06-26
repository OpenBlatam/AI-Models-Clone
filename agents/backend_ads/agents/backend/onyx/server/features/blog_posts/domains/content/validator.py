"""
Content Validation Service.

Handles validation of blog post content, titles, and metadata.
"""

import re
from typing import Dict, Any, List
import structlog

from ...interfaces.content_interfaces import IContentValidator
from ...config import BlogPostConfig

logger = structlog.get_logger(__name__)


class ContentValidatorService:
    """Service for content validation."""
    
    def __init__(self, config: BlogPostConfig):
        self.config = config
        self.logger = logger.bind(service="content_validator")
    
    def validate_content(self, content: str) -> Dict[str, Any]:
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
        if len(content.strip()) < self.config.min_content_length:
            errors.append(f"Content must be at least {self.config.min_content_length} characters long")
        
        # Check maximum length
        if len(content.strip()) > self.config.max_content_length:
            errors.append(f"Content must not exceed {self.config.max_content_length} characters")
        
        # Check word count
        word_count = len(content.split())
        min_words = self.config.min_content_length // 5  # Approximate words from characters
        
        if word_count < min_words:
            errors.append(f"Content must have at least {min_words} words")
        elif word_count < min_words * 2:
            warnings.append("Content is quite short, consider adding more detail")
        
        # Check for basic structure
        if not any(marker in content for marker in ['#', '<h', '<p', '\n\n']):
            warnings.append("Content lacks clear structure (headings, paragraphs)")
        
        # Check for HTML issues
        if '<script' in content.lower():
            errors.append("Script tags are not allowed in content")
        
        # Check for potentially unsafe HTML
        dangerous_tags = ['<iframe', '<object', '<embed', '<form']
        for tag in dangerous_tags:
            if tag in content.lower():
                warnings.append(f"Potentially unsafe HTML tag found: {tag}")
        
        # Check for empty paragraphs
        if re.search(r'<p>\s*</p>', content):
            warnings.append("Empty paragraphs found in content")
        
        # Check for excessive capitalization
        if re.search(r'[A-Z]{10,}', content):
            warnings.append("Excessive capitalization found - consider reducing for better readability")
        
        # Check for repeated words
        words = content.lower().split()
        repeated_sequences = self._find_repeated_sequences(words)
        if repeated_sequences:
            warnings.append(f"Repeated word sequences found: {', '.join(repeated_sequences)}")
        
        # Check for placeholder text
        placeholder_patterns = [
            r'\[.*?\]',  # [placeholder text]
            r'TODO:',
            r'PLACEHOLDER',
            r'Lorem ipsum'
        ]
        
        for pattern in placeholder_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append("Placeholder text found - ensure all content is finalized")
                break
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "word_count": word_count,
            "character_count": len(content),
            "readability_issues": self._check_readability_issues(content)
        }
    
    def validate_title(self, title: str) -> Dict[str, Any]:
        """Validate title format and length."""
        errors = []
        warnings = []
        
        # Check minimum length
        if len(title.strip()) < 10:
            errors.append("Title must be at least 10 characters long")
        
        # Check maximum length
        if len(title.strip()) > 100:
            errors.append("Title must not exceed 100 characters")
        elif len(title.strip()) > 60:
            warnings.append("Title is longer than 60 characters - may be truncated in search results")
        
        # Check for excessive capitalization
        if title.isupper():
            warnings.append("Title is all uppercase - consider using title case")
        
        # Check for special characters that might cause issues
        problematic_chars = ['<', '>', '&', '"', "'"]
        for char in problematic_chars:
            if char in title:
                warnings.append(f"Title contains potentially problematic character: {char}")
        
        # Check for clickbait patterns
        clickbait_patterns = [
            r'\b\d+\s+(amazing|incredible|unbelievable|shocking)',
            r'you won\'t believe',
            r'this will blow your mind',
            r'\b\d+\s+secrets?',
        ]
        
        for pattern in clickbait_patterns:
            if re.search(pattern, title, re.IGNORECASE):
                warnings.append("Title may contain clickbait language")
                break
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "character_count": len(title.strip()),
            "word_count": len(title.split())
        }
    
    def validate_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Validate blog post metadata."""
        errors = []
        warnings = []
        
        # Check required fields
        required_fields = ['author']
        for field in required_fields:
            if not metadata.get(field):
                errors.append(f"Required field '{field}' is missing or empty")
        
        # Validate author
        if metadata.get('author'):
            author = metadata['author']
            if len(author) < 2:
                errors.append("Author name must be at least 2 characters long")
            elif len(author) > 100:
                errors.append("Author name must not exceed 100 characters")
        
        # Validate tags
        if metadata.get('tags'):
            tags = metadata['tags']
            if not isinstance(tags, list):
                errors.append("Tags must be a list")
            else:
                if len(tags) > 20:
                    warnings.append("Too many tags - consider reducing to 10 or fewer")
                
                for tag in tags:
                    if not isinstance(tag, str):
                        errors.append("All tags must be strings")
                    elif len(tag.strip()) == 0:
                        warnings.append("Empty tags found - consider removing")
                    elif len(tag) > 50:
                        warnings.append(f"Tag too long: '{tag}' - consider shortening")
        
        # Validate category
        if metadata.get('category'):
            category = metadata['category']
            if len(category) > 100:
                errors.append("Category name must not exceed 100 characters")
        
        # Validate excerpt
        if metadata.get('excerpt'):
            excerpt = metadata['excerpt']
            if len(excerpt) > 500:
                warnings.append("Excerpt is quite long - consider shortening for better readability")
        
        # Validate featured image URL
        if metadata.get('featured_image'):
            url = metadata['featured_image']
            if not self._is_valid_url(url):
                errors.append("Featured image URL is not valid")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    
    def _find_repeated_sequences(self, words: List[str], min_length: int = 3) -> List[str]:
        """Find repeated word sequences in content."""
        repeated = []
        
        for i in range(len(words) - min_length + 1):
            sequence = words[i:i + min_length]
            sequence_str = ' '.join(sequence)
            
            # Look for this sequence elsewhere in the text
            for j in range(i + min_length, len(words) - min_length + 1):
                if words[j:j + min_length] == sequence:
                    if sequence_str not in repeated:
                        repeated.append(sequence_str)
                    break
        
        return repeated[:5]  # Return first 5 to avoid overwhelming output
    
    def _check_readability_issues(self, content: str) -> List[str]:
        """Check for common readability issues."""
        issues = []
        
        # Check average sentence length
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            words = content.split()
            avg_sentence_length = len(words) / len(sentences)
            
            if avg_sentence_length > 25:
                issues.append("Average sentence length is quite long - consider breaking up complex sentences")
        
        # Check for passive voice (simplified detection)
        passive_indicators = [
            r'\bis\s+\w+ed\b',
            r'\bare\s+\w+ed\b', 
            r'\bwas\s+\w+ed\b',
            r'\bwere\s+\w+ed\b',
            r'\bbeen\s+\w+ed\b'
        ]
        
        passive_count = 0
        for pattern in passive_indicators:
            passive_count += len(re.findall(pattern, content, re.IGNORECASE))
        
        if passive_count > len(content.split()) * 0.1:  # More than 10% passive voice
            issues.append("High usage of passive voice detected - consider using more active voice")
        
        # Check for transition words
        transition_words = [
            'however', 'therefore', 'furthermore', 'moreover', 'additionally',
            'consequently', 'meanwhile', 'nevertheless', 'nonetheless'
        ]
        
        has_transitions = any(word in content.lower() for word in transition_words)
        if not has_transitions and len(content.split()) > 500:
            issues.append("Content lacks transition words - consider adding them for better flow")
        
        return issues
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid (basic validation)."""
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        return url_pattern.match(url) is not None 