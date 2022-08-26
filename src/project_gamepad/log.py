import logging
from os import getenv

from colorama import Fore, Style


class CustomFormatter(logging.Formatter):

    format = f"[{Style.BRIGHT}%(levelname)s{Style.NORMAL}] %(asctime)s - %(name)s - %(message)s {Style.DIM}(%(filename)s:%(lineno)d){Style.RESET_ALL}"

    FORMATS = {
        logging.DEBUG: Fore.BLUE + format + Style.RESET_ALL,
        logging.INFO: Fore.WHITE + format + Style.RESET_ALL,
        logging.WARNING: Fore.YELLOW + format + Style.RESET_ALL,
        logging.ERROR: Fore.RED + format + Style.RESET_ALL,
        logging.CRITICAL: Fore.CYAN + format + Style.RESET_ALL,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name):
    level = logging.DEBUG if getenv("APP_ENV") == "DEV" else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)

    ch = logging.StreamHandler()
    ch.setLevel(level)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)
    return logger
