"""Visit number today condition"""

from typing import Any, Dict, Union, Optional
from datetime import datetime
from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.targeting.conditions.number_condition import NumberCondition


class VisitNumberTodayCondition(NumberCondition):
    """Visit number today condition uses in case if you need to target by value numeric"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition, "visitCount")

    def check(self, data: Optional[VisitorVisits]) -> bool:
        return self.__check(data)

    def __check(self, visitor_visits: Optional[VisitorVisits]) -> bool:
        if self._condition_value is None:
            return False
        number_of_visits_today = 0
        start_of_day = int(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000)
        # ... * 1000 for convert seconds to milliseconds
        for timestamp in VisitorVisits.get_previous_visit_timestamps(visitor_visits):
            if timestamp < start_of_day:
                break
            number_of_visits_today += 1
        return self._check_targeting(number_of_visits_today + 1)  # +1 for current visit
