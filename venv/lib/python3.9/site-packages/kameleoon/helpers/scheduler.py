"""Helper class for scheduling multiple repetitive jobs"""

import asyncio
import concurrent.futures
import inspect
import time
from typing import Any, Callable, Dict, Optional
from kameleoon.logging.kameleoon_logger import KameleoonLogger


class Scheduler:
    """
    `Scheduler` is a helper class for scheduling multiple repetitive jobs.

    The usage order:
    1. Initialize an instance of `Scheduler`
    2. Schedule multiple jobs with `schedule_job` method
    3. Start the scheduler with `start` method
    4. When need to dispose, stop the scheduler with `stop` method
    """

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._jobs: Dict[str, Scheduler.Job] = {}
        self._loop = loop

    def schedule_job(self, key: str, interval: float, func: Callable[[], Any]) -> None:
        """
        Schedules a job. Both synchronous and asynchronous handlers are supported.

        Should be called before the scheduler is started.
        """
        self._jobs[key] = Scheduler.Job(key, interval, func)

    def start(self) -> None:
        """
        Starts the scheduler.

        Should not be called more than once.
        """
        for job in self._jobs.values():
            job.run(self._loop)

    def stop(self) -> None:
        """
        Starts all scheduled jobs.

        Should not be called more than once.
        """
        try:
            self._loop.call_soon_threadsafe(self._stop)
        except Exception as err:  # pylint: disable=W0703
            KameleoonLogger.error("Failed to stop scheduler: %s", err)

    def _stop(self) -> None:
        for job in self._jobs.values():
            if job.stop_signal is not None:
                job.stop_signal.set()

    class Job:
        """`Job` represents a scheduled job"""

        def __init__(self, key: str, interval: float, func: Callable[[], Any]) -> None:
            self.key = key
            self.interval = interval
            self.func = func
            self.stop_signal: Optional[asyncio.Event] = None
            self.future: Optional[concurrent.futures.Future[Any]] = None

        def run(self, loop: asyncio.AbstractEventLoop) -> None:
            """Starts the job execution in the given event loop."""
            if self.future is None:
                self.future = asyncio.run_coroutine_threadsafe(self._cycle(), loop)

        async def _cycle(self) -> None:
            self.stop_signal = asyncio.Event()
            interval = self.interval
            stop_task = asyncio.create_task(self.stop_signal.wait())
            while True:
                interval_task = asyncio.create_task(asyncio.sleep(interval))
                await asyncio.wait([stop_task, interval_task], return_when=asyncio.FIRST_COMPLETED)
                if self.stop_signal.is_set():
                    interval_task.cancel()
                    break
                start = time.time()
                await self.__trigger()
                elapsed = time.time() - start
                interval = self.interval - elapsed

        async def __trigger(self) -> None:
            try:
                result = self.func()
                if inspect.isawaitable(result):
                    await result
            except Exception as err:  # pylint: disable=W0703
                KameleoonLogger.error("Error occurred within %s job: %s", self.key, err)
