"""Services"""
from typing import Any, Coroutine, Optional
from kameleoon.network.services.service import Service
from kameleoon.network.net_provider import Response


class ConfigurationService(Service):
    """Abstract configuration service"""
    def fetch_configuration(
        self, environment: Optional[str] = None, time_stamp: Optional[int] = None, timeout: Optional[float] = None
    ) -> Coroutine[Any, Any, Response]:
        """Asynchronously fetches configuration data from a remote service."""
        raise NotImplementedError()
