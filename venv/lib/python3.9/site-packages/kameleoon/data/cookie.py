"""Cookie data"""

from typing import Dict
from kameleoon.data.data import Data, DataType


class Cookie(Data):
    """Cookie data"""

    def __init__(self, cookies: Dict[str, str]) -> None:
        """
        :param cookies: values cookie from visitor
        :type cookies: Dict[str, str]

        Example:
        .. code-block:: python3
                kameleoon_client.add_data(visitor_code, Cookie({'key1' : 'value1'}))
        """
        super().__init__()
        self.__cookies = cookies

    @property
    def cookies(self) -> Dict[str, str]:
        """
        :return: cookie values
        :rtype: Dict[str, str]
        """
        return self.__cookies

    @property
    def data_type(self) -> DataType:
        return DataType.COOKIE

    def __str__(self):
        return f"Cookie{{cookies:{self.__cookies}}}"
