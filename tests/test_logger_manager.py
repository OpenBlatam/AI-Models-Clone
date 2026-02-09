"""
Enhanced Tests for the Centralized Logging Management System
==========================================================

Test coverage for:
- Logger initialization and configuration
- Multiple log handlers and formatters
- Performance and specialized logging functions
- Log rotation and compression
- Error handling and context logging
- Performance monitoring decorators
"""

import pytest
import tempfile
import os
import json
import logging
import gzip
import time
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock
import sys

# Import the logging system
from core.logger_manager import (
    StructuredFormatter, ColoredFormatter, CompressedRotatingFileHandler,
    LoggerManager, get_logger, log_performance, log_api_request, 
    log_security_event, log_database_operation, log_cache_operation, 
    log_error_with_context, performance_logger
)


class TestStructuredFormatter:
    """Test structured JSON formatter"""
    
    def test_structured_formatter_basic(self):
        """Test basic structured formatting"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test_logger"
        assert log_data["message"] == "Test message"
        assert log_data["module"] == "test"
        assert "timestamp" in log_data
        assert "process_id" in log_data
        assert "thread_id" in log_data
    
    def test_structured_formatter_with_exception(self):
        """Test structured formatting with exception"""
        formatter = StructuredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Test error message",
                args=(),
                exc_info=sys.exc_info()
            )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["level"] == "ERROR"
        assert "exception" in log_data
        assert log_data["exception"]["type"] == "ValueError"
        assert log_data["exception"]["message"] == "Test error"
        assert "traceback" in log_data["exception"]
        assert log_data["severity"] == "high"
    
    def test_structured_formatter_with_extra_fields(self):
        """Test structured formatting with extra fields"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Add extra fields
        record.extra_fields = {
            "user_id": "123",
            "operation": "test",
            "metadata": {"key": "value"}
        }
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["user_id"] == "123"
        assert log_data["operation"] == "test"
        assert log_data["metadata"]["key"] == "value"
    
    def test_structured_formatter_warning_level(self):
        """Test structured formatting with warning level"""
        formatter = StructuredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="Warning message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        assert log_data["severity"] == "high"


class TestColoredFormatter:
    """Test colored console formatter"""
    
    def test_colored_formatter_basic(self):
        """Test basic colored formatting"""
        formatter = ColoredFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should contain color codes and basic structure
        assert "INFO" in formatted
        assert "test_logger" in formatted
        assert "Test message" in formatted
        assert "|" in formatted  # Separator
    
    def test_colored_formatter_with_exception(self):
        """Test colored formatting with exception"""
        formatter = ColoredFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            record = logging.LogRecord(
                name="test_logger",
                level=logging.ERROR,
                pathname="test.py",
                lineno=10,
                msg="Test error message",
                args=(),
                exc_info=sys.exc_info()
            )
        
        formatted = formatter.format(record)
        
        # Should contain exception info
        assert "ERROR" in formatted
        assert "Test error message" in formatted
        assert "ValueError" in formatted
    
    def test_colored_formatter_no_colors(self):
        """Test colored formatting without colors"""
        formatter = ColoredFormatter(use_colors=False)
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        
        # Should not contain color codes
        assert "\033[" not in formatted
        assert "INFO" in formatted
        assert "test_logger" in formatted


class TestCompressedRotatingFileHandler:
    """Test compressed rotating file handler"""
    
    @pytest.fixture
    def temp_log_file(self):
        """Create a temporary log file"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            yield f.name
        os.unlink(f.name)
    
    def test_compressed_rotating_file_handler_initialization(self, temp_log_file):
        """Test handler initialization"""
        handler = CompressedRotatingFileHandler(
            filename=temp_log_file,
            max_bytes=1024,
            backup_count=3,
            compress=True
        )
        
        assert handler.compress is True
        assert handler.backup_count == 3
        assert handler.baseFilename == temp_log_file
        
        handler.close()
    
    def test_compressed_rotating_file_handler_rollover(self, temp_log_file):
        """Test file rollover with compression"""
        handler = CompressedRotatingFileHandler(
            filename=temp_log_file,
            max_bytes=100,  # Small size to trigger rollover
            backup_count=2,
            compress=True
        )
        
        # Write enough data to trigger rollover
        for i in range(20):
            handler.emit(logging.LogRecord(
                name="test",
                level=logging.INFO,
                pathname="test.py",
                lineno=10,
                msg=f"Test message {i} " * 10,  # Long message
                args=(),
                exc_info=None
            ))
        
        handler.close()
        
        # Check that backup files were created
        base_name = temp_log_file
        assert os.path.exists(f"{base_name}.1.gz")
        assert os.path.exists(f"{base_name}.2.gz")


class TestLoggerManager:
    """Test logger manager"""
    
    @pytest.fixture
    def temp_logs_dir(self):
        """Create a temporary logs directory"""
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_dir:
            yield Path(temp_dir)
            
            # Clean up any remaining handlers to avoid file permission issues
            import logging
            root_logger = logging.getLogger()
            for handler in root_logger.handlers[:]:
                if hasattr(handler, 'close'):
                    try:
                        handler.close()
                    except:
                        pass
                try:
                    root_logger.removeHandler(handler)
                except:
                    pass
    
    @patch('core.logger_manager.get_config')
    def test_logger_manager_initialization(self, mock_get_config, temp_logs_dir):
        """Test logger manager initialization"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024  # 1MB
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        assert isinstance(logger_manager.logs_dir, Path)
        assert len(logger_manager.handlers) > 0
        assert len(logger_manager.loggers) > 0
        assert logger_manager.performance_logger is not None
        assert logger_manager.api_logger is not None
        assert logger_manager.security_logger is not None
        assert logger_manager.database_logger is not None
        assert logger_manager.cache_logger is not None
        assert logger_manager.error_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_get_logger(self, mock_get_config, temp_logs_dir):
        """Test getting logger"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        logger = logger_manager.get_logger("test_logger")
        
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_logger"
        
        # Test that same logger is returned for same name
        logger2 = logger_manager.get_logger("test_logger")
        assert logger is logger2
    
    @patch('core.logger_manager.get_config')
    def test_log_performance(self, mock_get_config, temp_logs_dir):
        """Test performance logging"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test performance logging
        logger_manager.log_performance("test_operation", 0.125, table="users", rows=100)
        
        # Check that performance logger exists and was used
        assert "performance" in logger_manager.loggers
        assert logger_manager.performance_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_log_api_request(self, mock_get_config, temp_logs_dir):
        """Test API request logging"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test API request logging
        logger_manager.log_api_request("GET", "/api/users", 200, 0.045, user_id="123")
        
        # Check that API logger exists
        assert "api" in logger_manager.loggers
        assert logger_manager.api_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_log_security_event(self, mock_get_config, temp_logs_dir):
        """Test security event logging"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test security event logging
        logger_manager.log_security_event("login_failed", "Invalid credentials", ip_address="192.168.1.1")
        
        # Check that security logger exists
        assert "security" in logger_manager.loggers
        assert logger_manager.security_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_log_database_operation(self, mock_get_config, temp_logs_dir):
        """Test database operation logging"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test database operation logging
        logger_manager.log_database_operation("SELECT", "users", 0.125, rows_affected=100)
        
        # Check that database logger exists
        assert "database" in logger_manager.loggers
        assert logger_manager.database_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_log_cache_operation(self, mock_get_config, temp_logs_dir):
        """Test cache operation logging"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test cache operation logging
        logger_manager.log_cache_operation("GET", "user:123", True, 0.001)
        
        # Check that cache logger exists
        assert "cache" in logger_manager.loggers
        assert logger_manager.cache_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_log_error_with_context(self, mock_get_config, temp_logs_dir):
        """Test error logging with context"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Test error logging with context
        error = ValueError("Test error")
        context = {"user_id": "123", "operation": "test"}
        logger_manager.log_error_with_context(error, context, logger_name="error")
        
        # Check that error logger exists
        assert "error" in logger_manager.loggers
        assert logger_manager.error_logger is not None
    
    @patch('core.logger_manager.get_config')
    def test_get_log_stats(self, mock_get_config, temp_logs_dir):
        """Test getting log statistics"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        stats = logger_manager.get_log_stats()
        
        assert "total_loggers" in stats
        assert "total_handlers" in stats
        assert "log_level" in stats
        assert "log_file" in stats
        assert "max_log_size" in stats
        assert "backup_logs" in stats
        assert "environment" in stats
        assert "debug_mode" in stats
        assert "logs_directory" in stats
        assert "handlers" in stats
        assert "specialized_loggers" in stats
    
    @patch('core.logger_manager.get_config')
    def test_cleanup_old_logs(self, mock_get_config, temp_logs_dir):
        """Test cleanup of old log files"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Create some old log files
        old_log = temp_logs_dir / "old.log"
        old_log.write_text("old content")
        
        # Set old modification time
        old_time = time.time() - (31 * 24 * 3600)  # 31 days ago
        os.utime(old_log, (old_time, old_time))
        
        # Clean up old logs
        logger_manager.cleanup_old_logs(max_age_days=30)
        
        # Check that old log was removed
        assert not old_log.exists()
    
    @patch('core.logger_manager.get_config')
    def test_rotate_logs(self, mock_get_config, temp_logs_dir):
        """Test manual log rotation"""
        # Mock configuration
        mock_config = MagicMock()
        mock_config.system.log_file = str(temp_logs_dir / "test.log")
        mock_config.system.max_log_size = 1024 * 1024
        mock_config.system.backup_logs = 3
        mock_config.monitoring.log_level = "INFO"
        mock_config.monitoring.enable_metrics = True
        mock_config.system.debug = False
        mock_get_config.return_value = mock_config
        
        logger_manager = LoggerManager()
        
        # Manual log rotation should not raise errors
        logger_manager.rotate_logs()


class TestConvenienceFunctions:
    """Test convenience functions"""
    
    @patch('core.logger_manager._logger_manager')
    def test_get_logger(self, mock_logger_manager):
        """Test get_logger convenience function"""
        mock_logger = MagicMock()
        mock_logger_manager.get_logger.return_value = mock_logger
        
        logger = get_logger("test_logger")
        
        assert logger == mock_logger
        mock_logger_manager.get_logger.assert_called_once_with("test_logger")
    
    @patch('core.logger_manager._logger_manager')
    def test_log_performance(self, mock_logger_manager):
        """Test log_performance convenience function"""
        log_performance("test_operation", 0.125, table="users", rows=100)
        
        mock_logger_manager.log_performance.assert_called_once_with(
            "test_operation", 0.125, table="users", rows=100
        )
    
    @patch('core.logger_manager._logger_manager')
    def test_log_api_request(self, mock_logger_manager):
        """Test log_api_request convenience function"""
        log_api_request("GET", "/api/users", 200, 0.045, "123")

        mock_logger_manager.log_api_request.assert_called_once_with(
            "GET", "/api/users", 200, 0.045, "123"
        )
    
    @patch('core.logger_manager._logger_manager')
    def test_log_security_event(self, mock_logger_manager):
        """Test log_security_event convenience function"""
        log_security_event("login_failed", "Invalid credentials", ip_address="192.168.1.1")
        
        mock_logger_manager.log_security_event.assert_called_once_with(
            "login_failed", "Invalid credentials", None, "192.168.1.1"
        )
    
    @patch('core.logger_manager._logger_manager')
    def test_log_database_operation(self, mock_logger_manager):
        """Test log_database_operation convenience function"""
        log_database_operation("SELECT", "users", 0.125, rows_affected=100)
        
        mock_logger_manager.log_database_operation.assert_called_once_with(
            "SELECT", "users", 0.125, 100
        )
    
    @patch('core.logger_manager._logger_manager')
    def test_log_cache_operation(self, mock_logger_manager):
        """Test log_cache_operation convenience function"""
        log_cache_operation("GET", "user:123", True, 0.001)
        
        mock_logger_manager.log_cache_operation.assert_called_once_with(
            "GET", "user:123", True, 0.001
        )
    
    @patch('core.logger_manager._logger_manager')
    def test_log_error_with_context(self, mock_logger_manager):
        """Test log_error_with_context convenience function"""
        error = ValueError("Test error")
        context = {"user_id": "123", "operation": "test"}
        log_error_with_context(error, context, logger_name="error")
        
        mock_logger_manager.log_error_with_context.assert_called_once_with(
            error, context, "error"
        )


class TestPerformanceLoggerDecorator:
    """Test performance logger decorator"""
    
    @patch('core.logger_manager.log_performance')
    def test_performance_logger_decorator_success(self, mock_log_performance):
        """Test performance logger decorator with successful execution"""
        
        @performance_logger
        def test_function():
            time.sleep(0.001)  # Small delay
            return "success"
        
        result = test_function()
        
        assert result == "success"
        mock_log_performance.assert_called_once()
        
        # Check that the call includes the function name
        call_args = mock_log_performance.call_args[0]
        assert "test_function" in call_args[0]
        assert call_args[1] > 0  # Duration should be positive
    
    @patch('core.logger_manager.log_performance')
    def test_performance_logger_decorator_exception(self, mock_log_performance):
        """Test performance logger decorator with exception"""
        
        @performance_logger
        def test_function():
            time.sleep(0.001)
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            test_function()
        
        # Should still log performance with error
        assert mock_log_performance.call_count == 1
        
        # Check that error was logged
        call_args = mock_log_performance.call_args[0]
        assert "test_function" in call_args[0]
        assert call_args[1] > 0  # Duration should be positive


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
