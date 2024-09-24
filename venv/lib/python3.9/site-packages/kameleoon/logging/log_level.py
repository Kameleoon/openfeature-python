"""Log Level"""
from enum import IntEnum


class LogLevel(IntEnum):
    """Log Level"""
    NONE: int = 0
    ERROR: int = 1
    WARNING: int = 2
    INFO: int = 3
    DEBUG: int = 4
