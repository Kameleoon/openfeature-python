"""Kameleoon Configuration"""

from enum import Enum
import json
from typing import Any, List, Dict, Union

from kameleoon.helpers.string_utils import StringUtils


class Variable:
    """
    Variable is used for saving variables of variations of feature flags (v2) with rules
    """

    class Type(Enum):
        """Possible types of variables"""

        BOOLEAN = "BOOLEAN"
        JSON = "JSON"
        NUMBER = "NUMBER"
        STRING = "STRING"

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["Variable"]:
        """Create a list of variables from the json array"""
        return [Variable(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.key: str = dict_json.get("key", "")
        self.__type: str = dict_json.get("type", "")
        self.__value: Union[bool, float, str] = dict_json.get("value", False)

    def get_value(self) -> Union[bool, float, str, List[Any], Dict[str, Any], None]:
        """Returns a bare value of variable"""
        if self.__type in (
            Variable.Type.BOOLEAN.value,
            Variable.Type.NUMBER.value,
            Variable.Type.STRING.value,
        ):
            return self.__value
        if self.__type == Variable.Type.JSON.value and isinstance(self.__value, str):
            return json.loads(self.__value)
        return None

    def get_type(self) -> str:
        """Returns type value of variable"""
        return self.__type

    def __str__(self):
        return (f"Variable{{key:'{self.key},"
                f"type:'{self.__type}',"
                f"value:{StringUtils.object_to_string(self.__value)}}}")
