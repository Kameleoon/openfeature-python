"""Unique identifier"""


class UniqueIdentifier:
    """Unique identifier"""
    def __init__(self, value: bool) -> None:
        self.__value = value

    @property
    def value(self) -> bool:
        """Return value"""
        return self.__value
