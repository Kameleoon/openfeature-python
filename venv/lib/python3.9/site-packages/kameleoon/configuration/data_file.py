"""Kameleoon Configuration"""

from typing import Any, Dict, Optional
from kameleoon.configuration.custom_data_info import CustomDataInfo
from kameleoon.configuration.variation_by_exposition import VariationByExposition
from kameleoon.configuration.feature_flag import FeatureFlag
from kameleoon.configuration.rule import Rule
from kameleoon.configuration.settings import Settings
from kameleoon.exceptions import FeatureNotFound, FeatureEnvironmentDisabled
from kameleoon.logging.kameleoon_logger import KameleoonLogger


class DataFile:
    """`DataFile` is a container for an actual client-configuration data"""

    @staticmethod
    def default(environment: Optional[str]) -> "DataFile":
        """Creates new instance of `DataFile` initialized with default values"""
        data_file = DataFile(environment, Settings(), {}, CustomDataInfo(None))
        return data_file

    @staticmethod
    def from_json(
        environment: Optional[str], configuration: Dict[str, Any]
    ) -> "DataFile":
        """Creates new instance of `DataFile` initialized from the specified configuration JSON"""
        settings = Settings(configuration.get("configuration"))
        feature_flags = {
            (feature_flag := FeatureFlag(jobj)).feature_key: feature_flag
            for jobj in configuration.get("featureFlags") or []
        }
        custom_data_info = CustomDataInfo(configuration.get("customData"))
        data_file = DataFile(environment, settings, feature_flags, custom_data_info)
        return data_file

    # pylint: disable=R0913
    def __init__(
        self,
        environment: Optional[str],
        settings: Settings,
        feature_flags: Dict[str, FeatureFlag],
        custom_data_info: CustomDataInfo,
    ) -> None:
        KameleoonLogger.debug(
            'CALL: DataFile(environment: %s, settings: %s, feature_flags: %s, custom_data_info: %s)',
            environment, settings, feature_flags, custom_data_info)
        self.__environment = environment  # pylint: disable=W0238
        self.__settings = settings
        self.__feature_flags: Dict[str, FeatureFlag] = feature_flags
        self.__has_any_targeted_delivery_rule = any(
            rule.is_targeted_delivery
            for ff in self.__feature_flags.values()
            if ff.environment_enabled
            for rule in ff.rules
        )
        self.__variation_by_id: Dict[int, VariationByExposition] = {}
        self.__rule_by_segment_id: Dict[int, Rule] = {}
        self.__feature_flag_by_id: Dict[int, FeatureFlag] = {}
        self.__collect_indices()
        self.__custom_data_info = custom_data_info
        KameleoonLogger.debug(
            'RETURN: DataFile.new(environment: %s, settings: %s, feature_flags: %s, custom_data_info: %s)',
            environment, settings, feature_flags, custom_data_info)

    @property
    def settings(self) -> Settings:
        """Returns settings"""
        return self.__settings

    @property
    def feature_flags(self) -> Dict[str, FeatureFlag]:
        """Returns dictionary of all feature flags stored by feature keys"""
        return self.__feature_flags

    @property
    def feature_flag_by_id(self) -> Dict[int, FeatureFlag]:
        """Returns dictionary of all feature flags stored by id"""
        return self.__feature_flag_by_id

    @property
    def rule_by_segment_id(self) -> Dict[int, Rule]:
        """Returns dictionary of all rule stored by segment id"""
        return self.__rule_by_segment_id

    @property
    def variation_by_id(self) -> Dict[int, VariationByExposition]:
        """Returns dictionary of all variations stored by id"""
        return self.__variation_by_id

    @property
    def has_any_targeted_delivery_rule(self) -> bool:
        """Returns `True` if has a feature flag with a rule of the targeted delivery type, otherwise returns `False`"""
        return self.__has_any_targeted_delivery_rule

    def get_feature_flag(self, feature_key: str) -> FeatureFlag:
        """
        Returns feature flag with the specified feature key if it exists,
        otherwise raises `FeatureNotFound` exception.
        """
        feature_flag = self.__feature_flags.get(feature_key)
        if feature_flag is None:
            raise FeatureNotFound(feature_key)
        if not feature_flag.environment_enabled:
            raise FeatureEnvironmentDisabled(feature_key, self.__environment)
        return feature_flag

    @property
    def custom_data_info(self) -> CustomDataInfo:
        """Returns custom data info for mapping device`"""
        return self.__custom_data_info

    def __collect_indices(self) -> None:
        for _, feature_flag in self.__feature_flags.items():
            self.__feature_flag_by_id[feature_flag.id_] = feature_flag
            if feature_flag.rules is not None:
                for rule in feature_flag.rules:
                    self.__rule_by_segment_id[rule.segment_id] = rule
                    for variation in rule.variation_by_exposition:
                        if variation.variation_id is not None:
                            self.__variation_by_id[variation.variation_id] = variation

    def __str__(self):
        return (
            f"DataFile{{"
            f"environment:'{self.__environment}',"
            f"feature_flags:{len(self.__feature_flags)},"
            f"settings:{self.__settings}"
            f"}}"
        )
