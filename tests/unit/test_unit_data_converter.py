import random
import unittest

from kameleoon.data import Conversion, CustomData

from kameleoon_openfeature.data_converter import DataConverter
from kameleoon_openfeature.types import Data
from openfeature.evaluation_context import EvaluationContext


class TestDataConverter(unittest.TestCase):
    def setUp(self):
        pass

    def test_to_kameleoon_null_context_returns_empty(self):
        # arrange
        context = None

        # act
        result = DataConverter.to_kameleoon(context)

        # assert
        self.assertEqual([], result)

    def test_to_kameleoon_with_conversion_data_returns_conversion_data(self):
        tests = [
            {'name': 'WithRevenue', 'add_revenue': True},
            {'name': 'WithoutRevenue', 'add_revenue': False}
        ]

        for tt in tests:
            # arrange
            rand_goal_id = random.randint(1, 1000)
            rand_revenue = random.random() * 1000

            conversion_data = {Data.ConversionType.GOAL_ID: rand_goal_id}
            if tt['add_revenue']:
                conversion_data[Data.ConversionType.REVENUE] = rand_revenue

            context = {Data.Type.CONVERSION: conversion_data}
            eval_context = EvaluationContext(attributes=context)

            # act
            result = DataConverter.to_kameleoon(eval_context)

            # assert
            self.assertEqual(1, len(result))
            conversion = result[0]
            self.assertIsInstance(conversion, Conversion)
            self.assertEqual(rand_goal_id, conversion.goal_id)

            if tt['add_revenue']:
                self.assertEqual(rand_revenue, conversion.revenue)

    def test_to_kameleoon_with_custom_data_returns_custom_data(self):
        tests = [
            {'name': 'EmptyValues', 'expected_index': random.randint(1, 1000), 'expected_values': []},
            {'name': 'SingleValue', 'expected_index': random.randint(1, 1000), 'expected_values': ['v1']},
            {'name': 'MultipleValues', 'expected_index': random.randint(1, 1000), 'expected_values': ['v1', 'v2', 'v3']}
        ]

        for tt in tests:
            # arrange
            custom_data = {
                Data.CustomDataType.INDEX: tt['expected_index'],
                Data.CustomDataType.VALUES: tt['expected_values']
            }

            context = {Data.Type.CUSTOM_DATA: custom_data}
            eval_context = EvaluationContext(attributes=context)

            # act
            result = DataConverter.to_kameleoon(eval_context)

            # assert
            self.assertEqual(len(result), 1)
            custom_data_obj = result[0]
            self.assertIsInstance(custom_data_obj, CustomData)
            self.assertEqual(tt['expected_index'], custom_data_obj.id)
            self.assertEqual(list(tt['expected_values']), list(custom_data_obj.values))

    def test_to_kameleoon_data_all_types_returns_all_data(self):
        # arrange
        goal_id1 = random.randint(1, 1000)
        goal_id2 = random.randint(1, 1000)
        index1 = random.randint(1, 1000)
        index2 = random.randint(1, 1000)

        context_data = {
            Data.Type.CONVERSION: [
                {Data.ConversionType.GOAL_ID: goal_id1},
                {Data.ConversionType.GOAL_ID: goal_id2}
            ],
            Data.Type.CUSTOM_DATA: [
                {Data.CustomDataType.INDEX: index1},
                {Data.CustomDataType.INDEX: index2}
            ]
        }

        eval_context = EvaluationContext(attributes=context_data)

        # act
        result = DataConverter.to_kameleoon(eval_context)

        conversions = [item for item in result if isinstance(item, Conversion)]
        custom_data = [item for item in result if isinstance(item, CustomData)]

        # assert
        self.assertEqual(len(result), 4)
        self.assertEqual(conversions[0].goal_id, goal_id1)
        self.assertEqual(conversions[1].goal_id, goal_id2)
        self.assertEqual(custom_data[0].id, index1)
        self.assertEqual(custom_data[1].id, index2)
