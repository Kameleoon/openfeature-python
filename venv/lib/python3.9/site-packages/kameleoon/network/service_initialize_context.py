"""Network"""
from typing import Type
from kameleoon.network.services.service import Service


class ServiceInitializeContext:
    """Abstract service initialize context"""
    def set_service(self, service_type: Type[Service], service: Service):
        """Registers a service of the specified type in the context."""
        raise NotImplementedError()
