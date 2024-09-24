"""Targeting condition factory"""
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.browser_condition import BrowserCondition
from kameleoon.targeting.conditions.conversion_condition import ConversionCondition
from kameleoon.targeting.conditions.device_condition import DeviceCondition
from kameleoon.targeting.conditions.page_title_condition import PageTitleCondition
from kameleoon.targeting.conditions.page_url_condition import PageUrlCondition
from kameleoon.targeting.conditions.sdk_language_condition import SdkLanguageCondition
from kameleoon.targeting.conditions.unknown_condition import UnknownCondition
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition, TargetingConditionType
from kameleoon.targeting.conditions.custom_datum import CustomDatum
from kameleoon.targeting.conditions.exclusive_feature_flag_condition import ExclusiveFeatureFlagCondition
from kameleoon.targeting.conditions.visitor_code_condition import VisitorCodeCondition
from kameleoon.targeting.conditions.cookie_condition import CookieCondition
from kameleoon.targeting.conditions.geolocation_condition import GeolocationCondition
from kameleoon.targeting.conditions.kcs_heat_range_condition import KcsHeatRangeCondition
from kameleoon.targeting.conditions.operating_system_condition import OperatingSystemCondition
from kameleoon.targeting.conditions.segment_condition import SegmentCondition
from kameleoon.targeting.conditions.target_feature_flag_condition import TargetFeatureFlagCondition
from kameleoon.targeting.conditions.page_view_number_condition import PageViewNumberCondition
from kameleoon.targeting.conditions.previous_page_condition import PreviousPageCondition
from kameleoon.targeting.conditions.visit_number_today_condition import VisitNumberTodayCondition
from kameleoon.targeting.conditions.visit_number_total_condition import VisitNumberTotalCondition
from kameleoon.targeting.conditions.visitor_new_return_condition import VisitorNewReturnCondition
from kameleoon.targeting.conditions.time_elapsed_since_visit_condition import TimeElapsedSinceVisitCondition


class TreeConditionFactory:
    """Factory of targeting condition types"""

    @staticmethod
    def get_condition(condition_json) -> TargetingCondition:  # noqa: C901 pylint: disable=R0911,R0912
        """Create a proper condition from the given json object"""
        try:
            targeting_type = condition_json.get("targetingType", TargetingConditionType.UNKNOWN.value)
            condition_type = TargetingConditionType[targeting_type]
            if condition_type == TargetingConditionType.CUSTOM_DATUM:
                return CustomDatum(condition_json)

            if condition_type == TargetingConditionType.TARGET_FEATURE_FLAG:
                return TargetFeatureFlagCondition(condition_json)

            if condition_type == TargetingConditionType.EXCLUSIVE_FEATURE_FLAG:
                return ExclusiveFeatureFlagCondition(condition_json)

            if condition_type == TargetingConditionType.DEVICE_TYPE:
                return DeviceCondition(condition_json)

            if condition_type == TargetingConditionType.VISITOR_CODE:
                return VisitorCodeCondition(condition_json)

            if condition_type == TargetingConditionType.PAGE_URL:
                return PageUrlCondition(condition_json)

            if condition_type == TargetingConditionType.PAGE_VIEWS:
                return PageViewNumberCondition(condition_json)

            if condition_type == TargetingConditionType.PREVIOUS_PAGE:
                return PreviousPageCondition(condition_json)

            if condition_type == TargetingConditionType.PAGE_TITLE:
                return PageTitleCondition(condition_json)

            if condition_type == TargetingConditionType.SDK_LANGUAGE:
                return SdkLanguageCondition(condition_json)

            if condition_type == TargetingConditionType.CONVERSIONS:
                return ConversionCondition(condition_json)

            if condition_type == TargetingConditionType.BROWSER:
                return BrowserCondition(condition_json)

            if condition_type == TargetingConditionType.COOKIE:
                return CookieCondition(condition_json)

            if condition_type == TargetingConditionType.GEOLOCATION:
                return GeolocationCondition(condition_json)

            if condition_type == TargetingConditionType.OPERATING_SYSTEM:
                return OperatingSystemCondition(condition_json)

            if condition_type == TargetingConditionType.SEGMENT:
                return SegmentCondition(condition_json)

            if condition_type == TargetingConditionType.VISITS:
                return VisitNumberTotalCondition(condition_json)

            if condition_type == TargetingConditionType.SAME_DAY_VISITS:
                return VisitNumberTodayCondition(condition_json)

            if condition_type == TargetingConditionType.NEW_VISITORS:
                return VisitorNewReturnCondition(condition_json)

            if condition_type in (
                TargetingConditionType.FIRST_VISIT,
                TargetingConditionType.LAST_VISIT,
            ):
                return TimeElapsedSinceVisitCondition(condition_json)

            if condition_type == TargetingConditionType.HEAT_SLICE:
                return KcsHeatRangeCondition(condition_json)

            return UnknownCondition(condition_json)
        except KeyError as exception:
            KameleoonLogger.error("Unsupported targeted condition type found: %s", exception)
            return UnknownCondition(condition_json)
