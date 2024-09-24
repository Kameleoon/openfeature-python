"""Network"""
from typing import Optional
from kameleoon.network.access_token_source_factory import AccessTokenSourceFactory
from kameleoon.network.url_provider import UrlProvider
from kameleoon.network.net_provider import NetProvider
from kameleoon.network.network_manager import NetworkManager
from kameleoon.network.network_manager_impl import NetworkManagerImpl
from kameleoon.network.network_manager_factory import NetworkManagerFactory
from kameleoon.network.services.automation_service import AutomationService
from kameleoon.network.services.automation_service_impl import AutomationServiceImpl
from kameleoon.network.services.configuration_service import ConfigurationService
from kameleoon.network.services.configuration_service_impl import ConfigurationServiceImpl
from kameleoon.network.services.data_service import DataService
from kameleoon.network.services.data_service_impl import DataServiceImpl


class NetworkManagerFactoryImpl(NetworkManagerFactory):
    """Network manager factory implementation"""
    # fmt is disabled due issue in pylint, disabling R0801 doesn’t work
    # fmt: off
    # pylint: disable=R0913
    def create(
        self,
        site_code: str,
        environment: Optional[str], call_timeout: float,
        net_provider: NetProvider,
        access_token_source_factory: AccessTokenSourceFactory,
    ) -> NetworkManager:
        # fmt: on
        url_provider = UrlProvider(site_code, UrlProvider.DEFAULT_DATA_API_DOMAIN)
        network_manager = NetworkManagerImpl(
            url_provider, environment, call_timeout, net_provider, access_token_source_factory,
        )
        self.__link(network_manager)
        return network_manager

    @staticmethod
    def __link(network_manager: NetworkManagerImpl):
        context = network_manager.get_service_initialize_context()
        context.set_service(AutomationService, AutomationServiceImpl(network_manager))
        context.set_service(ConfigurationService, ConfigurationServiceImpl(network_manager))
        context.set_service(DataService, DataServiceImpl(network_manager))
