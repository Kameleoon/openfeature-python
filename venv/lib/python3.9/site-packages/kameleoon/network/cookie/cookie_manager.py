"""Cookie"""

import datetime
from http.cookies import SimpleCookie, Morsel
from typing import Dict, Optional, Union
from kameleoon.helpers.visitor_code import generate_visitor_code, validate_visitor_code
from kameleoon.logging.kameleoon_logger import KameleoonLogger
from kameleoon.managers.data.data_manager import DataManager


COOKIE_KEY_JS = "_js_"
VISITOR_CODE_COOKIE = "kameleoonVisitorCode"
COOKIE_TTL = datetime.timedelta(days=380)
MAX_AGE = str(int(COOKIE_TTL.total_seconds()))


class CookieManager:
    """Cookie manager"""

    _ENCODER: SimpleCookie[str] = SimpleCookie()

    def __init__(self, data_manager: DataManager, top_level_domain: str) -> None:
        KameleoonLogger.debug("CALL: CookieManager(data_manager, top_level_domain: %s)", top_level_domain)
        self._data_manager = data_manager
        self._top_level_domain = top_level_domain
        KameleoonLogger.debug("RETURN: CookieManager(data_manager, top_level_domain: %s)", top_level_domain)

    # fmt is disabled due issue in pylint, disabling R0801 doesn’t work
    # fmt: off
    def get_or_add(
        self, cookies_readonly: Optional[Dict[str, str]] = None,
        cookies: Optional[Dict[str, Morsel[str]]] = None,
        default_visitor_code: Optional[str] = None,
    ) -> str:
        # fmt: on
        """
        Retrieves and returns a visitor code from the provided cookies if it exists. In other case uses
        the `default_visitor_code` as a new visitor code if provided, otherwise generates a new visitor code.
        Then the new visitor code is added to the cookies unless the cookies are passed as `cookies_readonly`
        and not as `cookies`. Then returns the new visitor code.
        """
        KameleoonLogger.debug(
            "CALL: CookieManager.get_or_add(cookies_readonly: %s, cookies: %s, default_visitor_code: %s)",
            cookies_readonly, cookies, default_visitor_code)
        visitor_code = self._get_visitor_code_from_cookies(cookies_readonly or cookies or {})
        if visitor_code is not None:
            validate_visitor_code(visitor_code)
            KameleoonLogger.debug("Read visitor code %s from cookies %s", visitor_code, cookies)
        elif default_visitor_code is None:
            visitor_code = generate_visitor_code()
            KameleoonLogger.debug("Generated new visitor code %s", visitor_code)
            if not self._data_manager.is_visitor_code_managed and cookies is not None:
                self._add(visitor_code, cookies)
        else:
            validate_visitor_code(default_visitor_code)
            visitor_code = default_visitor_code
            KameleoonLogger.debug("Used default visitor code '%s'", default_visitor_code)
            if cookies is not None:
                self._add(visitor_code, cookies)
        KameleoonLogger.debug(
            "RETURN: CookieManager.get_or_add(cookies_readonly: %s, cookies: %s, default_visitor_code: %s)"
            " -> (visitor_code: %s)", cookies_readonly, cookies, default_visitor_code, visitor_code)
        return visitor_code

    def update(self, visitor_code: str, consent: bool, cookies: Dict[str, Morsel[str]]) -> None:
        """Updates cookies based on the visitor's consent."""
        KameleoonLogger.debug("CALL: CookieManager.update(visitor_code: %s, consent: %s, cookies: %s)",
                              visitor_code, consent, cookies)
        if consent:
            self._add(visitor_code, cookies)
        else:
            self._remove(cookies)
        KameleoonLogger.debug("RETURN: CookieManager.update(visitor_code: %s, consent: %s, cookies: %s)",
                              visitor_code, consent, cookies)

    def _add(self, visitor_code: str, cookies: Dict[str, Morsel[str]]) -> None:
        KameleoonLogger.debug("CALL: CookieManager._add(visitor_code: %s, cookies: %s)", visitor_code, cookies)
        morsel: Morsel[str] = Morsel()
        morsel.set(VISITOR_CODE_COOKIE, *self._ENCODER.value_encode(visitor_code))
        morsel["domain"] = self._top_level_domain
        morsel["path"] = "/"
        expires = datetime.datetime.now(datetime.timezone.utc) + COOKIE_TTL
        morsel["expires"] = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")
        morsel["max-age"] = MAX_AGE
        cookies[VISITOR_CODE_COOKIE] = morsel
        KameleoonLogger.debug("RETURN: CookieManager._add(visitor_code: %s, cookies: %s)", visitor_code, cookies)

    def _remove(self, cookies: Dict[str, Morsel[str]]) -> None:
        KameleoonLogger.debug("CALL: CookieManager._remove(cookies: %s)", cookies)
        if self._data_manager.is_visitor_code_managed:
            if morsel := cookies.get(VISITOR_CODE_COOKIE):
                morsel["domain"] = self._top_level_domain
                morsel["path"] = "/"
                morsel["max-age"] = "0"
        KameleoonLogger.debug("RETURN: CookieManager._remove(cookies: %s)", cookies)

    @staticmethod
    def _get_visitor_code_from_cookies(cookies: Union[Dict[str, str], Dict[str, Morsel[str]]]) -> Optional[str]:
        visitor_code = None
        visitor_code_cookie = cookies.get(VISITOR_CODE_COOKIE)
        if visitor_code_cookie:
            # SimpleCookie or request.COOKIES could be passed to the method, we should determine what exactly
            visitor_code = visitor_code_cookie if isinstance(visitor_code_cookie, str) else visitor_code_cookie.value
            if visitor_code.startswith(COOKIE_KEY_JS):
                visitor_code = visitor_code[len(COOKIE_KEY_JS) :]
            visitor_code = visitor_code if visitor_code else None
        return visitor_code
