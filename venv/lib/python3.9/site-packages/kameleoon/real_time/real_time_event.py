""" Kameleoon Real Time Event """
from typing import Any, Dict


class RealTimeEvent:
    """
    RealTimeEvent contains information about timestamp when configuration was updated.
    Timestamp parameter uses for fetching the latest configuration
    """

    def __init__(self, event_dict: Dict[str, Any]):
        """
        RealTimeEvent gets the new timestamp from and JSON message
        """
        self.time_stamp = event_dict["ts"]

    def get_time_stamp(self) -> int:
        """Returns the timestamp"""
        return self.time_stamp
