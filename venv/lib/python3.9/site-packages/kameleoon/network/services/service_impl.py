"""Services"""
import asyncio
from typing import Any, Coroutine

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.logging.log_level import LogLevel
from kameleoon.network.network_manager import NetworkManager
from kameleoon.network.services.service import Service
from kameleoon.network.net_provider import Response, Request


class ServiceImpl(Service):
    """Service implementation"""
    NUMBER_OF_RECONNECTION_ON_FAILURE_CRITICAL = 2
    NUMBER_OF_RECONNECTION_ON_FAILURE_UNCRITICAL = 1

    @property
    def network_manager(self):
        return self.__network_manager

    def __init__(self, network_manager: NetworkManager) -> None:
        super().__init__()
        self.__network_manager = network_manager

    async def _make_call(
        self, request: Request, try_access_token_auth: bool, retry_limit=0, retry_delay=0.0
    ) -> Response:
        KameleoonLogger.debug('Running request %s with access token %s, retry limit %s, retry delay %s ms',
                              request, try_access_token_auth, retry_limit, retry_delay)
        net_provider = self.__network_manager.net_provider
        access_token_source = self.__network_manager.access_token_source
        attempt = 0
        success = False
        while not success and (attempt <= retry_limit):
            if (attempt > 0) and (retry_delay > 0.0):
                await self._delay(retry_delay)
            if try_access_token_auth:
                token = await access_token_source.get_token(request.timeout)
                request.authorize(token)
            response = await net_provider.run_request(request)
            if response.error is not None:
                log_level = LogLevel.WARNING if attempt < retry_limit else LogLevel.ERROR
                KameleoonLogger.log(log_level, "%s call %s failed: Error occurred during request: %s",
                                    request.method.name, request.url, response.error)
            elif not response.is_expected_status_code:
                log_level = LogLevel.WARNING if attempt < retry_limit else LogLevel.ERROR
                KameleoonLogger.log(log_level, "%s call %s failed: Received unexpected status code %s",
                                    request.method.name, request.url, response.code)
                if request.access_token and (response.code == 401):
                    KameleoonLogger.warning("Unexpected rejection of access token %s", request.access_token)
                    access_token_source.discard_token(request.access_token)
                    if attempt == retry_limit:
                        try_access_token_auth = False
                        retry_delay = 0.0
                        request.authorize(None)
                        attempt -= 1
                        KameleoonLogger.error("Wrong Kameleoon API access token slows down the SDK's requests")
            else:
                success = True
            attempt += 1
        KameleoonLogger.debug("Fetched response %s for request %s", response, request)
        return response

    @staticmethod
    def _delay(period: float) -> Coroutine[Any, Any, None]:
        return asyncio.sleep(period)
