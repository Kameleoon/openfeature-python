"""Kameleoon Configuration"""

from enum import Enum
from kameleoon.helpers.functions import enum_from_literal


class RuleType(Enum):
    """Possible types of rules"""

    UNKNOWN: None = None
    EXPERIMENTATION = "EXPERIMENTATION"
    TARGETED_DELIVERY = "TARGETED_DELIVERY"


def rule_type_from_literal(literal: str) -> RuleType:
    """Converts rule type literal to RuleType value"""
    return enum_from_literal(literal, RuleType, RuleType.UNKNOWN)
