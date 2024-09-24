""" Kameleoon Visitor Variation """

from .cache import Cache, K, V
from .cache_impl import CacheImpl
from .cache_factory import CacheFactory


class CacheFactoryImpl(CacheFactory):
    """`CacheFactoryImpl` implements `CacheFactory` interface."""

    def create(self, expiration_period: float) -> Cache[K, V]:
        return CacheImpl(expiration_period)
