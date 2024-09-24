"""Services"""


class Service:
    """Abstract service"""
    @property
    def network_manager(self):
        """Returns the network manager instance."""
        raise NotImplementedError()
