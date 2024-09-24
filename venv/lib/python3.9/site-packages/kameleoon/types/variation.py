"""Variation"""
from typing import Optional, Dict

from kameleoon.helpers.string_utils import StringUtils
from kameleoon.types.variable import Variable


class Variation:
    """Variation"""

    def __init__(self, key: str, id_: Optional[int], experiment_id: Optional[int],
                 variables: Dict[str, Variable]):
        self.__key = key
        self.__id = id_
        self.__experiment_id = experiment_id
        self.__variables = variables

    @property
    def key(self) -> str:
        """Return key of variation"""
        return self.__key

    @property
    def id_(self) -> Optional[int]:
        """Return id"""
        return self.__id

    @property
    def experiment_id(self) -> Optional[int]:
        """Return id of experiment"""
        return self.__experiment_id

    @property
    def variables(self) -> Dict[str, Variable]:
        """Return variables"""
        return self.__variables

    def __str__(self):
        return (f"Variation{{key:'{self.__key}',"
                f"experiment_id:{self.__experiment_id},"
                f"variables:{StringUtils.object_to_string(self.__variables)}}}")
