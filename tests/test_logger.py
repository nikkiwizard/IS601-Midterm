import logging
from pathlib import Path

from app.logger import Logger


def test_logger_configure_and_helpers(tmp_path):
    log_file = tmp_path / "calculator.log"

    logger = Logger.configure(log_file)

    assert logger is not None
    assert logger.name == "calculator"

    Logger.info("info message")
    Logger.warning("warning message")
    Logger.error("error message")

    assert log_file.exists()


def test_logger_get_logger_returns_configured_instance(tmp_path):
    log_file = tmp_path / "nested" / "calculator.log"

    Logger.configure(log_file)
    logger = Logger.get_logger()

    assert logger is not None
    assert logger.name == "calculator"
    assert logger.level == logging.INFO


def test_logger_get_logger_initializes_when_unset():
    Logger._logger = None
    logger = Logger.get_logger()

    assert logger is not None
    assert logger.name == "calculator"
