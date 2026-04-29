import logging
from typing import final


@final
class ColorFormatter(logging.Formatter):
    cyan = "\x1b[36m"
    blue = "\x1b[34m"
    green = "\x1b[32m"
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    timestamp_format = "%(asctime)s"
    message_format = "%(levelname)-8s %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: blue
        + timestamp_format
        + reset
        + " "
        + cyan
        + message_format
        + reset,
        logging.INFO: blue
        + timestamp_format
        + reset
        + " "
        + green
        + message_format
        + reset,
        logging.WARNING: blue
        + timestamp_format
        + reset
        + " "
        + yellow
        + message_format
        + reset,
        logging.ERROR: blue
        + timestamp_format
        + reset
        + " "
        + red
        + message_format
        + reset,
        logging.CRITICAL: blue
        + timestamp_format
        + reset
        + " "
        + bold_red
        + message_format
        + reset,
    }

    def format(self, record):
        log_format = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)
