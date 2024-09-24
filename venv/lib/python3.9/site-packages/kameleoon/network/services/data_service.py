"""Services"""
from typing import Any, Coroutine, Optional
from kameleoon.network.services.service import Service
from kameleoon.network.net_provider import Response
from kameleoon.types.remote_visitor_data_filter import RemoteVisitorDataFilter


class DataService(Service):
    """Abstract data service"""
    def send_tracking_data(self, lines: str, timeout: Optional[float] = None) -> Coroutine[Any, Any, Response]:
        """Sends tracking data to a remote server."""
        raise NotImplementedError()

    def get_remote_data(self, key: str, timeout: Optional[float] = None) -> Coroutine[Any, Any, Response]:
        """Retrieves remote data based on the specified key."""
        raise NotImplementedError()

    def get_remote_visitor_data(
        self,
        visitor_code: str,
        data_filter: RemoteVisitorDataFilter,
        is_unique_identifier: bool,
        timeout: Optional[float] = None,
    ) -> Coroutine[Any, Any, Response]:
        """Fetches visitor-specific data from a remote source using filters and visitor identification."""
        raise NotImplementedError()
