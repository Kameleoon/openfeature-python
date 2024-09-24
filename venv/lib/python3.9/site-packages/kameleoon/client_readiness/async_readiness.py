"Async Client Readiness"

import asyncio
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from typing import Dict
from kameleoon.client_readiness.threading_readiness import ThreadingClientReadiness


class AsyncClientReadiness:
    """
    A class that provides an asynchronous interface for checking client readiness.

    This class wraps around a `ThreadingClientReadiness` object to provide asynchronous
    methods for waiting for the client to be ready. It uses a thread pool executor to
    run blocking operations in a separate thread.
    """

    def __init__(self, inner: ThreadingClientReadiness) -> None:
        """
        Initializes an AsyncClientReadiness instance.
        """
        super().__init__()
        self._inner = inner
        self._executor: Dict[int, ThreadPoolExecutor] = defaultdict(ThreadPoolExecutor)

    @property
    def inner(self) -> ThreadingClientReadiness:
        """
        Returns the inner ThreadingClientReadiness instance.
        """
        return self._inner

    def dispose_on_set(self) -> None:
        """
        Disposes of the executors by clearing the executor dictionary.
        """
        self._executor.clear()

    async def wait(self) -> bool:
        """
        Asynchronously waits for the client readiness operation to complete.
        """
        if self._inner.is_initializing:
            executor = self._executor[0]
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(executor, self._inner.wait)
        return self._inner.success
