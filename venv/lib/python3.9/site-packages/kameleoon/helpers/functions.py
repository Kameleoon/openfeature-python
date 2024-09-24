"""Helper functions"""
import hashlib
import json
import math
import sys
from enum import Enum
from typing import Dict, Any, Optional, Union, Type, TypeVar


def obtain_hash_double(
    visitor_code: str, respool_times=None, container_id: str = ""
) -> float:
    """Calculate the hash value for a given visitor_code"""
    return _obtain_hash_double(visitor_code, respool_times, container_id)


def obtain_hash_double_rule(
    visitor_code: str, container_id: int, respool_time: Optional[int] = None
) -> float:
    """Calculate the hash value for feature flag v2 for a given visitor_code"""
    return _obtain_hash_double(
        visitor_code=visitor_code,
        container_id=container_id,
        suffix=str(respool_time) if respool_time else "",
    )


def _obtain_hash_double(
    visitor_code: str,
    respool_times=None,
    container_id: Union[str, int] = "",
    suffix: str = "",
) -> float:
    if respool_times is None:
        respool_times = {}
    identifier = visitor_code
    identifier += str(container_id)
    identifier += suffix
    if respool_times:
        identifier += "".join([str(v) for k, v in sorted(respool_times.items())])
    return int(hashlib.sha256(identifier.encode("UTF-8")).hexdigest(), 16) / math.pow(
        2, 256
    )


def load_params_from_json(json_path) -> Dict[Any, Any]:
    """Load json for a file"""
    with open(json_path, encoding="utf-8") as file:
        return json.load(file)


def get_size(obj) -> float:
    """Get size of memory used by given obj"""
    return sum([sys.getsizeof(v) + sys.getsizeof(k) for k, v in obj.items()])


E = TypeVar('E', bound=Enum)  # pylint: disable=C0103


def enum_from_literal(literal: str, enum_type: Type[E], default_value: E) -> E:
    """
    Converts enum literal to enum value.
    Returns default enum value if literal does not correspond any enum value.
    """
    try:
        return enum_type(literal)
    except ValueError:
        return default_value


def enum_from_name_literal(literal: str, enum_type: Type[E], default_value: Optional[E]) -> Optional[E]:
    """
    Converts enum name literal to enum value.
    Returns default enum value if literal does not correspond any enum name.
    """
    try:
        return enum_type[literal]
    except ValueError:
        return default_value


def compare_str_ignore_case(value_1: Optional[str], value_2: Optional[str]) -> bool:
    """Comparing two strings ignoring case."""
    return (value_1 == value_2 or
            ((value_1 is not None and value_2 is not None) and value_1.lower() == value_2.lower()))
