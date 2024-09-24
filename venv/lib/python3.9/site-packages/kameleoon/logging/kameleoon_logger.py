"""Kameleoon Logger"""
from typing import Any, Union, Callable

from kameleoon import logging
from kameleoon.helpers.string_utils import StringUtils
from kameleoon.logging.log_level import LogLevel
from kameleoon.helpers.logger import Logger
from kameleoon.logging.logger import DefaultLogger


class KameleoonLogger:
    """Kameleoon Logger"""
    _logger: logging.logger.Logger = DefaultLogger(Logger.shared())
    _log_level: LogLevel = LogLevel.WARNING

    @staticmethod
    def log(level: LogLevel, data: Union[str, Callable[[], str]], *args: Any) -> None:
        """Logs a message at a specific log level."""
        if not KameleoonLogger._check_level(level):
            return

        if callable(data):
            message = data()
        elif args:
            try:
                message = data % tuple(StringUtils.object_to_string(arg) for arg in args)
            except TypeError:
                message = data
        else:
            message = data

        KameleoonLogger._write_message(level, message)

    @staticmethod
    def info(data: Union[str, Callable[[], str]], *args: Any) -> None:
        """Logs a message at a INFO log level."""
        KameleoonLogger.log(LogLevel.INFO, data, *args)

    @staticmethod
    def error(data: Union[str, Callable[[], str]], *args: Any) -> None:
        """Logs a message at a ERROR log level."""
        KameleoonLogger.log(LogLevel.ERROR, data, *args)

    @staticmethod
    def warning(data: Union[str, Callable[[], str]], *args: Any) -> None:
        """Logs a message at a WARNING log level."""
        KameleoonLogger.log(LogLevel.WARNING, data, *args)

    @staticmethod
    def debug(data: Union[str, Callable[[], str]], *args: Any) -> None:
        """Logs a message at a DEBUG log level."""
        KameleoonLogger.log(LogLevel.DEBUG, data, *args)

    @staticmethod
    def _check_level(level: LogLevel) -> bool:
        return level <= KameleoonLogger._log_level and level != LogLevel.NONE

    @staticmethod
    def _write_message(level: LogLevel, message: str) -> None:
        KameleoonLogger._logger.log(level, f"Kameleoon [{level.name}]: {message}")

    @staticmethod
    def set_logger(logger: logging.logger.Logger) -> None:
        """Sets the logger instance to be used by KameleoonLogger."""
        KameleoonLogger._logger = logger

    @staticmethod
    def set_log_level(level: LogLevel) -> None:
        """Sets the log level for KameleoonLogger."""
        KameleoonLogger._log_level = level
