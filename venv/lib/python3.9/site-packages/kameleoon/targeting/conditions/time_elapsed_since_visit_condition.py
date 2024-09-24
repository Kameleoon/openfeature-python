"""Time elapsed since visit condition"""

import time
from typing import Any, Dict, Union, Optional
from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.targeting.conditions.targeting_condition import TargetingConditionType
from kameleoon.targeting.conditions.number_condition import NumberCondition


class TimeElapsedSinceVisitCondition(NumberCondition):
    """Time elapsed since visit condition"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition, "countInMillis")
        self.__is_first_visit = self.type == TargetingConditionType.FIRST_VISIT.name

    def check(self, data: Optional[VisitorVisits]) -> bool:
        return self._condition_value is not None and self.__check(data)

    def __check(self, visitor_visits: Optional[VisitorVisits]) -> bool:
        timestamps = VisitorVisits.get_previous_visit_timestamps(visitor_visits)
        if len(timestamps) < 1:
            return False

        now = int(time.time() * 1000)  # Convert seconds to milliseconds
        visit_time = timestamps[-1 if self.__is_first_visit else 0]
        return self._check_targeting(now - visit_time)
