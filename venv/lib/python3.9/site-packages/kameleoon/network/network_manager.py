"""Network"""
from typing import Type, TypeVar, Optional
from kameleoon.network.access_token_source import AccessTokenSource
from kameleoon.network.net_provider import NetProvider
from kameleoon.network.url_provider import UrlProvider
from kameleoon.network.service_initialize_context import ServiceInitializeContext
from kameleoon.network.services.service import Service


S = TypeVar("S", bound=Service)  # pylint: disable=C0103


class NetworkManager:
    """Abstract network manager"""
    @property
    def url_provider(self) -> UrlProvider:
        """Returns the URL provider instance used for generating and managing URLs."""
        raise NotImplementedError()

    @property
    def net_provider(self) -> NetProvider:
        """Returns the network provider instance used for executing network requests."""
        raise NotImplementedError()

    @property
    def access_token_source(self) -> AccessTokenSource:
        """Returns the access token source instance used for obtaining access tokens."""
        raise NotImplementedError()

    @property
    def environment(self) -> Optional[str]:
        """Returns the current environment setting."""
        raise NotImplementedError()

    @property
    def call_timeout(self) -> float:
        """Returns the default timeout value for network calls."""
        raise NotImplementedError()

    def get_service_initialize_context(self) -> ServiceInitializeContext:
        """Returns the context for initializing services."""
        raise NotImplementedError()

    def get_service(self, service_type: Type[S]) -> S:
        """Returns the instance of the specified service type."""
        raise NotImplementedError()
