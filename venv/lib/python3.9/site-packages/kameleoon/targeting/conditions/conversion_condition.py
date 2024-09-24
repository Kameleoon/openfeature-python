"""Conversion condition"""
from typing import Any, Dict, List, Union
from kameleoon.data import Conversion
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class ConversionCondition(TargetingCondition):
    """Conversion condition uses in case if you need to target users by their conversion"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__goal_id = json_condition.get("goalId", TargetingCondition.NON_EXISTENT_IDENTIFIER)
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data: Any) -> bool:
        return isinstance(data, list) and self.__check(data)

    def __check(self, conversions: List[Conversion]) -> bool:
        # pylint: disable=R1706
        return ((self.__goal_id == TargetingCondition.NON_EXISTENT_IDENTIFIER) and len(conversions) > 0) or \
            any((isinstance(c, Conversion)) and (c.goal_id == self.__goal_id) for c in conversions)
