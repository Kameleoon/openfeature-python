""" WSGIMiddlewares """
from http.cookies import SimpleCookie
from typing import Optional
from kameleoon.kameleoon_client import KameleoonClient
from kameleoon.network.cookie.cookie_manager import VISITOR_CODE_COOKIE

__all__ = [
    "KameleoonWSGIMiddleware",
]


class KameleoonWSGIMiddleware:
    """
    Automatically set kameleoon cookies
    """

    def __init__(self, app, client: KameleoonClient, default_visitor_code: Optional[str] = None):
        self.app = app
        self._client = client
        self._default_visitor_code = default_visitor_code

    def __call__(self, environ, start_response):
        http_cookie = environ.get("HTTP_COOKIE", "")
        cookies: SimpleCookie[str] = SimpleCookie()
        cookies.load(http_cookie)
        contains_visitor_code_cookie = VISITOR_CODE_COOKIE in cookies
        visitor_code = self._client.get_visitor_code(cookies=cookies, default_visitor_code=self._default_visitor_code)
        if not contains_visitor_code_cookie:
            if "HTTP_COOKIE" in environ:
                environ["HTTP_COOKIE"] += f"; {VISITOR_CODE_COOKIE}={visitor_code}"
            else:
                environ["HTTP_COOKIE"] = f"{VISITOR_CODE_COOKIE}={visitor_code}"

        def _custom_start_response(status, headers, exc_info=None):
            # pylint: disable=W0212
            self._client._cookie_manager.update(visitor_code, self._client._is_consent_given(visitor_code), cookies)
            headers.append(("Set-Cookie", cookies.output(header="")))
            return start_response(status, headers, exc_info)

        return self.app(environ, _custom_start_response)
