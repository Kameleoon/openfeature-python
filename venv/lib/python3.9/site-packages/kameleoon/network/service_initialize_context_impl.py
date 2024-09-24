"""Network"""
from typing import Dict, Type
from kameleoon.network.service_initialize_context import ServiceInitializeContext
from kameleoon.network.services.service import Service


class ServiceInitializeContextImpl(ServiceInitializeContext):
    """Service initialize context implementation"""
    def __init__(self, services: Dict[Type[Service], Service]):
        super().__init__()
        self.__services = services

    def set_service(self, service_type: Type[Service], service: Service):
        self.__services[service_type] = service
