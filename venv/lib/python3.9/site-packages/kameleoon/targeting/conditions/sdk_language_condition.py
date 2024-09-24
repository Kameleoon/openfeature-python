"""Sdk language condition"""
from typing import Any, Dict, Union

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.sdk_version import SdkVersion
from kameleoon.targeting.conditions.constants import TargetingOperator
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class SdkLanguageCondition(TargetingCondition):
    """SdkLanguage uses in case if you need to target by sdk type and version"""

    class SdkInfo:
        """SdkInfo is a helper class to pass sdk name and version as parameters"""

        def __init__(self, sdk_language: str, version: str) -> None:
            self.__sdk_language = sdk_language
            self.__version = version

        @property
        def sdk_language(self):
            """Return sdk language (type)"""
            return self.__sdk_language

        @property
        def version(self):
            """Return sdk version"""
            return self.__version

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__sdk_language = json_condition.get("sdkLanguage", "")
            self.__version = json_condition.get("version", None)
            self.__operator = TargetingOperator[str(json_condition.get("versionMatchType", None))]
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data: Any) -> bool:
        return isinstance(data, SdkLanguageCondition.SdkInfo) and self.check_targeting(data)

    def check_targeting(self, sdk_info: SdkInfo) -> bool:  # pylint: disable=R0911
        """Helper method to check targeting"""

        # If sdk types are not equal, then return False
        if self.__sdk_language != sdk_info.sdk_language:
            return False

        # If sdk types are equal and sdk version isn't defined in condition, then return True
        if self.__version is None:
            return True

        # If sdk types are equal and sdk version is defined in condition, then need to compare versions
        version_components_condition = SdkVersion.get_version_components(str(self.__version))
        version_components_sdk = SdkVersion.get_version_components(sdk_info.version)
        if version_components_condition is None or version_components_sdk is None:
            return False

        major_condition, minor_condition, patch_condition = version_components_condition
        major_sdk, minor_sdk, patch_sdk = version_components_sdk
        if self.__operator == TargetingOperator.EQUAL:
            return major_sdk == major_condition and minor_sdk == minor_condition and patch_sdk == patch_condition

        if self.__operator == TargetingOperator.GREATER:
            return (
                major_sdk > major_condition
                or (major_sdk == major_condition and minor_sdk > minor_condition)
                or (major_sdk == major_condition and minor_sdk == minor_condition and patch_sdk > patch_condition)
            )

        if self.__operator == TargetingOperator.LOWER:
            return (
                major_sdk < major_condition
                or (major_sdk == major_condition and minor_sdk < minor_condition)
                or (major_sdk == major_condition and minor_sdk == minor_condition and patch_sdk < patch_condition)
            )

        KameleoonLogger.error("Unexpected comparing operation for SdkLanguage condition: %s", self.__operator)
        return False
