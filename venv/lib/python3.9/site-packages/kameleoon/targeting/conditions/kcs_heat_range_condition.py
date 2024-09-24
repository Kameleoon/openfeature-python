"""Device condition"""

from typing import Any, Dict, Union
from kameleoon.data.kcs_heat import KcsHeat
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class KcsHeatRangeCondition(TargetingCondition):
    """KCS heat range / Heat slice / AI predictive / Likelihood to convert"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        self.__goal_id = self.__get_json_value(json_condition, "goalId", int, -1)
        self.__key_moment_id = self.__get_json_value(json_condition, "keyMomentId", int, -1)
        # Goal score belongs to [0.0; 100.0] range
        self.__lower_bound = self.__get_json_value(json_condition, "lowerBound", (float, int), 101.0)
        self.__upper_bound = self.__get_json_value(json_condition, "upperBound", (float, int), -1.0)

    @staticmethod
    def __get_json_value(json_condition: Dict[str, Union[str, int, Any]], key: str, types, default):
        value = json_condition.get(key)
        return value if isinstance(value, types) else default

    def check(self, data: Any) -> bool:
        return isinstance(data, KcsHeat) and self.__check(data)

    def __check(self, kcs_heat: KcsHeat) -> bool:
        goal_scores = kcs_heat.values.get(self.__key_moment_id)
        if not isinstance(goal_scores, dict):
            return False
        score = goal_scores.get(self.__goal_id)
        return isinstance(score, (float, int)) and (self.__lower_bound <= score <= self.__upper_bound)
