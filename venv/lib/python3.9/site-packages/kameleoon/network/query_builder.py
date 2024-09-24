"""Network"""
from enum import Enum
from typing import List
from kameleoon.network.uri_helper import encode_uri


class QueryParams(str, Enum):
    """Enum representing various query parameter keys used in requests."""
    BODY_UA = "bodyUa"
    CLIENT_ID = "client_id"
    CLIENT_SECRET = "client_secret"
    BROWSER_INDEX = "browserIndex"
    BROWSER_VERSION = "browserVersion"
    CURRENT_VISIT = "currentVisit"
    CUSTOM_DATA = "customData"
    DEVICE_TYPE = "deviceType"
    ENVIRONMENT = "environment"
    EVENT_TYPE = "eventType"
    EXPERIMENT_ID = "id"
    GOAL_ID = "goalId"
    GRANT_TYPE = "grant_type"
    HREF = "href"
    INDEX = "index"
    KCS = "kcs"
    KEY = "key"
    MAX_NUMBER_PREVIOUS_VISITS = "maxNumberPreviousVisits"
    NEGATIVE = "negative"
    NONCE = "nonce"
    OVERWRITE = "overwrite"
    REFERRERS_INDICES = "referrersIndices"
    REVENUE = "revenue"
    SDK_NAME = "sdkName"
    SDK_VERSION = "sdkVersion"
    SITE_CODE = "siteCode"
    TITLE = "title"
    TS = "ts"
    USER_AGENT = "userAgent"
    VALUES_COUNT_MAP = "valuesCountMap"
    VARIATION_ID = "variationId"
    VERSION = "version"
    VISITOR_CODE = "visitorCode"
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"
    POSTAL_CODE = "postalCode"
    LATITUDE = "latitude"
    LONGITUDE = "longitude"
    OPERATING_SYSTEM = "os"
    GEOLOCATION = "geolocation"
    OPERATING_SYSTEM_INDEX = "osIndex"
    MAPPING_IDENTIFIER = "mappingIdentifier"
    MAPPING_VALUE = "mappingValue"
    CONVERSION = "conversion"
    EXPERIMENT = "experiment"
    PAGE = "page"
    STATIC_DATA = "staticData"

    def __str__(self) -> str:
        return self.value


class QueryParam:
    """Query param"""
    def __init__(self, name: QueryParams, value: str, encoding_required=True):
        self.__name = name
        self.__value = value
        self.__encoding_required = encoding_required

    @property
    def is_valid(self) -> bool:
        """Checks if the query parameter is valid."""
        return bool(self.__value and self.__name)

    def __str__(self) -> str:
        encoded_value = encode_uri(self.__value) if self.__encoding_required else self.__value
        return f"{self.__name}={encoded_value}"


class QueryBuilder:
    """Query builder"""
    def __init__(self, *args: QueryParam) -> None:
        self.__params: List[QueryParam] = list(args)

    def append(self, param: QueryParam) -> None:
        """Adds a single query parameter to the list of parameters."""
        self.__params.append(param)

    def extend(self, *params: QueryParam) -> None:
        """Adds multiple query parameters to the list of parameters."""
        self.__params.extend(params)

    def __str__(self) -> str:
        return "&".join(str(p) for p in self.__params if p.is_valid)
