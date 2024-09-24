"""Services"""
from typing import Any, Coroutine, Optional
from kameleoon.network.services.service import Service
from kameleoon.network.net_provider import Response


class AutomationService(Service):
    """Abstract automation service"""
    def fetch_access_jwtoken(
        self, client_id: str, client_secret: str, timeout: Optional[float] = None
    ) -> Coroutine[Any, Any, Response]:
        """Fetches an access JWT token asynchronously."""
        raise NotImplementedError()
