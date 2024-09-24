"""Browser condition"""
from typing import Any, Dict, Union
from kameleoon.data import Browser, BrowserType
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.sdk_version import SdkVersion
from kameleoon.targeting.conditions.constants import TargetingOperator
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class BrowserCondition(TargetingCondition):
    """Browser condition uses in case if you need to target by browser type and version"""

    INTERNET_EXPLORER_SHORT_NAME = "IE"

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            json_browser = str(json_condition.get("browser", ""))
            self.__browser_type = (
                BrowserType[json_browser]
                if json_browser != BrowserCondition.INTERNET_EXPLORER_SHORT_NAME
                else BrowserType.INTERNET_EXPLORER
            )
            self.__version = json_condition.get("version", None)
            self.__operator = TargetingOperator[str(json_condition.get("versionMatchType", None))]
        except KeyError as exeception:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, exeception)

    def check(self, data: Any) -> bool:
        return isinstance(data, Browser) and self.__check(data)

    # pylint: disable=R0911
    def __check(self, browser: Browser) -> bool:
        # If browser types are not equal, then return False
        if self.__browser_type != browser.browser_type:
            return False

        # If browser types are equal and browser version isn't defined in condition, then return True
        if self.__version is None:
            return True

        # If browser types are equal and browser version is defined in condition, then need to compare versions
        version_number = SdkVersion.get_float_version(str(self.__version))
        if version_number is None:
            return False

        browser_version = browser.version or TargetingCondition.NON_EXISTENT_IDENTIFIER

        if self.__operator == TargetingOperator.EQUAL:
            return browser_version == version_number

        if self.__operator == TargetingOperator.GREATER:
            return browser_version > version_number

        if self.__operator == TargetingOperator.LOWER:
            return browser_version < version_number

        KameleoonLogger.error("Unexpected comparing operation for Browser condition: %s", self.__operator)
        return False
