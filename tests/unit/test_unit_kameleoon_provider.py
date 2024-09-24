import unittest
from unittest.mock import Mock, patch

from kameleoon import KameleoonClientFactory
from openfeature.exception import ProviderNotReadyError
from openfeature.flag_evaluation import FlagResolutionDetails, Reason

from kameleoon_openfeature.kameleoon_provider import KameleoonProvider
from kameleoon.kameleoon_client_config import KameleoonClientConfig


class TestKameleoonProvider(unittest.TestCase):

    def setUp(self):
        self.resolver_mock = Mock()
        config = KameleoonClientConfig(
            "cid",
            "csecret",
        )
        self.provider = KameleoonProvider('siteCode', config=config)
        patcher = patch.object(self.provider, '_KameleoonProvider__resolver', self.resolver_mock)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_metadata(self):
        # arrange
        metadata = self.provider.get_metadata()

        # assert
        self.assertEqual('Kameleoon Provider', metadata.name)

    def test_exception_raised_when_error_create_provider(self):
        # arrange
        site_code = ''
        config = KameleoonClientConfig('clientId', 'clientSecret')

        # assert
        with self.assertRaises(ProviderNotReadyError):
            KameleoonProvider(site_code, config=config)

    def test_resolve_boolean_value_returns_correct_value(self):
        # arrange
        default_value = False
        expected_value = True
        self.setup_mock_resolver(expected_value)

        # act
        result = self.provider.resolve_boolean_details(flag_key='flagKey', default_value=default_value)

        # assert
        self.assertEqual(expected_value, result.value)

    def test_resolve_float_value_returns_correct_value(self):
        # arrange
        default_value = 0.5
        expected_value = 2.5
        self.setup_mock_resolver(expected_value)

        # act
        result = self.provider.resolve_float_details(flag_key='flagKey', default_value=default_value)

        # assert
        self.assertEqual(expected_value, result.value)

    def test_resolve_integer_value_returns_correct_value(self):
        # arrange
        default_value = 1
        expected_value = 2
        self.setup_mock_resolver(expected_value)

        # act
        result = self.provider.resolve_integer_details(flag_key='flagKey', default_value=default_value)

        # assert
        self.assertEqual(expected_value, result.value)

    def test_resolve_string_value_returns_correct_value(self):
        # arrange
        default_value = '1'
        expected_value = '2'
        self.setup_mock_resolver(expected_value)

        # act
        result = self.provider.resolve_string_details(flag_key='flagKey', default_value=default_value)

        # assert
        self.assertEqual(expected_value, result.value)

    def test_resolve_structure_value_returns_correct_value(self):
        # arrange
        default_value = {'k': 10}
        expected_value = {'k1': 20}
        self.setup_mock_resolver(expected_value)

        # act
        result = self.provider.resolve_object_details(flag_key='flagKey', default_value=default_value)

        # assert
        self.assertEqual(expected_value, result.value)

    def test_shutdown_forget_site_code(self):
        # arrange
        site_code = 'testSiteCode'
        config = KameleoonClientConfig('clientId', 'clientSecret')

        provider = KameleoonProvider(site_code, config=config)
        client_first = provider.get_client()
        client_to_check = KameleoonClientFactory.create(site_code, config=config)

        # act
        provider.shutdown()

        provider_second = KameleoonProvider(site_code, config=config)
        client_second = provider_second.get_client()

        # assert
        self.assertIs(client_to_check, client_first)
        self.assertIsNot(client_first, client_second)

    def setup_mock_resolver(self, expected_value):
        result = FlagResolutionDetails(
            value=expected_value,
            reason=Reason.STATIC
        )
        self.resolver_mock.resolve.return_value = result
