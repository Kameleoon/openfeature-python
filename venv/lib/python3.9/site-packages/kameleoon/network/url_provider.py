"""Network"""
from typing import Any, Optional
from kameleoon.sdk_version import SdkVersion
from kameleoon.network.query_builder import QueryBuilder, QueryParam, QueryParams
from kameleoon.types.remote_visitor_data_filter import RemoteVisitorDataFilter


class UrlProvider:
    """URL provider"""
    _TRACKING_PATH = "/visit/events"
    _VISITOR_DATA_PATH = "/visit/visitor"
    _EXPERIMENTS_CONFIGURATIONS_PATH = "/visit/experimentsConfigurations"
    _GET_DATA_PATH = "/map/map"
    _POST_DATA_PATH = "/map/maps"
    _ACCESS_TOKEN_PATH = "/oauth/token"
    _CONFIGURATION_API_URL_F = "https://sdk-config.kameleoon.eu/{0}"
    _RT_CONFIGURATION_URL = "https://events.kameleoon.com:8110/sse"

    DEFAULT_DATA_API_DOMAIN = "data.kameleoon.io"
    TEST_DATA_API_DOMAIN = "data.kameleoon.net"
    DEFAULT_AUTOMATION_API_DOMAIN = "api.kameleoon.com"
    TEST_AUTOMATION_API_DOMAIN = "api.master.preview.kameleoon.net"

    def __init__(
        self,
        site_code: str,
        data_api_domain=DEFAULT_DATA_API_DOMAIN,
        automation_api_domain=DEFAULT_AUTOMATION_API_DOMAIN,
    ) -> None:
        self.site_code = site_code
        self._data_api_domain = data_api_domain
        self._automation_api_domain = automation_api_domain
        self.__post_query_base = self.__make_post_query_base()

    def __make_post_query_base(self) -> str:
        # fmt: off
        query_builder = QueryBuilder(
            QueryParam(QueryParams.SDK_NAME, SdkVersion.NAME),
            QueryParam(QueryParams.SDK_VERSION, SdkVersion.VERSION),
            QueryParam(QueryParams.SITE_CODE, self.site_code),
            QueryParam(QueryParams.BODY_UA, "true"),
        )
        # fmt: on
        return str(query_builder)

    def apply_data_api_domain(self, domain: Any) -> None:
        """Sets the domain for the data API."""
        if isinstance(domain, str):
            self._data_api_domain = domain

    def make_tracking_url(self) -> str:
        """Constructs the URL for tracking events."""
        return f"https://{self._data_api_domain}{self._TRACKING_PATH}?{self.__post_query_base}"

    def make_visitor_data_get_url(
        self, visitor_code: str, data_filter: RemoteVisitorDataFilter, is_unique_identifier: bool = False
    ) -> str:
        """Constructs the URL for fetching visitor data with specified filters."""
        # fmt: off
        query_builder = QueryBuilder(
            QueryParam(QueryParams.SITE_CODE, self.site_code),
            QueryParam(QueryParams.MAPPING_VALUE if is_unique_identifier else QueryParams.VISITOR_CODE, visitor_code),
            QueryParam(QueryParams.MAX_NUMBER_PREVIOUS_VISITS, str(data_filter.previous_visit_amount)),
            QueryParam(QueryParams.VERSION, "0"),
        )
        # fmt: on
        if data_filter.kcs:
            query_builder.append(QueryParam(QueryParams.KCS, "true"))
        if data_filter.current_visit:
            query_builder.append(QueryParam(QueryParams.CURRENT_VISIT, "true"))
        if data_filter.custom_data:
            query_builder.append(QueryParam(QueryParams.CUSTOM_DATA, "true"))
        if data_filter.conversions:
            query_builder.append(QueryParam(QueryParams.CONVERSION, "true"))
        if data_filter.geolocation:
            query_builder.append(QueryParam(QueryParams.GEOLOCATION, "true"))
        if data_filter.experiments:
            query_builder.append(QueryParam(QueryParams.EXPERIMENT, "true"))
        if data_filter.page_views:
            query_builder.append(QueryParam(QueryParams.PAGE, "true"))
        if data_filter.device or data_filter.browser or data_filter.operating_system:
            query_builder.append(QueryParam(QueryParams.STATIC_DATA, "true"))
        return f"https://{self._data_api_domain}{self._VISITOR_DATA_PATH}?{query_builder}"

    def make_api_data_get_request_url(self, key: str) -> str:
        """Constructs the URL for fetching remote data from the Data API."""
        # fmt: off
        query_builder = QueryBuilder(
            QueryParam(QueryParams.SITE_CODE, self.site_code),
            QueryParam(QueryParams.KEY, key),
        )
        # fmt: on
        return f"https://{self._data_api_domain}{self._GET_DATA_PATH}?{query_builder}"

    def make_configuration_url(self, environment: Optional[str] = None, time_stamp: Optional[int] = None) -> str:
        """Constructs the URL for fetching configuration data with optional query parameters."""
        query_builder = QueryBuilder()
        if environment:
            query_builder.append(QueryParam(QueryParams.ENVIRONMENT, environment))
        if time_stamp is not None:
            query_builder.append(QueryParam(QueryParams.TS, str(time_stamp)))
        url = self._CONFIGURATION_API_URL_F.format(self.site_code)
        query = str(query_builder)
        if len(query) > 0:
            url = f"{url}?{query}"
        return url

    def make_real_time_url(self) -> str:
        """Constructs the URL for real-time configuration data."""
        query_builder = QueryParam(QueryParams.SITE_CODE, self.site_code)
        return f"{self._RT_CONFIGURATION_URL}?{query_builder}"

    def make_access_token_url(self) -> str:
        """Constructs the URL for fetching access tokens."""
        return f"https://{self._automation_api_domain}{self._ACCESS_TOKEN_PATH}"
