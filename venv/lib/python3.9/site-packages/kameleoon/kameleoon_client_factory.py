"""Factory for KameleoonClient"""
from threading import Lock
from typing import Dict, Optional
from kameleoon.kameleoon_client import KameleoonClient
from kameleoon.kameleoon_client_config import KameleoonClientConfig, DEFAULT_CONFIGURATION_PATH
from kameleoon.logging.kameleoon_logger import KameleoonLogger


class KameleoonClientFactory:
    """Factory of `KameleoonClient` instances"""

    _lock = Lock()
    _clients: Dict[str, KameleoonClient] = {}

    @staticmethod
    def create(
        site_code: str,
        config: Optional[KameleoonClientConfig] = None,
        config_path=DEFAULT_CONFIGURATION_PATH,
    ) -> KameleoonClient:
        """
        Creates a new instance of `KameleoonClient` with the specified site code and configuration
        or loads an existing one and returns it.

        :param site_code: Code of the website you want to run experiments on. This unique code id can
                          be found in our platform's back-office. This field is mandatory.
        :type site_code: str
        :param config: Configuration object which can be used instead of external file at configuration_path.
                       This field is optional set to None by default.
        :type config: Optional[KameleoonClientConfig]
        :param config_path: Path to a configuration file.
                            This field is optional set to '/etc/kameleoon/client-python.yaml' by default.
        :type config_path: str

        :raises ConfigFileNotFound: Indicates that a configuration file with the passed config path is not found
        :raises SiteCodeIsEmpty: Indicates that the specified site code is empty string which is invalid value
        """
        KameleoonLogger.info(
            "CALL: KameleoonClientFactory.create(site_code: %s, config: %s, config_path: %s)",
            site_code, config, config_path
        )
        client = KameleoonClientFactory._clients.get(site_code)
        if client is None:
            with KameleoonClientFactory._lock:
                client = KameleoonClientFactory._clients.get(site_code)
                if client is None:
                    if config is None:
                        config = KameleoonClientConfig.read_from_yaml(config_path)
                    client = KameleoonClient(site_code, config)
                    KameleoonClientFactory._clients[site_code] = client
        KameleoonLogger.info(
            "RETURN: KameleoonClientFactory.create(site_code: %s, config: %s, config_path: %s) -> (client)",
            site_code, config, config_path
        )
        return client

    @staticmethod
    def forget(site_code: str) -> None:
        """
        Removes a `KameleoonClient` instance with the specified site code and frees its resources.

        :param site_code: Code of the corresponding website. This unique code id can be found
                          in our platform's back-office. This field is mandatory.
        :type site_code: str
        """
        KameleoonLogger.info("CALL: KameleoonClientFactory.forget(site_code: %s)", site_code)
        KameleoonClientFactory._clients.pop(site_code, None)
        KameleoonLogger.info("RETURN: KameleoonClientFactory.forget(site_code: %s)", site_code)
