""" condition"""
from typing import Any, Union, Dict
from kameleoon.data.manager.page_view_visit import PageViewVisit
from kameleoon.targeting.conditions.string_value_condition import StringValueCondition


class PageTitleCondition(StringValueCondition):
    """Page title condition uses when you need to compare title of page"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition, json_condition.get("title"))

    def check(self, data: Any) -> bool:
        return isinstance(data, dict) and self.__check(data)

    def __check(self, page_view_visits: Dict[str, PageViewVisit]) -> bool:
        return any(
            isinstance(visit, PageViewVisit) and visit.page_view.title is not None and self._check(
                visit.page_view.title)
            for visit in page_view_visits.values()
        )
