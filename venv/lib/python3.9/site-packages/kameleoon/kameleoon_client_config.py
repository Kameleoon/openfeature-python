"""Kameleoon Client Configuration"""
import logging
import os
from typing import Any, Dict, Optional
import yaml

from kameleoon.exceptions import ConfigCredentialsInvalid, ConfigFileNotFound
from kameleoon.helpers.domain import validate_top_level_domain
from kameleoon.helpers.logger import Logger
from kameleoon.helpers.string_utils import StringUtils
from kameleoon.logging.kameleoon_logger import KameleoonLogger

DEFAULT_REFRESH_INTERVAL_MINUTES = 60
DEFAULT_SESSION_DURATION_MINUTES = 30
DEFAULT_DEFAULT_TIMEOUT_MILLISECONDS = 10_000
DEFAULT_TRACKING_INTERVAL_MILLISECONDS = 1000
MIN_TRACKING_INTERVAL_MILLISECONDS = 100
MAX_TRACKING_INTERVAL_MILLISECONDS = 1000
DEFAULT_CONFIGURATION_PATH = "/etc/kameleoon/client-python.yaml"


class KameleoonClientConfig:
    """Client configuration which can be used instead of external configuration file"""

    # pylint: disable=R0913
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        refresh_interval_minute=DEFAULT_REFRESH_INTERVAL_MINUTES,
        session_duration_minute=DEFAULT_SESSION_DURATION_MINUTES,
        default_timeout_millisecond=DEFAULT_DEFAULT_TIMEOUT_MILLISECONDS,
        environment: Optional[str] = None,
        top_level_domain="",
        logger: Optional[logging.Logger] = None,
        multi_threading: Optional[bool] = None,
        tracking_interval_millisecond=DEFAULT_TRACKING_INTERVAL_MILLISECONDS,
    ) -> None:
        """
        :param logger: (Deprecated)
        """
        if not client_id:
            raise ConfigCredentialsInvalid("Client ID is not specified")
        if not client_secret:
            raise ConfigCredentialsInvalid("Client secret is not specified")
        self.__client_id = client_id
        self.__client_secret = client_secret
        if logger is not None:
            KameleoonLogger.warning(
                "The parameter `logger` is deprecated. Please use `KameleoonLogger.set_logger` method instead."
            )
            self.__logger = logger
        else:
            self.__logger = Logger.shared()
        self.__refresh_interval_second = 0.0
        self.set_refresh_interval_minute(refresh_interval_minute)
        self.__session_duration_second = 0.0
        self.set_session_duration_minute(session_duration_minute)
        self.__default_timeout_second = 0.0
        self.set_default_timeout_millisecond(default_timeout_millisecond)
        self.__tracking_interval_second = 0.0
        self.set_tracking_interval_millisecond(tracking_interval_millisecond)
        self.__environment: Optional[str] = None
        self.set_environment(environment)
        self.__top_level_domain = ""
        self.set_top_level_domain(top_level_domain)
        self.__multi_threading = False
        if multi_threading is not None:
            self.set_multi_threading(multi_threading)

    @staticmethod
    def read_from_yaml(config_path=DEFAULT_CONFIGURATION_PATH) -> "KameleoonClientConfig":
        """
        Loads `KameleoonClientConfig` object from an SDK configuration file.

        A configuration file's fields with improper names or values are ignored.

        :param config_path: Path to a configuration file; the default value is '/etc/kameleoon/client-python.yaml'
        :type config_path: str

        :return: Loaded `KameleoonClientConfig` object
        :rtype: KameleoonClientConfig

        :raises ConfigFileNotFound: Indicates that a configuration file with the passed config path is not found
        """
        if not os.path.exists(config_path):
            raise ConfigFileNotFound(f"No config file {config_path} or config object is found")
        with open(config_path, "r", encoding="utf-8") as yaml_file:
            config_dict: Dict[str, Any] = yaml.load(yaml_file, Loader=yaml.SafeLoader)
        client_id: str = config_dict.get("client_id", "1")
        client_secret: str = config_dict.get("client_secret", "2")
        kwargs: Dict[str, Any] = {}
        if isinstance(refresh_interval_minute := config_dict.get("refresh_interval_minute"), (int, float)):
            kwargs["refresh_interval_minute"] = float(refresh_interval_minute)
        if isinstance(session_duration_minute := config_dict.get("session_duration_minute"), (int, float)):
            kwargs["session_duration_minute"] = float(session_duration_minute)
        if isinstance(default_timeout_millisecond := config_dict.get("default_timeout_millisecond"), int):
            kwargs["default_timeout_millisecond"] = default_timeout_millisecond
        if isinstance(tracking_interval_millisecond := config_dict.get("tracking_interval_millisecond"), int):
            kwargs["tracking_interval_millisecond"] = tracking_interval_millisecond
        if isinstance(environment := config_dict.get("environment"), str):
            kwargs["environment"] = environment
        if isinstance(top_level_domain := config_dict.get("top_level_domain"), str):
            kwargs["top_level_domain"] = top_level_domain
        if isinstance(multi_threading := config_dict.get("multi_threading"), bool):
            kwargs["multi_threading"] = multi_threading
        return KameleoonClientConfig(client_id, client_secret, **kwargs)

    @property
    def client_id(self) -> str:
        """Returns the client ID"""
        return self.__client_id

    @property
    def client_secret(self) -> str:
        """Returns the client secret"""
        return self.__client_secret

    @property
    def logger(self) -> logging.Logger:
        """(Deprecated) Returns the logger instance"""
        return self.__logger

    def set_logger(self, value: logging.Logger) -> None:
        """(Deprecated) Sets the logger instance"""
        KameleoonLogger.warning(
            "The method `KameleoonClientConfig.set_logger` is deprecated. "
            "Please use `KameleoonLogger.set_logger` method instead."
        )
        self.__logger = value

    @property
    def refresh_interval_second(self) -> float:
        """Returns the refresh interval in seconds"""
        return self.__refresh_interval_second

    def set_refresh_interval_minute(self, value: float) -> None:
        """Sets the refresh interval in minutes"""
        if value <= 0:
            KameleoonLogger.warning("Configuration refresh interval must have positive value. "
                                    "Default refresh interval (%s minutes) was applied.",
                                    DEFAULT_REFRESH_INTERVAL_MINUTES)
            value = DEFAULT_REFRESH_INTERVAL_MINUTES
        self.__refresh_interval_second = value * 60.0

    @property
    def session_duration_second(self) -> float:
        """Returns the session duration in seconds"""
        return self.__session_duration_second

    def set_session_duration_minute(self, value: float) -> None:
        """Sets the session duration in minutes"""
        if value <= 0:
            KameleoonLogger.warning("Session duration must have positive value. Default session duration "
                                    "(%s minutes) was applied.", DEFAULT_SESSION_DURATION_MINUTES)
            value = DEFAULT_SESSION_DURATION_MINUTES
        self.__session_duration_second = value * 60.0

    @property
    def default_timeout_second(self) -> float:
        """Returns the default timeout in seconds"""
        return self.__default_timeout_second

    def set_default_timeout_millisecond(self, value: int) -> None:
        """Sets the default timeout in milliseconds"""
        if value <= 0:
            KameleoonLogger.warning("Default timeout must have positive value. Default value (%s ms) was applied.",
                                    DEFAULT_DEFAULT_TIMEOUT_MILLISECONDS)
            value = DEFAULT_DEFAULT_TIMEOUT_MILLISECONDS
        self.__default_timeout_second = value / 1000.0

    @property
    def tracking_interval_second(self) -> float:
        """Returns the tracking interval in seconds"""
        return self.__tracking_interval_second

    def set_tracking_interval_millisecond(self, value: int) -> None:
        """Sets the tracking interval in milliseconds"""
        if value < MIN_TRACKING_INTERVAL_MILLISECONDS:
            KameleoonLogger.warning(
                "Tracking interval must not be shorter than (%s ms). Minimum possible interval was applied.",
                MIN_TRACKING_INTERVAL_MILLISECONDS)
            value = MIN_TRACKING_INTERVAL_MILLISECONDS
        elif value > MAX_TRACKING_INTERVAL_MILLISECONDS:
            KameleoonLogger.warning(
                "Tracking interval must not be longer than (%s ms). Maximum possible interval was applied.",
                MAX_TRACKING_INTERVAL_MILLISECONDS)
            value = MAX_TRACKING_INTERVAL_MILLISECONDS
        self.__tracking_interval_second = value / 1000.0

    @property
    def environment(self) -> Optional[str]:
        """Returns the environment"""
        return self.__environment

    def set_environment(self, value: Optional[str]) -> None:
        """Sets the environment"""
        self.__environment = value

    @property
    def top_level_domain(self) -> str:
        """Returns the top level domain"""
        return self.__top_level_domain

    def set_top_level_domain(self, value: str) -> None:
        """Sets the top level domain"""
        if not value:
            KameleoonLogger.warning("Setting top level domain is strictly recommended, "
                                    "otherwise you may have problems when using subdomains.")
        self.__top_level_domain = validate_top_level_domain(value)

    @property
    def multi_threading(self) -> bool:
        """Returns the multi_threading flag state"""
        return self.__multi_threading

    def set_multi_threading(self, value: bool) -> None:
        """Sets the multi_threading flag state"""
        self.__multi_threading = value
        KameleoonLogger.warning("Configuration parameter 'multi_threading' is deprecated.")

    def __str__(self):
        return (
            f"KameleoonClientConfig{{"
            f"client_id:'{StringUtils.secret(self.__client_id)}',"
            f"client_secret:'{StringUtils.secret(self.__client_secret)}',"
            f"refresh_interval_second:{self.__refresh_interval_second},"
            f"session_duration_second:{self.__session_duration_second},"
            f"environment:'{self.__environment}',"
            f"default_timeout_millisecond:{self.__default_timeout_second},"
            f"top_level_domain:'{self.__top_level_domain}'}}")
