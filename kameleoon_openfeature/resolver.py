""" Kameleoon OpenFeature """
from typing import Optional, Any

from kameleoon import KameleoonClient
from kameleoon.exceptions import VisitorCodeInvalid, FeatureVariationNotFound, FeatureError, FeatureNotFound
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ErrorCode
from openfeature.flag_evaluation import FlagResolutionDetails, Reason

from kameleoon_openfeature.data_converter import DataConverter


class Resolver:
    """
    Abstract class for resolving the value of the flag for the given flag key and evaluation context.
    """
    def resolve(self, flag_key: str, default_value: Any, evaluation_context: Optional[EvaluationContext] = None
                ) -> FlagResolutionDetails[Any]:
        """
        Resolves the value of the flag for the given flag key and evaluation context.
        :param flag_key:
        :param default_value:
        :param evaluation_context:
        :return FlagResolutionDetails:
        """
        raise NotImplementedError('Subclasses must implement the resolve method')


class KameleoonResolver(Resolver):
    """
    Implementation of the Resolver class for Kameleoon.
    """
    VARIABLE_KEY = 'variableKey'

    def __init__(self, client: KameleoonClient):
        self.client = client

    # pylint: disable=R0911
    def resolve(self, flag_key: str, default_value: Any, evaluation_context: Optional[EvaluationContext] = None
                ) -> FlagResolutionDetails[Any]:
        try:
            visitor_code = self.__get_targeting_key(evaluation_context) if evaluation_context is not None else None
            if visitor_code is None or visitor_code == '':
                return self._create_error_response(
                    default_value,
                    ErrorCode.TARGETING_KEY_MISSING,
                    'The TargetingKey is required in context and cannot be omitted.'
                )

            self.client.add_data(visitor_code, *DataConverter.to_kameleoon(evaluation_context))

            variant = self.client.get_feature_variation_key(visitor_code, flag_key)
            variables = self.client.get_feature_variation_variables(flag_key, variant)

            variable_key = self.__get_variable_key(evaluation_context, variables)
            value = variables.get(variable_key)

            if value is None or variable_key == '':
                return self._create_error_response(default_value, ErrorCode.FLAG_NOT_FOUND,
                                                   self.__make_error_description(variant, variable_key), variant)

            if type(value) is type(default_value):
                return FlagResolutionDetails(
                    value=value,
                    reason=Reason.STATIC,
                    variant=variant
                )
            return self._create_error_response(default_value,
                                               ErrorCode.TYPE_MISMATCH,
                                               'The type of value received is different from the requested value.',
                                               variant)
        except VisitorCodeInvalid as exception:
            return self._create_error_response(default_value, ErrorCode.INVALID_CONTEXT, str(exception))
        except (FeatureError, FeatureNotFound, FeatureVariationNotFound) as exception:
            return self._create_error_response(default_value, ErrorCode.FLAG_NOT_FOUND, str(exception))
        except Exception as exception:  # pylint: disable=W0718
            return self._create_error_response(default_value, ErrorCode.GENERAL, str(exception))

    @staticmethod
    def __get_targeting_key(evaluation_context) -> Optional[str]:
        """
        Extracts the TargetingKey from the evaluation context.
        :param evaluation_context:
        :return Optional[str]:
        """
        targeting_key = evaluation_context.targeting_key
        if isinstance(targeting_key, str):
            return targeting_key
        return None

    @staticmethod
    def __get_variable_key(context, variables) -> Optional[str]:
        """
        Extracts the variable key from the evaluation context.
        :param context:
        :param variables:
        :return Optional[str]:
        """
        if context is None or not isinstance(context, EvaluationContext):
            return None
        variable_key = context.attributes.get(KameleoonResolver.VARIABLE_KEY)
        if variable_key is None or variable_key == '':
            variable_key = next(iter(variables.keys()), None)
        return variable_key

    @staticmethod
    def __make_error_description(variant, variable_key) -> str:
        """
        Creates an error description.
        :param variant:
        :param variable_key:
        :return str:
        """
        if variable_key is None or variable_key == '':
            return f"The variation '{variant}' has no variables"
        return f"The value for provided variable key '{variable_key}' isn't found in variation '{variant}'"

    @staticmethod
    def _create_error_response(default_value, error_code, error_message, variant=None) -> FlagResolutionDetails[Any]:
        """
        Creates a FlagResolutionDetails object for error responses.
        :param default_value:
        :param error_code:
        :param error_message:
        :param variant:
        :return FlagResolutionDetails:
        """
        return FlagResolutionDetails(
            value=default_value,
            error_code=error_code,
            error_message=error_message,
            reason=Reason.ERROR,
            variant=variant
        )
