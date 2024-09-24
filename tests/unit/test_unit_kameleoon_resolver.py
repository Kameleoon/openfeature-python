import unittest
from unittest.mock import Mock, call

from kameleoon.exceptions import FeatureNotFound, VisitorCodeInvalid
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ErrorCode

from kameleoon_openfeature.resolver import KameleoonResolver

TARGETING_KEY = 'targeting_key'


class TestKameleoonResolver(unittest.TestCase):
    def setUp(self):
        self.client_mock = Mock()
        self.resolver = KameleoonResolver(self.client_mock)

    def test_resolve_with_nil_context_returns_error_for_missing_targeting_key(self):
        # arrange
        flag_key = 'testFlag'
        default_value = 'defaultValue'
        expected_error_code = ErrorCode.TARGETING_KEY_MISSING
        expected_error_message = 'The TargetingKey is required in context and cannot be omitted.'

        # act
        result = self.resolver.resolve(flag_key=flag_key, default_value=default_value)

        # assert
        self.assert_result(result, default_value, None, expected_error_code, expected_error_message)

    def test_resolve_no_match_variables_returns_error_for_flag_not_found(self):
        # arrange
        flag_key = 'testFlag'
        default_value = 42
        visitor_code = 'testVisitor'

        test_cases = [
            {'variant': 'on', 'add_variable_key': False, 'variables': {},
             'expected_error_msg': "The variation 'on' has no variables"},
            {'variant': 'var', 'add_variable_key': True, 'variables': {'key': None},
             'expected_error_msg': "The value for provided variable key 'variableKey' isn't found in variation 'var'"}
        ]

        for tc in test_cases:
            self.client_mock.get_feature_variation_key.return_value = tc['variant']
            self.client_mock.get_feature_variation_variables.return_value = tc['variables']
            self.client_mock.add_data.return_value = None

            eval_context = {}
            if tc['add_variable_key']:
                eval_context['variableKey'] = 'variableKey'
            eval_context = EvaluationContext(attributes=eval_context, targeting_key=visitor_code)

            expected_error_code = ErrorCode.FLAG_NOT_FOUND
            expected_error_message = tc['expected_error_msg']

            # act
            result = self.resolver.resolve(flag_key=flag_key, default_value=default_value,
                                           evaluation_context=eval_context)

            # assert
            self.assert_result(result, default_value, tc['variant'], expected_error_code, expected_error_message)

    def test_resolve_mismatch_type_returns_error_type_mismatch(self):
        # arrange
        flag_key = 'testFlag'
        expected_variant = 'on'
        default_value = 42
        visitor_code = 'testVisitor'

        test_cases = [True, 'string', 10.0]

        for return_value in test_cases:
            self.client_mock.get_feature_variation_key.return_value = expected_variant
            self.client_mock.get_feature_variation_variables.return_value = {'key': return_value}
            self.client_mock.add_data.return_value = None

            eval_context = EvaluationContext(targeting_key=visitor_code)
            expected_error_code = ErrorCode.TYPE_MISMATCH
            expected_error_message = 'The type of value received is different from the requested value.'

            # act
            result = self.resolver.resolve(flag_key=flag_key, default_value=default_value,
                                           evaluation_context=eval_context)

            # assert
            self.assert_result(result, default_value, expected_variant, expected_error_code, expected_error_message)

    def test_resolve_kameleoon_exception_flag_not_found(self):
        # arrange
        flag_key = 'testFlag'
        visitor_code = 'testVisitor'
        default_value = 42

        exception = FeatureNotFound('featureException')
        self.client_mock.add_data.return_value = None
        self.client_mock.get_feature_variation_key.side_effect = exception

        eval_context = EvaluationContext(targeting_key=visitor_code)
        expected_error_code = ErrorCode.FLAG_NOT_FOUND
        expected_error_message = 'featureException'

        # act
        result = self.resolver.resolve(flag_key=flag_key, default_value=default_value, evaluation_context=eval_context)

        # assert
        self.assert_result(result, default_value, None, expected_error_code, expected_error_message)

    def test_resolve_kameleoon_exception_visitor_code_invalid(self):
        # arrange
        flag_key = 'testFlag'
        visitor_code = 'testVisitor'
        default_value = 42

        exception = VisitorCodeInvalid('visitorCodeInvalid')
        self.client_mock.add_data.side_effect = exception

        eval_context = EvaluationContext(targeting_key=visitor_code)
        expected_error_code = ErrorCode.INVALID_CONTEXT
        expected_error_message = 'visitorCodeInvalid'

        # act
        result = self.resolver.resolve(flag_key=flag_key, default_value=default_value,
                                       evaluation_context=eval_context)

        # assert
        self.assert_result(result, default_value, None, expected_error_code, expected_error_message)

    def test_resolve_returns_result_details(self):
        # arrange
        flag_key = 'testFlag'
        visitor_code = 'testVisitor'
        expected_variant = 'variant'

        test_cases = [
            {'variable_key': None, 'variables': {'k': 10}, 'expected_value': 10, 'default_value': 9},
            {'variable_key': None, 'variables': {'k1': 'str'}, 'expected_value': 'str', 'default_value': 'st'},
            {'variable_key': None, 'variables': {'k2': True}, 'expected_value': True, 'default_value': False},
            {'variable_key': None, 'variables': {'k3': 10.0}, 'expected_value': 10.0, 'default_value': 11.0},
            {'variable_key': 'varKey', 'variables': {'varKey': 10.0}, 'expected_value': 10.0, 'default_value': 11.0}
        ]

        for tc in test_cases:
            self.client_mock.add_data.return_value = None
            self.client_mock.get_feature_variation_key.return_value = expected_variant
            self.client_mock.get_feature_variation_variables.return_value = tc['variables']

            eval_context = {}
            if tc['variable_key']:
                eval_context['variableKey'] = tc['variable_key']
            eval_context = EvaluationContext(attributes=eval_context, targeting_key=visitor_code)

            # act
            result = self.resolver.resolve(flag_key=flag_key, default_value=tc['default_value'],
                                           evaluation_context=eval_context)

            # assert
            self.assert_result(result, tc['expected_value'], expected_variant, None, None)

    def assert_result(self, result, expected_value, expected_variant, expected_error_code, expected_error_message):
        if expected_value is None:
            self.assertIsNone(result.value)
        else:
            self.assertEqual(expected_value, result.value)
        if expected_error_code is None:
            self.assertIsNone(result.error_code)
        else:
            self.assertEqual(expected_error_code, result.error_code)
        if expected_error_message is None:
            self.assertIsNone(result.error_message)
        else:
            self.assertIn(expected_error_message, result.error_message)
        if expected_variant is None:
            self.assertIsNone(result.variant)
        else:
            self.assertEqual(expected_variant, result.variant)
