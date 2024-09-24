"""Segment condition"""

from typing import Any, Dict, Union, Callable
from kameleoon.data import Data
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class SegmentCondition(TargetingCondition):
    """Exclusive feature flag condition"""

    class SegmentInfo:
        """SegmentInfo is a helper class to pass
        data file and func get_condition_data as parameters"""

        def __init__(self, data_file: Any, condition_data: Callable[[str], Data]):
            self.__data_file = data_file
            self.__condition_data = condition_data

        def data_file(self) -> Any:
            """
            :return: data file from visitor
            :rtype: DataFile
            """
            return self.__data_file

        def condition_data(self) -> Callable[[str], Data]:
            """
            :return: callable with get condition data
            :rtype: Callable[[str], Data]
            """
            return self.__condition_data

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition)
        try:
            self.__segment_id = json_condition.get("segmentId")
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return isinstance(data, SegmentCondition.SegmentInfo) and self.__check(data)

    def __check(self, segment_info: SegmentInfo) -> bool:
        rule = segment_info.data_file().rule_by_segment_id.get(self.__segment_id)
        return rule is not None and rule.targeting_segment.check_tree(segment_info.condition_data())
