"""Helper for domain"""
import re

from kameleoon.logging.kameleoon_logger import KameleoonLogger

HTTP = "http://"
HTTPS = "https://"
REGEX_DOMAIN = (
    r"^(\.?(([a-zA-Z\d][a-zA-Z\d-]*[a-zA-Z\d])|[a-zA-Z\d]))"
    r"(\.(([a-zA-Z\d][a-zA-Z\d-]*[a-zA-Z\d])|[a-zA-Z\d])){1,126}$"
)


def validate_top_level_domain(top_level_domain: str) -> str:
    """
    Validate the given top-level domain.

    Args:
        top_level_domain (str): The top-level domain to validate.

    Returns:
        str or None: The validated top-level domain, or None if invalid.
    """
    if top_level_domain == "":
        return top_level_domain

    top_level_domain = top_level_domain.lower()

    protocols = [HTTP, HTTPS]
    for protocol in protocols:
        if top_level_domain.startswith(protocol):
            top_level_domain = top_level_domain[len(protocol):]
            KameleoonLogger.warning(
                "The top-level domain contains %s. Domain after protocol trimming: %s",
                protocol, top_level_domain)
            break

    if not re.match(REGEX_DOMAIN, top_level_domain):
        KameleoonLogger.error(f"The top-level domain '{top_level_domain}' is invalid.")
        return ""

    return top_level_domain
