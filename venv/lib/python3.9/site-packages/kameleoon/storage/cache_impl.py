""" Kameleoon Visitor Variation """

import time
from typing import Dict, Tuple, Optional
from .cache import Cache, K, V


class CacheImpl(Cache[K, V]):
    """`CacheImpl` implements `Cache` interface."""

    def __init__(self, expiration_period: float):
        super().__init__(expiration_period)
        self.__items: Dict[K, Tuple[V, float]] = {}

    def __len__(self) -> int:
        return len(self.__items)

    def set(self, key: K, value: V) -> None:
        expiration_ts = time.time() + self._expiration_period
        self.__items[key] = (value, expiration_ts)

    def get(self, key: K) -> Optional[V]:
        item = self.__items.get(key, None)
        return item[0] if item is not None else None

    def clear(self) -> None:
        self.__items.clear()

    def purge(self) -> None:
        now = time.time()
        to_be_removed = [k for k, v in self.__items.items() if v[1] <= now]
        for key in to_be_removed:
            del self.__items[key]

    def __iter__(self):
        return ((k, v[0]) for k, v in self.__items.items())
