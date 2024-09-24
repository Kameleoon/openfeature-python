"""Services"""
from typing import Any, Coroutine, Optional

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.network.services.service_impl import ServiceImpl
from kameleoon.network.services.data_service import DataService
from kameleoon.network.net_provider import ResponseContentType, Response, Request, HttpMethod
from kameleoon.types.remote_visitor_data_filter import RemoteVisitorDataFilter


class DataServiceImpl(DataService, ServiceImpl):
    """Data service implementation"""
    _TRACKING_CALL_RETRY_DELAY = 5.0  # in seconds

    def __init__(self, network_manager) -> None:
        KameleoonLogger.debug('CALL: DataServiceImpl(networkManager)')
        DataService.__init__(self)
        ServiceImpl.__init__(self, network_manager)
        KameleoonLogger.debug('RETURN: DataServiceImpl(networkManager)')

    def send_tracking_data(self, lines: str, timeout: Optional[float] = None) -> Coroutine[Any, Any, Response]:
        KameleoonLogger.debug("CALL: DataServiceImpl.send_tracking_data(lines: %s, timeout: %s)", lines, timeout)
        if timeout is None:
            timeout = self.network_manager.call_timeout
        url = self.network_manager.url_provider.make_tracking_url()
        request = Request(HttpMethod.POST, url, timeout, body=lines)
        response = self._make_call(
            request, True, self.NUMBER_OF_RECONNECTION_ON_FAILURE_UNCRITICAL, self._TRACKING_CALL_RETRY_DELAY
        )
        KameleoonLogger.debug(
            "RETURN: DataServiceImpl.send_tracking_data(lines: %s, timeout: %s) -> (response_coroutine)",
            lines, timeout)
        return response

    def get_remote_data(self, key: str, timeout: Optional[float] = None
                        ) -> Coroutine[Any, Any, Response]:
        KameleoonLogger.debug("CALL: DataServiceImpl.get_remote_data(key: %s, timeout: %s)", key, timeout)
        if timeout is None:
            timeout = self.network_manager.call_timeout
        url = self.network_manager.url_provider.make_api_data_get_request_url(key)
        request = Request(HttpMethod.GET, url, timeout, response_content_type=ResponseContentType.JSON)
        response = self._make_call(request, True)
        KameleoonLogger.debug(
            "RETURN: DataServiceImpl.get_remote_data(key: %s, timeout: %s) -> (response_coroutine)",
            key, timeout
        )
        return response

    # fmt is disabled due issue in pylint, disabling R0801 doesn’t work
    # fmt: off
    def get_remote_visitor_data(
        self, visitor_code: str,
        data_filter: RemoteVisitorDataFilter,
        is_unique_identifier: bool,
        timeout: Optional[float] = None,
    ) -> Coroutine[Any, Any, Response]:
        # fmt: on
        KameleoonLogger.debug(
            "CALL: DataServiceImpl.get_remote_visitor_data(visitor_code: %s, data_filter: %s, "
            "is_unique_identifier: %s, timeout: %s)",
            visitor_code, data_filter, is_unique_identifier, timeout
        )
        if timeout is None:
            timeout = self.network_manager.call_timeout
        url = self.network_manager.url_provider.make_visitor_data_get_url(
            visitor_code, data_filter, is_unique_identifier
        )
        request = Request(HttpMethod.GET, url, timeout, response_content_type=ResponseContentType.JSON)
        response = self._make_call(request, True)
        KameleoonLogger.debug(
            "RETURN: DataServiceImpl.get_remote_visitor_data(visitor_code: %s, data_filter: %s, "
            "is_unique_identifier: %s, timeout: %s) -> (response_coroutine)",
            visitor_code, data_filter, is_unique_identifier, timeout
        )
        return response
