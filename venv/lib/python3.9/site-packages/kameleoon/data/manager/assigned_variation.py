"""Assigned Variation"""
import time
from typing import Optional
from kameleoon.configuration.rule_type import RuleType
from kameleoon.data.data import BaseData, DataType
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class AssignedVariation(BaseData, DuplicationUnsafeSendableBase):
    """Assigned variation"""
    EVENT_TYPE = "experiment"

    def __init__(
        self,
        experiment_id: int,
        variation_id: int,
        rule_type: RuleType = RuleType.UNKNOWN,
        assignment_time: Optional[float] = None,
    ) -> None:
        super().__init__()
        self.__experiment_id = experiment_id
        self.__variation_id = variation_id
        self.__rule_type = rule_type
        self.__assignment_time = assignment_time or time.time()

    @property
    def experiment_id(self) -> int:
        """Returns the experiment ID."""
        return self.__experiment_id

    @property
    def variation_id(self) -> int:
        """Returns the variation ID."""
        return self.__variation_id

    @property
    def rule_type(self) -> RuleType:
        """Returns the rule type associated with the variation."""
        return self.__rule_type

    @property
    def assignment_time(self) -> float:
        """Returns the time when the assignment occurred."""
        return self.__assignment_time

    @property
    def data_type(self) -> DataType:
        """Returns the data type for the assigned variation."""
        return DataType.ASSIGNED_VARIATION

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        # fmt: off
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.EXPERIMENT_ID, str(self.__experiment_id)),
            QueryParam(QueryParams.VARIATION_ID, str(self.__variation_id)),
        )
        # fmt: on

    def is_valid(self, respool_time: Optional[int]) -> bool:
        """Checks if the assigned variation is valid based on the respool time."""
        return (respool_time is None) or (self.assignment_time >= respool_time)

    def __str__(self):
        return (
            f"AssignedVariation{{experiment_id:{self.__experiment_id},"
            f"variation_id:{self.__variation_id},"
            f"assignment_time:{self.__assignment_time},"
            f"rule_type:{self.__rule_type}}}"
        )
