"""Network"""
from enum import Enum
from typing import Any, Dict, Optional


class ResponseContentType(Enum):
    """Response content type"""
    NONE = 0
    TEXT = 1
    JSON = 2


class HttpMethod(Enum):
    """Http method"""
    GET = "GET"
    POST = "POST"


class Response:
    """Response"""
    def __init__(self, error: Optional[Exception], code: Optional[int], content: Optional[Any]):
        self.error = error
        self.code = code
        self.content = content

    @property
    def success(self) -> bool:
        """Determines if the response was successful."""
        return (self.error is None) and self.is_expected_status_code

    @property
    def is_expected_status_code(self) -> bool:
        """Checks if the status code is one of the expected codes."""
        return (self.code is not None) and ((self.code // 100 == 2) or (self.code == 403))

    def __str__(self):
        return f"HttpResponse{{Code:{self.code},Error:{self.error},Body:'{self.content}'}}"


class Request:
    """Request"""
    # pylint: disable=R0913
    def __init__(
        self, method: HttpMethod, url: str, timeout: float,
        headers: Optional[Dict[str, str]] = None, body: Optional[str] = None,
        response_content_type=ResponseContentType.NONE,
    ) -> None:
        self.method = method
        self.url = url
        self.timeout = timeout
        self.headers = headers
        self.body = body
        self.response_content_type = response_content_type
        self.access_token: Optional[str] = None

    def authorize(self, access_token: Optional[str]) -> None:
        """Sets the access token for the request."""
        self.access_token = access_token

    def __str__(self):
        body = "None"
        if self.body is not None:
            body = "'****'" if self.body.startswith('grant_type=client_credentials') else f"'{self.body}'"
        return f"HttpRequest{{Method:'{self.method}',Url:'{self.url}',Headers:{self.headers},Body:{body}}}"


class NetProvider:
    """Abstract network provider"""
    async def close(self) -> None:
        """Closes the network provider."""
        raise NotImplementedError()

    async def run_request(self, request: Request) -> Response:
        """Executes an HTTP request."""
        raise NotImplementedError()
