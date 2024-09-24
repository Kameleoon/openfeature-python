"""Helpers for running functions in multi-threading"""

import asyncio
import threading
import concurrent.futures
import time
from typing import Any, Callable, Coroutine, Optional


class ThreadEventLoop:
    """
    ThreadEventLoop is helper object to handle asynchronous tasks execution in a separate thread.
    """

    def __init__(self) -> None:
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.thread: Optional[threading.Thread] = None
        self.running_allowed = True

    def __thread_main(self) -> None:
        self.loop = asyncio.new_event_loop()
        self.loop.run_forever()

    def start(self) -> None:
        """Starts the thread and the event loop"""
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self.__thread_main, daemon=True)
        self.thread.start()

    def get_loop(self) -> asyncio.AbstractEventLoop:
        """
        Awaits the initialization of the event loop used by the `ThreadEventLoop` instance and returns it.

        It is a blocking operation with no timeout. Calling the method on the not started `ThreadEventLoop` instance
        will cause the deadlock.
        """
        while self.loop is None:
            time.sleep(0.01)
        return self.loop

    def stop(self) -> None:
        """Stops the thread and the event loop"""
        if self.thread is None:
            return
        self.running_allowed = False
        time.sleep(0.001)
        while self.count_tasks() > 0:
            time.sleep(0.01)
        loop = self.get_loop()
        loop.call_soon_threadsafe(loop.stop)
        self.thread.join()
        loop.close()

    def run_coro(self, coro: Coroutine[Any, Any, Any]) -> Optional[concurrent.futures.Future[Any]]:
        """
        Puts the specified coroutine to the event loop for background execution.
        :param coro: Coroutine to be executed
        :type coro: Coroutine[Any, Any, Any]
        :return: The future linked with the coroutine, or `None` if the thread event loop is closing.
        :rtype: Optional[concurrent.futures.Future[Any]]
        """
        if not self.running_allowed:
            return None
        if self.thread is None:
            self.start()
        return asyncio.run_coroutine_threadsafe(coro, self.get_loop())

    def count_tasks(self) -> int:
        """Returns the number of running tasks."""
        return len(asyncio.all_tasks(self.get_loop()))


def run_in_thread(
    func: Callable[[], Any], thread_name: Optional[str] = None, with_event_loop=False
) -> threading.Thread:
    """
    It's a wrapper function which runs the `func` in another thread.
    :param func: Function need to be called
    :type func: Callable[[], Any]
    :param with_event_loop: Flag enabling management of event loop.
    :type with_event_loop: bool
    :param thread_name: Name of thread if `func` runs in another thread
    :type args: Optional[str]
    :return: Created thread
    :rtype: threading.Thread
    """
    if with_event_loop:
        def target():
            loop = asyncio.new_event_loop()
            func()
            loop.close()
    else:
        target = func
    thread = threading.Thread(target=target)
    thread.daemon = True
    if thread_name:
        thread.setName(thread_name)
    thread.start()
    return thread


# def invoke_coro(coro: Coroutine[Any, Any, Any]) -> None:
#     """
#     Assigns the specified coroutine to a running event loop if has
#     otherwise invokes the coroutine in a new event loop.
#     """
#     try:
#         loop = asyncio.get_running_loop()
#         loop.create_task(coro)
#     except Exception:  # pylint: disable=W0703
#         get_loop().run_until_complete(coro)


def get_loop() -> asyncio.AbstractEventLoop:
    """Returns exisitng event loop or newly created one."""
    try:
        return asyncio.get_running_loop()
    except Exception:  # pylint: disable=W0703
        return asyncio.new_event_loop()


def has_running_event_loop() -> bool:
    """Checks if has a running event loop."""
    return get_running_loop() is not None


def get_running_loop() -> Optional[asyncio.AbstractEventLoop]:
    """Returns a running event loop if possible, otherwise returns `None`."""
    try:
        return asyncio.get_running_loop()
    except Exception:  # pylint: disable=W0703
        return None
