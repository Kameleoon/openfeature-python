"""KCS heat"""

from typing import Dict
from kameleoon.data import DataType
from kameleoon.data.data import BaseData


class KcsHeat(BaseData):
    """KCS heat"""

    def __init__(self, values: Dict[int, Dict[int, float]]) -> None:
        super().__init__()
        self.__values = values

    @property
    def values(self) -> Dict[int, Dict[int, float]]:
        """Returns goal scores stored by goal IDs within dictionaries stored by key moment IDs within a dictionary"""
        return self.__values

    @property
    def data_type(self) -> DataType:
        return DataType.KCS_HEAT

    def __str__(self):
        return f"KcsHeat{{values:{self.__values}}}"
