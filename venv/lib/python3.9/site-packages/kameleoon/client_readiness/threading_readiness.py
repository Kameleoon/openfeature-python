"""ThreadingClientReadiness"""
from threading import Lock


class ThreadingClientReadiness:
    """A class to manage and track the readiness of a component using threading."""

    def __init__(self) -> None:
        """Initializes the ThreadingClientReadiness object."""
        self._is_initializing = False
        self._success = False
        self._condition = Lock()
        self.reset()

    @property
    def is_initializing(self) -> bool:
        """Returns whether the component is currently initializing."""
        return self._is_initializing

    @property
    def success(self) -> bool:
        """Returns whether the initialization was successful."""
        return self._success

    def reset(self) -> None:
        """Resets the readiness state to initializing."""
        self._success = False
        if not self._is_initializing:
            self._is_initializing = True
            self._condition.acquire()  # pylint: disable=R1732

    def set(self, success: bool) -> None:
        """Sets the readiness state to initialized with a success status."""
        self._success = success
        if self._is_initializing:
            self._condition.release()
            self._is_initializing = False

    def wait(self) -> bool:
        """Waits for the initialization to complete and returns the success status."""
        if self._is_initializing:
            with self._condition:
                pass
        return self._success
