from src.thebot.core.logger import logger
"""
Tests unitaires pour StructuredLogger et ContextLogger - Phase 4
"""

import pytest
import logging
import json
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
from dash_modules.core.structured_logger import StructuredLogger, ContextLogger, StructuredFormatter


class TestStructuredFormatter:
    """Tests pour le formatter structuré"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.formatter = StructuredFormatter()

    def test_format_basic(self):
        """Test formatage basique"""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )

        result = self.formatter.format(record)
        parsed = json.loads(result)

        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test.logger"
        assert parsed["message"] == "Test message"
        assert "timestamp" in parsed

    def test_format_with_extra_fields(self):
        """Test formatage avec champs extra"""
        record = logging.LogRecord(
            name="test.logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=None
        )
        record.extra_fields = {"user_id": 123, "action": "login"}

        result = self.formatter.format(record)
        parsed = json.loads(result)

        assert parsed["level"] == "ERROR"
        assert parsed["user_id"] == 123
        assert parsed["action"] == "login"


class TestStructuredLogger:
    """Tests pour le logger structuré"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.logger = StructuredLogger(app_name="test_app", log_level="DEBUG")

    @patch('dash_modules.core.structured_logger.logging')
    def test_init(self, mock_logging):
        """Test initialisation du logger structuré"""
        # Configurer le mock pour retourner la valeur numérique correcte
        mock_logging.INFO = 20
        
        logger = StructuredLogger(app_name="myapp", log_level="INFO")

        assert logger.app_name == "myapp"
        assert logger.log_level == 20  # logging.INFO
        assert logger._loggers == {}

    @patch('dash_modules.core.structured_logger.logging')
    def test_get_logger_new(self, mock_logging):
        """Test récupération d'un nouveau logger"""
        # Configurer le root logger (logging.getLogger() sans argument)
        mock_root_logger = Mock()
        mock_root_logger.handlers = []
        
        # Configurer le logger spécifique
        mock_base_logger = Mock()
        
        def get_logger_side_effect(name=None):
            if name is None:  # root logger
                return mock_root_logger
            else:  # named logger
                return mock_base_logger
        
        mock_logging.getLogger.side_effect = get_logger_side_effect

        logger = StructuredLogger()
        context_logger = logger.get_logger("test")

        assert "test" in logger._loggers
        assert isinstance(context_logger, ContextLogger)
        mock_logging.getLogger.assert_called_with("thebot.test")

    def test_get_logger_existing(self):
        """Test récupération d'un logger existant"""
        logger = StructuredLogger()
        context_logger1 = logger.get_logger("test")
        context_logger2 = logger.get_logger("test")

        assert context_logger1 is context_logger2
        assert "test" in logger._loggers

    def test_get_stats(self):
        """Test récupération des statistiques"""
        logger = StructuredLogger(app_name="myapp", log_level="INFO")
        stats = logger.get_stats()

        assert stats["log_level"] == "INFO"
        assert stats["active_loggers"] == []


class TestContextLogger:
    """Tests pour le logger de contexte"""

    def setup_method(self):
        """Configuration avant chaque test"""
        self.mock_logger = Mock()
        self.context_logger = ContextLogger(self.mock_logger)

    def test_info(self):
        """Test log info"""
        self.context_logger.info("Test message", extra={"user_id": 123})

        self.mock_logger.handle.assert_called_once()
        call_args = self.mock_logger.handle.call_args
        record = call_args[0][0]
        assert record.levelno == logging.INFO
        assert record.getMessage() == "Test message"
        assert record.extra_fields["user_id"] == 123

    def test_error(self):
        """Test log error"""
        self.context_logger.error("Error message", extra={"error_code": 500})

        self.mock_logger.handle.assert_called_once()
        call_args = self.mock_logger.handle.call_args
        record = call_args[0][0]
        assert record.levelno == logging.ERROR
        assert record.getMessage() == "Error message"
        assert record.extra_fields["error_code"] == 500

    def test_debug(self):
        """Test log debug"""
        self.context_logger.debug("Debug message")

        self.mock_logger.handle.assert_called_once()
        call_args = self.mock_logger.handle.call_args
        record = call_args[0][0]
        assert record.levelno == logging.DEBUG
        assert record.getMessage() == "Debug message"
