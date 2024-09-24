import unittest
from kameleoon_openfeature.types import Data


class TestTypes(unittest.TestCase):
    def test_proper_values(self):
        # assert
        self.assertEqual('conversion', Data.Type.CONVERSION)
        self.assertEqual('customData', Data.Type.CUSTOM_DATA)

        self.assertEqual('index', Data.CustomDataType.INDEX)
        self.assertEqual('values', Data.CustomDataType.VALUES)

        self.assertEqual('goalId', Data.ConversionType.GOAL_ID)
        self.assertEqual('revenue', Data.ConversionType.REVENUE)

