"""
Comprehensive Unit Tests for Core Helpers

Tests cover all helper functions with diverse test cases including:
- Edge cases
- Error handling
- Boundary conditions
- Type validation
- Normal operations
"""

import pytest
import json
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from core.helpers import (
    generate_id,
    hash_string,
    safe_json_loads,
    safe_json_dumps,
    format_duration,
    format_file_size,
    ensure_directory,
    chunk_list,
    merge_dicts,
    get_nested_value,
    set_nested_value,
    sanitize_filename,
    retry_on_failure
)


class TestGenerateId:
    """Test cases for generate_id function"""
    
    def test_generate_id_without_prefix(self):
        """Test ID generation without prefix returns valid UUID"""
        id_str = generate_id()
        assert isinstance(id_str, str)
        assert len(id_str) > 0
        # Should be a valid UUID format
        uuid.UUID(id_str)
    
    def test_generate_id_with_prefix(self):
        """Test ID generation with prefix includes prefix"""
        prefix = "song"
        id_str = generate_id(prefix=prefix)
        assert id_str.startswith(f"{prefix}_")
        # Extract UUID part
        uuid_part = id_str.split("_", 1)[1]
        uuid.UUID(uuid_part)
    
    def test_generate_id_uniqueness(self):
        """Test that generated IDs are unique"""
        ids = [generate_id() for _ in range(100)]
        assert len(ids) == len(set(ids)), "Generated IDs should be unique"
    
    def test_generate_id_with_empty_prefix(self):
        """Test ID generation with empty prefix behaves like no prefix"""
        id1 = generate_id(prefix="")
        id2 = generate_id()
        # Both should be valid UUIDs
        uuid.UUID(id1)
        uuid.UUID(id2)
    
    def test_generate_id_with_special_characters_in_prefix(self):
        """Test ID generation handles special characters in prefix"""
        prefix = "test-song_123"
        id_str = generate_id(prefix=prefix)
        assert id_str.startswith(f"{prefix}_")


class TestHashString:
    """Test cases for hash_string function"""
    
    def test_hash_string_sha256_default(self):
        """Test hashing with default SHA256 algorithm"""
        value = "test_string"
        hash_result = hash_string(value)
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA256 produces 64 char hex
        assert hash_result.isalnum() or all(c in 'abcdef0123456789' for c in hash_result)
    
    def test_hash_string_md5(self):
        """Test hashing with MD5 algorithm"""
        value = "test_string"
        hash_result = hash_string(value, algorithm="md5")
        assert isinstance(hash_result, str)
        assert len(hash_result) == 32  # MD5 produces 32 char hex
    
    def test_hash_string_sha1(self):
        """Test hashing with SHA1 algorithm"""
        value = "test_string"
        hash_result = hash_string(value, algorithm="sha1")
        assert isinstance(hash_result, str)
        assert len(hash_result) == 40  # SHA1 produces 40 char hex
    
    def test_hash_string_deterministic(self):
        """Test that same input produces same hash"""
        value = "consistent_test"
        hash1 = hash_string(value)
        hash2 = hash_string(value)
        assert hash1 == hash2
    
    def test_hash_string_different_inputs(self):
        """Test that different inputs produce different hashes"""
        hash1 = hash_string("input1")
        hash2 = hash_string("input2")
        assert hash1 != hash2
    
    def test_hash_string_empty_string(self):
        """Test hashing empty string"""
        hash_result = hash_string("")
        assert isinstance(hash_result, str)
        assert len(hash_result) > 0
    
    def test_hash_string_unicode(self):
        """Test hashing unicode characters"""
        value = "测试🎵音乐"
        hash_result = hash_string(value)
        assert isinstance(hash_result, str)
        assert len(hash_result) == 64


class TestSafeJsonLoads:
    """Test cases for safe_json_loads function"""
    
    def test_safe_json_loads_valid_json(self):
        """Test loading valid JSON string"""
        json_str = '{"key": "value", "number": 123}'
        result = safe_json_loads(json_str)
        assert result == {"key": "value", "number": 123}
    
    def test_safe_json_loads_invalid_json(self):
        """Test loading invalid JSON returns default"""
        invalid_json = "{invalid json}"
        result = safe_json_loads(invalid_json)
        assert result is None
    
    def test_safe_json_loads_invalid_json_with_default(self):
        """Test loading invalid JSON with custom default"""
        invalid_json = "{invalid}"
        default = {"error": "failed"}
        result = safe_json_loads(invalid_json, default=default)
        assert result == default
    
    def test_safe_json_loads_empty_string(self):
        """Test loading empty string"""
        result = safe_json_loads("")
        assert result is None
    
    def test_safe_json_loads_none_input(self):
        """Test loading None input"""
        result = safe_json_loads(None)
        assert result is None
    
    def test_safe_json_loads_array(self):
        """Test loading JSON array"""
        json_str = '[1, 2, 3, "test"]'
        result = safe_json_loads(json_str)
        assert result == [1, 2, 3, "test"]
    
    def test_safe_json_loads_nested_structure(self):
        """Test loading nested JSON structure"""
        json_str = '{"user": {"name": "John", "age": 30}, "tags": ["music", "ai"]}'
        result = safe_json_loads(json_str)
        assert result["user"]["name"] == "John"
        assert result["tags"] == ["music", "ai"]


class TestSafeJsonDumps:
    """Test cases for safe_json_dumps function"""
    
    def test_safe_json_dumps_valid_dict(self):
        """Test dumping valid dictionary"""
        data = {"key": "value", "number": 123}
        result = safe_json_dumps(data)
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data
    
    def test_safe_json_dumps_list(self):
        """Test dumping list"""
        data = [1, 2, 3, "test"]
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data
    
    def test_safe_json_dumps_with_datetime(self):
        """Test dumping object with datetime (should use default=str)"""
        from datetime import datetime
        data = {"timestamp": datetime(2023, 1, 1, 12, 0, 0)}
        result = safe_json_dumps(data)
        assert isinstance(result, str)
        assert "2023" in result
    
    def test_safe_json_dumps_non_serializable(self):
        """Test dumping non-serializable object returns default"""
        class CustomClass:
            pass
        
        data = CustomClass()
        result = safe_json_dumps(data, default="{}")
        assert result == "{}"
    
    def test_safe_json_dumps_nested_structure(self):
        """Test dumping nested structure"""
        data = {"user": {"name": "John"}, "tags": ["music"]}
        result = safe_json_dumps(data)
        parsed = json.loads(result)
        assert parsed == data
    
    def test_safe_json_dumps_empty_dict(self):
        """Test dumping empty dictionary"""
        result = safe_json_dumps({})
        assert result == "{}"


class TestFormatDuration:
    """Test cases for format_duration function"""
    
    def test_format_duration_seconds_only(self):
        """Test formatting duration less than a minute"""
        result = format_duration(45.5)
        assert result == "0:45"
    
    def test_format_duration_minutes_and_seconds(self):
        """Test formatting duration with minutes and seconds"""
        result = format_duration(125.7)
        assert result == "2:05"
    
    def test_format_duration_exact_minute(self):
        """Test formatting exact minute"""
        result = format_duration(60.0)
        assert result == "1:00"
    
    def test_format_duration_zero(self):
        """Test formatting zero duration"""
        result = format_duration(0.0)
        assert result == "0:00"
    
    def test_format_duration_large_value(self):
        """Test formatting large duration"""
        result = format_duration(3661.0)
        assert result == "61:01"
    
    def test_format_duration_float_precision(self):
        """Test formatting float with decimal precision"""
        result = format_duration(90.9)
        assert result == "1:30"  # Should truncate, not round


class TestFormatFileSize:
    """Test cases for format_file_size function"""
    
    def test_format_file_size_bytes(self):
        """Test formatting size in bytes"""
        result = format_file_size(512)
        assert "B" in result
        assert "512" in result
    
    def test_format_file_size_kilobytes(self):
        """Test formatting size in kilobytes"""
        result = format_file_size(2048)
        assert "KB" in result
    
    def test_format_file_size_megabytes(self):
        """Test formatting size in megabytes"""
        result = format_file_size(2 * 1024 * 1024)
        assert "MB" in result
    
    def test_format_file_size_gigabytes(self):
        """Test formatting size in gigabytes"""
        result = format_file_size(2 * 1024 * 1024 * 1024)
        assert "GB" in result
    
    def test_format_file_size_zero(self):
        """Test formatting zero size"""
        result = format_file_size(0)
        assert "0.00" in result
        assert "B" in result
    
    def test_format_file_size_decimal_precision(self):
        """Test formatting with decimal precision"""
        result = format_file_size(1536)  # 1.5 KB
        assert "1.50" in result or "1.5" in result


class TestEnsureDirectory:
    """Test cases for ensure_directory function"""
    
    def test_ensure_directory_creates_new(self, temp_dir):
        """Test creating new directory"""
        new_dir = temp_dir / "new_directory"
        result = ensure_directory(str(new_dir))
        assert result.exists()
        assert result.is_dir()
    
    def test_ensure_directory_existing(self, temp_dir):
        """Test with existing directory"""
        existing_dir = temp_dir / "existing"
        existing_dir.mkdir()
        result = ensure_directory(str(existing_dir))
        assert result.exists()
        assert result.is_dir()
    
    def test_ensure_directory_nested(self, temp_dir):
        """Test creating nested directories"""
        nested = temp_dir / "level1" / "level2" / "level3"
        result = ensure_directory(str(nested))
        assert result.exists()
        assert result.is_dir()
    
    def test_ensure_directory_returns_path(self, temp_dir):
        """Test function returns Path object"""
        new_dir = temp_dir / "test"
        result = ensure_directory(str(new_dir))
        assert isinstance(result, Path)


class TestChunkList:
    """Test cases for chunk_list function"""
    
    def test_chunk_list_even_division(self):
        """Test chunking list with even division"""
        items = list(range(10))
        chunks = chunk_list(items, chunk_size=5)
        assert len(chunks) == 2
        assert chunks[0] == [0, 1, 2, 3, 4]
        assert chunks[1] == [5, 6, 7, 8, 9]
    
    def test_chunk_list_uneven_division(self):
        """Test chunking list with uneven division"""
        items = list(range(10))
        chunks = chunk_list(items, chunk_size=3)
        assert len(chunks) == 4
        assert chunks[0] == [0, 1, 2]
        assert chunks[3] == [9]
    
    def test_chunk_list_empty(self):
        """Test chunking empty list"""
        chunks = chunk_list([], chunk_size=5)
        assert chunks == []
    
    def test_chunk_list_single_chunk(self):
        """Test chunking into single chunk"""
        items = [1, 2, 3]
        chunks = chunk_list(items, chunk_size=10)
        assert len(chunks) == 1
        assert chunks[0] == [1, 2, 3]
    
    def test_chunk_list_chunk_size_one(self):
        """Test chunking with chunk size of 1"""
        items = [1, 2, 3]
        chunks = chunk_list(items, chunk_size=1)
        assert len(chunks) == 3
        assert all(len(chunk) == 1 for chunk in chunks)
    
    def test_chunk_list_larger_than_list(self):
        """Test chunking when chunk size larger than list"""
        items = [1, 2]
        chunks = chunk_list(items, chunk_size=5)
        assert len(chunks) == 1
        assert chunks[0] == [1, 2]


class TestMergeDicts:
    """Test cases for merge_dicts function"""
    
    def test_merge_dicts_two_dicts(self):
        """Test merging two dictionaries"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"c": 3, "d": 4}
        result = merge_dicts(dict1, dict2)
        assert result == {"a": 1, "b": 2, "c": 3, "d": 4}
    
    def test_merge_dicts_overlapping_keys(self):
        """Test merging with overlapping keys (later wins)"""
        dict1 = {"a": 1, "b": 2}
        dict2 = {"b": 3, "c": 4}
        result = merge_dicts(dict1, dict2)
        assert result["b"] == 3  # dict2 value wins
        assert result["a"] == 1
        assert result["c"] == 4
    
    def test_merge_dicts_three_dicts(self):
        """Test merging three dictionaries"""
        dict1 = {"a": 1}
        dict2 = {"b": 2}
        dict3 = {"c": 3}
        result = merge_dicts(dict1, dict2, dict3)
        assert result == {"a": 1, "b": 2, "c": 3}
    
    def test_merge_dicts_empty(self):
        """Test merging empty dictionaries"""
        result = merge_dicts({}, {})
        assert result == {}
    
    def test_merge_dicts_nested(self):
        """Test merging nested dictionaries (shallow merge)"""
        dict1 = {"nested": {"a": 1}}
        dict2 = {"nested": {"b": 2}}
        result = merge_dicts(dict1, dict2)
        # Shallow merge - nested dict2 overwrites nested dict1
        assert result["nested"] == {"b": 2}


class TestGetNestedValue:
    """Test cases for get_nested_value function"""
    
    def test_get_nested_value_simple_key(self):
        """Test getting simple key"""
        data = {"key": "value"}
        result = get_nested_value(data, "key")
        assert result == "value"
    
    def test_get_nested_value_nested_path(self):
        """Test getting nested value with dot notation"""
        data = {"user": {"profile": {"name": "John"}}}
        result = get_nested_value(data, "user.profile.name")
        assert result == "John"
    
    def test_get_nested_value_missing_key(self):
        """Test getting missing key returns default"""
        data = {"key": "value"}
        result = get_nested_value(data, "missing", default="default")
        assert result == "default"
    
    def test_get_nested_value_missing_nested(self):
        """Test getting missing nested key"""
        data = {"user": {"profile": {}}}
        result = get_nested_value(data, "user.profile.name", default="Unknown")
        assert result == "Unknown"
    
    def test_get_nested_value_default_none(self):
        """Test default is None when not specified"""
        data = {"key": "value"}
        result = get_nested_value(data, "missing")
        assert result is None
    
    def test_get_nested_value_intermediate_missing(self):
        """Test when intermediate key is missing"""
        data = {"user": {}}
        result = get_nested_value(data, "user.profile.name")
        assert result is None


class TestSetNestedValue:
    """Test cases for set_nested_value function"""
    
    def test_set_nested_value_simple_key(self):
        """Test setting simple key"""
        data = {}
        set_nested_value(data, "key", "value")
        assert data["key"] == "value"
    
    def test_set_nested_value_nested_path(self):
        """Test setting nested value"""
        data = {}
        set_nested_value(data, "user.profile.name", "John")
        assert data["user"]["profile"]["name"] == "John"
    
    def test_set_nested_value_overwrite_existing(self):
        """Test overwriting existing value"""
        data = {"user": {"profile": {"name": "Old"}}}
        set_nested_value(data, "user.profile.name", "New")
        assert data["user"]["profile"]["name"] == "New"
    
    def test_set_nested_value_creates_intermediate(self):
        """Test creating intermediate dictionaries"""
        data = {}
        set_nested_value(data, "level1.level2.level3", "value")
        assert data["level1"]["level2"]["level3"] == "value"
    
    def test_set_nested_value_preserves_existing(self):
        """Test preserving existing keys when setting nested"""
        data = {"user": {"profile": {"age": 30}}}
        set_nested_value(data, "user.profile.name", "John")
        assert data["user"]["profile"]["name"] == "John"
        assert data["user"]["profile"]["age"] == 30


class TestSanitizeFilename:
    """Test cases for sanitize_filename function"""
    
    def test_sanitize_filename_normal(self):
        """Test sanitizing normal filename"""
        filename = "song_123.mp3"
        result = sanitize_filename(filename)
        assert result == "song_123.mp3"
    
    def test_sanitize_filename_dangerous_chars(self):
        """Test removing dangerous characters"""
        filename = "song<>:\"/\\|?*.mp3"
        result = sanitize_filename(filename)
        assert "<" not in result
        assert ">" not in result
        assert ":" not in result
        assert '"' not in result
        assert "/" not in result
        assert "\\" not in result
        assert "|" not in result
        assert "?" not in result
        assert "*" not in result
    
    def test_sanitize_filename_too_long(self):
        """Test truncating too long filename"""
        long_name = "a" * 300 + ".mp3"
        result = sanitize_filename(long_name)
        assert len(result) <= 255
        assert result.endswith(".mp3")
    
    def test_sanitize_filename_no_extension(self):
        """Test filename without extension"""
        filename = "song_file"
        result = sanitize_filename(filename)
        assert len(result) <= 255
    
    def test_sanitize_filename_unicode(self):
        """Test filename with unicode characters"""
        filename = "测试🎵.mp3"
        result = sanitize_filename(filename)
        assert isinstance(result, str)


class TestRetryOnFailure:
    """Test cases for retry_on_failure decorator"""
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_success_first_try(self):
        """Test function succeeds on first try"""
        call_count = 0
        
        @retry_on_failure(max_retries=3)
        async def test_func():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_succeeds_after_retries(self):
        """Test function succeeds after retries"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        async def test_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ValueError("Temporary error")
            return "success"
        
        result = await test_func()
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_exhausts_retries(self):
        """Test function fails after exhausting retries"""
        call_count = 0
        
        @retry_on_failure(max_retries=3, delay=0.1)
        async def test_func():
            nonlocal call_count
            call_count += 1
            raise ValueError("Persistent error")
        
        with pytest.raises(ValueError, match="Persistent error"):
            await test_func()
        
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_retry_on_failure_custom_delay(self):
        """Test retry with custom delay"""
        import time
        call_count = 0
        delays = []
        last_time = time.time()
        
        @retry_on_failure(max_retries=3, delay=0.2)
        async def test_func():
            nonlocal call_count, last_time
            call_count += 1
            current_time = time.time()
            if call_count > 1:
                delays.append(current_time - last_time)
            last_time = current_time
            if call_count < 2:
                raise ValueError("Error")
            return "success"
        
        await test_func()
        # Verify delay was applied (allowing some tolerance)
        assert len(delays) > 0










