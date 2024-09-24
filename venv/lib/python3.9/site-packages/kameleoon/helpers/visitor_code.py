"""Helper methods for working with visitor codes"""

from secrets import token_hex
from typing import Optional
from kameleoon.exceptions import VisitorCodeInvalid


VISITOR_CODE_MAX_LENGTH = 255
VISITOR_CODE_LENGTH = 16


def generate_visitor_code() -> str:
    """Generates a random visitor code"""
    return token_hex(VISITOR_CODE_LENGTH >> 1)


def validate_visitor_code(visitor_code: Optional[str]) -> None:
    """
    Validates a visitor code.

    Raises `VisitorCodeInvalid` if visitor_code is `None`, empty, or longer than 255 chars.
    """
    if not visitor_code:
        raise VisitorCodeInvalid("empty visitor code")
    if len(visitor_code) > VISITOR_CODE_MAX_LENGTH:
        raise VisitorCodeInvalid("is longer than 255 chars")
