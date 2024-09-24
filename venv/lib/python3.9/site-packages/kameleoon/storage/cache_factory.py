""" Kameleoon Visitor Variation """

from .cache import Cache, K, V


class CacheFactory:
    """`CacheFactory` is supposed to be used for creating instances of `Cache` type."""

    def create(self, expiration_period: float) -> Cache[K, V]:
        """
        Creates an instance of `Cache` type with specified expiration period.
        :param expiration_period: Expiration period of new instance of `Cache` type
        :type expiration_period: float
        :return: New instance of `Cache` type
        :rtype: Cache
        """
        raise NotImplementedError()
