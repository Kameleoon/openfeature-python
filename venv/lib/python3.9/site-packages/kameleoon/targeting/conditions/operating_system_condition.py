"""Operating system condition"""

from typing import Any, Dict, Union
from kameleoon.data.operating_system import OperatingSystem, OperatingSystemType
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class OperatingSystemCondition(TargetingCondition):
    """Operating system condition uses in case if you need to target by operating system type"""

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        super().__init__(json_condition)
        try:
            self.__os_type = OperatingSystemType[str(json_condition.get("os", ""))]
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return isinstance(data, OperatingSystem) and self.__check(data)

    def __check(self, operating_system: OperatingSystem) -> bool:
        return self.__os_type is not None and operating_system.os_type == self.__os_type
