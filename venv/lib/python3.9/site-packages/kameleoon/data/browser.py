"""Browser data"""

from enum import IntEnum
from typing import Optional
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class BrowserType(IntEnum):
    """Browser types"""

    CHROME: int = 0
    INTERNET_EXPLORER: int = 1
    FIREFOX: int = 2
    SAFARI: int = 3
    OPERA: int = 4
    OTHER: int = 5


class Browser(Data, DuplicationUnsafeSendableBase):
    """Browser data"""

    EVENT_TYPE = "staticData"

    def __init__(self, browser_type: BrowserType, version: Optional[float] = None) -> None:
        """
        :param browser_type: BrowserType, can be: CHROME, INTERNET_EXPLORER, FIREFOX, SAFARI, OPERA, OTHER

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
        """
        super().__init__()
        self.__browser_type = browser_type
        self.__version = version

    @property
    def browser_type(self) -> BrowserType:
        """Returns browser type"""
        return self.__browser_type

    @property
    def version(self) -> Optional[float]:
        """Returns version"""
        return self.__version

    @property
    def data_type(self) -> DataType:
        return DataType.BROWSER

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.BROWSER_INDEX, str(self.browser_type.value)),
        )
        if self.version:
            query_builder.append(QueryParam(QueryParams.BROWSER_VERSION, str(self.version)))

    def __str__(self):
        return (
            f"Browser{{browser_type:{self.__browser_type},"
            f"version:{self.__version}}}"
        )
