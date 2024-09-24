# pylint: disable=duplicate-code
"""Conversion data"""
from kameleoon.data.data import Data, DataType
from kameleoon.network.sendable import DuplicationSafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


# pylint: disable=R0801
class Conversion(Data, DuplicationSafeSendableBase):
    """Conversion is used for tracking visitors conversions"""

    EVENT_TYPE = "conversion"

    def __init__(self, goal_id: int, revenue: float = 0.0, negative: bool = False) -> None:
        """
        :param goal_id: Id of the goal associated to the conversion
        :type goal_id: int
        :param revenue: Optional field - Revenue associated to the conversion, defaults to 0.0
        :type revenue: float
        :param negative: Optional field - If the revenue is negative. By default it's positive, defaults to False
        :type negative: bool

        Example:

        .. code-block:: python3

                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))

        """
        super().__init__()
        self.__goal_id = goal_id
        self.__revenue = revenue
        self.__negative = negative

    @property
    def goal_id(self) -> int:
        """Returns goal ID"""
        return self.__goal_id

    @property
    def revenue(self) -> float:
        """Returns revenue"""
        return self.__revenue

    @property
    def negative(self) -> bool:
        """Returns negative flag state"""
        return self.__negative

    @property
    def data_type(self) -> DataType:
        return DataType.CONVERSION

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        # remove query_builder, it's done due due pylint issue with R0801 - duplicate_code,
        # need to update pylint and return str(QueryBuilder) straightaway
        query_builder.extend(
            QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE),
            QueryParam(QueryParams.GOAL_ID, str(self.goal_id)),
            QueryParam(QueryParams.REVENUE, str(self.revenue)),
            QueryParam(QueryParams.NEGATIVE, "true" if self.negative else "false"),
        )

    def __str__(self):
        return (
            f"Conversion{{goal_id:{self.__goal_id},"
            f"revenue:{self.__revenue},"
            f"negative:{self.__negative}}}"
        )
