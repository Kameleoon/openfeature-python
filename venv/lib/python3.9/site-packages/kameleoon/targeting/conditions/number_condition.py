"""Number condition"""

from typing import Any, Dict, Union

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.constants import TargetingOperator
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class NumberCondition(TargetingCondition):
    """Number condition uses in case if you need to target by value numeric"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]], value_key: str):
        super().__init__(json_condition)
        try:
            self._match_type = TargetingOperator[str(json_condition.get("matchType"))]
            self._condition_value = json_condition.get(value_key)
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return self._check_targeting(data)

    def _check_targeting(self, value: Any) -> bool:
        if self._match_type == TargetingOperator.EQUAL:
            return value == self._condition_value
        if self._match_type == TargetingOperator.GREATER:
            return self._condition_value is not None and value > self._condition_value
        if self._match_type == TargetingOperator.LOWER:
            return self._condition_value is not None and value < self._condition_value
        KameleoonLogger.error(
            "Unexpected comparing operation for %s condition: %s",
            self.__class__,
            self._match_type,
        )
        return False
