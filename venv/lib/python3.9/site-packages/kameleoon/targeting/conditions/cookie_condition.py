"""Cookie condition"""

from typing import Any, Dict, Union, Generator
from kameleoon.data.cookie import Cookie
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.constants import TargetingOperator
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class CookieCondition(TargetingCondition):
    """Cookie condition uses in case if you need to target by value in cookie"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__condition_name = str(json_condition.get("name", None))
            self.__name_match_type = TargetingOperator[str(json_condition.get("nameMatchType"))]
            self.__condition_value = str(json_condition.get("value", None))
            self.__value_match_type = TargetingOperator[str(json_condition.get("valueMatchType"))]
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return isinstance(data, Cookie) and self.__check_values(self.__select_values(data))

    # pylint: disable=R0911
    def __select_values(self, cookie: Cookie):
        if self.__name_match_type == TargetingOperator.EXACT:
            value = cookie.cookies.get(self.__condition_name)
            if value is not None:
                return [value]
        elif self.__name_match_type == TargetingOperator.CONTAINS:
            return (value for key, value in cookie.cookies.items() if self.__condition_name in key)
        elif self.__name_match_type == TargetingOperator.REGULAR_EXPRESSION:
            return (value for key, value in cookie.cookies.items() if self._is_regex_math(self.__condition_name, key))
        else:
            KameleoonLogger.error(
                "Unexpected comparing operation for Cookie condition (name): %s",
                self.__class__,
            )
        return []

    def __check_values(self, values: Generator[str, Any, None]) -> bool:
        if self.__value_match_type == TargetingOperator.EXACT:
            return any(value == self.__condition_value for value in values)
        if self.__value_match_type == TargetingOperator.CONTAINS:
            return any(self.__condition_value in value for value in values)
        if self.__value_match_type == TargetingOperator.REGULAR_EXPRESSION:
            return any(self._is_regex_math(self.__condition_value, value) for value in values)
        KameleoonLogger.error(
            "Unexpected comparing operation for Cookie condition (name): %s",
            self.__class__,
        )
        return False
