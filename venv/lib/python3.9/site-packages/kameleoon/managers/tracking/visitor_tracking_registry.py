"""Tracking"""
from threading import Lock
from typing import Iterable, List, Set
from kameleoon.data.manager.visitor_manager import VisitorManager


class VisitorTrackingRegistry:
    """
    Abstract visitor tracking registry.

    Must be thread-safe
    """
    def add(self, visitor_code: str) -> None:
        """Adds a single visitor code to the registry."""
        raise NotImplementedError()

    def add_all(self, visitor_codes: Iterable[str]) -> None:
        """Adds multiple visitor codes to the registry."""
        raise NotImplementedError()

    def extract(self) -> Iterable[str]:
        """Extracts and returns stored visitor codes from the registry."""
        raise NotImplementedError()


class LockVisitorTrackingRegistry(VisitorTrackingRegistry):
    """An implementation of the `VisitorTrackingRegistry` based on the `threading.Lock`"""
    LIMITED_EXTRACTION_THRESHOLD_COEFFICIENT = 2
    REMOVAL_FACTOR = 0.8

    def __init__(self, visitor_manager: VisitorManager, storage_limit=1000_000, extraction_limit=20_000) -> None:
        self._visitor_manager = visitor_manager
        self._storage_limit = storage_limit
        self._extraction_limit = extraction_limit
        self._visitors: Set[str] = set()
        self._lock = Lock()

    def add(self, visitor_code: str) -> None:
        """Adds a single visitor code to the registry."""
        with self._lock:
            self._visitors.add(visitor_code)

    def add_all(self, visitor_codes: Iterable[str]) -> None:
        """Adds multiple visitor codes to the registry."""
        with self._lock:
            self._visitors.update(visitor_codes)
            if len(self._visitors) > self._storage_limit:
                self.__erase_nonexistent_visitors()
                self.__erase_to_storage_limit()

    def __erase_nonexistent_visitors(self) -> None:
        """Not thread-safe"""
        visitors_to_remove = [vc for vc in self._visitors if self._visitor_manager.get_visitor(vc) is None]
        self._visitors.difference_update(visitors_to_remove)

    def __erase_to_storage_limit(self) -> None:
        """Not thread-safe"""
        visitors_to_remove_count = len(self._visitors) - int(self._storage_limit * self.REMOVAL_FACTOR)
        for _ in range(visitors_to_remove_count):
            self._visitors.pop()

    def extract(self) -> Iterable[str]:
        """
        Extracts and returns visitor codes from the registry. The number of the extracted visitor codes
        is limited to the doubled `extraction_limit`.
        """
        return self.__extract_all() if self.__should_extract_all_be_used() else self.__extract_limited()

    def __should_extract_all_be_used(self) -> bool:
        return len(self._visitors) < self._extraction_limit * self.LIMITED_EXTRACTION_THRESHOLD_COEFFICIENT

    def __extract_all(self) -> Iterable[str]:
        new_visitors: Set[str] = set()
        with self._lock:
            old_visitors = self._visitors
            self._visitors = new_visitors
        return old_visitors

    def __extract_limited(self) -> Iterable[str]:
        with self._lock:
            if self.__should_extract_all_be_used():
                return self.__extract_all()
            extracted: List[str] = [""] * self._extraction_limit
            for i, visitor_code in enumerate(self._visitors):
                if i >= self._extraction_limit:
                    break
                extracted[i] = visitor_code
            self._visitors.difference_update(extracted)
            return extracted
