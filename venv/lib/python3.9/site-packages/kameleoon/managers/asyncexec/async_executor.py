"""Asyncexec"""
import asyncio
import concurrent.futures
from typing import Any, Coroutine, Optional
from kameleoon.helpers.multi_threading import ThreadEventLoop, get_running_loop
from kameleoon.helpers.scheduler import Scheduler
from kameleoon.logging.kameleoon_logger import KameleoonLogger


class AsyncExecutor:
    """Async Executor"""
    @property
    def thread_event_loop(self) -> Optional[ThreadEventLoop]:
        """Returns the thread event loop if it exists, otherwise returns `None`."""
        return self._thread_event_loop

    @property
    def scheduler(self) -> Scheduler:
        """Returns the scheduler."""
        return self._scheduler

    def __init__(self) -> None:
        self._thread_event_loop: Optional[ThreadEventLoop] = None
        if (loop := get_running_loop()) is not None:
            self._scheduler = Scheduler(loop)
        else:
            self._thread_event_loop = ThreadEventLoop()
            self._thread_event_loop.start()
            self._scheduler = Scheduler(self._thread_event_loop.get_loop())

    def run_coro(self, coro: Coroutine[Any, Any, Any], name: str) -> None:
        """Runs a coroutine using the appropriate event loop."""
        if self._thread_event_loop:
            if self._thread_event_loop.run_coro(coro) is not None:
                KameleoonLogger.debug("Coroutine %s is run on %s thread event loop",
                                      name, self._thread_event_loop.loop)
                return
            KameleoonLogger.warning("Failed to run %s on %s thread event loop.", name, self._thread_event_loop.loop)
        if (loop := get_running_loop()) is not None:
            try:
                loop.create_task(coro)
                KameleoonLogger.debug("Coroutine %s is run on %s event loop", name, loop)
                return
            except Exception:  # pylint: disable=W0703
                KameleoonLogger.warning("Failed to run %s on %s event loop.", name, loop)
        try:
            loop = asyncio.new_event_loop()
            loop.run_until_complete(coro)
            KameleoonLogger.debug("Coroutine %s was run on new %s event loop", name, loop)
            return
        except Exception:  # pylint: disable=W0703
            KameleoonLogger.warning("Failed to run %s on new %s event loop.", name, loop)
        KameleoonLogger.error("Unable to run %s: no running event loop, no thread event loop", name)

    def await_coro_synchronously(self, coro: Coroutine[Any, Any, Any], method_name: str) -> Optional[Any]:
        """
        Awaits a coroutine synchronously using the thread event loop.

        This is a blocking operation without timeout.
        """
        if self._thread_event_loop is None:
            tel = ThreadEventLoop()
            tel.start()
            self._thread_event_loop = tel
            KameleoonLogger.warning("Despite the mono-thread mode an event loop background thread has "
                                    "been started because of the call of synchronous %s method", method_name)
        future = self._thread_event_loop.run_coro(coro)
        if future is None:
            KameleoonLogger.error("Failed to run %s on %s thread event loop", method_name, self._thread_event_loop.loop)
            return None
        KameleoonLogger.debug("Asynchronous method %s is run on %s thread event loop",
                              method_name, self._thread_event_loop.loop)
        concurrent.futures.wait([future])
        if future.cancelled():
            KameleoonLogger.error("%s was cancelled", method_name)
        elif future.exception():
            KameleoonLogger.error("%s failed with exception: %s", method_name, future.exception())
        else:
            return future.result()
        return None
