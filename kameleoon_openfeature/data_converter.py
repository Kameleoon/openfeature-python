""" Kameleoon OpenFeature """
from typing import Optional, Callable, Dict, List, Union, Any

from kameleoon.data import CustomData
from kameleoon.data import Conversion
from openfeature.evaluation_context import EvaluationContext

from kameleoon_openfeature.types import Data


class DataConverter:
    """
    DataConverter is used to convert context data to Kameleoon-specific data structures.
    """

    # pylint: disable=W0108
    _conversion_methods: Dict[str, Callable[[Any], Optional[Union[CustomData, Conversion]]]] = {
        Data.Type.CONVERSION: lambda value: DataConverter.__make_conversion(value),
        Data.Type.CUSTOM_DATA: lambda value: DataConverter.__make_custom_data(value)
    }

    @classmethod
    def to_kameleoon(cls, context: Optional[EvaluationContext]) -> List[Union[CustomData, Conversion]]:
        """
        Converts the given context to a list of Kameleoon data objects.

        Args:
            context (object): The context containing attributes to be converted.

        Returns:
            list: A list of Kameleoon data objects.
        """
        if context is None:
            return []

        data = []
        for key, value in context.attributes.items():
            method = DataConverter._conversion_methods.get(key)
            if method is None or value is None:
                continue
            values = value if isinstance(value, list) else [value]
            for val in values:
                data.append(method(val))

        return data

    @classmethod
    def __make_conversion(cls, value) -> Optional[Conversion]:
        """
        Converts a dictionary to a Conversion object.

        Args:
            value (dict): The dictionary containing conversion data.

        Returns:
            Conversion: A Conversion object initialized with the data from the dictionary.
            None: If the input value is not a dictionary.
        """
        if not isinstance(value, dict):
            return None

        goal_id = value.get(Data.ConversionType.GOAL_ID)
        revenue = value.get(Data.ConversionType.REVENUE, 0.0)
        if isinstance(revenue, int):
            revenue = float(revenue)

        return Conversion(goal_id, revenue, False)

    @classmethod
    def __make_custom_data(cls, value) -> Optional[CustomData]:
        """
        Converts a dictionary to a CustomData object.

        Args:
            value (dict): The dictionary containing custom data.

        Returns:
            CustomData: A CustomData object initialized with the data from the dictionary.
            None: If the input value is not a dictionary.
        """
        if not isinstance(value, dict):
            return None

        index = value.get(Data.CustomDataType.INDEX)
        values = value.get(Data.CustomDataType.VALUES, [])
        if isinstance(values, str):
            values = [values]
        elif values is None:
            values = []

        return CustomData(index, *values)
