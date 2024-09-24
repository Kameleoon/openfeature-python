"""Network"""
import asyncio
import time
from typing import Optional

from kameleoon.helpers.string_utils import StringUtils
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.network.services.automation_service import AutomationService


class AccessTokenSource:
    """Access Token Source"""
    _TOKEN_EXPIRATION_GAP = 60.0  # in seconds
    _TOKEN_OBSOLESCENCE_GAP = 1800.0  # in seconds
    _JWT_ACCESS_TOKEN_FIELD = "access_token"
    _JWT_EXPIRES_IN_FIELD = "expires_in"

    def __init__(self, network_manager, client_id: str, client_secret: str) -> None:
        KameleoonLogger.debug(
            lambda: f"CALL: AccessTokenSource(network_manager, client_id: '{StringUtils.secret(client_id)}', "
                    f"client_secret: '{StringUtils.secret(client_secret)}')"
        )
        self._network_manager = network_manager
        self._client_id = client_id
        self._client_secret = client_secret
        self._cached_token: Optional[AccessTokenSource.ExpiringToken] = None
        self._fetching = False
        KameleoonLogger.debug(
            lambda: f"RETURN: AccessTokenSource(network_manager, client_id: '{StringUtils.secret(client_id)}', "
                    f"client_secret: '{StringUtils.secret(client_secret)}')"
        )

    async def get_token(self, timeout: Optional[float] = None) -> Optional[str]:
        """Returns the access token. Fetches a new token if the cached one is expired or obsolete."""
        KameleoonLogger.debug("CALL: AccessTokenSource.get_token(timeout: %s)", timeout)
        now = time.time()
        token = self._cached_token
        if (token is None) or token.is_expired(now):
            return await self._call_fetch_token(timeout)
        if not self._fetching and token.is_obsolete(now):
            self._run_fetch_token()
        value = token.value
        KameleoonLogger.debug("RETURN: AccessTokenSource.get_token(timeout: %s) -> (token: %s)",
                              timeout, token)
        return value

    def discard_token(self, token: str) -> None:
        """Discards the specified token, if it matches the cached token."""
        KameleoonLogger.debug("CALL: AccessTokenSource.discard_token(token: %s)", token)
        cached_token = self._cached_token
        if cached_token and (cached_token.value == token):
            self._cached_token = None
        KameleoonLogger.debug("RETURN: AccessTokenSource.discard_token(token: %s)", token)

    async def _call_fetch_token(self, timeout: Optional[float]) -> Optional[str]:
        try:
            self._fetching = True
            return await self._fetch_token(timeout)
        except Exception as exception:  # pylint: disable=W0703
            KameleoonLogger.error("Failed to call access token fetching: %s", exception)
            self._fetching = False
            return None

    def _run_fetch_token(self) -> None:
        try:
            self._fetching = True
            asyncio.create_task(self._fetch_token())
        except Exception as exception:  # pylint: disable=W0703
            KameleoonLogger.error("Failed to run access token fetching: %s", exception)
            self._fetching = False

    async def _fetch_token(self, timeout: Optional[float] = None) -> Optional[str]:
        KameleoonLogger.debug("CALL: AccessTokenSource._fetch_token(timeout: %s)", timeout)
        try:
            service: AutomationService = self._network_manager.get_service(AutomationService)
            response = await service.fetch_access_jwtoken(self._client_id, self._client_secret, timeout)
            if not response.success:
                KameleoonLogger.error("Failed to fetch access JWT")
                return None
            if not isinstance(response.content, dict):
                KameleoonLogger.error("Failed to obtain proper access JWT")
                return None
            try:
                jwt = response.content
                token = jwt[self._JWT_ACCESS_TOKEN_FIELD]
                expires_in = jwt[self._JWT_EXPIRES_IN_FIELD]
            except Exception as exception:  # pylint: disable=W0703
                KameleoonLogger.error("Failed to parse access JWT: %s", exception)
                return None
            if not (isinstance(token, str) and token and isinstance(expires_in, int) and expires_in):
                KameleoonLogger.error("Failed to read access JWT")
                return None
            self._handle_fetched_token(token, expires_in)
            KameleoonLogger.debug("RETURN: AccessTokenSource._fetch_token(timeout: %s) -> (token: %s)",
                                  timeout, token)
            return token
        finally:
            self._fetching = False

    def _handle_fetched_token(self, token: str, expires_in: int) -> None:
        now = time.time()
        exp_time = now + expires_in - self._TOKEN_EXPIRATION_GAP
        if expires_in > self._TOKEN_OBSOLESCENCE_GAP:
            obs_time = now + expires_in - self._TOKEN_OBSOLESCENCE_GAP
        else:
            obs_time = exp_time
            if expires_in <= self._TOKEN_EXPIRATION_GAP:
                KameleoonLogger.error(
                    "Access token life time (%ss) is not long enough to cache the token", expires_in
                )
            else:
                KameleoonLogger.warning(
                    'Access token life time (%ss) is not long enough to refresh cached token in background', expires_in
                )
        self._cached_token = self.ExpiringToken(token, exp_time, obs_time)

    class ExpiringToken:
        """Expiring Token"""
        def __init__(self, value: str, expiration_time: float, obsolescence_time: float) -> None:
            self.value = value
            self.expiration_time = expiration_time
            self.obsolescence_time = obsolescence_time

        def is_expired(self, now: float) -> bool:
            """Checks if the token has expired based on the provided time."""
            return now >= self.expiration_time

        def is_obsolete(self, now: float) -> bool:
            """Checks if the token has become obsolete based on the provided time."""
            return now >= self.obsolescence_time
