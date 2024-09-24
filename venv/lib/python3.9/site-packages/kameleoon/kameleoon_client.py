"""Client for Kameleoon"""

from http.cookies import Morsel
from typing import cast, Callable, Coroutine, Optional, Tuple, Union, Any, List, Dict, Iterable

from kameleoon.client_readiness.async_readiness import AsyncClientReadiness
from kameleoon.client_readiness.threading_readiness import ThreadingClientReadiness

from kameleoon import configuration
from kameleoon.configuration.data_file import DataFile
from kameleoon.configuration.feature_flag import FeatureFlag
from kameleoon.configuration.rule import Rule
from kameleoon.configuration.variation_by_exposition import VariationByExposition

from kameleoon.data import Conversion, CustomData, Data, UniqueIdentifier
from kameleoon.data.manager.assigned_variation import AssignedVariation
from kameleoon.data.manager.visitor_manager import VisitorManager

from kameleoon.exceptions import (
    FeatureVariationNotFound,
    FeatureVariableNotFound,
    FeatureEnvironmentDisabled,
    SiteCodeIsEmpty,
)

from kameleoon.helpers.functions import obtain_hash_double_rule
from kameleoon.helpers.visitor_code import validate_visitor_code

from kameleoon.hybrid.hybrid_manager_impl import HybridManagerImpl

from kameleoon.kameleoon_client_config import KameleoonClientConfig
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.logging.logger import DefaultLogger

from kameleoon.managers.asyncexec.async_executor import AsyncExecutor
from kameleoon.managers.data.data_manager import DataManager
from kameleoon.managers.remote_data.remote_data_manager import RemoteDataManager
from kameleoon.managers.tracking.tracking_manager import TrackingManager
from kameleoon.managers.warehouse.warehouse_manager import WarehouseManager

from kameleoon.network.access_token_source_factory import AccessTokenSourceFactory
from kameleoon.network.net_provider_impl import NetProviderImpl
from kameleoon.network.network_manager_factory import NetworkManagerFactory
from kameleoon.network.network_manager_factory_impl import NetworkManagerFactoryImpl
from kameleoon.network.sendable import Sendable
from kameleoon.network.services.configuration_service import ConfigurationService
from kameleoon.network.cookie.cookie_manager import CookieManager

from kameleoon.real_time.real_time_configuration_service import RealTimeConfigurationService

from kameleoon.targeting.targeting_manager import TargetingManager

from kameleoon.types.remote_visitor_data_filter import RemoteVisitorDataFilter
from kameleoon.types.variable import Variable
from kameleoon.types.variation import Variation

__all__ = [
    "KameleoonClient",
]

REFERENCE = 0
X_PAGINATION_PAGE_COUNT = "X-Pagination-Page-Count"
SEGMENT = "targetingSegment"
KAMELEOON_TRACK_EXPERIMENT_THREAD = "KameleoonTrackExperimentThread"
KAMELEOON_TRACK_DATA_THREAD = "KameleoonTrackDataThread"
STATUS_ACTIVE = "ACTIVE"
FEATURE_STATUS_DEACTIVATED = "DEACTIVATED"
# pylint: disable=W0511
HYBRID_EXPIRATION_TIME = 5.0  # TODO: hybrid manager timeout is less than call timeout; affects on sync-monothread mode


# pylint: disable=R0904
class KameleoonClient:
    """
    KameleoonClient

    Example:

    .. code-block:: python3

        from kameleoon import KameleoonClientFactory
        from kameleoon import KameleoonClientConfig

        SITE_CODE = 'a8st4f59bj'

        kameleoon_client = KameleoonClientFactory.create(SITE_CODE)

        kameleoon_client = KameleoonClientFactory.create(SITE_CODE,
                                                         config_path='/etc/kameleoon/client-python.yaml')

        kameleoon_client_config = KameleoonClientConfig('client_id', 'client_secret')
        kameleoon_client = KameleoonClientFactory.create(SITE_CODE, kameleoon_client_config)
    """

    _network_manager_factory: NetworkManagerFactory = NetworkManagerFactoryImpl()

    # pylint: disable=R0913
    def __init__(self, site_code: str, config: KameleoonClientConfig) -> None:
        """
        This initializer should not be called explicitly. Use `KameleoonClientFactory.create` instead.

        :param site_code: Code of the website you want to run experiments on. This unique code id can
                              be found in our platform's back-office. This field is mandatory.
        :type site_code: str
        :param config: Configuration object which can be used instead of external file at configuration_path.
                                This field is optional set to None by default.
        :type config: KameleoonClientConfig

        :raises SiteCodeIsEmpty: Indicates that the specified site code is empty string which is invalid value
        """
        # pylint: disable=too-many-instance-attributes
        # Eight is reasonable in this case.
        KameleoonLogger.info("CALL: KameleoonClient(site_code: %s, config: %s)", site_code, config)
        if not site_code:
            raise SiteCodeIsEmpty("Provided site_code is empty")
        self._disposed = False
        self.site_code = site_code
        self._config = config
        KameleoonLogger.set_logger(DefaultLogger(config.logger))
        self._real_time_configuration_service: Optional[RealTimeConfigurationService] = None
        self._update_configuration_handler: Optional[Callable[[], None]] = None
        self._async_executor = AsyncExecutor()
        self.__add_fetch_configuration_job()
        self._threading_readiness = ThreadingClientReadiness()
        self._async_readiness = AsyncClientReadiness(self._threading_readiness)
        data_file: DataFile = DataFile.default(config.environment)
        self._data_manager = DataManager(data_file)
        self._visitor_manager = VisitorManager(
            self._data_manager, config.session_duration_second, self._async_executor.scheduler
        )
        self._hybrid_manager = HybridManagerImpl(HYBRID_EXPIRATION_TIME)

        self._cookie_manager = CookieManager(self._data_manager, config.top_level_domain)
        atsf = AccessTokenSourceFactory(config.client_id, config.client_secret)
        self._network_manager = self._network_manager_factory.create(
            self.site_code,
            config.environment,
            config.default_timeout_second,
            NetProviderImpl(),
            atsf,
        )
        self._targeting_manager = TargetingManager(self._data_manager, self._visitor_manager)
        self._warehouse_manager = WarehouseManager(self._network_manager, self._visitor_manager)
        self._remote_data_manager = \
            RemoteDataManager(self._data_manager, self._network_manager, self._visitor_manager)
        self._tracking_manager = TrackingManager(
            self._data_manager, self._network_manager, self._visitor_manager,
            config.tracking_interval_second, self._async_executor,
        )

        # All the jobs should be added before the scheduler is started.
        # The scheduler should not be started more than once.
        self._async_executor.scheduler.start()

        self._init_fetch_configuration()
        KameleoonLogger.info("RETURN: KameleoonClient(site_code: %s, config: %s)", site_code, config)

    def __del__(self) -> None:
        if self._disposed:
            return
        self._disposed = True
        KameleoonLogger.info("CALL: KameleoonClient.__del__()")
        self._async_executor.scheduler.stop()
        try:
            self._async_executor.run_coro(self._network_manager.net_provider.close(), "net_provider.close")
            if self._async_executor.thread_event_loop:
                self._async_executor.thread_event_loop.stop()
        except AttributeError:
            pass
        KameleoonLogger.info("RETURN: KameleoonClient.__del__()")

    ###
    #   Public API methods
    ###

    def wait_init_async(self) -> Coroutine[Any, Any, bool]:
        """
        Asynchronously waits for the initialization of the Kameleoon client.
        This method allows you to pause the execution of your code until the client is initialized.

        :return: A coroutine that returns a flag indicating if the initialization process has succeeded
        :rtype: Coroutine[Any, Any, bool]
        """
        KameleoonLogger.info("CALL: KameleoonClient.wait_init_async()")
        result = self._async_readiness.wait()
        KameleoonLogger.info("RETURN: KameleoonClient.wait_init_async() -> (readiness_coroutine)")
        return result

    def wait_init(self) -> bool:
        """
        Synchronously waits for the initialization of the Kameleoon client.
        This method allows you to pause the execution of your code until the client is initialized.

        :return: A flag indicating if the initialization process has succeeded
        :rtype: bool
        """
        KameleoonLogger.info("CALL: KameleoonClient.wait_init()")
        success = self._threading_readiness.wait()
        KameleoonLogger.info("CALL: KameleoonClient.wait_init() -> (success: %s)", success)
        return success

    def get_visitor_code(
        self,
        cookies_readonly: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, Morsel[str]]] = None,
        default_visitor_code: Optional[str] = None,
    ) -> str:
        """
        Reads and updates visitor code in cookies. Possible optional parameters:
        - `Dict[str, str]` (e.g. `request.COOKIES`). It's recommended to use in conjunction
        with `KameleoonWSGIMiddleware`
        - `http.cookies.SimpleCookie` (see https://docs.python.org/3/library/http.cookies.html)

        The method updates the cookies with a new visitor code if it's needed in case of `http.cookies.SimpleCookie`
        is passed.

        If the cookies does not contain a visitor code, a new visitor code is set to the `default_visitor_code`
        if it is specified, otherwise a new visitor code is randomly generated.

        :param cookies_readonly: Readonly dictionary (usually, request.COOKIES) which would not be modified.
        Should be used in conjunction with `KameleoonWSGIMiddleware` service.
        :type cookies_readonly: Optional[Dict[str, str]]
        :param cookies: Mutable dictionary (usually, `http.cookies.SimpleCookie`) which will be filled during method
        call.
        Should be used if you want to manage cookies manually (without KameleoonWSGIMiddleware service).
        :type cookies: Dict[str, Morsel[str]]
        :param default_visitor_code: Visitor code to be used if no visitor code in cookies
        :type default_visitor_code: Optional[str]
        :return: The visitor code
        :rtype: str

        Example:

        .. code-block:: python3
            visitor_code = kameleoon_client.get_visitor_code(cookies_readonly=request.COOKIES)
            # or
            simple_cookies = SimpleCookie()
            simple_cookies.load(cookie_header)

            visitor_code = kameleoon_client.get_visitor_code(cookies=simple_cookies)

            cookie_header = simple_cookies.output()
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_visitor_code(cookies_readonly: %s, cookies: %s, default_visitor_code: %s)",
            cookies_readonly, cookies, default_visitor_code)
        visitor_code = self._cookie_manager.get_or_add(cookies_readonly, cookies, default_visitor_code)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_visitor_code(cookies_readonly: %s, cookies: %s, default_visitor_code: %s)"
            " -> (visitor_code: %s)", cookies_readonly, cookies, default_visitor_code, visitor_code)
        return visitor_code

    def set_legal_consent(
        self,
        visitor_code: str,
        consent: bool,
        cookies: Optional[Dict[str, Morsel[str]]] = None,
    ) -> None:
        """
        Sets or updates the legal consent status for a visitor identified by their unique visitor code,
        affecting values in the cookies based on the consent status.

        This method allows you to set or update the legal consent status for a specific visitor
        identified by their visitor code and adjust values in the cookies accordingly. The legal
        consent status is represented by a boolean value, where 'True' indicates consent, and 'False'
        indicates a withdrawal or absence of consent. Depending on the consent status, various values in
        the cookies may be affected.

        :param visitor_code: The unique visitor code identifying the visitor.
        :type visitor_code: str
        :param consent: A boolean value representing the legal consent status.
        :type consent: bool
        :param cookies: Request-respose cookies. Optional parameter.
        :type cookies: Optional[Dict[str, Morsel[str]]]

        Example:

        .. code-block:: python3
        # Set legal consent for a specific visitor and adjust cookie values accordingly
        kameeloon_client.set_legal_consent("visitor123", True)

        # Update legal consent for another visitor and modify cookie values based on the consent status
        kameeloon_client.set_legal_consent("visitor456", False)

        # Set legal consent for a specific visitor and adjust cookie values accordingly
        kameeloon_client.set_legal_consent("visitor123", True, cookies)

        # Update legal consent for another visitor and modify cookie values based on the consent status
        kameeloon_client.set_legal_consent("visitor456", False, cookies)
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.set_legal_consent(visitor_code: %s, consent: %s, cookies: %s)",
            visitor_code, consent, cookies)
        validate_visitor_code(visitor_code)
        visitor = self._visitor_manager.get_or_create_visitor(visitor_code)
        visitor.legal_consent = consent
        if cookies is not None:
            self._cookie_manager.update(visitor_code, consent, cookies)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.set_legal_consent(visitor_code: %s, consent: %s, cookies: %s)",
            visitor_code, consent, cookies)

    def add_data(self, visitor_code: str, *args) -> None:
        """
        To associate various data with the current user, we can use the add_data() method.
        This method requires the visitor_code as a first parameter, and then accepts several additional parameters.
        These additional parameters represent the various Data Types allowed in Kameleoon.

        Note that the add_data() method doesn't return any value and doesn't interact with the Kameleoon back-end
        servers by itself. Instead, all declared data is saved for further sending via the flush() method described
        in the next paragraph. This reduces the number of server calls made, as data is usually grouped
        into a single server call triggered by the execution of flush()

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param args:
        :return: None

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
        """
        KameleoonLogger.info("CALL: KameleoonClient.add_data(visitor_code: %s, args: %s)", visitor_code, args)
        validate_visitor_code(visitor_code)
        self._visitor_manager.add_data(visitor_code, *args)
        KameleoonLogger.info("RETURN: KameleoonClient.add_data(visitor_code: %s, args: %s)", visitor_code, args)

    def track_conversion(
        self, visitor_code: str, goal_id: int, revenue: float = 0.0, is_unique_identifier: Optional[bool] = None
    ) -> None:
        """
        To track conversion, use the track_conversion() method. This method requires visitor_code and goal_id to track
        conversion on this particular goal. In addition, this method also accepts revenue as a third optional argument
        to track revenue. The visitor_code is usually identical to the one that was used when triggering the experiment.
        The track_conversion() method doesn't return any value. This method is non-blocking as the server
        call is made asynchronously.

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param goal_id: ID of the goal. This field is mandatory.
        :type goal_id: int
        :param revenue: Revenue of the conversion. This field is optional.
        :type revenue: float
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]
        :return: None
        """
        KameleoonLogger.info("CALL: KameleoonClient.track_conversion(visitor_code: %s, goal_id: %s, revenue: %s, "
                             "is_unique_identifier: %s)", visitor_code, goal_id, revenue, is_unique_identifier)
        validate_visitor_code(visitor_code)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        self.add_data(visitor_code, Conversion(goal_id, revenue))
        self._tracking_manager.add_visitor_code(visitor_code)
        KameleoonLogger.info("RETURN: KameleoonClient.track_conversion(visitor_code: %s, goal_id: %s, revenue: %s, "
                             "is_unique_identifier: %s)", visitor_code, goal_id, revenue, is_unique_identifier)

    def flush(
        self, visitor_code: Optional[str] = None, is_unique_identifier: Optional[bool] = None, instant=False
    ) -> None:
        """
        Data associated with the current user via add_data() method is not immediately sent to the server.
        It is stored and accumulated until it is sent automatically by the trigger_experiment()
        or track_conversion() methods, or manually by the flush() method.
        This allows the developer to control exactly when the data is flushed to our servers. For instance,
        if you call the add_data() method a dozen times, it would be a waste of ressources to send data to the
        server after each add_data() invocation. Just call flush() once at the end.
        The flush() method doesn't return any value. This method is non-blocking as the server call
        is made asynchronously.


        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: Optional[str]
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]
        :param instant: Boolean flag indicating whether the data should be sent instantly (`true`)
        or according to the scheduled tracking interval (`false`).
        :type instant: bool

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
                kameleoon_client.add_data(visitor_code, Interest(1))

                kameleoon_client.flush()

        """
        KameleoonLogger.info("CALL: KameleoonClient.flush(visitor_code: %s, is_unique_identifier: %s, instant: %s)",
                             visitor_code, is_unique_identifier, instant)
        if visitor_code is not None:
            validate_visitor_code(visitor_code)
            if is_unique_identifier is not None:
                self.__set_unique_identifier(visitor_code, is_unique_identifier)
            if instant:
                self._tracking_manager.track_visitor(visitor_code)
            else:
                self._tracking_manager.add_visitor_code(visitor_code)
        else:
            for visitor_code in self._visitor_manager:  # pylint: disable=R1704
                visitor = self._visitor_manager.get_visitor(visitor_code)
                if visitor and cast(Iterable[Optional[Sendable]], next(visitor.enumerate_sendable_data(), None)):
                    self._tracking_manager.add_visitor_code(visitor_code)
                if instant:
                    self._tracking_manager.track_all()
        KameleoonLogger.info("RETURN: KameleoonClient.flush(visitor_code: %s, is_unique_identifier: %s, instant: %s)",
                             visitor_code, is_unique_identifier, instant)

    def is_feature_active(
        self, visitor_code: str, feature_key: str, is_unique_identifier: Optional[bool] = None
    ) -> bool:
        """
        Check if feature is active for a given visitor code

        This method takes a visitor_code and feature_key (or feature_id) as mandatory arguments to check
        if the specified feature will be active for a given user.
        If such a user has never been associated with this feature flag, the SDK returns a boolean
        value randomly (true if the user should have this feature or false if not). If a user with a given visitor_code
        is already registered with this feature flag, it will detect the previous feature flag value.
        You have to make sure that proper error handling is set up in your code as shown in the example to the right
        to catch potential exceptions.


        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param feature_key: Key of the feature flag you want to expose to a user. This field is mandatory.
        :type feature_key: str
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]
        :return: Value of the feature that is active for a given visitor_code.
        :rtype: bool


        :raises:
            FeatureNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            VisitorCodeInvalid: Raise when the provided visitor code is not valid
                        (empty, or longer than 255 characters)

        Examples:

        .. code-block:: python3

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                feature_key = "new_checkout"
                has_new_checkout = False

                try:
                    has_new_checkout = kameleoon_client.is_feature_active(visitor_code, feature_key)
                except FeatureNotFound:
                    # The user will not be counted into the experiment, but should see the reference variation
                    logger.debug(...)

                if has_new_checkout:
                    # Implement new checkout code here
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.is_feature_active(visitor_code: %s, feature_key: %s, is_unique_identifier: %s)",
            visitor_code, feature_key, is_unique_identifier)
        validate_visitor_code(visitor_code)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        try:
            (_, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
            feature_active = variation_key != configuration.Variation.Type.OFF.value
        except FeatureEnvironmentDisabled:
            feature_active = False
        KameleoonLogger.info(
            "RETURN: KameleoonClient.is_feature_active(visitor_code: %s, feature_key: %s, is_unique_identifier: %s)"
            " -> (feature_active: %s)", visitor_code, feature_key, is_unique_identifier, feature_active)
        return feature_active

    def get_feature_variation_variables(self, feature_key: str, variation_key: str) -> Dict[str, Any]:
        """
        Retrieve all feature variables.
        A feature variables can be changed easily via our web application.

        :param feature_key: str Key of the feature you want to obtain to a user.
                            This field is mandatory.
        :return: Dictionary of feature variables
        :rtype: Dict[str, Any]

        :raises: FeatureNotFound: Exception indicating that the requested feature Key has not been found
                                               in the internal configuration of the SDK. This is usually normal and
                                               means that the feature flag has not yet been activated on
                                               Kameleoon's side.
                 FeatureVariationNotFound: Variation key isn't found for current feature flag.

        Example:

        .. code-block:: python3
                try:
                    data = kameleoon_client.get_feature_variation_variables(feature_key)
                except FeatureNotFound:
                    # The feature is not yet activated on Kameleoon's side
                except FeatureVariationNotFound:
                    # The variation key is not found for current feature flag
                    pass
        """

        # pylint: disable=no-else-raise
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_feature_variation_variables(feature_key: %s, variation_key: %s)",
            feature_key, variation_key)
        feature_flag = self._data_manager.data_file.get_feature_flag(feature_key)
        variation = feature_flag.get_variation(variation_key)
        if not variation:
            raise FeatureVariationNotFound(variation_key)
        variables: Dict[str, Any] = {}
        for var in variation.variables:
            variables[var.key] = var.get_value()
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_feature_variation_variables(feature_key: %s, variation_key: %s) -> "
            "(variables: %s)", feature_key, variation_key, variables)
        return variables

    async def get_remote_data_async(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        The get_remote_data_async method allows you to retrieve data asynchronously (according to a key passed as
        argument) stored on a remote Kameleoon server. Usually data will be stored on our remote servers
        via the use of our Data API. This method, along with the availability of our highly scalable servers
        for this purpose, provides a convenient way to quickly store massive amounts of data that
        can be later retrieved for each of your visitors / users.

        :param key: key you want to retrieve data. This field is mandatory.
        :type key: str
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]

        :return: data assosiated with this key, decoded into json
        :rtype: Optional[Any]
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_remote_data_async(key: %s, timeout: %s)", key, timeout)
        remote_data = await self._remote_data_manager.get_data(key, timeout)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_remote_data_async(key: %s, timeout: %s) -> (remote_data: %s)",
            key, timeout, remote_data)
        return remote_data

    def get_remote_data(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        The get_remote_data method allows you to retrieve data (according to a key passed as
        argument) stored on a remote Kameleoon server. Usually data will be stored on our remote servers
        via the use of our Data API. This method, along with the availability of our highly scalable servers
        for this purpose, provides a convenient way to quickly store massive amounts of data that
        can be later retrieved for each of your visitors / users.

        :param key: key you want to retrieve data. This field is mandatory.
        :type key: str
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]

        :return: data assosiated with this key, decoded into json
        :rtype: Optional[Any]
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_remote_data(key: %s, timeout: %s)", key, timeout)
        coro = self._remote_data_manager.get_data(key, timeout)
        remote_data = self._async_executor.await_coro_synchronously(coro, "get_remote_data")
        KameleoonLogger.info("RETURN: KameleoonClient.get_remote_data(key: %s, timeout: %s) -> (remote_data: %s)",
                             key, timeout, remote_data)
        return remote_data

    async def get_remote_visitor_data_async(
        self,
        visitor_code: str,
        add_data=True,
        timeout: Optional[float] = None,
        data_filter: Optional[RemoteVisitorDataFilter] = None,
        is_unique_identifier: Optional[bool] = None,
    ) -> List[Data]:
        """
        The get_remote_visitor_data_async is an asynchronous method for retrieving custom data for
        the latest visit of `visitor_code` from Kameleoon Data API and optionally adding it
        to the storage so that other methods could decide whether the current visitor is targeted or not.

        :param visitor_code: The visitor code for which you want to retrieve the assigned data. This field is mandatory.
        :type visitor_code: str
        :param add_data: A boolean indicating whether the method should automatically add retrieved data for a visitor.
        If not specified, the default value is `True`. This field is optional.
        :type add_data: bool
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]
        :param data_filter: Filter that specifies which data should be retrieved from visits.
        :type data_filter: RemoteVisitorDataFilter
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]

        :return: A list of data assigned to the given visitor.
        :rtype: List[Data]
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_remote_visitor_data_async(visitor_code: %s, add_data: %s, timeout: %s,"
            " data_filter: %s, is_unique_identifier: %s)",
            visitor_code, add_data, timeout, data_filter, is_unique_identifier)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        remote_visitor_data = await self._remote_data_manager.get_visitor_data(
            visitor_code, add_data, data_filter, timeout)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_remote_visitor_data_async(visitor_code: %s, add_data: %s, timeout: %s,"
            " data_filter: %s, is_unique_identifier: %s) -> (remote_visitor_data: %s)",
            visitor_code, add_data, timeout, data_filter, is_unique_identifier, remote_visitor_data)
        return remote_visitor_data

    def get_remote_visitor_data(
        self,
        visitor_code: str,
        add_data=True,
        timeout: Optional[float] = None,
        data_filter: Optional[RemoteVisitorDataFilter] = None,
        is_unique_identifier: Optional[bool] = None,
    ) -> List[Data]:
        """
        The get_remote_visitor_data is a synchronous method for retrieving custom data for
        the latest visit of `visitor_code` from Kameleoon Data API and optionally adding it
        to the storage so that other methods could decide whether the current visitor is targeted or not.

        :param visitor_code: The visitor code for which you want to retrieve the assigned data. This field is mandatory.
        :type visitor_code: str
        :param add_data: A boolean indicating whether the method should automatically add retrieved data for a visitor.
        If not specified, the default value is `True`. This field is optional.
        :type add_data: bool
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]
        :param data_filter: Filter that specifies which data should be retrieved from visits.
        :type data_filter: RemoteVisitorDataFilter
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]

        :return: A list of data assigned to the given visitor.
        :rtype: List[Data]
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_remote_visitor_data(visitor_code: %s, add_data: %s, timeout: %s,"
            " data_filter: %s, is_unique_identifier: %s)",
            visitor_code, add_data, timeout, data_filter, is_unique_identifier)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        coro = self._remote_data_manager.get_visitor_data(visitor_code, add_data, data_filter, timeout)
        result = self._async_executor.await_coro_synchronously(coro, "get_remote_visitor_data")
        result = cast(List[Data], result)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_remote_visitor_data(visitor_code: %s, add_data: %s, timeout: %s,"
            " data_filter: %s, is_unique_identifier: %s) -> (remote_visitor_data: %s)",
            visitor_code, add_data, timeout, data_filter, is_unique_identifier, result)
        return result

    def get_visitor_warehouse_audience_async(
        self,
        visitor_code: str,
        custom_data_index: int,
        warehouse_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Coroutine[Any, Any, Optional[CustomData]]:
        """
        Asynchronously retrieves data associated with a visitor's warehouse audiences and adds it to the visitor.
        Retrieves all audience data associated with the visitor in your data warehouse using the specified
        `visitor_code` and `warehouse_key`. The `warehouse_key` is typically your internal user ID.
        The `custom_data_index` parameter corresponds to the Kameleoon custom data that Kameleoon uses to target your
        visitors. You can refer to the
        <a href="https://help.kameleoon.com/warehouse-audience-targeting/">warehouse targeting documentation</a>
        for additional details. The method returns a `CustomData` object, confirming
        that the data has been added to the visitor and is available for targeting purposes.

        :param visitor_code: A unique visitor identification string, can't exceed 255 characters length.
        This field is mandatory.
        :type visitor_code: str
        :param custom_data_index: An integer representing the index of the custom data you want to use to target
        your BigQuery Audiences. This field is mandatory.
        :type custom_data_index: int
        :param warehouse_key: A key to identify the warehouse data, typically your internal user ID.
        This field is optional.
        :type warehouse_key: Optional[str]
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]

        :return: A `CustomData` instance confirming that the data has been added to the visitor.
        :rtype: Optional[CustomData]

        :raises:
            VisitorCodeInvalid: Raise when the provided visitor code is not valid (empty, or longer than 255 characters)
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_visitor_warehouse_audience_async(visitor_code: %s, custom_data_index: %s, "
            "warehouse_key: %s, timeout: %s)", visitor_code, custom_data_index, warehouse_key, timeout)
        custom_data = self._warehouse_manager.get_visitor_warehouse_audience(
            visitor_code, custom_data_index, warehouse_key, timeout
        )
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_visitor_warehouse_audience_async(visitor_code: %s, custom_data_index: %s, "
            "warehouse_key: %s, timeout: %s) -> (warehouse_audience_coroutine)",
            visitor_code, custom_data_index, warehouse_key, timeout)
        return custom_data

    def get_visitor_warehouse_audience(
        self,
        visitor_code: str,
        custom_data_index: int,
        warehouse_key: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[CustomData]:
        """
        Synchronously retrieves data associated with a visitor's warehouse audiences and adds it to the visitor.
        Retrieves all audience data associated with the visitor in your data warehouse using the specified
        `visitor_code` and `warehouse_key`. The `warehouse_key` is typically your internal user ID.
        The `custom_data_index` parameter corresponds to the Kameleoon custom data that Kameleoon uses to target your
        visitors. You can refer to the
        <a href="https://help.kameleoon.com/warehouse-audience-targeting/">warehouse targeting documentation</a>
        for additional details. The method returns a `CustomData` object, confirming
        that the data has been added to the visitor and is available for targeting purposes.

        :param visitor_code: A unique visitor identification string, can't exceed 255 characters length.
        This field is mandatory.
        :type visitor_code: str
        :param custom_data_index: An integer representing the index of the custom data you want to use to target
        your BigQuery Audiences. This field is mandatory.
        :type custom_data_index: int
        :param warehouse_key: A key to identify the warehouse data, typically your internal user ID.
        This field is optional.
        :type warehouse_key: Optional[str]
        :param timeout: requests Timeout for request (in seconds). Equals default_timeout in a config file.
        This field is optional.
        :type timeout: Optional[float]

        :return: A `CustomData` instance confirming that the data has been added to the visitor.
        :rtype: Optional[CustomData]

        :raises:
            VisitorCodeInvalid: Raise when the provided visitor code is not valid (empty, or longer than 255 characters)
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_visitor_warehouse_audience(visitor_code: %s, custom_data_index: %s, "
            "warehouse_key: %s, timeout: %s)", visitor_code, custom_data_index, warehouse_key, timeout)
        coro = self._warehouse_manager.get_visitor_warehouse_audience(
            visitor_code,
            custom_data_index,
            warehouse_key,
            timeout,
        )
        custom_data = self._async_executor.await_coro_synchronously(coro, "get_visitor_warehouse_audience")
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_visitor_warehouse_audience(visitor_code: %s, custom_data_index: %s, "
            "warehouse_key: %s, timeout: %s) -> (warehouse_audience: %s)",
            visitor_code, custom_data_index, warehouse_key, timeout, custom_data)
        return custom_data

    def get_feature_list(self) -> List[str]:
        """
        The get_feature_list method uses for obtaining a list of feature flag IDs:
        - currently available for the SDK

        :return: List of all feature flag IDs
        :rtype: List[int]
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_feature_list()")
        features = list(self._data_manager.data_file.feature_flags)
        KameleoonLogger.info("RETURN: KameleoonClient.get_feature_list() -> (features: %s)", features)
        return features

    def get_active_feature_list_for_visitor(self, visitor_code: str) -> List[str]:
        """
        Depreacted function. Please use `get_active_features_for_visitor` instead.
        The get_active_feature_list_for_visitor method uses for obtaining a list of feature flag IDs:
        - currently targeted and active simultaneously for a visitor

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: Optional[str]

        :return: List of all feature flag IDs or targeted and active simultaneously
                 for current visitorCode
        :rtype: List[int]
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_active_feature_list_for_visitor(visitor_code: %s)",
                             visitor_code)
        KameleoonLogger.warning("Call to deprecated function `get_active_feature_list_for_visitor`. "
                                "Please use `get_active_features` instead.")

        def filter_conditions(feature_flag: FeatureFlag) -> bool:
            if not feature_flag.environment_enabled:
                return False
            (variation, rule) = self.__calculate_variation_rule_for_feature(visitor_code, feature_flag)
            variation_key = self.__calculate_variation_key(variation, rule, feature_flag)
            return variation_key != configuration.Variation.Type.OFF.value

        active_features = list(
            map(
                lambda feature_flag: feature_flag.feature_key,
                filter(
                    filter_conditions,
                    self._data_manager.data_file.feature_flags.values(),
                ),
            )
        )
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_active_feature_list_for_visitor(visitor_code: %s) -> (active_features: %s)",
            visitor_code, active_features)
        return active_features

    def get_active_features(self, visitor_code: str) -> Dict[str, Variation]:
        """
        The get_active_features method uses for obtaining a information about the active feature flags
         that are available for the visitor.

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: str

        :return: Dictionary that contains the assigned variations of the active features using the keys
         of the corresponding active features.
        :rtype: Dict[str, Variation]

        :raises:
            VisitorCodeInvalid: Raise when the provided visitor code is not valid
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_active_features(visitor_code: %s)", visitor_code)
        validate_visitor_code(visitor_code)
        map_active_features: Dict[str, Variation] = {}
        for feature_flag in self._data_manager.data_file.feature_flags.values():
            if not feature_flag.environment_enabled:
                continue
            (var_by_exp, rule) = self.__calculate_variation_rule_for_feature(visitor_code, feature_flag)
            variation_key = self.__calculate_variation_key(var_by_exp, rule, feature_flag)
            if variation_key == configuration.Variation.Type.OFF.value:
                continue
            variation = feature_flag.get_variation(variation_key)
            variables: Dict[str, Variable] = {}
            if variation is not None:
                for variable in variation.variables:
                    variables[variable.key] = Variable(variable.key, variable.get_type(), variable.get_value())
            map_active_features[feature_flag.feature_key] = Variation(
                variation_key,
                var_by_exp.variation_id if var_by_exp is not None else None,
                rule.experiment_id if rule is not None else None,
                variables,
            )
        KameleoonLogger.info("RETURN: KameleoonClient.get_active_features(visitor_code: %s) -> (active_features: %s)",
                             visitor_code, map_active_features)
        return map_active_features

    def get_feature_variation_key(
        self, visitor_code: str, feature_key: str, is_unique_identifier: Optional[bool] = None
    ) -> str:
        """
        Returns a variation key for visitor code

        This method takes a visitor_code and feature_key as mandatory arguments and
        returns a variation assigned for a given visitor
        If such a user has never been associated with any feature flag rules, the SDK returns a default variation key
        You have to make sure that proper error handling is set up in your code as shown in the example
        to the right to catch potential exceptions.

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: str
        :param feature_key: unique identifier of feature flag
        :type feature_key: str
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]

        :return: Returns a variation key for visitor code
        :rtype: str

        :raises:
            FeatureNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            VisitorCodeInvalid: Raise when the provided visitor code is not valid
                                 (empty, or longer than 255 characters)
            FeatureEnvironmentDisabled: Exception indicating that feature flag is disabled for the
                                        visitor's current environment.
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_feature_variation_key(visitor_code: %s, feature_key: %s, "
            "is_unique_identifier: %s)", visitor_code, feature_key, is_unique_identifier)
        validate_visitor_code(visitor_code)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        (_, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_feature_variation_key(visitor_code: %s, feature_key: %s, "
            "is_unique_identifier: %s) -> (variation_key: %s)",
            visitor_code, feature_key, is_unique_identifier, variation_key)
        return variation_key

    def get_feature_variable(
        self, visitor_code: str, feature_key: str, variable_key: str, is_unique_identifier: Optional[bool] = None
    ) -> Union[bool, str, float, Dict[str, Any], List[Any], None]:
        """
        Retrieves a feature variable value from assigned for visitor variation
        A feature variable can be changed easily via our web application.

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: str
        :param feature_key: unique identifier of feature flag
        :type feature_key: str
        :param variable_name: variable name you want to retrieve
        :type variable_name: str
        :param is_unique_identifier: (Deprecated) Parameter that specifies whether the visitorCode is
        a unique identifier.
        :type is_unique_identifier: Optional[bool]

        :return: Feature variable value from assigned for visitor variation
        :rtype: Union[bool, str, float, Dict, List]

        :raises:
            FeatureNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            FeatureVariableNotFound: Variable provided name doesn't exist in this feature
            VisitorCodeInvalid: Raise when the provided visitor code is not valid
                                 (empty, or longer than 255 characters)
            FeatureEnvironmentDisabled: Exception indicating that feature flag is disabled for the
                                        visitor's current environment.
        """
        KameleoonLogger.info(
            "CALL: KameleoonClient.get_feature_variable(visitor_code: %s, feature_key: %s, "
            "variable_key: %s, is_unique_identifier: %s)",
            visitor_code, feature_key, variable_key, is_unique_identifier)
        validate_visitor_code(visitor_code)
        if is_unique_identifier is not None:
            self.__set_unique_identifier(visitor_code, is_unique_identifier)
        (feature_flag, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
        variation = feature_flag.get_variation(variation_key)
        variable = variation.get_variable_by_key(variable_key) if variation else None
        if variable is None:
            raise FeatureVariableNotFound(variable_key)
        value = variable.get_value()
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_feature_variable(visitor_code: %s, feature_key: %s, "
            "variable_key: %s, is_unique_identifier: %s) -> (variable: %s)",
            visitor_code, feature_key, variable_key, is_unique_identifier, value)
        return value

    ###
    #   Private API methods
    ###

    # Useless without storage
    # def __is_valid_saved_variation(
    #     self, visitor_code: str, experiment_id: int, respool_times: Dict[str, int]
    # ) -> Optional[int]:
    #     # get saved variation
    #     saved_variation_id = self.variation_storage.get_variation_id(
    #         visitor_code, experiment_id
    #     )
    #     if saved_variation_id is not None:
    #         # get respool time for saved variation id
    #         respool_time = respool_times.get(str(saved_variation_id))
    #         # checking variation for validity along with respoolTime
    #         return self.variation_storage.is_variation_id_valid(
    #             visitor_code, experiment_id, respool_time
    #         )
    #     return None

    # pylint: disable=W0238
    def __check_targeting(self, visitor_code: str, campaign_id: int, rule: Rule):
        KameleoonLogger.debug(
            "CALL: KameleoonClient.__check_targeting(visitor_code: %s, campaign_id: %s, rule: %s)",
            visitor_code, campaign_id, rule)
        targeting = self._targeting_manager.check_targeting(visitor_code, campaign_id, rule)
        KameleoonLogger.debug(
            "RETURN: KameleoonClient.__check_targeting(visitor_code: %s, campaign_id: %s, rule: %s) -> "
            "(targeting: %s)", visitor_code, campaign_id, rule, targeting)
        return targeting

    # pylint: disable=W0105
    """
    def _parse_json(self, custom_json: Dict[str, Any]):
        if custom_json["type"] == "Boolean":
            return bool(custom_json["value"])
        if custom_json["type"] == "String":
            return str(custom_json["value"])
        if custom_json["type"] == "Number":
            return float(custom_json["value"])
        if custom_json["type"] == "JSON":
            return json.loads(custom_json["value"])
        raise TypeError("Unknown type for feature variable")
    """

    def _init_fetch_configuration(self) -> None:
        """
        :return:
        """
        KameleoonLogger.debug("CALL: KameleoonClient._init_fetch_configuration()")

        async def initial_fetch() -> None:
            success = await self._fetch_configuration()
            self._threading_readiness.set(success)
            self._async_readiness.dispose_on_set()
        self._async_executor.run_coro(initial_fetch(), "initial_fetch")
        KameleoonLogger.debug("RETURN: KameleoonClient._init_fetch_configuration()")

    async def _fetch_configuration(self, time_stamp: Optional[int] = None) -> bool:
        """
        Fetches configuration from CDN service.
        Should be run in a separate thead.
        :return: True if succeeds, otherwise - False.
        :rtype: bool
        """
        # pylint: disable=W0703
        KameleoonLogger.debug("CALL: KameleoonClient._fetch_configuration(time_stamp: %s)", time_stamp)
        success = False
        try:
            configuration_json = await self._obtain_configuration(time_stamp)
            if configuration_json:
                data_file = DataFile.from_json(self._config.environment, configuration_json)
                self._data_manager.data_file = data_file
                self._network_manager.url_provider.apply_data_api_domain(data_file.settings.data_api_domain)
                self._call_update_handler_if_needed(time_stamp is not None)
            success = True
        except Exception as ex:
            KameleoonLogger.error("Error occurred during configuration fetching: %s", ex)
        self._manage_configuration_update(self._data_manager.data_file.settings.real_time_update)
        KameleoonLogger.debug("RETURN: KameleoonClient._fetch_configuration(time_stamp: %s) -> (success: %s)",
                              time_stamp, success)
        return success

    def _call_update_handler_if_needed(self, need_call: bool) -> None:
        """
        Call the handler when configuraiton was updated with new time stamp
        :param need_call: this parameters indicates if we need to call handler or not
        :type need_call: bool
        :return:  None
        """
        KameleoonLogger.debug("CALL: KameleoonClient._call_update_handler_if_needed(need_call: %s)", need_call)
        if need_call and self._update_configuration_handler is not None:
            KameleoonLogger.info("Triggered update_configuration_handler")
            self._update_configuration_handler()
        KameleoonLogger.debug("RETURN: KameleoonClient._call_update_handler_if_needed(need_call: %s)", need_call)

    def _manage_configuration_update(self, is_real_time_update: bool):
        KameleoonLogger.debug("CALL: KameleoonClient._manage_configuration_update(is_real_time_update: %s)",
                              is_real_time_update)
        if is_real_time_update:
            if self._real_time_configuration_service is None:
                url = self._network_manager.url_provider.make_real_time_url()
                self._real_time_configuration_service = RealTimeConfigurationService(
                    url,
                    lambda real_time_event: self._async_executor.run_coro(
                        self._fetch_configuration(real_time_event.time_stamp), "fetch_configuration"
                    ),
                )
        else:
            if self._real_time_configuration_service is not None:
                self._real_time_configuration_service.close()
                self._real_time_configuration_service = None
        KameleoonLogger.debug("RETURN: KameleoonClient._manage_configuration_update(is_real_time_update: %s)",
                              is_real_time_update)

    def get_engine_tracking_code(self, visitor_code: str) -> str:
        """
        The `get_engine_tracking_code` returns the JavaScript code to be inserted in your page
        to send automatically the exposure events to the analytics solution you are using.
        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :return: Tracking code
        :rtype: str
        """
        KameleoonLogger.info("CALL: KameleoonClient.get_engine_tracking_code(visitor_code: %s)", visitor_code)
        visitor = self._visitor_manager.get_visitor(visitor_code)
        visitor_variations = visitor.variations if visitor else None
        tracking_code = self._hybrid_manager.get_engine_tracking_code(visitor_variations)
        KameleoonLogger.info(
            "RETURN: KameleoonClient.get_engine_tracking_code(visitor_code: %s) -> (tracking_code: %s)",
            visitor_code, tracking_code)
        return tracking_code

    def on_update_configuration(self, handler: Callable[[], None]):
        """
        The `on_update_configuration()` method allows you to handle the event when configuration
        has updated data. It takes one input parameter: callable **handler**. The handler
        that will be called when the configuration is updated using a real-time configuration event.
        :param handler: The handler that will be called when the configuration
        is updated using a real-time configuration event.
        :type need_call: Callable[[None], None]
        :return:  None
        """
        self._update_configuration_handler = handler
        KameleoonLogger.info("CALL/RETURN: KameleoonClient.on_update_configuration(handler)")

    def __add_fetch_configuration_job(self) -> None:
        """
        Add job for updating configuration with specific interval (polling mode)
        :return: None
        """
        self._async_executor.scheduler.schedule_job(
            "Client._fetch_configuration_job",
            self._config.refresh_interval_second,
            self._fetch_configuration_job,
        )

    async def _fetch_configuration_job(self) -> None:
        if not self._data_manager.data_file.settings.real_time_update:
            await self._fetch_configuration()

    async def _obtain_configuration(self, time_stamp: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Obtaining configuration from CDN service.
        Should be run in a separate thead.
        :param sitecode:
        :type: str
        :return: None
        """
        KameleoonLogger.debug("CALL: KameleoonClient._obtain_configuration(time_stamp: %s)", time_stamp)
        service: ConfigurationService = self._network_manager.get_service(ConfigurationService)
        response = await service.fetch_configuration(self._config.environment, time_stamp)
        content = None
        if response.code and (response.code // 100 == 2):
            content = response.content
        KameleoonLogger.debug("RETURN: KameleoonClient._obtain_configuration(time_stamp: %s) -> (content: %s)",
                              time_stamp, content)
        return content

    def __get_feature_variation_key(self, visitor_code: str, feature_key: str) -> Tuple[FeatureFlag, str]:
        """
        helper method for getting variation key for feature flag
        """
        KameleoonLogger.debug(
            "CALL: KameleoonClient.__get_feature_variation_key(visitor_code: %s, feature_key: %s)",
            visitor_code, feature_key)
        feature_flag = self._data_manager.data_file.get_feature_flag(feature_key)
        (variation, rule) = self.__calculate_variation_rule_for_feature(visitor_code, feature_flag)
        variation_key = self.__calculate_variation_key(variation, rule, feature_flag)
        self.__assign_feature_variation(visitor_code, rule, variation)
        self._tracking_manager.add_visitor_code(visitor_code)
        KameleoonLogger.debug(
            "RETURN: KameleoonClient.__get_feature_variation_key(visitor_code: %s, feature_key: %s) -> "
            "(feature_flag: %s, variation_key: %s)", visitor_code, feature_key, feature_flag, variation_key)
        return (feature_flag, variation_key)

    def __assign_feature_variation(
        self, visitor_code: str, rule: Optional[Rule], variation: Optional[VariationByExposition]
    ) -> None:
        if rule is None:
            return
        KameleoonLogger.debug(
            "CALL: KameleoonClient.__assign_feature_variation(visitor_code: %s, rule: %s, variation: %s)",
            visitor_code, rule, variation)
        visitor = self._visitor_manager.get_or_create_visitor(visitor_code)
        experiment_id = rule.experiment_id
        variation_id = variation.variation_id if variation is not None else None
        if experiment_id is not None and variation_id is not None:
            as_variation = AssignedVariation(experiment_id, variation_id, rule.type)
            visitor.assign_variation(as_variation)
        KameleoonLogger.debug(
            "RETURN: KameleoonClient.__assign_feature_variation(visitor_code: %s, rule: %s, variation: %s)",
            visitor_code, rule, variation)

    def __calculate_variation_rule_for_feature(
        self, visitor_code: str, feature_flag: FeatureFlag
    ) -> Tuple[Optional[VariationByExposition], Optional[Rule]]:
        """helper method for calculate variation key for feature flag"""
        KameleoonLogger.debug(
            "CALL: KameleoonClient.__calculate_variation_rule_for_feature(visitor_code: %s, feature_flag: %s)",
            visitor_code, feature_flag)
        for rule in feature_flag.rules:
            # check if visitor is targeted for rule, else next rule
            if not self.__check_targeting(visitor_code, rule.experiment_id, rule):
                continue
            visitor = self._visitor_manager.get_visitor(visitor_code)
            # use mappingIdentifier instead of visitorCode if it was set up
            code_for_hash = (
                visitor.mapping_identifier
                if visitor is not None and visitor.mapping_identifier is not None
                else visitor_code
            )
            # uses for rule exposition
            hash_rule = obtain_hash_double_rule(code_for_hash, rule.id_, rule.respool_time)
            KameleoonLogger.debug("Calculated hash_rule: %s for visitor_code: %s", hash_rule, code_for_hash)
            # check main expostion for rule with hashRule
            if hash_rule <= rule.exposition:
                if rule.is_targeted_delivery:
                    KameleoonLogger.debug(
                        "RETURN: KameleoonClient.__calculate_variation_rule_for_feature(visitor_code: %s, "
                        "feature_flag: %s) -> (variation: %s, rule: %s)",
                        visitor_code, feature_flag, rule.first_variation, rule)
                    return (rule.first_variation, rule)

                # uses for variation's expositions
                hash_variation = obtain_hash_double_rule(code_for_hash, rule.experiment_id, rule.respool_time)
                KameleoonLogger.debug(
                    "Calculated hash_variation: %s for visitor_code: %s", hash_variation, code_for_hash)
                # get variation with hash_variation
                variation = rule.get_variation(hash_variation)
                if variation:
                    KameleoonLogger.debug(
                        "RETURN: KameleoonClient.__calculate_variation_rule_for_feature(visitor_code: %s, "
                        "feature_flag: %s) -> (variation: %s, rule: %s)",
                        visitor_code, feature_flag, variation, rule)
                    return (variation, rule)
            elif rule.is_targeted_delivery:
                break
        KameleoonLogger.debug(
            "RETURN: KameleoonClient.__calculate_variation_rule_for_feature(visitor_code: %s, feature_flag: %s) "
            "-> (variation: None, rule: None)", visitor_code, feature_flag)
        return None, None

    @staticmethod
    def __calculate_variation_key(
        var_by_exp: Optional[VariationByExposition],
        rule: Optional[Rule],
        feature_flag: FeatureFlag,
    ) -> str:
        KameleoonLogger.debug(
            "CALL: KameleoonClient.__calculate_variation_key(var_by_exp: %s, rule: %s, feature_flag: %s) ",
            var_by_exp, rule, feature_flag)
        if var_by_exp:
            variation_key = var_by_exp.variation_key
        elif rule and rule.is_experimentation:
            variation_key = configuration.Variation.Type.OFF.value
        else:
            variation_key = feature_flag.default_variation_key
        KameleoonLogger.debug(
            "RETURN: KameleoonClient.__calculate_variation_key(var_by_exp: %s, rule: %s, feature_flag: %s) "
            "-> (variation_key: %s)", var_by_exp, rule, feature_flag, variation_key)
        return variation_key

    def __set_unique_identifier(self, visitor_code: str, is_unique_identifier: bool) -> None:
        KameleoonLogger.warning(
            "The 'is_unique_identifier' parameter is deprecated. Please, add 'UniqueIdentifier' to a visitor instead."
        )
        self._visitor_manager.add_data(visitor_code, UniqueIdentifier(is_unique_identifier))

    def _is_consent_given(self, visitor_code: str) -> bool:
        return not self._data_manager.data_file.settings.is_consent_required or \
            ((visitor := self._visitor_manager.get_visitor(visitor_code)) is not None) and visitor.legal_consent
