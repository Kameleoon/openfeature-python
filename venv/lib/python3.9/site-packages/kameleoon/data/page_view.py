"""Page view"""

import json
from typing import List, Optional
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationSafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class PageView(Data, DuplicationSafeSendableBase):
    """Page view"""

    EVENT_TYPE = "page"

    def __init__(self, url: str, title: Optional[str], referrers: Optional[List[int]] = None) -> None:
        """
        :param url: Url of the page
        :type url: str
        :param title: Optional field - Title of the page
        :type title: Optional[str]
        :param referrers: Optional field - Referrer ids
        :type referrers: Optional[List[int]]

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
        """
        super().__init__()
        self.__url = url
        self.__title = title
        self.__referrers = referrers

    @property
    def url(self) -> str:
        """Returns URL"""
        return self.__url

    @property
    def title(self) -> Optional[str]:
        """Returns title"""
        return self.__title

    @property
    def referrers(self) -> Optional[List[int]]:
        """Returns referrer list"""
        return self.__referrers

    @property
    def data_type(self) -> DataType:
        return DataType.PAGE_VIEW

    def encode_query(self) -> str:
        return super().encode_query() if len(self.__url) > 0 else ""

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.HREF, self.url),
        )
        if self.title:
            query_builder.append(QueryParam(QueryParams.TITLE, self.title))
        if self.referrers:
            str_referrers = json.dumps(self.referrers, separators=(",", ":"))
            query_builder.append(QueryParam(QueryParams.REFERRERS_INDICES, str_referrers))

    def __str__(self):
        return (
            f"PageView{{url:'{self.url}',"
            f"title:'{self.title}',"
            f"referrers:{self.referrers}}}"
        )
