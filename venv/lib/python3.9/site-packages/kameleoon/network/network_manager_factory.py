"""Network"""
from typing import Optional
from kameleoon.network.access_token_source_factory import AccessTokenSourceFactory
from kameleoon.network.net_provider import NetProvider
from kameleoon.network.network_manager import NetworkManager


class NetworkManagerFactory:
    """Abstract network manager factory"""
    # pylint: disable=R0913
    def create(
        self,
        site_code: str,
        environment: Optional[str],
        call_timeout: float,
        net_provider: NetProvider,
        access_token_source_factory: AccessTokenSourceFactory,
    ) -> NetworkManager:
        """Creates and returns an instance of `NetworkManager` with the specified parameters."""
        raise NotImplementedError()
