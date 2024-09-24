"""Kameleoon Configuration"""

from enum import Enum
from typing import Any, List, Dict, Optional

from kameleoon.configuration.variable import Variable
from kameleoon.helpers.string_utils import StringUtils


class Variation:
    """
    Variation is used for saving variations of feature flags (v2) with rules
    """

    class Type(Enum):
        """Possible types of variations"""
        OFF = "off"

    @staticmethod
    def from_array(array: List[Dict[str, Any]]) -> List["Variation"]:
        """Creates a list of Varations from array of dictionaries"""
        return [Variation(item) for item in array]

    def __init__(self, dict_json: Dict[str, Any]):
        self.key: str = dict_json.get("key", "")
        self.variables: List[Variable] = Variable.from_array(
            dict_json.get("variables", [])
        )

    def get_variable_by_key(self, key: str) -> Optional[Variable]:
        """Retrun a variable for the given key"""
        return next((v for v in self.variables if v.key == key), None)

    def __str__(self):
        return (f"Variation{{key:'{self.key}',"
                f"variables:{StringUtils.object_to_string(self.variables)}}}")
