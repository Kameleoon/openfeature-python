"""Exclusive feature flag condition"""

from typing import Any, Union, Dict
from kameleoon.data.manager.assigned_variation import AssignedVariation
from kameleoon.targeting.conditions.targeting_condition import TargetingCondition


class ExclusiveFeatureFlagCondition(TargetingCondition):
    """Exclusive feature flag condition"""

    class ExclusiveFeatureFlagInfo:
        """ExclusiveFeatureFlagInfo is a helper class to pass
        current experiment id and variation storage as parameters"""

        def __init__(
            self,
            current_experiment_id: int,
            variations_storage: Dict[int, AssignedVariation],
        ):
            self.__current_experiment_id = current_experiment_id
            self.__variations_storage = variations_storage

        def current_experiment_id(self) -> int:
            """
            :return: experiment_id
            :rtype: int
            """
            return self.__current_experiment_id

        def variations_storage(self) -> Dict[int, AssignedVariation]:
            """
            :return: variations storage from visitor
            :rtype: Dict[int, AssignedVariation]
            """
            return self.__variations_storage

    def __init__(self, json_condition: Dict[str, Union[str, int, Any]]):
        super().__init__(json_condition)

    def check(self, data: ExclusiveFeatureFlagInfo) -> bool:
        size = len(data.variations_storage())
        return size == 0 or (size == 1 and data.variations_storage().get(data.current_experiment_id()) is not None)
