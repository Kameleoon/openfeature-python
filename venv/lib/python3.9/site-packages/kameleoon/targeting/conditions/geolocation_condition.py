"""Geolocation condition"""

from typing import Any, Dict, Union
from kameleoon.helpers.functions import compare_str_ignore_case
from kameleoon.data.geolocation import Geolocation
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class GeolocationCondition(TargetingCondition):
    """Geolocation condition uses in case if you need to target by geolocation info"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition)
        try:
            self.__country = json_condition.get("country")
            self.__region = json_condition.get("region")
            self.__city = json_condition.get("city")
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return isinstance(data, Geolocation) and self.__check(data)

    # pylint: disable=R0911
    def __check(self, geolocation: Geolocation) -> bool:
        return (
            (self.__country is not None and compare_str_ignore_case(self.__country, geolocation.country))
            and (self.__region is None or compare_str_ignore_case(self.__region, geolocation.region))
            and (self.__city is None or compare_str_ignore_case(self.__city, geolocation.city))
        )
