"""Network"""
from kameleoon.network.sendable import DuplicationUnsafeSendableBase
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class ActivityEvent(DuplicationUnsafeSendableBase):
    """Activity event"""
    EVENT_TYPE = "activity"

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        query_builder.append(QueryParam(QueryParams.EVENT_TYPE, self.EVENT_TYPE))
