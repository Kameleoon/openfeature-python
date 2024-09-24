"""Variable"""
from typing import Any, Optional

from kameleoon.helpers.string_utils import StringUtils


class Variable:
    """Variable"""

    def __init__(self, key: str, type_: str, value: Optional[Any]):
        self.__key = key
        self.__type = type_
        self.__value = value

    @property
    def key(self) -> str:
        """Return key"""
        return self.__key

    @property
    def type(self) -> str:
        """Return type"""
        return self.__type

    @property
    def value(self) -> Optional[Any]:
        """Return value"""
        return self.__value

    def __str__(self):
        return (f"Variable{{key:'{self.__key}',"
                f"type:'{self.__type}',"
                f"value:{StringUtils.object_to_string(self.__value)}}}")
