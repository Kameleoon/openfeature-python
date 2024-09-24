"""Logger"""

import logging


class Logger:
    """Singletong logger class"""

    def __new__(cls) -> "Logger":
        if not hasattr(cls, "instance"):
            cls.instance = super(Logger, cls).__new__(cls)
            cls.instance.__init_logger()
        return cls.instance

    def __init_logger(self) -> None:  # pylint: disable=W0238
        self.kameleoon_logger = logging.getLogger("Kameleoon SDK")
        self.kameleoon_logger.setLevel(logging.DEBUG)

        # Add a handler (console handler in this example)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # Create a formatter and attach it to the handler
        formatter = logging.Formatter("%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s")
        console_handler.setFormatter(formatter)

        # Attach the handler to the logger
        self.kameleoon_logger.addHandler(console_handler)

    @staticmethod
    def shared() -> logging.Logger:
        """Return default logger instance"""
        return Logger().instance.kameleoon_logger
