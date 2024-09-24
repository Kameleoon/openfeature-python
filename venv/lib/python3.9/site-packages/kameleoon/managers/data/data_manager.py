"""Data manager"""

from kameleoon.configuration.data_file import DataFile
from kameleoon.logging.kameleoon_logger import KameleoonLogger


class DataManager:
    """Data manager"""

    def __init__(self, data_file: DataFile) -> None:
        KameleoonLogger.debug("CALL: DataManager(data_file: %s)", data_file)
        self.__container = DataManager.Container(data_file)
        KameleoonLogger.debug("RETURN: DataManager(data_file: %s)", data_file)

    @property
    def data_file(self) -> DataFile:
        """Returns the `DataFile` associated with this instance."""
        return self.__container.data_file

    @data_file.setter
    def data_file(self, value: DataFile) -> None:
        """Sets a new `DataFile` for this instance by updating the container."""
        self.__container = DataManager.Container(value)

    @property
    def is_visitor_code_managed(self) -> bool:
        """Returns `True` if consent is required, otherwise returns `False`."""
        return self.__container.is_visitor_code_managed

    # pylint: disable=R0903
    class Container:
        """Container"""

        def __init__(self, data_file: DataFile) -> None:
            KameleoonLogger.debug("CALL: DataManager.Container(data_file: %s)", data_file)
            self.data_file = data_file
            # Regarding GDPR policy we should set visitorCode if legal consent isn't required or we have at
            # least one Targeted Delivery rule in datafile
            self.is_visitor_code_managed = (
                data_file.settings.is_consent_required and not data_file.has_any_targeted_delivery_rule
            )
            KameleoonLogger.debug("RETURN: DataManager.Container(data_file: %s)", data_file)
