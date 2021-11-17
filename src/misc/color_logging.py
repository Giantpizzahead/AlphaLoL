"""
Helper file for colorful logging!
"""

import logging
import os

import colorlog

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR
CRITICAL = logging.CRITICAL
LOG_FORMAT = "%(asctime)s %(name)-9.9s %(levelname)+9.9s  %(message)s"
basicFormatter = logging.Formatter(LOG_FORMAT)
colorFormatter = colorlog.ColoredFormatter("%(log_color)s" + LOG_FORMAT)


def getLogger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.hasHandlers():
        # Output colored logs to stderr
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(colorFormatter)
        consoleHandler.setLevel(level)
        logger.addHandler(consoleHandler)
        # Record logs in a file
        fileHandler = logging.FileHandler("{}/../../logs/{}.log".format(
            os.path.dirname(os.path.realpath(__file__)), name))
        fileHandler.setFormatter(basicFormatter)
        fileHandler.setLevel(level)
        logger.addHandler(fileHandler)
    return logger
