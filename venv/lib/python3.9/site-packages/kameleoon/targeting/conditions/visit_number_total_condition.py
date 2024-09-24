"""Visit number total condition"""

from typing import Any, Dict, Union, Optional

from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.targeting.conditions.number_condition import NumberCondition


class VisitNumberTotalCondition(NumberCondition):
    """Visit number total condition uses in case if you need to target by value numeric"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition, "visitCount")

    def check(self, data: Optional[VisitorVisits]) -> bool:
        if self._condition_value is None:
            return False
        return self._check_targeting(len(VisitorVisits.get_previous_visit_timestamps(data)) + 1)  # +1 for current visit
