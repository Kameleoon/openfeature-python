"""Network"""
import asyncio
import threading
from typing import Dict

import aiohttp

from kameleoon.network.net_provider import NetProvider, ResponseContentType, Response, Request


class NetProviderImpl(NetProvider):
    """Network provider implementation"""
    __SESSIONS_PURGE_TRIGGER_THRESHOLD = 8
    _H_AUTHORIZATION = "Authorization"

    def __init__(self) -> None:
        self.__sessions: Dict[asyncio.AbstractEventLoop, aiohttp.ClientSession] = {}
        self.__sessions_lock = threading.Lock()

    @property
    async def _session(self) -> aiohttp.ClientSession:
        loop = asyncio.get_running_loop()
        session = self.__sessions.get(loop)
        if session is None:
            with self.__sessions_lock:
                session = self.__sessions.get(loop)
                if session is None:
                    if len(self.__sessions) > self.__SESSIONS_PURGE_TRIGGER_THRESHOLD:
                        await self.__purge_sessions()
                    session = aiohttp.ClientSession()
                    self.__sessions[loop] = session
        return session

    async def __purge_sessions(self) -> None:
        for loop, session in list(self.__sessions.items()):
            if loop.is_closed():
                await session.close()
                del self.__sessions[loop]

    async def close(self) -> None:
        with self.__sessions_lock:
            await asyncio.gather(*(session.close() for session in self.__sessions.values()))

    async def run_request(self, request: Request) -> Response:
        try:
            session = await self._session
            headers = self._collect_headers(request)
            async with await session.request(
                request.method.value, request.url, headers=headers, timeout=request.timeout, data=request.body
            ) as resp:
                response = await self.__form_response(resp, request.response_content_type)
                resp.close()
                return response
        except KeyError as exception:
            raise exception
        except Exception as err:  # pylint: disable=W0703
            return Response(err, None, None)

    @staticmethod
    def _collect_headers(request: Request) -> Dict[str, str]:
        headers = {}
        if request.headers:
            headers.update(request.headers)
        if request.access_token:
            headers[NetProviderImpl._H_AUTHORIZATION] = f"Bearer {request.access_token}"
        return headers

    @staticmethod
    async def __form_response(resp, response_content_type: ResponseContentType) -> Response:
        try:
            if response_content_type == ResponseContentType.TEXT:
                content = await resp.text()
            elif response_content_type == ResponseContentType.JSON:
                content = await resp.json()
            else:
                content = None
        except aiohttp.ContentTypeError:
            content = None
        return Response(None, resp.status, content)
