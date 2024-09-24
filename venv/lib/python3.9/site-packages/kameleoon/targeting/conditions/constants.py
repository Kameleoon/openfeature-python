""" Constants """

from enum import Enum


class TargetingOperator(Enum):
    """Targeting operator in condition"""

    UNDEFINED = "UNDEFINED"
    CONTAINS = "CONTAINS"
    EXACT = "EXACT"
    REGULAR_EXPRESSION = "REGULAR_EXPRESSION"
    LOWER = "LOWER"
    EQUAL = "EQUAL"
    GREATER = "GREATER"
    TRUE = "TRUE"
    FALSE = "FALSE"
    AMONG_VALUES = "AMONG_VALUES"
    ANY = "ANY"
