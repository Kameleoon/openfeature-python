"""Target feature flag condition"""

from typing import Any, Union, Dict

from kameleoon.data.manager.assigned_variation import AssignedVariation
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class TargetFeatureFlagCondition(TargetingCondition):
    """Target feature flag condition"""

    class TargetFeatureFlagInfo:
        """TargetFeatureFlagInfo is a helper class to pass dataFile and variation storage as parameters"""

        def __init__(self, data_file: Any, variations_storage: Dict[int, AssignedVariation]):
            self.__data_file = data_file
            self.__variations_storage = variations_storage

        def data_file(self) -> Any:
            """
            :return: data file from visitor
            :rtype: DataFile
            """
            return self.__data_file

        def variations_storage(self) -> Dict[int, AssignedVariation]:
            """
            :return: variations storage from visitor
            :rtype: Dict[int, AssignedVariation]
            """
            return self.__variations_storage

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)
        try:
            self.__feature_flag_id = json_condition.get("featureFlagId")
            self.__condition_variation_key = json_condition.get("variationKey")
            self.__condition_rule_id = json_condition.get("ruleId")
        except KeyError as ex:
            KameleoonLogger.error("%s has wrong JSON structure: %s", self.__class__, ex)

    def check(self, data: TargetFeatureFlagInfo) -> bool:
        if (
            not isinstance(data, TargetFeatureFlagCondition.TargetFeatureFlagInfo)
            or len(data.variations_storage()) == 0
        ):
            return False
        return any(self.__check_rule(data, rule) for rule in self.__get_rules(data))

    def __check_rule(self, data: TargetFeatureFlagInfo, rule: Any) -> bool:
        if rule is None or rule.experiment_id is None:
            return False
        if self.__condition_rule_id is not None and self.__condition_rule_id != rule.id_:
            return False
        variation = data.variations_storage().get(rule.experiment_id, None)
        if variation is None:
            return False
        if self.__condition_variation_key is None:
            return True
        variation_by_exposition = data.data_file().variation_by_id.get(variation.variation_id, None)
        if variation_by_exposition is None:
            return False
        return variation_by_exposition.variation_key == self.__condition_variation_key

    def __get_rules(self, data: TargetFeatureFlagInfo):
        feature_flag = data.data_file().feature_flag_by_id.get(self.__feature_flag_id)
        return feature_flag.rules if feature_flag else []
