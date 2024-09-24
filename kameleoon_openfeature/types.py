""" Kameleoon OpenFeature """


# pylint: disable=R0903
class Data:
    """
    This module defines the data types used for Kameleoon integration with OpenFeature SDK.

    Classes:
        Data: Contains nested classes for different Kameleoon data types.

    Nested Classes:
        Data.Type: Defines constants for different Kameleoon data types.
            - CONVERSION: Represents conversion data type.
            - CUSTOM_DATA: Represents custom data type.

        Data.CustomDataType: Defines constants for Kameleoon CustomData attributes.
            - INDEX: Represents the index attribute of CustomData.
            - VALUES: Represents the values attribute of CustomData.

        Data.ConversionType: Defines constants for Kameleoon Conversion attributes.
            - GOAL_ID: Represents the goal ID attribute of Conversion.
            - REVENUE: Represents the revenue attribute of Conversion.
    """
    class Type:
        """
        Defines constants for different Kameleoon data types.
        """
        CONVERSION = 'conversion'
        CUSTOM_DATA = 'customData'

    class CustomDataType:
        """
        Defines constants for Kameleoon CustomData attributes.
        """
        INDEX = 'index'
        VALUES = 'values'

    class ConversionType:
        """
        Defines constants for Kameleoon Conversion attributes.
        """
        GOAL_ID = 'goalId'
        REVENUE = 'revenue'
