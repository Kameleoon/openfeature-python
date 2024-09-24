"""Device condition"""
from typing import Any, Dict, Union
from kameleoon.data import Device
from kameleoon.data.device import DeviceType
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class DeviceCondition(TargetingCondition):
    """Device condition uses in case if you need to target by device type"""

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__device_type = DeviceType[str(json_condition.get("device", "")).upper()]
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data: Any) -> bool:
        return isinstance(data, Device) and self.__check(data)

    def __check(self, device: Device) -> bool:
        return (self.__device_type is not None) and (device.device_type == self.__device_type)
