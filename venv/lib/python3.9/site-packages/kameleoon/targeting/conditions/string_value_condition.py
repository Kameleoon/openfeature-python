"""Device condition"""
import re
from typing import Any, Dict, Optional, Union

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.constants import TargetingOperator
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class StringValueCondition(TargetingCondition):
    """
    String value condition should be used when you need to compare string values

    It should be used as parent class for other conditions
    """

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]], value: Optional[str]):
        super().__init__(json_condition)
        self._condition_value = value
        try:
            self._operator = TargetingOperator[str(json_condition["matchType"])]
        except KeyError as ex:
            KameleoonLogger.error("Unknown operation for %s condition, error: %s", self.type, ex)

    def check(self, data: Any) -> bool:
        return isinstance(data, str) and self._check(data)

    def _check(self, value: str) -> bool:
        if self._condition_value is None:
            return False

        if self._operator == TargetingOperator.EXACT:
            return value == self._condition_value

        if self._operator == TargetingOperator.CONTAINS:
            return self._condition_value in value

        if self._operator == TargetingOperator.REGULAR_EXPRESSION:
            try:
                pattern = re.compile(self._condition_value)
            except re.error:
                return False
            return bool(re.fullmatch(pattern, value))

        KameleoonLogger.error("Unexpected comparing operation for condition: %s", self._operator)
        return False
