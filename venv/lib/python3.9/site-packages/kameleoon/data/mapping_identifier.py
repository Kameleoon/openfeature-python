"""Mapping identifier"""
from kameleoon.data.custom_data import CustomData
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams


class MappingIdentifier(CustomData):
    """Mapping identifier"""
    def __init__(self, custom_data: CustomData) -> None:
        super().__init__(custom_data.id, *custom_data.values)

    @property
    def unsent(self) -> bool:
        return True

    @property
    def transmitting(self) -> bool:
        return False

    @property
    def sent(self) -> bool:
        return False

    def _add_query_params(self, query_builder: QueryBuilder) -> None:
        super()._add_query_params(query_builder)
        query_builder.append(QueryParam(QueryParams.MAPPING_IDENTIFIER, "true", False))
