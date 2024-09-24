"""Remote data"""
from typing import Dict, Optional, Any, List

from kameleoon.helpers.functions import enum_from_name_literal

from kameleoon.data.data import BaseData

from kameleoon.network.sendable import Sendable
from kameleoon.configuration.custom_data_info import CustomDataInfo
from kameleoon.configuration.rule_type import RuleType
from kameleoon.data.visitor_visits import VisitorVisits
from kameleoon.data.kcs_heat import KcsHeat
from kameleoon.data.manager.assigned_variation import AssignedVariation
from kameleoon.data.manager.page_view_visit import PageViewVisit
from kameleoon.data import (
    CustomData,
    PageView,
    Conversion,
    Geolocation,
    Device,
    Browser,
    OperatingSystem,
    DeviceType,
    BrowserType,
    OperatingSystemType, Data,
)


class RemoteVisitorData:
    """Remote visitor data"""
    def __init__(self, json: Dict[str, Any]) -> None:
        self.__geolocation: Optional[Geolocation] = None
        self.__device: Optional[Device] = None
        self.__browser: Optional[Browser] = None
        self.__operating_system: Optional[OperatingSystem] = None
        self.__page_view_visits: Optional[Dict[str, PageViewVisit]] = None
        self.__custom_data_dict: Optional[Dict[int, CustomData]] = None
        self.__experiments: Optional[Dict[int, AssignedVariation]] = None
        self.__conversions: Optional[List[Conversion]] = None
        self.__previous_visitor_visits: Optional[VisitorVisits] = None
        current_visit = json.get("currentVisit")
        if current_visit is not None:
            self.__parse_visit(current_visit)
        previous_visits = json.get("previousVisits")
        if previous_visits:
            times_started = []
            for visit in previous_visits:
                times_started.append(visit.get("timeStarted", 0))
                self.__parse_visit(visit)
            self.__previous_visitor_visits = VisitorVisits(times_started)
        self.__kcs_heat = self.__parse_kcs_heat(json.get("kcs"))

    def collect_data_to_add(self) -> List[BaseData]:
        """Collects all data from remote visitor data that needs to be added."""
        data_to_add: List[BaseData] = []
        if self.__custom_data_dict:
            data_to_add += self.__custom_data_dict.values()
        if self.__previous_visitor_visits:
            data_to_add.append(self.__previous_visitor_visits)
        if self.__kcs_heat:
            data_to_add.append(self.__kcs_heat)
        if self.__page_view_visits:
            data_to_add += self.__page_view_visits.values()
        if self.__experiments:
            data_to_add += self.__experiments.values()
        if self.__conversions:
            data_to_add += self.__conversions
        data_to_add += self.__single_data()
        return data_to_add

    def collect_data_to_return(self) -> List[Data]:
        """Collects all data from remote visitor data that should be returned."""
        data_to_return: List[Data] = []
        if self.__custom_data_dict:
            data_to_return += self.__custom_data_dict.values()
        if self.__page_view_visits:
            for visit in self.__page_view_visits.values():
                data_to_return.append(visit.page_view)
        data_to_return += self.__single_data()
        if self.__conversions:
            data_to_return += self.__conversions
        return data_to_return

    def mark_data_as_sent(self, custom_data_info: Optional[CustomDataInfo]) -> None:  # noqa: C901
        """Marks data as sent based on the provided `custom_data_info`."""
        if self.__custom_data_dict:
            for data in self.__custom_data_dict.values():
                if custom_data_info is None or not custom_data_info.is_visitor_scope(data.id):
                    data.mark_as_sent()
        if self.__experiments:
            for experiment in self.__experiments.values():
                experiment.mark_as_sent()
        if self.__page_view_visits:
            for visit in self.__page_view_visits.values():
                visit.page_view.mark_as_sent()
        for single_data in self.__single_data():
            if isinstance(single_data, Sendable):
                single_data.mark_as_sent()
        if self.__conversions:
            for conversion in self.__conversions:
                conversion.mark_as_sent()

    def __parse_visit(self, json_visit: Dict[str, Any]) -> None:
        custom_data_events = json_visit.get("customDataEvents")
        if custom_data_events:
            self.__parse_custom_data(custom_data_events)
        page_events = json_visit.get("pageEvents")
        if page_events:
            self.__parse_pages(page_events)
        experiment_events = json_visit.get("experimentEvents")
        if experiment_events:
            self.__parse_experiments(experiment_events)
        conversion_events = json_visit.get("conversionEvents")
        if conversion_events:
            self.__parse_conversions(conversion_events)
        geolocation_events = json_visit.get("geolocationEvents")
        if self.__geolocation is None and geolocation_events:
            self.__parse_geolocation(geolocation_events[-1])
        static_data_event = json_visit.get("staticDataEvent")
        if static_data_event:
            self.__parse_static_data(static_data_event)

    def __parse_custom_data(self, custom_data_events: List[Dict[str, Any]]) -> None:
        if self.__custom_data_dict is None:
            self.__custom_data_dict = {}
        for custom_data_event in reversed(custom_data_events):
            data = custom_data_event.get("data")
            if data is not None:
                index = data.get("index", -1)
                if index not in self.__custom_data_dict:
                    data_keys = [*data.get("valuesCountMap")]
                    self.__custom_data_dict[index] = CustomData(index, *data_keys)

    def __parse_pages(self, page_events: List[Dict[str, Any]]) -> None:
        if self.__page_view_visits is None:
            self.__page_view_visits = {}
        for page_event in reversed(page_events):
            data = page_event.get("data")
            if data is None:
                continue
            href = data.get("href")
            if href is None:
                continue
            page_view_visit = self.__page_view_visits.get(href)
            if page_view_visit is None:
                page_view = PageView(href, data.get("title"))
                self.__page_view_visits[href] = PageViewVisit(page_view, 1, page_event.get("time"))
            else:
                page_view_visit.increase_page_visits()

    def __parse_experiments(self, experiment_events: List[Dict[str, Any]]) -> None:
        if self.__experiments is None:
            self.__experiments = {}
        for experiment_event in reversed(experiment_events):
            data = experiment_event.get("data")
            if data is not None:
                index = data.get("id")
                variation_id = data.get("variationId")
                if index is not None and variation_id is not None:
                    if index not in self.__experiments:
                        time = experiment_event.get("time")
                        if time is not None:
                            time /= 1000
                        variation = AssignedVariation(
                            index, variation_id, RuleType.UNKNOWN, time
                        )
                        self.__experiments[index] = variation

    def __parse_conversions(self, conversion_events: List[Dict[str, Any]]) -> None:
        if self.__conversions is None:
            self.__conversions = []
        for conversion_event in conversion_events:
            data = conversion_event.get("data")
            if data is not None:
                goal_id = data.get("goalId")
                if goal_id is not None:
                    self.__conversions.append(Conversion(goal_id, data.get("revenue"), data.get("negative")))

    def __parse_geolocation(self, geolocation_event: Dict[str, Any]) -> None:
        data = geolocation_event.get("data")
        if data is not None:
            country = data.get("country")
            if country is not None:
                self.__geolocation = Geolocation(country, data.get("region"), data.get("city"))

    def __parse_static_data(self, static_data_event: Dict[str, Any]) -> None:
        if self.__device and self.__browser and self.__operating_system:
            return
        data = static_data_event.get("data")
        if data is not None:
            if self.__device is None:
                device_type = enum_from_name_literal(data.get("deviceType"), DeviceType, None)
                if device_type is not None:
                    self.__device = Device(device_type)
            if self.__browser is None:
                browser_type = enum_from_name_literal(data.get("browser"), BrowserType, None)
                if browser_type is not None:
                    self.__browser = Browser(browser_type, data.get("browserVersion"))
            if self.__operating_system is None:
                operating_system_type = enum_from_name_literal(data.get("os"), OperatingSystemType, None)
                if operating_system_type is not None:
                    self.__operating_system = OperatingSystem(operating_system_type)

    def __single_data(self) -> List[Data]:
        objects: List[Data] = []
        if self.__device:
            objects.append(self.__device)
        if self.__browser:
            objects.append(self.__browser)
        if self.__operating_system:
            objects.append(self.__operating_system)
        if self.__geolocation:
            objects.append(self.__geolocation)
        return objects

    @staticmethod
    def __parse_kcs_heat(kcs: Optional[Any]) -> Optional[KcsHeat]:
        if not isinstance(kcs, dict):
            return None
        value_map: Dict[int, Dict[int, float]] = {}
        for key_moment_id, goal_scores in kcs.items():
            if not (isinstance(goal_scores, dict) and isinstance(key_moment_id, str) and key_moment_id.isnumeric()):
                continue
            goal_score_map: Dict[int, float] = {}
            for goal_id, score in goal_scores.items():
                if not (isinstance(score, (float, int)) and isinstance(goal_id, str) and goal_id.isnumeric()):
                    continue
                goal_score_map[int(goal_id)] = score
            value_map[int(key_moment_id)] = goal_score_map
        return KcsHeat(value_map) if len(value_map) > 0 else None
