"""Base class for all conditions"""

from enum import Enum
import re
from typing import Any, TypeVar, Union, Dict, Optional

from kameleoon.data.data import Data

T = TypeVar("T", bound=Data)  # pylint: disable=C0103


class TargetingConditionType(Enum):
    """Targeting condition types"""

    CUSTOM_DATUM = "CUSTOM_DATUM"
    TARGET_FEATURE_FLAG = "TARGET_FEATURE_FLAG"
    EXCLUSIVE_FEATURE_FLAG = "EXCLUSIVE_FEATURE_FLAG"
    DEVICE_TYPE = "DEVICE_TYPE"
    VISITOR_CODE = "VISITOR_CODE"
    PAGE_URL = "PAGE_URL"
    PAGE_VIEWS = "PAGE_VIEWS"
    PREVIOUS_PAGE = "PREVIOUS_PAGE"
    PAGE_TITLE = "PAGE_TITLE"
    CONVERSIONS = "CONVERSIONS"
    SDK_LANGUAGE = "SDK_LANGUAGE"
    BROWSER = "BROWSER"
    EXPLICIT_TRIGGER = "EXPLICIT_TRIGGER"
    COOKIE = "COOKIE"
    GEOLOCATION = "GEOLOCATION"
    OPERATING_SYSTEM = "OPERATING_SYSTEM"
    SEGMENT = "SEGMENT"
    FIRST_VISIT = "FIRST_VISIT"
    LAST_VISIT = "LAST_VISIT"
    VISITS = "VISITS"
    SAME_DAY_VISITS = "SAME_DAY_VISITS"
    NEW_VISITORS = "NEW_VISITORS"
    HEAT_SLICE = "HEAT_SLICE"
    UNKNOWN = "UNKNOWN"


class TargetingCondition:
    """Condition is a base class for all SDK conditions"""

    NON_EXISTENT_IDENTIFIER = -1

    def __init__(self, json_condition: Dict[str, Union[str, Any]]):
        self.type = json_condition.get("targetingType")
        self.include = json_condition.get("isInclude", True) is not False

    def check(self, data: Any) -> bool:
        """Check the condition for targeting"""
        raise NotImplementedError

    @staticmethod
    def _is_regex_math(condition_value: Optional[str], value: Optional[str]) -> bool:
        if condition_value is None or value is None:
            return False
        try:
            pattern = re.compile(condition_value)
        except re.error:
            return False
        return bool(re.fullmatch(pattern, value))
