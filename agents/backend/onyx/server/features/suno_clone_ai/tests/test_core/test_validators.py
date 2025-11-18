"""
Comprehensive Unit Tests for Core Validators

Tests cover all validator functions with diverse test cases including:
- Valid inputs
- Invalid inputs
- Edge cases
- Boundary conditions
- Type validation
"""

import pytest
import uuid
from datetime import datetime

from core.validators import Validator, ValidationError, validate_and_raise


class TestValidatorUUID:
    """Test cases for validate_uuid function"""
    
    def test_validate_uuid_valid(self):
        """Test validating valid UUID"""
        valid_uuid = str(uuid.uuid4())
        assert Validator.validate_uuid(valid_uuid) is True
    
    def test_validate_uuid_invalid_format(self):
        """Test validating invalid UUID format"""
        invalid_uuid = "not-a-uuid"
        assert Validator.validate_uuid(invalid_uuid) is False
    
    def test_validate_uuid_empty_string(self):
        """Test validating empty string"""
        assert Validator.validate_uuid("") is False
    
    def test_validate_uuid_none(self):
        """Test validating None"""
        assert Validator.validate_uuid(None) is False
    
    def test_validate_uuid_wrong_length(self):
        """Test validating UUID with wrong length"""
        assert Validator.validate_uuid("12345") is False
    
    def test_validate_uuid_missing_segments(self):
        """Test validating UUID with missing segments"""
        assert Validator.validate_uuid("12345678-1234-1234-1234") is False


class TestValidatorEmail:
    """Test cases for validate_email function"""
    
    def test_validate_email_valid(self):
        """Test validating valid email addresses"""
        valid_emails = [
            "user@example.com",
            "test.user@example.co.uk",
            "user+tag@example.com",
            "user_name@example-domain.com"
        ]
        for email in valid_emails:
            assert Validator.validate_email(email) is True
    
    def test_validate_email_invalid_no_at(self):
        """Test validating email without @"""
        assert Validator.validate_email("userexample.com") is False
    
    def test_validate_email_invalid_no_domain(self):
        """Test validating email without domain"""
        assert Validator.validate_email("user@") is False
    
    def test_validate_email_invalid_no_tld(self):
        """Test validating email without TLD"""
        assert Validator.validate_email("user@example") is False
    
    def test_validate_email_empty(self):
        """Test validating empty email"""
        assert Validator.validate_email("") is False
    
    def test_validate_email_special_chars(self):
        """Test validating email with special characters"""
        assert Validator.validate_email("user@ex@mple.com") is False


class TestValidatorURL:
    """Test cases for validate_url function"""
    
    def test_validate_url_valid_http(self):
        """Test validating valid HTTP URL"""
        assert Validator.validate_url("http://example.com") is True
    
    def test_validate_url_valid_https(self):
        """Test validating valid HTTPS URL"""
        assert Validator.validate_url("https://example.com/path") is True
    
    def test_validate_url_with_port(self):
        """Test validating URL with port"""
        assert Validator.validate_url("http://example.com:8080") is True
    
    def test_validate_url_with_path(self):
        """Test validating URL with path"""
        assert Validator.validate_url("https://example.com/api/v1/songs") is True
    
    def test_validate_url_with_query(self):
        """Test validating URL with query parameters"""
        assert Validator.validate_url("https://example.com?param=value") is True
    
    def test_validate_url_invalid_no_protocol(self):
        """Test validating URL without protocol"""
        assert Validator.validate_url("example.com") is False
    
    def test_validate_url_invalid_empty(self):
        """Test validating empty URL"""
        assert Validator.validate_url("") is False


class TestValidatorISODatetime:
    """Test cases for validate_iso_datetime function"""
    
    def test_validate_iso_datetime_valid(self):
        """Test validating valid ISO datetime"""
        valid_dt = "2023-01-01T12:00:00"
        assert Validator.validate_iso_datetime(valid_dt) is True
    
    def test_validate_iso_datetime_with_timezone(self):
        """Test validating ISO datetime with timezone"""
        valid_dt = "2023-01-01T12:00:00+00:00"
        assert Validator.validate_iso_datetime(valid_dt) is True
    
    def test_validate_iso_datetime_with_z(self):
        """Test validating ISO datetime with Z"""
        valid_dt = "2023-01-01T12:00:00Z"
        assert Validator.validate_iso_datetime(valid_dt) is True
    
    def test_validate_iso_datetime_invalid_format(self):
        """Test validating invalid datetime format"""
        assert Validator.validate_iso_datetime("2023-01-01") is False
    
    def test_validate_iso_datetime_invalid_date(self):
        """Test validating invalid date"""
        assert Validator.validate_iso_datetime("2023-13-45T12:00:00") is False
    
    def test_validate_iso_datetime_empty(self):
        """Test validating empty string"""
        assert Validator.validate_iso_datetime("") is False
    
    def test_validate_iso_datetime_none(self):
        """Test validating None"""
        assert Validator.validate_iso_datetime(None) is False


class TestValidatorAudioFormat:
    """Test cases for validate_audio_format function"""
    
    def test_validate_audio_format_wav(self):
        """Test validating WAV format"""
        assert Validator.validate_audio_format("song.wav") is True
    
    def test_validate_audio_format_mp3(self):
        """Test validating MP3 format"""
        assert Validator.validate_audio_format("song.mp3") is True
    
    def test_validate_audio_format_ogg(self):
        """Test validating OGG format"""
        assert Validator.validate_audio_format("song.ogg") is True
    
    def test_validate_audio_format_flac(self):
        """Test validating FLAC format"""
        assert Validator.validate_audio_format("song.flac") is True
    
    def test_validate_audio_format_m4a(self):
        """Test validating M4A format"""
        assert Validator.validate_audio_format("song.m4a") is True
    
    def test_validate_audio_format_invalid(self):
        """Test validating invalid format"""
        assert Validator.validate_audio_format("song.txt") is False
    
    def test_validate_audio_format_case_insensitive(self):
        """Test format validation is case insensitive"""
        assert Validator.validate_audio_format("song.WAV") is True
        assert Validator.validate_audio_format("song.MP3") is True
    
    def test_validate_audio_format_custom_allowed(self):
        """Test with custom allowed formats"""
        assert Validator.validate_audio_format("song.wav", allowed_formats=["wav", "mp3"]) is True
        assert Validator.validate_audio_format("song.ogg", allowed_formats=["wav", "mp3"]) is False
    
    def test_validate_audio_format_no_extension(self):
        """Test filename without extension"""
        assert Validator.validate_audio_format("song") is False


class TestValidatorPrompt:
    """Test cases for validate_prompt function"""
    
    def test_validate_prompt_valid(self):
        """Test validating valid prompt"""
        assert Validator.validate_prompt("Create a happy song") is True
    
    def test_validate_prompt_min_length(self):
        """Test prompt with minimum length"""
        assert Validator.validate_prompt("A", min_length=1) is True
    
    def test_validate_prompt_max_length(self):
        """Test prompt at maximum length"""
        long_prompt = "A" * 1000
        assert Validator.validate_prompt(long_prompt, max_length=1000) is True
    
    def test_validate_prompt_too_short(self):
        """Test prompt too short"""
        assert Validator.validate_prompt("", min_length=1) is False
    
    def test_validate_prompt_too_long(self):
        """Test prompt too long"""
        long_prompt = "A" * 1001
        assert Validator.validate_prompt(long_prompt, max_length=1000) is False
    
    def test_validate_prompt_whitespace_only(self):
        """Test prompt with only whitespace"""
        assert Validator.validate_prompt("   ", min_length=1) is False
    
    def test_validate_prompt_not_string(self):
        """Test prompt that is not a string"""
        assert Validator.validate_prompt(123) is False
        assert Validator.validate_prompt(None) is False
        assert Validator.validate_prompt([]) is False


class TestValidatorBPM:
    """Test cases for validate_bpm function"""
    
    def test_validate_bpm_valid(self):
        """Test validating valid BPM values"""
        valid_bpms = [60, 120, 180, 100.5]
        for bpm in valid_bpms:
            assert Validator.validate_bpm(bpm) is True
    
    def test_validate_bpm_minimum(self):
        """Test BPM at minimum boundary"""
        assert Validator.validate_bpm(20) is True
    
    def test_validate_bpm_maximum(self):
        """Test BPM at maximum boundary"""
        assert Validator.validate_bpm(300) is True
    
    def test_validate_bpm_below_minimum(self):
        """Test BPM below minimum"""
        assert Validator.validate_bpm(19) is False
        assert Validator.validate_bpm(0) is False
        assert Validator.validate_bpm(-10) is False
    
    def test_validate_bpm_above_maximum(self):
        """Test BPM above maximum"""
        assert Validator.validate_bpm(301) is False
        assert Validator.validate_bpm(500) is False
    
    def test_validate_bpm_not_number(self):
        """Test BPM that is not a number"""
        assert Validator.validate_bpm("120") is False
        assert Validator.validate_bpm(None) is False


class TestValidatorDuration:
    """Test cases for validate_duration function"""
    
    def test_validate_duration_valid(self):
        """Test validating valid duration"""
        valid_durations = [1, 30, 180, 3600, 45.5]
        for duration in valid_durations:
            assert Validator.validate_duration(duration) is True
    
    def test_validate_duration_minimum(self):
        """Test duration at minimum (greater than 0)"""
        assert Validator.validate_duration(0.1) is True
    
    def test_validate_duration_maximum(self):
        """Test duration at maximum"""
        assert Validator.validate_duration(3600) is True
    
    def test_validate_duration_zero(self):
        """Test duration of zero"""
        assert Validator.validate_duration(0) is False
    
    def test_validate_duration_negative(self):
        """Test negative duration"""
        assert Validator.validate_duration(-10) is False
    
    def test_validate_duration_above_maximum(self):
        """Test duration above maximum"""
        assert Validator.validate_duration(3601) is False
        assert Validator.validate_duration(10000) is False
    
    def test_validate_duration_not_number(self):
        """Test duration that is not a number"""
        assert Validator.validate_duration("30") is False
        assert Validator.validate_duration(None) is False


class TestValidatorPrice:
    """Test cases for validate_price function"""
    
    def test_validate_price_valid(self):
        """Test validating valid prices"""
        valid_prices = [0, 10, 99.99, 1000]
        for price in valid_prices:
            assert Validator.validate_price(price) is True
    
    def test_validate_price_zero(self):
        """Test price of zero (free)"""
        assert Validator.validate_price(0) is True
    
    def test_validate_price_negative(self):
        """Test negative price"""
        assert Validator.validate_price(-10) is False
    
    def test_validate_price_not_number(self):
        """Test price that is not a number"""
        assert Validator.validate_price("10") is False
        assert Validator.validate_price(None) is False


class TestValidatorRating:
    """Test cases for validate_rating function"""
    
    def test_validate_rating_valid(self):
        """Test validating valid ratings"""
        for rating in [1, 2, 3, 4, 5]:
            assert Validator.validate_rating(rating) is True
    
    def test_validate_rating_minimum(self):
        """Test rating at minimum"""
        assert Validator.validate_rating(1) is True
    
    def test_validate_rating_maximum(self):
        """Test rating at maximum"""
        assert Validator.validate_rating(5) is True
    
    def test_validate_rating_below_minimum(self):
        """Test rating below minimum"""
        assert Validator.validate_rating(0) is False
        assert Validator.validate_rating(-1) is False
    
    def test_validate_rating_above_maximum(self):
        """Test rating above maximum"""
        assert Validator.validate_rating(6) is False
        assert Validator.validate_rating(10) is False
    
    def test_validate_rating_not_integer(self):
        """Test rating that is not an integer"""
        assert Validator.validate_rating(3.5) is False
        assert Validator.validate_rating("5") is False
        assert Validator.validate_rating(None) is False


class TestValidateAndRaise:
    """Test cases for validate_and_raise function"""
    
    def test_validate_and_raise_valid(self):
        """Test validation passes with valid value"""
        def is_positive(x):
            return x > 0
        
        # Should not raise
        validate_and_raise(is_positive, 10, "Must be positive")
    
    def test_validate_and_raise_invalid(self):
        """Test validation fails and raises error"""
        def is_positive(x):
            return x > 0
        
        with pytest.raises(ValidationError, match="Must be positive"):
            validate_and_raise(is_positive, -10, "Must be positive")
    
    def test_validate_and_raise_custom_message(self):
        """Test custom error message"""
        def is_even(x):
            return x % 2 == 0
        
        with pytest.raises(ValidationError, match="Number must be even"):
            validate_and_raise(is_even, 3, "Number must be even")










