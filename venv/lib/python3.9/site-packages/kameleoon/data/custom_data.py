"""Custom data"""

import json
from typing import Tuple
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class CustomData(Data, DuplicationUnsafeSendableBase):
    """Custom data"""

    EVENT_TYPE = "customData"

    def __init__(self, id: int, *args: str) -> None:
        """
        :param id: Index / ID of the custom data to be stored. This field is mandatory.
        :type id: int
        :param `*args`: Values of the custom data to be stored. This field is optional.
        :type `*args`: str

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, CustomData(123, "some-value"))
        """
        # pylint: disable=invalid-name,redefined-builtin
        super().__init__()
        # pylint: disable=W0511
        self.__id = id
        self.__values = args

    @property
    def id(self) -> int:  # pylint: disable=C0103
        """Returns ID"""
        return self.__id

    @property
    def values(self) -> Tuple[str, ...]:
        """Stored values."""
        return self.__values

    @property
    def data_type(self) -> DataType:
        return DataType.CUSTOM_DATA

    def encode_query(self) -> str:
        return super().encode_query() if len(self.__values) > 0 else ""

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        str_values = json.dumps({v: 1 for v in self.__values}, separators=(",", ":"))
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE, False),
            QueryParam(QueryParams.INDEX, str(self.id), False),
            QueryParam(QueryParams.VALUES_COUNT_MAP, str_values),
            QueryParam(QueryParams.OVERWRITE, "true", False),
        )

    def __str__(self):
        return (
            f"CustomData{{id:{self.__id},"
            f"values:{self.__values}}}"
        )
