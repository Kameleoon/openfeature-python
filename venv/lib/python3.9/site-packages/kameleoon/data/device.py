# pylint: disable=duplicate-code
"""Device data"""

from enum import Enum
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class DeviceType(Enum):
    """Device types"""

    PHONE: str = "PHONE"
    TABLET: str = "TABLET"
    DESKTOP: str = "DESKTOP"


class Device(Data, DuplicationUnsafeSendableBase):
    """Device data"""

    EVENT_TYPE = "staticData"

    def __init__(self, device_type: DeviceType) -> None:
        """
        :param device_type: DeviceType, can be: PHONE, TABLET, DESKTOP

        Example:
        .. code-block:: python3
                kameleoon_client.add_data(visitor_code, Device(DeviceType.PHONE))
        """
        super().__init__()
        self.__device_type = device_type

    @property
    def device_type(self) -> DeviceType:
        """Returns device type"""
        return self.__device_type

    @property
    def data_type(self) -> DataType:
        return DataType.DEVICE

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.DEVICE_TYPE, self.device_type.value),
        )

    def __str__(self):
        return f"Device{{device_type:{self.__device_type}}}"
