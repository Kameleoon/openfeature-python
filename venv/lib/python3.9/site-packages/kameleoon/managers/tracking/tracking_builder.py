"""Tracking"""
from typing import Iterable, List, Optional, Tuple
from kameleoon.configuration.data_file import DataFile
from kameleoon.configuration.rule_type import RuleType
from kameleoon.data.custom_data import CustomData
from kameleoon.data.manager.visitor import Visitor
from kameleoon.data.manager.visitor_manager import VisitorManager
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.network.activity_event import ActivityEvent
from kameleoon.network.sendable import Sendable
from kameleoon.network.query_builder import QueryParam, QueryParams


class TrackingBuilder:
    """Tracking builder"""
    def __init__(
        self, visitor_codes: Iterable[str], data_file: DataFile, visitor_manager: VisitorManager,
        request_size_limit: int
    ) -> None:
        self.__visitor_codes = visitor_codes
        self.__data_file = data_file
        self.__visitor_manager = visitor_manager
        self.__request_size_limit = request_size_limit
        self.__built = False
        self.__total_size = 0
        # result
        self.__visitor_codes_to_send: List[str] = []
        self.__visitor_codes_to_keep: List[str] = []
        self.__unsent_visitor_data: List[Sendable] = []
        self.__tracking_lines: List[str] = []

    @property
    def visitor_codes_to_send(self) -> List[str]:
        """Returns the visitor codes of the visitors which are to be tracked."""
        return self.__visitor_codes_to_send

    @property
    def visitor_codes_to_keep(self) -> List[str]:
        """Returns the visitor codes which are to be kept for the future tracking."""
        return self.__visitor_codes_to_keep

    @property
    def unsent_visitor_data(self) -> List[Sendable]:
        """Return the visitor data which is selected to be sent."""
        return self.__unsent_visitor_data

    @property
    def tracking_lines(self) -> List[str]:
        """Returns the tracking lines of the visitor data which is selected to be sent."""
        return self.__tracking_lines

    def build(self) -> None:
        """
        Processes the provided data to form the `visitor_codes_to_send`, `visitor_codes_to_keep`,
        `unsent_visitor_data`, and `tracking_lines` lists.

        Not thread-safe.
        """
        if self.__built:
            return
        for visitor_code in self.__visitor_codes:
            if self.__total_size <= self.__request_size_limit:
                visitor = self.__visitor_manager.get_visitor(visitor_code)
                is_consent_given = self.__is_consent_given(visitor)
                data = self.__collect_tracking_data(visitor_code, visitor, is_consent_given)
                if len(data) > 0:
                    TrackingBuilder.__log_visitor_track_sending(visitor_code, is_consent_given, data)
                    self.__visitor_codes_to_send.append(visitor_code)
                    self.__unsent_visitor_data.extend(data)
                else:
                    TrackingBuilder.__log_visitor_track_no_data(visitor_code, is_consent_given)
            else:
                self.__visitor_codes_to_keep.append(visitor_code)
        self.__built = True

    @staticmethod
    def __log_visitor_track_sending(visitor_code: str, is_consent_given: bool, data: List[Sendable]) -> None:
        KameleoonLogger.debug(
            "Sending tracking request for unsent data %s of visitor %s with given (or not required) consent %s",
            data, visitor_code, is_consent_given)

    @staticmethod
    def __log_visitor_track_no_data(visitor_code: str, is_consent_given: bool) -> None:
        KameleoonLogger.debug(
            "No data to send for visitor %s with given (or not required) consent %s",
            visitor_code, is_consent_given)

    def __is_consent_given(self, visitor: Optional[Visitor]) -> bool:
        return not self.__data_file.settings.is_consent_required or ((visitor is not None) and visitor.legal_consent)

    def __collect_tracking_data(
        self, visitor_code: str, visitor: Optional[Visitor], is_consent_given: bool
    ) -> List[Sendable]:
        use_mapping_value, visitor = self.__create_self_visitor_link_if_required(visitor_code, visitor)
        id_type = "mapping value" if use_mapping_value else "visitor code"
        KameleoonLogger.info("%s was used as a %s for visitor data tracking.", visitor_code, id_type)
        unsent_data = self.__get_unsent_visitor_data(visitor, is_consent_given)
        self.__collect_tracking_lines(visitor_code, visitor, unsent_data, use_mapping_value)
        return unsent_data

    def __create_self_visitor_link_if_required(
        self, visitor_code: str, visitor: Optional[Visitor]
    ) -> Tuple[bool, Optional[Visitor]]:
        is_mapped = (visitor is not None) and (visitor.mapping_identifier is not None)
        is_unique_identifier = (visitor is not None) and visitor.is_unique_identifier
        # need to find if anonymous visitor is behind unique (anonym doesn't exist if MappingIdentifier == null)
        if is_unique_identifier and not is_mapped:
            # We haven't anonymous behind, in this case we should create "fake" anonymous with id == visitorCode
            # and link it with with mapping value == visitorCode (like we do as we have real anonymous visitor)
            mapping_index = self.__data_file.custom_data_info.mapping_identifier_index
            if mapping_index is not None:
                visitor = self.__visitor_manager.add_data(visitor_code, CustomData(mapping_index, visitor_code))
        use_mapping_value = is_unique_identifier and \
            (visitor is not None) and (visitor_code != visitor.mapping_identifier)
        return use_mapping_value, visitor

    @staticmethod
    def __get_unsent_visitor_data(visitor: Optional[Visitor], is_consent_given: bool) -> List[Sendable]:
        unsent_data: List[Sendable] = []
        if visitor:
            if is_consent_given:
                unsent_data.extend(sd for sd in visitor.enumerate_sendable_data() if sd.unsent)
            else:
                unsent_data.extend(c for c in visitor.conversions if c.unsent)
                unsent_data.extend(
                    av for av in visitor.variations.values()
                    if av.unsent and (av.rule_type == RuleType.TARGETED_DELIVERY)
                )
        if not unsent_data and is_consent_given:
            unsent_data.append(ActivityEvent())
        return unsent_data

    def __collect_tracking_lines(
        self, visitor_code: str, visitor: Optional[Visitor], unsent_data: List[Sendable], use_mapping_value: bool
    ) -> None:
        visitor_code_param = \
            str(QueryParam(QueryParams.MAPPING_VALUE if use_mapping_value else QueryParams.VISITOR_CODE, visitor_code))
        user_agent = visitor.user_agent if visitor else None
        for data in unsent_data:
            line = data.encode_query()
            if line:
                line = self.__add_line_params(line, visitor_code_param, user_agent)
                self.__total_size += len(line)
                self.__tracking_lines.append(line)
                user_agent = None

    @staticmethod
    def __add_line_params(tracking_line: str, visitor_code_param: str, user_agent: Optional[str]) -> str:
        tracking_line += f"&{visitor_code_param}"
        if user_agent:
            ua_qp = QueryParam(QueryParams.USER_AGENT, user_agent)
            tracking_line += f"&{ua_qp}"
        return tracking_line
