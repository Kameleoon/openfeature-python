"""Helpers for nonce"""

import random


ALPHA_NUMERIC_CHARS = "0123456789ABCDEF"
NONCE_LENGTH = 16


def get_nonce() -> str:
    """Generates alphanumeric characters"""
    return "".join(random.choice(ALPHA_NUMERIC_CHARS) for _ in range(NONCE_LENGTH))
