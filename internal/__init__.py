import logging
import sys


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
logger = logging.getLogger(name="RSA_PARSER")
logger.setLevel(logging.INFO)
logger.addHandler(get_console_handler())


def getLogger():
    return logger
