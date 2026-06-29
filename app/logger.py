########################
# Logger Utility       #
########################

import logging
from pathlib import Path
from typing import Optional


class Logger:
    """
    Utility wrapper around Python's logging module.

    Provides a consistent interface for configuring and using the calculator's
    logger throughout the application.
    """

    _logger: Optional[logging.Logger] = None

    @classmethod
    def configure(cls, log_file: Path, level: int = logging.INFO) -> logging.Logger:
        """
        Configure and return the shared logger.

        Args:
            log_file (Path): File path for log output.
            level (int): Logging level to use.

        Returns:
            logging.Logger: Configured logger instance.
        """
        log_file.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(
            filename=str(log_file),
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            force=True,
        )
        logger = logging.getLogger("calculator")
        logger.setLevel(level)
        logger.propagate = False
        cls._logger = logger
        return logger

    @classmethod
    def get_logger(cls) -> logging.Logger:
        """
        Return the configured shared logger.

        Returns:
            logging.Logger: Shared logger instance.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger("calculator")
        return cls._logger

    @classmethod
    def info(cls, message: str) -> None:
        logging.info(message)

    @classmethod
    def warning(cls, message: str) -> None:
        logging.warning(message)

    @classmethod
    def error(cls, message: str) -> None:
        logging.error(message)
