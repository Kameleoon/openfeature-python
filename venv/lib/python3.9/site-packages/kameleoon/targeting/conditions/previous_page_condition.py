"""Previous page condition"""

from typing import Any, Dict, Union, Optional
from kameleoon.targeting.conditions.string_value_condition import StringValueCondition
from kameleoon.data.manager.page_view_visit import PageViewVisit


class PreviousPageCondition(StringValueCondition):
    """Previous page condition"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition, json_condition.get("url"))

    def check(self, data: Any) -> bool:
        return isinstance(data, Dict) and self.__check(data)

    def __check(self, data: Dict[str, PageViewVisit]) -> bool:
        most_recent_visit: Optional[PageViewVisit] = None
        second_most_recent_visit: Optional[PageViewVisit] = None
        for visit in data.values():
            if most_recent_visit is None or visit.last_timestamp > most_recent_visit.last_timestamp:
                second_most_recent_visit = most_recent_visit
                most_recent_visit = visit
            elif second_most_recent_visit is None or visit.last_timestamp > second_most_recent_visit.last_timestamp:
                second_most_recent_visit = visit

        return second_most_recent_visit is not None and self._check(second_most_recent_visit.page_view.url)
