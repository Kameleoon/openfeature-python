"""Page view number condition"""

from typing import Any, Dict, Union, Optional
from kameleoon.data.manager.page_view_visit import PageViewVisit
from kameleoon.targeting.conditions.number_condition import NumberCondition


class PageViewNumberCondition(NumberCondition):
    """Page view number condition uses in case if you need to target by value numeric"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition, "pageCount")

    def check(self, data: Optional[Dict[str, PageViewVisit]]) -> bool:
        if data is None:
            return False
        count = sum(visit.count for visit in data.values())
        return self._check_targeting(count)
