"""Kameleoon Configuration"""

from typing import Any, Dict, Optional


class Settings:
    """
    KameleoonConfigurationSettings is used for saving setting's parameters, e.g
    state of real time update for site code and etc
    """

    _CONSENT_TYPE_REQUIRED = "REQUIRED"

    # pylint: disable=R0903
    def __init__(self, configuration: Optional[Dict[str, Any]] = None):
        if configuration is None:
            configuration = {}
        self.__real_time_update: bool = bool(configuration.get("realTimeUpdate"))
        self.__is_consent_required = configuration.get("consentType") == self._CONSENT_TYPE_REQUIRED
        self.__data_api_domain = configuration.get("dataApiDomain")

    @property
    def real_time_update(self) -> bool:
        """Returns streaming mode flag state"""
        return self.__real_time_update

    @property
    def is_consent_required(self) -> bool:
        """Returns consent required flag state"""
        return self.__is_consent_required

    @property
    def data_api_domain(self) -> Any:
        """Returns Data API domain to be switched to"""
        return self.__data_api_domain

    def __str__(self):
        return (
            f"Settings{{real_time_update:{self.__real_time_update},"
            f"is_consent_required:{self.__is_consent_required},"
            f"data_api_domain:'{self.__data_api_domain}'}}"
        )
