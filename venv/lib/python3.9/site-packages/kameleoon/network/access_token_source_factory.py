"""Network"""
from kameleoon.network.access_token_source import AccessTokenSource


class AccessTokenSourceFactory:
    """Access token source factory"""
    def __init__(self, client_id: str, client_secret: str) -> None:
        self._client_id = client_id
        self._client_secret = client_secret

    def create(self, network_manager) -> AccessTokenSource:
        """
        Creates an instance of `AccessTokenSource` with the provided network manager
        and the existing client credentials.
        """
        return AccessTokenSource(network_manager, self._client_id, self._client_secret)
