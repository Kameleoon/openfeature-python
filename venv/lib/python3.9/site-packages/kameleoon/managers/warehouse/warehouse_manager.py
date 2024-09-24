"""Warehouse"""
from typing import Any, Coroutine, Optional
from kameleoon.data.custom_data import CustomData
from kameleoon.data.manager.visitor_manager import VisitorManager
from kameleoon.helpers.visitor_code import validate_visitor_code
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.network.network_manager import NetworkManager
from kameleoon.network.net_provider import Response
from kameleoon.network.services.data_service import DataService


# pylint: disable=R0801
class WarehouseManager:
    """Warehouse manager"""
    _WAREHOUSE_AUDIENCES_FIELD_NAME = "warehouseAudiences"

    def __init__(
        self, network_manager: NetworkManager, visitor_manager: VisitorManager
    ) -> None:
        KameleoonLogger.debug("CALL: WarehouseManager(network_manager, visitor_manager)")
        self._network_manager = network_manager
        self._visitor_manager = visitor_manager
        KameleoonLogger.debug("RETURN: WarehouseManager(network_manager, visitor_manager)")

    # fmt is disabled due issue in pylint, disabling R0801 doesn’t work
    # fmt: off
    async def get_visitor_warehouse_audience(
        self, visitor_code: str,
        custom_data_index: int,
        warehouse_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[CustomData]:
        # fmt: on
        """Retrieves and processes warehouse audience data for a given visitor."""
        KameleoonLogger.debug(
            "CALL: WarehouseManager.get_visitor_warehouse_audience(visitor_code: %s, custom_data_index: %s,"
            " warehouse_key: %s, timeout: %s)", visitor_code, custom_data_index, warehouse_key, timeout
        )
        validate_visitor_code(visitor_code)
        response = await self._request_visitor_warehouse_audience(visitor_code, warehouse_key, timeout)
        warehouse_audiences_data = self._parse_visitor_warehouse_audience_response(response, custom_data_index)
        if warehouse_audiences_data:
            self._visitor_manager.add_data(visitor_code, warehouse_audiences_data)
        KameleoonLogger.debug(
            "CALL: WarehouseManager.get_visitor_warehouse_audience(visitor_code: %s, custom_data_index: %s,"
            " warehouse_key: %s, timeout: %s) -> (custom_data: %s)",
            visitor_code, custom_data_index, warehouse_key, timeout, warehouse_audiences_data
        )
        return warehouse_audiences_data

    def _request_visitor_warehouse_audience(
        self, visitor_code: str, warehouse_key: Optional[str], timeout: Optional[float]
    ) -> Coroutine[Any, Any, Response]:
        remote_data_key = warehouse_key if warehouse_key else visitor_code
        service = self._network_manager.get_service(DataService)
        return service.get_remote_data(remote_data_key, timeout)

    def _parse_visitor_warehouse_audience_response(
        self, response: Response, custom_data_index: int
    ) -> Optional[CustomData]:
        if not response.success or (response.content is None):
            return None
        warehouse_audiences = response.content.get(self._WAREHOUSE_AUDIENCES_FIELD_NAME) \
            if response.success and isinstance(response.content, dict) else None
        data_values = warehouse_audiences.keys() if isinstance(warehouse_audiences, dict) else []
        return CustomData(custom_data_index, *data_values)
