"""Visitor visits"""

from typing import List, Optional

from kameleoon.data import DataType

from kameleoon.data.data import BaseData


class VisitorVisits(BaseData):
    """Visitor visits"""

    def __init__(self, previous_visit_timestamps: List[int]) -> None:
        super().__init__()
        self.__previous_visit_timestamps = previous_visit_timestamps

    @property
    def previous_visit_timestamps(self) -> List[int]:
        """Return timestamps for visit"""
        return self.__previous_visit_timestamps

    @property
    def data_type(self) -> DataType:
        return DataType.VISITOR_VISITS

    @staticmethod
    def get_previous_visit_timestamps(visitor_visits: Optional["VisitorVisits"]) -> List[int]:
        """Return timestamps for visit"""
        return visitor_visits.previous_visit_timestamps if visitor_visits is not None else []

    def __str__(self):
        return f"VisitorVisits{{previous_visit_timestamps:{self.__previous_visit_timestamps}}}"
