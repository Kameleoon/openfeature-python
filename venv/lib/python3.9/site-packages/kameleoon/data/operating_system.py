# pylint: disable=duplicate-code
"""Operating system data"""

from enum import IntEnum
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class OperatingSystemType(IntEnum):
    """Operating system types"""

    WINDOWS: int = 0
    MAC: int = 1
    IOS: int = 2
    LINUX: int = 3
    ANDROID: int = 4
    WINDOWS_PHONE: int = 5


class OperatingSystem(Data, DuplicationUnsafeSendableBase):
    """Operating system data"""

    EVENT_TYPE = "staticData"

    def __init__(self, os_type: OperatingSystemType) -> None:
        """
        :param os_type: OperatingSystemType, can be: WINDOWS, MAC, IOS, LINUX, ANDROID, WINDOWS_PHONE
        :type os_type: OperatingSystemType

        Example:
        .. code-block:: python3
                kameleoon_client.add_data(visitor_code, OperatingSystem(OperatingSystemType.ANDROID))
        """
        super().__init__()
        self.__os_type = os_type

    @property
    def os_type(self) -> OperatingSystemType:
        """Returns operating system type"""
        return self.__os_type

    @property
    def data_type(self) -> DataType:
        return DataType.OPERATING_SYSTEM

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.OPERATING_SYSTEM, self.os_type.name),
            QueryParam(QueryParams.OPERATING_SYSTEM_INDEX, str(self.os_type.value)),
        )

    def __str__(self):
        return f"OperatingSystem{{os_type:{self.__os_type}}}"
