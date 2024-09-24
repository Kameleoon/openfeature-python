"""Visitor"""
from threading import Lock
from typing import Any, Callable, Optional, Dict, List, Iterator, cast

from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.data.data import Data
from kameleoon.data.browser import Browser
from kameleoon.data.conversion import Conversion
from kameleoon.data.cookie import Cookie
from kameleoon.data.custom_data import CustomData
from kameleoon.data.device import Device
from kameleoon.data.geolocation import Geolocation
from kameleoon.data.kcs_heat import KcsHeat
from kameleoon.data.mapping_identifier import MappingIdentifier
from kameleoon.data.operating_system import OperatingSystem
from kameleoon.data.page_view import PageView
from kameleoon.data.unique_identifier import UniqueIdentifier
from kameleoon.data.user_agent import UserAgent
from kameleoon.data.manager.assigned_variation import AssignedVariation
from kameleoon.data.manager.page_view_visit import PageViewVisit
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.network.sendable import Sendable


EMPTY_DICT: Dict[Any, Any] = {}
EMPTY_LIST: List[Any] = []


class Visitor:
    """Visitor"""
    def __init__(self, source: Optional["Visitor"] = None) -> None:
        if source is None:
            self._data = Visitor.VisitorData()
            self._is_unique_identifier = False
        else:
            self._data = source._data
            self._is_unique_identifier = source._is_unique_identifier

    def clone(self) -> "Visitor":
        """Creates and returns a clone of the current Visitor instance which shares all the visitor data."""
        return Visitor(self)

    def enumerate_sendable_data(self) -> Iterator[Sendable]:
        """Enumerates all sendable data associated with this Visitor."""
        KameleoonLogger.debug('CALL: Visitor.enumerate_sendable_data()')
        sendable_data = self._data.enumerate_sendable_data()
        KameleoonLogger.debug('RETURN: Visitor.enumerate_sendable_data() -> (sendable_data)')
        return sendable_data

    def count_sendable_data(self) -> int:
        """Counts the number of sendable data items associated with this Visitor."""
        KameleoonLogger.debug('CALL: Visitor.count_sendable_data()')
        count_sendable_data = self._data.count_sendable_data()
        KameleoonLogger.debug('RETURN: Visitor.count_sendable_data() -> (count: %s)', count_sendable_data)
        return count_sendable_data

    @property
    def user_agent(self) -> Optional[str]:
        """Returns the user agent string associated with this Visitor."""
        user_agent = self._data.user_agent
        KameleoonLogger.debug('CALL/RETURN: Visitor.user_agent -> (user_agent: %s)', user_agent)
        return user_agent

    @property
    def device(self) -> Optional[Device]:
        """Returns the device information associated with this Visitor."""
        device = self._data.device
        KameleoonLogger.debug('CALL/RETURN: Visitor.device -> (device: %s)', device)
        return device

    @property
    def browser(self) -> Optional[Browser]:
        """Returns the browser information associated with this Visitor."""
        browser = self._data.browser
        KameleoonLogger.debug('CALL/RETURN: Visitor.browser -> (browser: %s)', browser)
        return browser

    @property
    def geolocation(self) -> Optional[Geolocation]:
        """Returns the geolocation information associated with this Visitor."""
        geolocation = self._data.geolocation
        KameleoonLogger.debug('CALL/RETURN: Visitor.geolocation -> (geolocation: %s)', geolocation)
        return geolocation

    @property
    def operating_system(self) -> Optional[OperatingSystem]:
        """Returns the operating system information associated with this Visitor."""
        operating_system = self._data.operating_system
        KameleoonLogger.debug('CALL/RETURN: Visitor.operating_system -> (operating_system: %s)', operating_system)
        return operating_system

    @property
    def cookie(self) -> Optional[Cookie]:
        """Returns the cookie information associated with this Visitor."""
        cookie = self._data.cookie
        KameleoonLogger.debug('CALL/RETURN: Visitor.cookie -> (cookie: %s)', cookie)
        return cookie

    @property
    def custom_data(self) -> Dict[int, CustomData]:
        """Returns the custom data associated with this Visitor."""
        custom_data = EMPTY_DICT if self._data.custom_data_dict is None else self._data.custom_data_dict.copy()
        KameleoonLogger.debug('CALL/RETURN: Visitor.custom_data -> (custom_data: %s)', custom_data)
        return custom_data

    @property
    def page_view_visits(self) -> Dict[str, PageViewVisit]:
        """Returns the page view visits associated with this Visitor."""
        page_view_visits = EMPTY_DICT if self._data.page_view_visits is None else self._data.page_view_visits.copy()
        KameleoonLogger.debug('CALL/RETURN: Visitor.page_view_visits -> (page_view_visits: %s)', page_view_visits)
        return page_view_visits

    @property
    def conversions(self) -> List[Conversion]:
        """Returns the conversions associated with this Visitor."""
        conversions = EMPTY_LIST if self._data.conversions is None else self._data.conversions.copy()
        KameleoonLogger.debug('CALL/RETURN: Visitor.conversions -> (conversions: %s)', conversions)
        return conversions

    @property
    def variations(self) -> Dict[int, AssignedVariation]:
        """Returns the variations associated with this Visitor."""
        variations = EMPTY_DICT if self._data.variations is None else self._data.variations.copy()
        KameleoonLogger.debug('CALL/RETURN: Visitor.variations -> (variations: %s)', variations)
        return variations

    @property
    def kcs_heat(self) -> Optional[KcsHeat]:
        """Returns the KCS heat data associated with this Visitor."""
        kcs_heat = self._data.kcs_heat
        KameleoonLogger.debug('CALL/RETURN: Visitor.kcs_heat -> (kcs_heat: %s)', kcs_heat)
        return kcs_heat

    @property
    def visitor_visits(self) -> Optional[VisitorVisits]:
        """Returns the visitor visits data associated with this Visitor."""
        visitor_visits = self._data.visitor_visits
        KameleoonLogger.debug('CALL/RETURN: Visitor.visitor_visits -> (visitor_visits: %s)', visitor_visits)
        return visitor_visits

    def assign_variation(self, variation: AssignedVariation) -> None:
        """Assigns a variation to the Visitor."""
        KameleoonLogger.debug('CALL: Visitor.assign_variation(variation: %s)', variation)
        if self._data.variations is None:
            with self._data.lock:
                if self._data.variations is None:
                    self._data.variations = {variation.experiment_id: variation}
                    KameleoonLogger.debug('RETURN: Visitor.assign_variation(variation: %s)', variation)
                    return
        self._data.variations[variation.experiment_id] = variation
        KameleoonLogger.debug('RETURN: Visitor.assign_variation(variation: %s)', variation)

    def add_data(self, *args, overwrite: bool = True) -> None:
        """Adds data to the Visitor."""
        KameleoonLogger.debug('CALL: Visitor.add_data(args: %s, overwrite: %s)', args, overwrite)
        with self._data.lock:
            for data in args:
                data_type = type(data)
                data_adder = self.DATA_ADDERS.get(data_type)
                if data_adder:
                    data_adder(self, self.DataAddingContext(data, overwrite))
                else:
                    KameleoonLogger.warning("Data has unsupported type %s", data_type)
        KameleoonLogger.debug('RETURN: Visitor.add_data(args: %s, overwrite: %s)', args, overwrite)

    @property
    def mapping_identifier(self) -> Optional[str]:
        """Returns the mapping identifier associated with this Visitor."""
        mapping_identifier = self._data.mapping_identifier
        KameleoonLogger.debug('CALL/RETURN: Visitor.mapping_identifier -> (mapping_identifier: %s)',
                              mapping_identifier)
        return mapping_identifier

    @mapping_identifier.setter
    def mapping_identifier(self, value: str):
        """Sets the mapping identifier for this Visitor."""
        self._data.mapping_identifier = value
        KameleoonLogger.debug("CALL/RETURN: Visitor.mapping_identifier <- (mapping_identifier: %s)", value)

    @property
    def legal_consent(self) -> bool:
        """Returns the legal consent status for this Visitor."""
        legal_consent = self._data.legal_consent
        KameleoonLogger.debug('CALL/RETURN: Visitor.legal_consent -> (legal_consent: %s)', legal_consent)
        return legal_consent

    @legal_consent.setter
    def legal_consent(self, value: bool):
        """Sets the legal consent status for this Visitor."""
        self._data.legal_consent = value
        KameleoonLogger.debug("CALL/RETURN: Visitor.legal_consent <- (legal_consent: %s)", value)

    @property
    def is_unique_identifier(self) -> bool:
        """Returns the unique identifier status for this Visitor."""
        is_unique_identifier = self._is_unique_identifier
        KameleoonLogger.debug('CALL/RETURN: Visitor.is_unique_identifier -> (is_unique_identifier: %s)',
                              is_unique_identifier)
        return is_unique_identifier

    class VisitorData:
        """Visitor Data"""
        def __init__(self) -> None:
            self.lock = Lock()
            self.user_agent: Optional[str] = None
            self.device: Optional[Device] = None
            self.browser: Optional[Browser] = None
            self.geolocation: Optional[Geolocation] = None
            self.operating_system: Optional[OperatingSystem] = None
            self.cookie: Optional[Cookie] = None
            self.custom_data_dict: Optional[Dict[int, CustomData]] = None
            self.page_view_visits: Optional[Dict[str, PageViewVisit]] = None
            self.conversions: Optional[List[Conversion]] = None
            self.variations: Optional[Dict[int, AssignedVariation]] = None
            self.kcs_heat: Optional[KcsHeat] = None
            self.visitor_visits: Optional[VisitorVisits] = None
            self.mapping_identifier: Optional[str] = None
            self.legal_consent = False

        def enumerate_sendable_data(self) -> Iterator[Sendable]:
            """Iterates over all sendable data associated with the visitor."""
            if self.device:
                yield self.device
            if self.browser:
                yield self.browser
            if self.geolocation:
                yield self.geolocation
            if self.operating_system:
                yield self.operating_system
            if self.custom_data_dict is not None:
                yield from list(self.custom_data_dict.values())
            if self.page_view_visits is not None:
                yield from (visit.page_view for visit in list(self.page_view_visits.values()))
            if self.conversions is not None:
                yield from list(self.conversions)
            if self.variations is not None:
                yield from list(self.variations.values())

        def count_sendable_data(self) -> int:
            """Counts the total number of sendable data items associated with the visitor."""
            count = 0
            if self.device is not None:
                count += 1
            if self.browser is not None:
                count += 1
            if self.geolocation is not None:
                count += 1
            if self.operating_system is not None:
                count += 1
            if self.custom_data_dict is not None:
                count += len(self.custom_data_dict)
            if self.page_view_visits is not None:
                count += len(self.page_view_visits)
            if self.conversions is not None:
                count += len(self.conversions)
            if self.variations is not None:
                count += len(self.variations)
            return count

    class DataAddingContext:
        """Data adding context"""
        def __init__(
            self, data: Data, overwrite: bool = True
        ) -> None:
            self._data = data
            self._overwrite = overwrite

        @property
        def data(self) -> Data:
            """Returns the data."""
            return self._data

        @property
        def overwrite(self) -> bool:
            """Returns the overwrite."""
            return self._overwrite

    def _set_user_agent(self, context: DataAddingContext) -> None:
        self._data.user_agent = cast(UserAgent, context.data).value

    def _set_device(self, context: DataAddingContext) -> None:
        if context.overwrite or self._data.device is None:
            self._data.device = cast(Device, context.data)

    def _add_variation(self, context: DataAddingContext) -> None:
        variation = cast(AssignedVariation, context.data)
        if self._data.variations is None:
            self._data.variations = {}
        if context.overwrite or variation.experiment_id not in self.variations:
            self._data.variations[variation.experiment_id] = variation

    def _set_browser(self, context: DataAddingContext) -> None:
        if context.overwrite or self._data.browser is None:
            self._data.browser = cast(Browser, context.data)

    def _set_geolocation(self, context: DataAddingContext) -> None:
        if context.overwrite or self._data.geolocation is None:
            self._data.geolocation = cast(Geolocation, context.data)

    def _set_operating_system(self, context: DataAddingContext) -> None:
        if context.overwrite or self._data.operating_system is None:
            self._data.operating_system = cast(OperatingSystem, context.data)

    def _set_cookie(self, context: DataAddingContext) -> None:
        self._data.cookie = cast(Cookie, context.data)

    def _add_custom_data(self, context: DataAddingContext) -> None:
        custom_data = cast(CustomData, context.data)
        if self._data.custom_data_dict is None:
            self._data.custom_data_dict = {}
        if context.overwrite or custom_data.id not in self._data.custom_data_dict:
            self._data.custom_data_dict[custom_data.id] = custom_data

    def _add_page_view(self, context: DataAddingContext) -> None:
        page_view = cast(PageView, context.data)
        if len(page_view.url) == 0:
            KameleoonLogger.error("Passed PageView data is invalid because of empty 'url' field; the data was ignored.")
            return
        if self._data.page_view_visits is None:
            self._data.page_view_visits = {page_view.url: PageViewVisit(page_view)}
        else:
            if visit := self._data.page_view_visits.get(page_view.url):
                visit.overwrite(page_view)
            else:
                self._data.page_view_visits[page_view.url] = PageViewVisit(page_view)

    def _add_page_view_visit(self, context: DataAddingContext) -> None:
        page_view_visit = cast(PageViewVisit, context.data)
        if self._data.page_view_visits is None:
            self._data.page_view_visits = {}
        if visit := self._data.page_view_visits.get(page_view_visit.page_view.url):
            visit.merge(page_view_visit)
        else:
            self._data.page_view_visits[page_view_visit.page_view.url] = page_view_visit

    def _add_conversion(self, context: DataAddingContext) -> None:
        conversion = cast(Conversion, context.data)
        if self._data.conversions is None:
            self._data.conversions = [conversion]
        else:
            self._data.conversions.append(conversion)

    def _set_kcs_heat(self, context: DataAddingContext) -> None:
        self._data.kcs_heat = cast(KcsHeat, context.data)

    def _set_visitor_visits(self, context: DataAddingContext) -> None:
        self._data.visitor_visits = cast(VisitorVisits, context.data)

    def _set_is_unique_identifier(self, context: DataAddingContext) -> None:
        self._is_unique_identifier = cast(UniqueIdentifier, context.data).value

    def __str__(self):
        return "Visitor{}"

    DATA_ADDERS: Dict[type, Callable[["Visitor", DataAddingContext], None]] = {
        UserAgent: _set_user_agent,
        Device: _set_device,
        Browser: _set_browser,
        Geolocation: _set_geolocation,
        OperatingSystem: _set_operating_system,
        Cookie: _set_cookie,
        CustomData: _add_custom_data,
        MappingIdentifier: _add_custom_data,
        PageView: _add_page_view,
        PageViewVisit: _add_page_view_visit,
        Conversion: _add_conversion,
        KcsHeat: _set_kcs_heat,
        VisitorVisits: _set_visitor_visits,
        AssignedVariation: _add_variation,
        UniqueIdentifier: _set_is_unique_identifier,
    }
