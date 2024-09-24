import unittest

from openfeature import api
from openfeature.evaluation_context import EvaluationContext
from openfeature.exception import ErrorCode

from kameleoon_openfeature.types import Data
from kameleoon_openfeature.kameleoon_provider import KameleoonProvider, KameleoonClientConfig


class TestExample(unittest.TestCase):
    def test_client(self):
        visitor_code = '222D7B50-A0C7-435B-B628-E86670DDBDB9'
        feature_key = 'test_feature_variables'

        client_config = KameleoonClientConfig(
            'clientId',
            'clientSecret',
            top_level_domain='topLevelDomain'
        )
        provider = KameleoonProvider('tndueuutdq', config=client_config)

        api.set_provider(provider)

        client = api.get_client()

        data_dictionary = {
            Data.Type.CONVERSION: {
                Data.ConversionType.GOAL_ID: 1,
                Data.ConversionType.REVENUE: 200
            },
            Data.Type.CUSTOM_DATA: [
                {
                    Data.CustomDataType.INDEX: 1,
                    Data.CustomDataType.VALUES: ['10', '30']
                },
                {
                    Data.CustomDataType.INDEX: 2,
                    Data.CustomDataType.VALUES: '20'
                }
            ]
        }

        eval_context = EvaluationContext(attributes=data_dictionary, targeting_key=visitor_code)

        evaluation_details = client.get_boolean_details(flag_key=feature_key, default_value=False,
                                                        evaluation_context=eval_context)
        self.assertEqual(True, evaluation_details.value)
        self.assertEqual('off', evaluation_details.variant)

        evaluation_details = client.get_string_details(flag_key=feature_key, default_value='test')
        self.assertEqual('test', evaluation_details.value)
        self.assertEqual(ErrorCode.TARGETING_KEY_MISSING, evaluation_details.error_code)

        eval_context = EvaluationContext(targeting_key=visitor_code)

        evaluation_details = client.get_string_details(flag_key=feature_key, default_value='test',
                                                       evaluation_context=eval_context)
        self.assertEqual('test', evaluation_details.value)
        self.assertIsNone(evaluation_details.variant)
        self.assertEqual(ErrorCode.TYPE_MISMATCH, evaluation_details.error_code)

        values = {
            'variableKey': 'stringKey'
        }

        eval_context = EvaluationContext(attributes=values, targeting_key=visitor_code)

        evaluation_details = client.get_string_details(flag_key=feature_key, default_value="test",
                                                       evaluation_context=eval_context)
        self.assertEqual("TestString", evaluation_details.value)
        self.assertEqual('off', evaluation_details.variant)
        self.assertIsNone(evaluation_details.error_code)

        data_dictionary = {
            Data.Type.CUSTOM_DATA: [
                {
                    Data.CustomDataType.INDEX: 2,
                    Data.CustomDataType.VALUES: "true"
                }
            ]
        }

        eval_context = EvaluationContext(attributes=data_dictionary, targeting_key=visitor_code)

        evaluation_details = client.get_string_details(flag_key=feature_key, default_value="test",
                                                       evaluation_context=eval_context)
        self.assertEqual("test", evaluation_details.value)
        self.assertIsNone(evaluation_details.variant)
        self.assertEqual(ErrorCode.TYPE_MISMATCH, evaluation_details.error_code)

        data_dictionary = {
            'variableKey': 'stringKey'
        }

        eval_context = EvaluationContext(attributes=data_dictionary, targeting_key=visitor_code)

        evaluation_details = client.get_string_details(flag_key=feature_key, default_value="test",
                                                       evaluation_context=eval_context)
        self.assertEqual("TestString", evaluation_details.value)
        self.assertEqual('on', evaluation_details.variant)
        self.assertIsNone(evaluation_details.error_code)
