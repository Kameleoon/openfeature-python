"""Network"""
from typing import cast, Dict, Type, Optional
from kameleoon.network.access_token_source import AccessTokenSource
from kameleoon.network.access_token_source_factory import AccessTokenSourceFactory
from kameleoon.network.network_manager import NetworkManager, S
from kameleoon.network.net_provider import NetProvider
from kameleoon.network.url_provider import UrlProvider
from kameleoon.network.service_initialize_context import ServiceInitializeContext
from kameleoon.network.service_initialize_context_impl import ServiceInitializeContextImpl
from kameleoon.network.services.service import Service


class NetworkManagerImpl(NetworkManager):
    """Network manager implementation"""
    @property
    def url_provider(self) -> UrlProvider:
        return self._url_provider

    @property
    def net_provider(self) -> NetProvider:
        return self._net_provider

    @property
    def access_token_source(self) -> AccessTokenSource:
        return self._access_token_source

    @property
    def environment(self) -> Optional[str]:
        return self._environment

    @property
    def call_timeout(self) -> float:
        return self._call_timeout

    # pylint: disable=R0913
    def __init__(
        self,
        url_provider: UrlProvider,
        environment: Optional[str],
        call_timeout: float,
        net_provider: NetProvider,
        access_token_source_factory: AccessTokenSourceFactory,
    ) -> None:
        super().__init__()
        self._url_provider = url_provider
        self._environment = environment
        self._call_timeout = call_timeout
        self._net_provider = net_provider
        self._access_token_source = access_token_source_factory.create(self)
        self._services: Dict[Type[Service], Service] = {}

    def get_service_initialize_context(self) -> ServiceInitializeContext:
        return ServiceInitializeContextImpl(self._services)

    def get_service(self, service_type: Type[S]) -> S:
        return cast(S, self._services[service_type])
