"""CustomData condition"""
import re
import json
from typing import Any, Union, Dict, Optional
from kameleoon.data import CustomData
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition
from kameleoon.targeting.conditions.constants import TargetingOperator

__all__ = [
    "CustomDatum",
]


class CustomDatum(TargetingCondition):
    """CustomDatum represents a Custom Data condition from back-office"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition)
        try:
            str_index = json_condition["customDataIndex"]
            self.__index = int(str_index) if str_index.isnumeric() else -1
            self.__operator = TargetingOperator[json_condition["valueMatchType"]]
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)
        self.value = json_condition.get("value", None)
        self.__op_func = {
            TargetingOperator.UNDEFINED: self.__op_undefined,
            TargetingOperator.REGULAR_EXPRESSION: self.__op_regular_expression,
            TargetingOperator.CONTAINS: self.__op_contains,
            TargetingOperator.EXACT: self.__op_exact,
            TargetingOperator.EQUAL: self.__op_equal,
            TargetingOperator.GREATER: self.__op_greater,
            TargetingOperator.LOWER: self.__op_lower,
            TargetingOperator.TRUE: self.__op_true,
            TargetingOperator.FALSE: self.__op_false,
            TargetingOperator.AMONG_VALUES: self.__op_among_values,
        }[self.__operator]

    def check(self, data: Any) -> bool:  # noqa: C901
        if isinstance(data, dict):
            custom_data = data.get(self.__index)
            return self.__check(custom_data)
        return False

    # pylint: disable=R0912,R0915
    def __check(self, custom_data: Optional[CustomData]) -> bool:  # noqa: C901
        if isinstance(custom_data, CustomData):
            try:
                return self.__op_func(custom_data)
            except Exception as err:  # pylint: disable=W0703
                KameleoonLogger.error("Error occurred in check for CustomData condition: %s", err)
        else:
            return self.__operator == TargetingOperator.UNDEFINED
        return False

    def __op_undefined(self, custom_data: CustomData) -> bool:  # pylint: disable=R0201,W0613
        return False

    def __op_regular_expression(self, custom_data: CustomData) -> bool:
        pattern = re.compile(self.value)
        return any(re.fullmatch(pattern, val) is not None for val in custom_data.values)

    def __op_contains(self, custom_data: CustomData) -> bool:
        return any(self.value in val for val in custom_data.values)

    def __op_exact(self, custom_data: CustomData) -> bool:
        return self.value in custom_data.values

    def __op_equal(self, custom_data: CustomData) -> bool:
        epsilon = 1e-9
        value = float(self.value)
        return any(abs(float(val) - value) < epsilon for val in custom_data.values)

    def __op_greater(self, custom_data: CustomData) -> bool:
        value = float(self.value)
        return any(float(val) > value for val in custom_data.values)

    def __op_lower(self, custom_data: CustomData) -> bool:
        value = float(self.value)
        return any(float(val) < value for val in custom_data.values)

    def __op_true(self, custom_data: CustomData) -> bool:  # pylint: disable=R0201
        return "true" in custom_data.values

    def __op_false(self, custom_data: CustomData) -> bool:  # pylint: disable=R0201
        return "false" in custom_data.values

    def __op_among_values(self, custom_data: CustomData) -> bool:
        all_matches = json.loads(self.value)
        parse_dict = {False: "false", True: "true"}
        condtition_values = {parse_dict.get(m, str(m)) for m in all_matches}
        return any(val in condtition_values for val in custom_data.values)
