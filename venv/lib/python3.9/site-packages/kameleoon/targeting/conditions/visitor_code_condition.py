""" condition"""
from typing import Any, Union, Dict

from kameleoon.targeting.conditions.string_value_condition import StringValueCondition


class VisitorCodeCondition(StringValueCondition):
    """Visitor condition uses when you need to compare visitor code value"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition, json_condition.get("visitorCode"))
