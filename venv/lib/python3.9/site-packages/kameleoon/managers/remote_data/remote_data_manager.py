"""Remote data"""
from typing import Optional, Any, List
from kameleoon.configuration.custom_data_info import CustomDataInfo
from kameleoon.data import Data
from kameleoon.data.data import BaseData
from kameleoon.data.manager.visitor_manager import VisitorManager
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.managers.data.data_manager import DataManager
from kameleoon.managers.remote_data.remote_visitor_data import RemoteVisitorData
from kameleoon.network.net_provider import Response
from kameleoon.network.network_manager import NetworkManager
from kameleoon.network.services.data_service import DataService
from kameleoon.types.remote_visitor_data_filter import RemoteVisitorDataFilter


class RemoteDataManager:
    """Remote data manager"""
    def __init__(
        self, data_manager: DataManager, network_manager: NetworkManager, visitor_manager: VisitorManager
    ) -> None:
        KameleoonLogger.debug("CALL: RemoteDataManager(data_manager, network_manager, visitor_manager)")
        self._data_manager = data_manager
        self._network_manager = network_manager
        self._visitor_manager = visitor_manager
        KameleoonLogger.debug("RETURN: RemoteDataManager(data_manager, network_manager, visitor_manager)")

    async def get_data(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """Retrieves remote data from a remote service based on the provided key."""
        KameleoonLogger.debug("CALL: RemoteDataManager.get_data(key: %s, timeout: %s)", key, timeout)
        service: DataService = self._network_manager.get_service(DataService)
        response = await service.get_remote_data(key, timeout)
        remote_data = response.content
        KameleoonLogger.debug("RETURN: RemoteDataManager.get_data(key: %s, timeout: %s) -> (remote_data: %s)",
                              key, timeout, remote_data)
        return remote_data

    async def get_visitor_data(
        self,
        visitor_code: str,
        add_data: bool = True,
        data_filter: Optional[RemoteVisitorDataFilter] = None,
        timeout: Optional[float] = None,
    ) -> List[Data]:
        """Retrieves remote visitor data from a remote service based on the provided visitor code."""
        KameleoonLogger.debug(
            "CALL: RemoteDataManager.get_visitor_data(visitor_code: %s, add_data: %s, data_filter: %s, timeout: %s)",
            visitor_code, add_data, data_filter, timeout)
        # TODO: Uncomment with the next major update # pylint: disable=W0511
        # validate_visitor_code(visitor_code)
        visitor = self._visitor_manager.get_visitor(visitor_code)
        is_unique_identifier = (visitor is not None) and visitor.is_unique_identifier
        if data_filter is None:
            data_filter = RemoteVisitorDataFilter()
        service: DataService = self._network_manager.get_service(DataService)
        response = await service.get_remote_visitor_data(visitor_code, data_filter, is_unique_identifier, timeout)
        visitor_data = self.__handle_remote_visitor_data_response(response, visitor_code, add_data)
        KameleoonLogger.debug(
            "CALL: RemoteDataManager.get_visitor_data(visitor_code: %s, add_data: %s, data_filter: %s, timeout: %s) "
            "-> (visitor_data: %s)", visitor_code, add_data, data_filter, timeout, visitor_data)
        return visitor_data

    def __handle_remote_visitor_data_response(
        self, response: Response, visitor_code: str, add_data: bool
    ) -> List[Data]:
        if response.content is None:
            return []
        custom_data_info = self._data_manager.data_file.custom_data_info
        data_to_add, data_to_return = RemoteDataManager.__parse_remote_visitor_data(custom_data_info, response.content)
        if add_data and data_to_add:
            # Cannot use `VisitorManager.add_data` because it could use remote visitor data for mapping.
            visitor = self._visitor_manager.get_or_create_visitor(visitor_code)
            visitor.add_data(*data_to_add, overwrite=False)
        return data_to_return

    @staticmethod
    def __parse_remote_visitor_data(
            custom_data_info: CustomDataInfo, raw: Any
    ) -> tuple[List[BaseData], List[Data]]:
        try:
            remote_visitor_data = RemoteVisitorData(raw)
            remote_visitor_data.mark_data_as_sent(custom_data_info)
            return remote_visitor_data.collect_data_to_add(), remote_visitor_data.collect_data_to_return()
        except Exception as ex:  # pylint: disable=W0703
            KameleoonLogger.error("Parsing of remote visitor data failed: %s", ex)
            return [], []
