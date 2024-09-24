"""Visitor new return condition"""

from enum import Enum
from typing import Any, Dict, Union

from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class VisitorType(Enum):
    """Visitor types"""

    NEW: str = "NEW"
    RETURNING: str = "RETURNING"


class VisitorNewReturnCondition(TargetingCondition):
    """Visitor new return condition"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__visitor_type = VisitorType[str(json_condition.get("visitorType", "")).upper()]
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data: VisitorVisits) -> bool:
        count_timestamps = len(VisitorVisits.get_previous_visit_timestamps(data))
        if self.__visitor_type == VisitorType.NEW:
            return count_timestamps == 0
        return count_timestamps > 0
