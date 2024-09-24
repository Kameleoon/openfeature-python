"""Logger"""
import logging
from kameleoon.logging.log_level import LogLevel


class Logger:
    """
    Logger
    A base class for logging messages at different log levels.
    """
    def log(self, level: LogLevel, message: str) -> None:
        """Logs a message at the specified log level."""
        raise NotImplementedError("Subclasses must implement log(level, message)")


class DefaultLogger(Logger):
    """
    A default logger implementation that uses Python's built-in logging module.

    This class extends the base `Logger` class and implements the `log` method
    to delegate logging to a standard Python logger provided during initialization.
    """
    def __init__(self, inner_logger: logging.Logger) -> None:
        """Initializes the DefaultLogger with a standard Python logger."""
        self._inner_logger = inner_logger

    def log(self, level: LogLevel, message: str) -> None:
        """Logs a message with the given log level using the standard Python logger."""
        if level == LogLevel.ERROR:
            self._inner_logger.error(message)
        elif level == LogLevel.WARNING:
            self._inner_logger.warning(message)
        elif level == LogLevel.INFO:
            self._inner_logger.info(message)
        elif level == LogLevel.DEBUG:
            self._inner_logger.debug(message)
