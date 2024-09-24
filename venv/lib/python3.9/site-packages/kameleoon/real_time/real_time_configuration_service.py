""" Kameleoon Real Time Configuration Service """
import json
from typing import Any, Callable, Dict, Optional

import requests
import sseclient

from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.helpers.multi_threading import run_in_thread
from kameleoon.real_time.real_time_event import RealTimeEvent

KAMELEOON_REAL_TIME_CONFIGURATION_THREAD = "KameleoonRealTimeConfigurationThread"
CONFIGURATION_UPDATE_EVENT = "configuration-update-event"


class RealTimeConfigurationService:
    """
    RealTimeConfigurationService uses for fetching updates of configuration
    (experiments and feature flags) in real time
    """

    def __init__(self, url: str, update_handler: Callable[[RealTimeEvent], Any]):
        """
        For RealTimeConfigurationService must be provided an url
        from where it can read the updates
        """
        self.url = url
        self.update_handler = update_handler
        self.need_close = False
        self.headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "Keep-Alive",
        }
        self.response: Optional[Any] = None
        self._create_sse_client()

    def _create_sse_client(self) -> None:
        if not self.need_close:
            run_in_thread(self._run_sse_client, KAMELEOON_REAL_TIME_CONFIGURATION_THREAD, with_event_loop=True)

    def _run_sse_client(self):
        KameleoonLogger.debug("Create SSE client")
        self.response = RealTimeConfigurationService._with_requests(self.url, self.headers)
        client = sseclient.SSEClient(self.response)
        try:
            for message in client.events():
                if self.need_close:
                    break
                if message.event == CONFIGURATION_UPDATE_EVENT:
                    event_dict = json.loads(message.data)
                    self.update_handler(RealTimeEvent(event_dict))
        except Exception as ex:  # pylint: disable=W0703
            KameleoonLogger.error("Error occurred within SSE client: %s", ex)
            self._create_sse_client()

    def close(self) -> None:
        """Closes the connection to the server"""
        KameleoonLogger.info('Real-time configuration service is shutting down')
        self.need_close = True
        if self.response is not None:
            self.response.close()

    @staticmethod
    def _with_requests(url: str, headers: Dict[str, Any]):
        """Get a streaming response for the given event feed using requests."""
        return requests.get(url, stream=True, headers=headers)

    # def _with_urllib3(self, url: str, headers: Dict[str, Any]):
    #     """Get a streaming response for the given event feed using urllib3."""
    #     http = urllib3.PoolManager()
    #     return http.request("GET", url, preload_content=False, headers=headers)
