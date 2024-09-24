""" Kameleoon Visitor Variation """

from typing import TypeVar, Generic, Optional


K = TypeVar("K")  # pylint: disable=C0103
V = TypeVar("V")  # pylint: disable=C0103


class Cache(Generic[K, V]):
    """
    Interface `Cache` represents a container type that is supposed to store relevant values by distinct keys
    and to manage relevance of the stored values and is not supposed to be thread safe.
    """

    def __init__(self, expiration_period: float):
        if expiration_period <= 0.0:
            raise ValueError("'expiration_period' arg must have positive value!")
        self._expiration_period = expiration_period

    @property
    def expiration_period(self) -> float:
        """
        Period during which a stored value is considered as relevant.
        :return: Expiration period
        :rtype: float
        """
        return self._expiration_period

    def __len__(self) -> int:
        raise NotImplementedError()

    def set(self, key: K, value: V) -> None:
        """
        If item stored by specified key exists, this method updates its value and its relevance,
        otherwise this method creates new relevant item with specified key and value.
        :param key: Key
        :type key: K
        :param value: New value
        :type value: V
        """
        raise NotImplementedError()

    def get(self, key: K) -> Optional[V]:
        """
        Makes an attempt to get value of item stored by specified key.
        :param key: Key
        :type key: K
        :return: Stored value or None if operation fails
        :rtype: Optional[V]
        """
        raise NotImplementedError()

    def clear(self) -> None:
        """
        Removes all stored values.
        """
        raise NotImplementedError()

    def purge(self) -> None:
        """
        Removes all expired items.
        """
        raise NotImplementedError()

    def __iter__(self):
        raise NotImplementedError()
