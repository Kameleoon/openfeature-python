"""Network"""
from urllib.parse import quote


def encode_uri(to_encode: str) -> str:
    """Encodes a given string to be safely included in a URI."""
    return quote(to_encode, safe="~()*!.'")
