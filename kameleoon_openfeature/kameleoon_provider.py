""" Kameleoon OpenFeature """
import typing

from kameleoon import KameleoonClientFactory, KameleoonClientConfig, KameleoonClient
from kameleoon.exceptions import KameleoonError
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ProviderNotReadyError
from openfeature.flag_evaluation import FlagResolutionDetails
from openfeature.hook import Hook
from openfeature.provider import AbstractProvider, Metadata

from kameleoon_openfeature.resolver import KameleoonResolver


class KameleoonProvider(AbstractProvider):
    """
    The KameleoonProvider class is an implementation of the AbstractProvider interface for the Kameleoon SDK.
    """
    META_NAME = "Kameleoon Provider"

    def __init__(self, site_code, config: typing.Optional[KameleoonClientConfig] = None, ):
        super().__init__()
        self.__site_code = site_code
        self.__client = self.__make_kameleoon_client(site_code, config)
        self.__resolver = KameleoonResolver(self.__client)

    @staticmethod
    def __make_kameleoon_client(site_code: str, config: typing.Optional[KameleoonClientConfig] = None
                                ) -> KameleoonClient:
        """
        Creates a KameleoonClient SDK instance.
        :param site_code:
        :param config:
        :return KameleoonClient:
        """
        try:
            return KameleoonClientFactory.create(site_code, config)
        except KameleoonError as ex:
            raise ProviderNotReadyError(ex.message) from ex

    def get_metadata(self) -> Metadata:
        """
        Returns the metadata of the provider.
        """
        return Metadata(name=self.META_NAME)

    def resolve_boolean_details(
            self,
            flag_key: str,
            default_value: bool,
            evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[bool]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        return self.__resolver.resolve(flag_key, default_value, evaluation_context)

    def resolve_string_details(
            self,
            flag_key: str,
            default_value: str,
            evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[str]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        return self.__resolver.resolve(flag_key, default_value, evaluation_context)

    def resolve_integer_details(
            self,
            flag_key: str,
            default_value: int,
            evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[int]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        return self.__resolver.resolve(flag_key, default_value, evaluation_context)

    def resolve_float_details(
            self,
            flag_key: str,
            default_value: float,
            evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[float]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        return self.__resolver.resolve(flag_key, default_value, evaluation_context)

    def resolve_object_details(
            self,
            flag_key: str,
            default_value: typing.Union[typing.Dict[typing.Any, typing.Any], typing.List[typing.Any]],
            evaluation_context: typing.Optional[EvaluationContext] = None,
    ) -> FlagResolutionDetails[typing.Union[typing.Dict[typing.Any, typing.Any], typing.List[typing.Any]]]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        return self.__resolver.resolve(flag_key, default_value, evaluation_context)

    def initialize(self, evaluation_context: EvaluationContext) -> None:
        """
        Initializes the KameleoonClient SDK instance.
        :param evaluation_context:
        :return None:
        """
        try:
            self.__client.wait_init()
        except (TimeoutError, Exception) as exception:
            raise ProviderNotReadyError(str(exception)) from exception

    def shutdown(self) -> None:
        """
        Forgets the KameleoonClient SDK instance.
        :return None:
        """
        KameleoonClientFactory.forget(self.__site_code)
        self.__client = None

    def get_client(self) -> KameleoonClient:
        """
        Returns the KameleoonClient SDK instance.

        @return: the KameleoonClient SDK instance
        """
        return self.__client

    def get_provider_hooks(self) -> typing.List[Hook]:
        """
        Returns the list of hooks.
        :return:
        """
        return []
