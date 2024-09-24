"""Tracking"""
from typing import Iterable, List
from kameleoon.data.manager.visitor_manager import VisitorManager
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.managers.asyncexec.async_executor import AsyncExecutor
from kameleoon.managers.data.data_manager import DataManager
from kameleoon.managers.tracking.tracking_builder import TrackingBuilder
from kameleoon.managers.tracking.visitor_tracking_registry import (
    VisitorTrackingRegistry,
    LockVisitorTrackingRegistry,
)
from kameleoon.network.net_provider import Response
from kameleoon.network.network_manager import NetworkManager
from kameleoon.network.sendable import Sendable
from kameleoon.network.services.data_service import DataService


class TrackingManager:
    """Tracking manager"""
    LINES_DELIMITER = "\n"
    REQUEST_SIZE_LIMIT = 2560 * 1024  # 2.5 * 1024^2 characters

    # pylint: disable=R0913
    def __init__(
        self, data_manager: DataManager,
        network_manager: NetworkManager, visitor_manager: VisitorManager,
        track_interval_seconds: float, async_executor: AsyncExecutor
    ) -> None:
        KameleoonLogger.debug(
            "CALL: TrackingManager(data_manager, network_manager. visitor_manager, "
            "track_interval_seconds: %s, scheduler)", track_interval_seconds
        )
        self._tracking_visitors: VisitorTrackingRegistry = LockVisitorTrackingRegistry(visitor_manager)
        self._data_manager = data_manager
        self._network_manager = network_manager
        self._visitor_manager = visitor_manager
        self._async_executor = async_executor
        async_executor.scheduler.schedule_job("TrackingManager.track_all", track_interval_seconds, self.track_all)
        KameleoonLogger.debug(
            "RETURN: TrackingManager(data_manager, network_manager. visitor_manager, "
            "track_interval_seconds: %s, scheduler)", track_interval_seconds
        )

    def add_visitor_code(self, visitor_code: str) -> None:
        """Adds a visitor code to the tracking registry."""
        KameleoonLogger.debug("CALL: TrackingManager.add_visitor_code(visitor_code: %s)", visitor_code)
        self._tracking_visitors.add(visitor_code)
        KameleoonLogger.debug("RETURN: TrackingManager.add_visitor_code(visitor_code: %s)", visitor_code)

    def track_all(self) -> None:
        """
        Extracts the visitor codes from the tracking registry and tracks the corresponding visitors.

        `track_all` is triggered by the interval tracking timer.
        """
        KameleoonLogger.debug("CALL: TrackingManager.track_all()")
        self.__track(self._tracking_visitors.extract())
        KameleoonLogger.debug("RETURN: TrackingManager.track_all()")

    def track_visitor(self, visitor_code: str) -> None:
        """Tracks a single visitor code. Does not affect the tracking registry."""
        KameleoonLogger.debug("CALL: TrackingManager.track_visitor(visitor_code: %s)", visitor_code)
        self.__track([visitor_code])
        KameleoonLogger.debug("RETURN: TrackingManager.track_visitor(visitor_code: %s)", visitor_code)

    def __track(self, visitor_codes: Iterable[str]) -> None:
        builder = TrackingBuilder(
            visitor_codes, self._data_manager.data_file, self._visitor_manager, self.REQUEST_SIZE_LIMIT
        )
        builder.build()
        if builder.visitor_codes_to_keep:
            KameleoonLogger.warning(
                "Visitor data to be tracked exceeded the request size limit. "
                "Some visitor data is kept to be sent later. "
                "If it is not caused by the peak load, decreasing the tracking interval is recommended."
            )
            self._tracking_visitors.add_all(builder.visitor_codes_to_keep)
        self.__perform_tracking_request(
            builder.visitor_codes_to_send, builder.unsent_visitor_data, builder.tracking_lines
        )

    def __perform_tracking_request(
        self, visitor_codes: List[str], visitors_data: List[Sendable], tracking_lines: List[str]
    ) -> None:
        if not tracking_lines:
            return
        lines = self.LINES_DELIMITER.join(tracking_lines)
        # Mark unsent data as transmitted
        for sendable_data in visitors_data:
            sendable_data.mark_as_transmitting()

        async def call() -> Response:
            service = self._network_manager.get_service(DataService)
            response = await service.send_tracking_data(lines)
            if response.success:
                KameleoonLogger.debug("Successful request for tracking visitors: %s, data: %s",
                                      visitor_codes, visitors_data)
                for sendable_data in visitors_data:
                    sendable_data.mark_as_sent()
            else:
                KameleoonLogger.debug("Failed request for tracking visitors: %s, data: %s",
                                      visitor_codes, visitors_data)
                for sendable_data in visitors_data:
                    sendable_data.mark_as_unsent()
                self._tracking_visitors.add_all(visitor_codes)
            return response
        self._async_executor.run_coro(call(), "send_tracking_data")
