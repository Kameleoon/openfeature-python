""" Kameleoon data module"""
from enum import IntEnum
from typing import Any, Dict


class DataType(IntEnum):
    """Data types"""

    CUSTOM_DATA = 0
    BROWSER = 1
    CONVERSION = 2
    DEVICE = 3
    PAGE_VIEW = 4
    USER_AGENT = 5
    ASSIGNED_VARIATION = 6
    COOKIE = 7
    OPERATING_SYSTEM = 8
    GEOLOCATION = 9
    PAGE_VIEW_VISIT = 10
    VISITOR_VISITS = 11
    KCS_HEAT = 12
    UNIQUE_IDENTIFIER = 13


class BaseData:
    """Base data class"""

    @property
    def data_type(self) -> DataType:
        """Returns data type of the instance"""
        raise NotImplementedError

    def to_dict(self) -> Dict[str, Any]:
        """Convert class instance to dict"""
        return {k: str(v) for k, v in self.__dict__.items()}


class Data(BaseData):  # pylint: disable=W0223
    """Base external data class"""
